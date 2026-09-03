# digital-twin/src/main.py
import asyncio
import signal
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.config import settings
from src.logger import setup_logging
from src.twin import PumpingStationTwin
from src.opcua_server import OPCUAServer
from src.mqtt_client import MQTTClient

logger = setup_logging()


async def run_opcua_until_stopped(opcua_server: OPCUAServer, stop_event: asyncio.Event):
    task = asyncio.create_task(opcua_server.start())
    await stop_event.wait()
    logger.info("🛑 Arrêt du serveur OPC UA...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def main():
    logger.info("🚀 Démarrage du Jumeau Numérique")
    logger.info(f"Config OPC UA={settings.opcua_host}:{settings.opcua_port} "
                f"MQTT(controle uniquement)={settings.mqtt_broker}:{settings.mqtt_port}")

    twin = PumpingStationTwin()
    # system_state reste False (defaut) -> demarrage manuel via MQTT (topic pompage/control)
    twin.demand_flow = settings.initial_demand_flow
    logger.info(f"✅ Jumeau initialisé en mode ARRÊTÉ - DemandFlow: {twin.demand_flow}")
    logger.info("   -> publier START sur pompage/control pour démarrer")

    opcua_server = OPCUAServer(twin)

    # MQTT uniquement pour ECOUTER les commandes de controle - aucune publication
    # periodique de donnees ici (les donnees transitent par OPC UA -> Node-RED -> MQTT)
    mqtt_client = MQTTClient(twin)
    if not mqtt_client.connect():
        logger.warning("⚠️ MQTT non connecté — les commandes START/STOP/TEST_* ne fonctionneront pas")
    else:
        logger.info("✅ MQTT connecté (écoute pompage/control et pompage/commands)")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def request_shutdown(sig_name: str):
        logger.info(f"🛑 Signal {sig_name} reçu")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_shutdown, sig.name)
        except NotImplementedError:
            pass

    try:
        await run_opcua_until_stopped(opcua_server, stop_event)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
    finally:
        mqtt_client.disconnect()
        logger.info("👋 Jumeau numérique arrêté proprement")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Interruption clavier")