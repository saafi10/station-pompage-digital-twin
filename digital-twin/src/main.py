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


async def publish_mqtt_periodically(mqtt_client: MQTTClient, interval: float, stop_event: asyncio.Event):
    """Publie les données MQTT périodiquement jusqu'à ce que stop_event soit levé."""
    while not stop_event.is_set():
        try:
            mqtt_client.publish_twin_data()
        except Exception as e:
            logger.error(f"Erreur de publication MQTT: {e}")
        try:
            await asyncio.wait_for(stop_event.wait(), timeout=interval)
        except asyncio.TimeoutError:
            pass  # cycle normal, on reboucle


async def run_opcua_until_stopped(opcua_server: OPCUAServer, stop_event: asyncio.Event):
    """Enveloppe opcua_server.start() (boucle infinie) et s'arrête proprement sur stop_event."""
    task = asyncio.create_task(opcua_server.start())
    await stop_event.wait()
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


async def main():
    logger.info("🚀 Démarrage du Jumeau Numérique")
    logger.info(f"Config: MQTT={settings.mqtt_broker}:{settings.mqtt_port} "
                f"OPC UA={settings.opcua_host}:{settings.opcua_port}")

    twin = PumpingStationTwin()
    twin.system_state = True
    twin.demand_flow = settings.initial_demand_flow
    logger.info(f"✅ Jumeau initialisé - DemandFlow: {twin.demand_flow}")

    opcua_server = OPCUAServer(twin)
    mqtt_client = MQTTClient(twin)

    if not mqtt_client.connect():
        logger.warning("⚠️ MQTT non connecté, le twin continue sans publication MQTT")
    else:
        logger.info("✅ MQTT connecté")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    def _request_shutdown(sig_name: str):
        logger.info(f"🛑 Signal {sig_name} reçu, arrêt en cours...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _request_shutdown, sig.name)
        except NotImplementedError:
            # add_signal_handler non supporté (ex: Windows) — fallback silencieux,
            # KeyboardInterrupt sera capturé plus bas
            pass

    tasks = [
        run_opcua_until_stopped(opcua_server, stop_event),
        publish_mqtt_periodically(mqtt_client, settings.mqtt_publish_interval, stop_event),
    ]

    try:
        await asyncio.gather(*tasks)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
    finally:
        mqtt_client.disconnect()
        logger.info("👋 Jumeau numérique arrêté proprement")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Interruption clavier — arrêt")