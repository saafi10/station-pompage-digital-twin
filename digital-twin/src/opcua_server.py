# digital-twin/src/opcua_server.py
import asyncio
import logging
from asyncua import Server

from src.config import settings

logger = logging.getLogger(__name__)


class OPCUAServer:
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

        # Variables à exposer (nom -> valeur par défaut, définit aussi le type OPC UA)
        variables = {
            'pump_a_flow': 0.0,
            'pump_a_pressure': 0.0,
            'pump_a_current': 0.0,
            'pump_a_vibration': 0.0,
            'pump_a_temperature': 25.0,
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
            'hx_heat_transfer': 0.0,
            'discharge_temp': 0.0,
            'discharge_flow': 0.0,
            'system_efficiency': 0.0,
            'energy_consumption': 0.0,
            'alarm_system_error': False,
            'demand_flow': 100.0,
        }

        for var_name, default_value in variables.items():
            try:
                var = await twin_node.add_variable(self.idx, var_name, default_value)
                is_writable = var_name == 'demand_flow'
                await var.set_writable(is_writable)
                self.vars[var_name] = var
                logger.debug(f"✅ Variable OPC UA ajoutée: {var_name}")
            except Exception as e:
                logger.error(f"Erreur ajout variable {var_name}: {e}")

        logger.info(f"✅ {len(self.vars)} variables OPC UA exposées")

    async def update(self):
        try:
            data = self.twin.get_all_data()
            for var_name, var in self.vars.items():
                if var_name in data and data[var_name] is not None:
                    await var.write_value(data[var_name])
        except Exception as e:
            logger.error(f"Erreur écriture variables OPC UA: {e}")

        # Lecture de la consigne écrite par un client externe (ex: UaExpert)
        if 'demand_flow' in self.vars:
            try:
                self.twin.demand_flow = await self.vars['demand_flow'].read_value()
            except Exception as e:
                logger.debug(f"Lecture demand_flow impossible ce cycle: {e}")

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