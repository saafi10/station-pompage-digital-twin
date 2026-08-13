# digital-twin/src/mqtt_client.py
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
        
        self.topic_data_raw = "pompage/data/raw"
        self.topic_data_processed = "pompage/data/processed"
        self.topic_commands = "pompage/commands"
        self.topic_alarms = "pompage/alarms"
        self.topic_metrics = "pompage/metrics"
        self.topic_status = "pompage/status"
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connecté au broker MQTT {self.broker}:{self.port}")
            client.subscribe(self.topic_commands)
            client.subscribe("pompage/+/set")
        else:
            self.connected = False
            logger.error(f"❌ Erreur de connexion MQTT: {rc}")
    
    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            logger.info(f"📩 Message reçu sur {topic}: {payload}")
            
            if 'demand_flow' in payload:
                self.twin.demand_flow = max(0, min(200, float(payload['demand_flow'])))
                logger.info(f"📈 DemandFlow modifié: {self.twin.demand_flow} m³/h")
            if 'pump_a_fault' in payload:
                self.twin.pump_a_fault = bool(payload['pump_a_fault'])
                logger.info(f"⚠️ Pompe A panne: {self.twin.pump_a_fault}")
            if 'pump_b_fault' in payload:
                self.twin.pump_b_fault = bool(payload['pump_b_fault'])
                logger.info(f"⚠️ Pompe B panne: {self.twin.pump_b_fault}")
            if 'reset' in payload and payload['reset']:
                self.twin.pump_a_fault = False
                self.twin.pump_b_fault = False
                self.twin.filter_fault = False
                self.twin.power_outage = False
                logger.info("🔄 Réinitialisation du système")
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
    
    def publish(self, topic: str, data: dict, retain: bool = False):
        if not self.connected:
            logger.debug(f"MQTT non connecté, message non publié sur {topic}")
            return
        try:
            self.client.publish(topic, json.dumps(data, default=str), qos=1, retain=retain)
            logger.debug(f"📤 Données publiées sur {topic}")
        except Exception as e:
            logger.error(f"❌ Erreur de publication MQTT: {e}")
    
    def publish_twin_data(self):
        if not self.connected:
            return
        
        data = self.twin.get_all_data()
        logger.info("📤 Publication des données du jumeau")
        
        # Données traitées (simplifiées)
        processed = {
            'timestamp': data['simulation_time'],
            'pumps': {
                'a': {
                    'flow': data['pump_a_flow'],
                    'pressure': data['pump_a_pressure'],
                    'current': data['pump_a_current'],
                    'vibration': data['pump_a_vibration'],
                    'temperature': data['pump_a_temperature'],
                    'status': data['pump_a_status'],
                    'efficiency': data['pump_a_efficiency'],
                    'power': data['pump_a_power']
                },
                'b': {
                    'flow': data['pump_b_flow'],
                    'pressure': data['pump_b_pressure'],
                    'current': data['pump_b_current'],
                    'vibration': data['pump_b_vibration'],
                    'temperature': data['pump_b_temperature'],
                    'status': data['pump_b_status'],
                    'efficiency': data['pump_b_efficiency'],
                    'power': data['pump_b_power']
                },
                'active': data['active_pump']
            },
            'filter': {
                'flow': data['filter_flow_rate'],
                'pressure_drop': data['filter_pressure_drop'],
                'clogging': data['filter_clogging'],
                'efficiency': data['filter_efficiency']
            },
            'tank': {
                'level': data['tank_level']
            },
            'performance': {
                'efficiency': data['system_efficiency'],
                'energy_consumption': data['energy_consumption']
            }
        }
        self.publish(self.topic_data_processed, processed)
        
        # Statut
        status = {
            'timestamp': data['simulation_time'],
            'system_state': data['system_state'],
            'active_pump': data['active_pump'],
            'pump_a': 'RUNNING' if data['pump_a_status'] else 'STOPPED',
            'pump_b': 'RUNNING' if data['pump_b_status'] else 'STOPPED',
            'alarm': data['alarm_system_error']
        }
        self.publish(self.topic_status, status, retain=True)
    
    def disconnect(self):
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Déconnecté du broker MQTT")
