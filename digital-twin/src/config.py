# digital-twin/src/config.py
"""Configuration centralisée du digital twin, chargée depuis les variables
d'environnement (avec valeurs par défaut). Évite les adresses/ports en dur
dispersés dans le code."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # MQTT
    mqtt_broker: str = os.getenv("MQTT_BROKER", "mqtt-broker")
    mqtt_port: int = int(os.getenv("MQTT_PORT", 1883))
    mqtt_keepalive: int = int(os.getenv("MQTT_KEEPALIVE", 60))

    # OPC UA
    opcua_host: str = os.getenv("OPCUA_HOST", "0.0.0.0")
    opcua_port: int = int(os.getenv("OPCUA_PORT", 4840))

    # Simulation
    twin_update_interval: float = float(os.getenv("TWIN_UPDATE_INTERVAL", 0.1))
    mqtt_publish_interval: float = float(os.getenv("MQTT_PUBLISH_INTERVAL", 1.0))
    initial_demand_flow: float = float(os.getenv("INITIAL_DEMAND_FLOW", 100.0))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_dir: str = os.getenv("LOG_DIR", "/app/data")
    log_file: str = os.getenv("LOG_FILE", "twin.log")


settings = Settings()