# digital-twin/src/main.py
import asyncio
import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.twin import PumpingStationTwin
from src.opcua_server import OPCUAServer
from src.mqtt_client import MQTTClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def publish_mqtt_periodically(mqtt_client, interval=1.0):
    """Publie les données MQTT périodiquement"""
    while True:
        try:
            mqtt_client.publish_twin_data()
            logger.debug("📤 Données MQTT publiées")
        except Exception as e:
            logger.error(f"Erreur de publication MQTT: {e}")
        await asyncio.sleep(interval)

async def main():
    logger.info("🚀 Démarrage du Jumeau Numérique avec MQTT")
    
    # Créer le jumeau
    twin = PumpingStationTwin()
    twin.system_state = True
    twin.demand_flow = 100.0
    logger.info(f"✅ Jumeau initialisé - DemandFlow: {twin.demand_flow}")
    
    # Démarrer les composants
    opcua_server = OPCUAServer(twin)
    mqtt_client = MQTTClient(twin)
    
    # Connecter MQTT
    if not mqtt_client.connect():
        logger.warning("⚠️ MQTT non connecté, continuation sans MQTT")
    else:
        logger.info("✅ MQTT connecté")
    
    # Démarrer tous les services en parallèle
    tasks = [
        opcua_server.start(),
        publish_mqtt_periodically(mqtt_client, 1.0)
    ]
    
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("👋 Arrêt du jumeau numérique")
        mqtt_client.disconnect()
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 Arrêt du jumeau numérique")
