import json
import logging
import os
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class MQTTClient:
    def __init__(self, twin):
        self.twin = twin
        self.broker = os.getenv('MQTT_BROKER', 'mqtt-broker')
        self.port = int(os.getenv('MQTT_PORT', 1883))
        self.client = None
        self.connected = False
        self.topic_commands = "pompage/commands"
        self.topic_control = "pompage/control"

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connecté au broker MQTT {self.broker}:{self.port}")
            client.subscribe(self.topic_commands)
            client.subscribe(self.topic_control)
            logger.info(f"✅ Abonné à {self.topic_control} et {self.topic_commands}")
        else:
            self.connected = False
            logger.error(f"❌ Erreur de connexion MQTT: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload_str = msg.payload.decode()
            logger.info(f"📩 Message reçu sur {topic}: {payload_str}")

            if topic == self.topic_control:
                command = payload_str.strip()
                if command == "START":
                    self.twin.system_state = True
                    logger.info("▶️ system_state -> True")
                elif command == "STOP":
                    self.twin.system_state = False
                    logger.info("⏹️ system_state -> False")
                elif command == "TEST_OVERHEAT":
                    self.twin.set_mode('TEST_OVERHEAT')
                    logger.info("🔥 system_mode -> TEST_OVERHEAT")
                elif command == "TEST_VIBRATION":
                    self.twin.set_mode('TEST_VIBRATION')
                    logger.info("⚡ system_mode -> TEST_VIBRATION")
                elif command == "TEST_FILTER":
                    self.twin.set_mode('TEST_FILTER')
                    logger.info("🧹 system_mode -> TEST_FILTER")
                elif command == "NORMAL":
                    self.twin.set_mode('NORMAL')
                    logger.info("✅ system_mode -> NORMAL")
                else:
                    logger.warning(f"⚠️ Commande inconnue: {command}")
                return

            payload = json.loads(payload_str)
            if 'demand_flow' in payload:
                self.twin.demand_flow = max(0, min(200, float(payload['demand_flow'])))
                logger.info(f"📈 demand_flow -> {self.twin.demand_flow}")
        except Exception as e:
            logger.error(f"❌ Erreur de traitement MQTT: {e}")

    def connect(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"❌ Erreur de connexion MQTT: {e}")
            return False

    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False