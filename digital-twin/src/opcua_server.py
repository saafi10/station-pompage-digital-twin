# digital-twin/src/opcua_server.py
import asyncio
import logging
from asyncua import Server, ua

from src.config import settings

logger = logging.getLogger(__name__)


class OPCUAServer:
    """Expose la télémétrie du twin en lecture seule sur OPC UA.
    Le contrôle (START/STOP/TEST_*) passe par MQTT (mqtt_client.py), pas par ici."""

    def __init__(self, twin):
        self.twin = twin
        self.server = Server()
        self.server.set_endpoint(f"opc.tcp://{settings.opcua_host}:{settings.opcua_port}/freeopcua/server/")
        self.server.set_server_name("Pumping Station Digital Twin")
        self.uri = "http://pumpingstation.twin"
        self.idx = None
        self.vars = {}

    async def init(self):
        await self.server.init()
        self.idx = await self.server.register_namespace(self.uri)
        logger.info(f"✅ Namespace OPC UA enregistré: {self.idx}")

        objects = self.server.nodes.objects
        twin_node = await objects.add_object(self.idx, "DigitalTwin")

        variables = {
            'system_state': False,
            'system_mode': 'NORMAL',
            'demand_flow': 100.0,
            'pump_a_flow': 0.0,
            'pump_a_pressure': 0.0,
            'pump_a_current': 0.0,
            'pump_a_vibration': 0.0,
            'pump_a_temperature': 25.0,
            'pump_a_status': False,
            'pump_a_efficiency': 0.0,
            'pump_a_power': 0.0,
            'pump_b_flow': 0.0,
            'pump_b_pressure': 0.0,
            'filter_flow_rate': 0.0,
            'filter_pressure_drop': 0.0,
            'filter_clogging': 0.0,
            'tank_level': 2.5,
            'sea_water_temp': 22.5,
            'chlore_residuel': 0.8,
            'chlore_injection_rate': 0.0,
            'hx_sea_water_out_temp': 0.0,
            'hx_delta_t': 0.0,
            'discharge_temp': 0.0,
            'discharge_flow': 0.0,
            'system_efficiency': 0.0,
            'energy_consumption': 0.0,
            'alarm_system_error': False,
        }

        for var_name, default_value in variables.items():
            try:
                nodeid = ua.NodeId(var_name, self.idx, ua.NodeIdType.String)
                var = await twin_node.add_variable(nodeid, var_name, default_value)
                await var.set_writable(False)  # lecture seule - le controle passe par MQTT
                self.vars[var_name] = var
            except Exception as e:
                logger.error(f"Erreur ajout variable {var_name}: {e}")

        logger.info(f"✅ {len(self.vars)} variables OPC UA exposées (lecture seule)")

    async def update(self):
        try:
            data = self.twin.get_all_data()
            for var_name, var in self.vars.items():
                if var_name in data and data[var_name] is not None:
                    await var.write_value(data[var_name])
        except Exception as e:
            logger.error(f"Erreur écriture variables OPC UA: {e}")

    async def start(self):
        await self.init()
        async with self.server:
            logger.info(f"✅ Serveur OPC UA démarré sur opc.tcp://{settings.opcua_host}:{settings.opcua_port}")
            while True:
                try:
                    self.twin.update(settings.twin_update_interval)
                    await self.update()
                except Exception as e:
                    logger.error(f"Erreur cycle OPC UA: {e}")
                await asyncio.sleep(settings.twin_update_interval)