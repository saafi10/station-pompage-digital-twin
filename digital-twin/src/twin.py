# digital-twin/src/twin.py
import math
from typing import Dict, Any

class PumpingStationTwin:
    def __init__(self):
        self.system_state = False           # démarre à l'arrêt (controle manuel)
        self.system_mode = 'NORMAL'         # NORMAL | TEST_OVERHEAT | TEST_VIBRATION | TEST_FILTER
        self.simulation_time = 0
        self.cycle_count = 0

        # Prise d'eau
        self.sea_water_temp = 22.5
        self.sea_water_turbidity = 5.2
        self.sea_water_salinity = 35.0
        self.intake_flow_rate = 0.0

        # Grille
        self.screen_pressure_drop = 0.02
        self.screen_clogging = 0.0
        self.debris_level = 0.0
        self.screen_cleaning_active = False

        # Bac
        self.tank_level = 2.5
        self.tank_min_level = 1.0
        self.tank_max_level = 4.0
        self.tank_volume = 50.0
        self.tank_inflow = 0.0
        self.tank_outflow = 0.0

        # Dosage chlore
        self.chlore_dosing_pump_active = False
        self.chlore_residuel = 0.8
        self.chlore_setpoint = 0.8
        self.chlore_injection_rate = 0.0

        # Pompes
        self.pump_a_command = False
        self.pump_b_command = False
        self.pump_a_status = False
        self.pump_b_status = False
        self.pump_a_speed = 0.0
        self.pump_b_speed = 0.0
        self.active_pump = 0
        self.pump_a_pressure = 0.0
        self.pump_b_pressure = 0.0
        self.pump_a_flow = 0.0
        self.pump_b_flow = 0.0
        self.pump_a_current = 0.0
        self.pump_b_current = 0.0
        self.pump_a_vibration = 0.0
        self.pump_b_vibration = 0.0
        self.pump_a_temperature = 25.0
        self.pump_b_temperature = 25.0
        self.pump_a_efficiency = 85.0
        self.pump_b_efficiency = 85.0
        self.pump_a_power = 0.0
        self.pump_b_power = 0.0
        self.pump_a_running_hours = 0.0
        self.pump_b_running_hours = 0.0
        self.pump_a_total_flow = 0.0
        self.pump_b_total_flow = 0.0

        # Filtre
        self.filter_flow_rate = 0.0
        self.filter_pressure_drop = 0.05
        self.filter_clogging = 0.0
        self.filter_clean_cycle = False
        self.filter_efficiency = 98.5
        self.filter_backwash_count = 0

        # Échangeur
        self.hx_sea_water_in_temp = 22.5
        self.hx_sea_water_out_temp = 0.0
        self.hx_sea_water_flow = 0.0
        self.hx_sea_water_delta_p = 0.0
        self.hx_process_in_temp = 45.0
        self.hx_process_out_temp = 0.0
        self.hx_process_flow = 100.0
        self.hx_process_delta_p = 0.0
        self.hx_delta_t = 0.0
        self.hx_heat_transfer = 0.0
        self.hx_efficiency = 85.0
        self.hx_fouling_factor = 0.0

        # Rejet
        self.discharge_temp = 0.0
        self.discharge_turbidity = 0.0
        self.discharge_flow = 0.0

        # Paramètres
        self.demand_flow = 100.0
        self.ambient_temp = 22.5
        self.season_factor = 1.0
        self.time_of_day = 0.0

        # Défauts
        self.pump_a_fault = False
        self.pump_b_fault = False
        self.filter_fault = False
        self.power_outage = False

        # Alarmes
        self.alarm_pump_a_overload = False
        self.alarm_pump_a_high_vibration = False
        self.alarm_pump_a_high_temp = False
        self.alarm_pump_b_overload = False
        self.alarm_pump_b_high_vibration = False
        self.alarm_pump_b_high_temp = False
        self.alarm_filter_clogged = False
        self.alarm_tank_low_level = False
        self.alarm_tank_high_level = False
        self.alarm_hx_overheat = False
        self.alarm_chlore_out_of_range = False
        self.alarm_system_error = False

        # Performances
        self.system_efficiency = 0.0
        self.energy_consumption = 0.0
        self.water_consumption = 0.0
        self.co2_footprint = 0.0
        self.operating_cost = 0.0

    def set_mode(self, mode: str):
        """Change le mode de fonctionnement. Modes de test PERSISTANTS
        (ne se lèvent pas seuls — repasser explicitement en NORMAL)."""
        valid = ('NORMAL', 'TEST_OVERHEAT', 'TEST_VIBRATION', 'TEST_FILTER')
        if mode in valid:
            self.system_mode = mode

    def _apply_test_mode(self):
        if self.system_mode == 'TEST_OVERHEAT':
            self.pump_a_temperature = 50.0
            self.alarm_pump_a_high_temp = True
        elif self.system_mode == 'TEST_VIBRATION':
            self.pump_a_vibration = 4.5
            self.alarm_pump_a_high_vibration = True
        elif self.system_mode == 'TEST_FILTER':
            self.filter_clogging = 95.0
            self.alarm_filter_clogged = True

    def update(self, dt: float = 0.1):
        self.simulation_time += dt
        self.cycle_count += 1
        self.time_of_day = (self.simulation_time / 3600) % 24
        self.season_factor = 1.0 + 0.2 * math.sin(self.simulation_time / 86400 * 6.2832)

        if self.system_state and not self.power_outage:
            self._update_intake()
            self._update_screen()
            self._update_tank()
            self._update_dosing()
            self._update_pumps(dt)
            self._update_filter()
            self._update_heat_exchanger()
            self._update_discharge()
            self._update_performance(dt)
            self._update_alarms()
            self._apply_test_mode()

    def _update_intake(self):
        self.sea_water_temp = max(-2.0, min(35.0,
            self.ambient_temp + 0.5 * math.sin(self.time_of_day / 24.0 * 6.2832) + 2.0 * (self.season_factor - 1.0)))
        self.sea_water_turbidity = max(0.0, min(50.0,
            5.2 + 2.0 * math.sin(self.simulation_time / 43200 * 6.2832) + 1.0 * (self.season_factor - 1.0)))
        self.intake_flow_rate = self.demand_flow * (1.0 + (self.tank_level - 2.5) / 10.0)

    def _update_screen(self):
        self.debris_level += (self.sea_water_turbidity / 10.0) * 0.5
        self.debris_level = max(0.0, min(100.0, self.debris_level))
        self.screen_clogging = max(0.0, min(100.0, self.debris_level * 0.7 + 10.0 * (self.intake_flow_rate / 150.0)))
        self.screen_pressure_drop = 0.02 + (self.screen_clogging / 100.0) * 0.25

        if self.screen_clogging > 85.0 and not self.screen_cleaning_active:
            self.screen_cleaning_active = True
        if self.screen_cleaning_active:
            self.debris_level -= 20.0
            if self.debris_level < 10.0:
                self.screen_cleaning_active = False
                self.debris_level = 0.0

    def _update_tank(self):
        self.tank_inflow = self.intake_flow_rate
        self.tank_outflow = self.pump_a_flow + self.pump_b_flow
        self.tank_level = max(self.tank_min_level, min(self.tank_max_level,
            self.tank_level + (self.tank_inflow - self.tank_outflow) * 0.002))
        self.alarm_tank_low_level = self.tank_level < 1.2
        self.alarm_tank_high_level = self.tank_level > 3.8

    def _update_dosing(self):
        if self.filter_flow_rate > 0.0 or self.intake_flow_rate > 0.0:
            self.chlore_dosing_pump_active = True
            error = self.chlore_setpoint - self.chlore_residuel
            self.chlore_injection_rate = max(0.0, min(5.0, 2.0 + error * 3.0))
            self.chlore_residuel += (self.chlore_injection_rate - self.chlore_setpoint * 1.1) * 0.02
            self.chlore_residuel = max(0.0, min(3.0, self.chlore_residuel))
        else:
            self.chlore_dosing_pump_active = False
            self.chlore_injection_rate = 0.0
            self.chlore_residuel = max(0.0, self.chlore_residuel - 0.01)
        self.alarm_chlore_out_of_range = self.chlore_residuel < 0.3 or self.chlore_residuel > 1.5

    def _update_pumps(self, dt: float):
        if self.demand_flow > 0 and not self.pump_a_fault:
            self.pump_a_command = True
            self.active_pump = 1
        elif self.demand_flow > 0 and not self.pump_b_fault:
            self.pump_b_command = True
            self.active_pump = 2
        else:
            self.pump_a_command = False
            self.pump_b_command = False
            self.active_pump = 0

        if self.pump_a_command and not self.pump_a_fault and not self.power_outage:
            self.pump_a_status = True
            self.pump_a_speed = max(0.0, min(100.0, 50.0 + 50.0 * (self.tank_level - 1.5) / 2.5))
            self.pump_a_flow = max(0.0, min(160.0, (self.pump_a_speed / 100.0) * 150.0))
            self.pump_a_pressure = max(0.0, min(6.0, 3.0 + (self.pump_a_speed / 100.0)**2 * 2.0))
            self.pump_a_current = max(0.0, min(120.0, 50.0 + (self.pump_a_speed / 100.0)**2 * 50.0))
            self.pump_a_vibration = max(0.0, min(5.0, 0.5 + 0.01 * self.pump_a_flow + 0.001 * self.pump_a_running_hours))
            self.pump_a_temperature = max(20.0, min(60.0, 25.0 + 0.02 * self.pump_a_flow + 0.001 * self.pump_a_running_hours))
            self.pump_a_efficiency = max(60.0, min(88.0, 85.0 - 5.0 * ((self.pump_a_speed - 80.0) / 80.0)**2))
            self.pump_a_power = max(0.0, min(55.0, self.pump_a_flow * self.pump_a_pressure / 36.0 / (self.pump_a_efficiency / 100.0)))
            self.pump_a_running_hours += dt / 3600
            self.pump_a_total_flow += self.pump_a_flow * dt / 3600
            self.alarm_pump_a_overload = self.pump_a_current > 110.0
            self.alarm_pump_a_high_vibration = self.pump_a_vibration > 3.5
            self.alarm_pump_a_high_temp = self.pump_a_temperature > 45.0
        else:
            self.pump_a_status = False
            self.pump_a_flow = 0.0
            self.pump_a_pressure = 0.0
            self.pump_a_speed = 0.0
            self.pump_a_current = 0.0
            self.pump_a_vibration = 0.0
            self.pump_a_power = 0.0

        if self.active_pump == 1:
            self.pump_b_status = False
            self.pump_b_flow = 0.0
            self.pump_b_pressure = 0.0
            self.pump_b_speed = 0.0
            self.pump_b_current = 0.0
            self.pump_b_vibration = 0.0
            self.pump_b_power = 0.0
            if self.pump_a_fault or not self.pump_a_status:
                self.pump_b_command = True
                self.active_pump = 2
                self.pump_a_fault = False
        elif self.active_pump == 2:
            self.pump_b_status = True
            self.pump_b_speed = max(0.0, min(100.0, 50.0 + 50.0 * (self.tank_level - 1.5) / 2.5))
            self.pump_b_flow = max(0.0, min(160.0, (self.pump_b_speed / 100.0) * 150.0))
            self.pump_b_pressure = max(0.0, min(6.0, 3.0 + (self.pump_b_speed / 100.0)**2 * 2.0))
            self.pump_b_current = max(0.0, min(120.0, 50.0 + (self.pump_b_speed / 100.0)**2 * 50.0))
            self.pump_b_vibration = max(0.0, min(5.0, 0.5 + 0.01 * self.pump_b_flow + 0.001 * self.pump_b_running_hours))
            self.pump_b_temperature = max(20.0, min(60.0, 25.0 + 0.02 * self.pump_b_flow + 0.001 * self.pump_b_running_hours))
            self.pump_b_efficiency = max(60.0, min(88.0, 85.0 - 5.0 * ((self.pump_b_speed - 80.0) / 80.0)**2))
            self.pump_b_power = max(0.0, min(55.0, self.pump_b_flow * self.pump_b_pressure / 36.0 / (self.pump_b_efficiency / 100.0)))
            self.pump_b_running_hours += dt / 3600
            self.pump_b_total_flow += self.pump_b_flow * dt / 3600
            self.alarm_pump_b_overload = self.pump_b_current > 110.0
            self.alarm_pump_b_high_vibration = self.pump_b_vibration > 3.5
            self.alarm_pump_b_high_temp = self.pump_b_temperature > 45.0

        self.filter_flow_rate = self.pump_a_flow if (self.active_pump == 1 and self.pump_a_status) else (self.pump_b_flow if (self.active_pump == 2 and self.pump_b_status) else 0.0)

    def _update_filter(self):
        if self.filter_flow_rate > 0.0:
            self.filter_clogging += (self.sea_water_turbidity / 10.0) * 0.5 + (self.filter_flow_rate / 150.0) * 0.2
            self.filter_clogging = max(0.0, min(100.0, self.filter_clogging))
            self.filter_pressure_drop = 0.05 + (self.filter_clogging / 100.0) * 0.65
            self.filter_efficiency = max(85.0, min(99.0, 98.5 - (self.filter_clogging / 100.0) * 12.0))

            if self.filter_clogging > 85.0 and not self.filter_clean_cycle:
                self.filter_clean_cycle = True
                self.filter_backwash_count += 1
            if self.filter_clean_cycle:
                self.filter_clogging -= 50.0
                if self.filter_clogging < 20.0:
                    self.filter_clean_cycle = False
                    self.filter_clogging = 10.0

            if self.filter_fault:
                self.filter_flow_rate *= 0.5
                self.filter_pressure_drop = 2.0
            self.alarm_filter_clogged = self.filter_clogging > 90.0
        else:
            self.filter_pressure_drop = 0.0
            self.filter_efficiency = 0.0

    def _update_heat_exchanger(self):
        if self.filter_flow_rate > 0.0:
            self.hx_sea_water_in_temp = self.sea_water_temp
            self.hx_sea_water_flow = self.filter_flow_rate
            self.hx_process_in_temp = 45.0 + 2.0 * math.sin(self.time_of_day / 24.0 * 6.2832) + 5.0 * (self.season_factor - 1.0)
            self.hx_process_flow = self.demand_flow
            self.hx_fouling_factor = max(0.0, min(1.0, self.filter_clogging / 100.0 * 0.3))
            self.hx_efficiency = max(50.0, min(90.0, 85.0 - self.hx_fouling_factor * 25.0))
            self.hx_delta_t = (self.hx_process_in_temp - self.hx_sea_water_in_temp) * (self.hx_efficiency / 100.0)
            self.hx_process_out_temp = self.hx_process_in_temp - self.hx_delta_t
            self.hx_sea_water_out_temp = self.hx_sea_water_in_temp + self.hx_delta_t * (self.hx_process_flow / self.hx_sea_water_flow) * 0.5
            self.hx_heat_transfer = max(0.0, min(1000.0, self.hx_sea_water_flow * 4.186 * (self.hx_sea_water_out_temp - self.hx_sea_water_in_temp) / 3.6))
            self.hx_sea_water_delta_p = 0.2 + self.hx_fouling_factor * 0.5
            self.hx_process_delta_p = 0.3 + self.hx_fouling_factor * 0.4
            self.alarm_hx_overheat = self.hx_process_out_temp > 38.0
        else:
            self.hx_sea_water_out_temp = self.hx_sea_water_in_temp
            self.hx_process_out_temp = self.hx_process_in_temp
            self.hx_delta_t = 0.0
            self.hx_heat_transfer = 0.0

    def _update_discharge(self):
        if self.filter_flow_rate > 0.0:
            self.discharge_flow = self.filter_flow_rate
            self.discharge_temp = self.hx_sea_water_out_temp
            self.discharge_turbidity = max(0.0, min(60.0, self.sea_water_turbidity * (1.0 + (self.filter_clogging / 100.0) * 0.2)))

    def _update_performance(self, dt: float):
        self.system_efficiency = max(0.0, min(100.0, (self.hx_heat_transfer / 1000.0) * (self.pump_a_efficiency / 100.0)))
        self.energy_consumption += (self.pump_a_power + self.pump_b_power) * dt / 3600
        self.water_consumption += self.filter_flow_rate * dt / 3600
        self.co2_footprint = self.energy_consumption * 0.4
        self.operating_cost = self.energy_consumption * 0.15

    def _update_alarms(self):
        self.alarm_system_error = any([
            self.alarm_pump_a_overload, self.alarm_pump_a_high_vibration, self.alarm_pump_a_high_temp,
            self.alarm_filter_clogged, self.alarm_tank_low_level, self.alarm_tank_high_level,
            self.alarm_hx_overheat, self.alarm_chlore_out_of_range
        ])

    def get_all_data(self) -> Dict[str, Any]:
        return {
            'system_state': self.system_state,
            'system_mode': self.system_mode,
            'simulation_time': self.simulation_time,
            'sea_water_temp': self.sea_water_temp,
            'sea_water_turbidity': self.sea_water_turbidity,
            'sea_water_salinity': self.sea_water_salinity,
            'intake_flow_rate': self.intake_flow_rate,
            'tank_level': self.tank_level,
            'chlore_residuel': self.chlore_residuel,
            'chlore_injection_rate': self.chlore_injection_rate,
            'pump_a_status': self.pump_a_status,
            'pump_a_flow': self.pump_a_flow,
            'pump_a_pressure': self.pump_a_pressure,
            'pump_a_current': self.pump_a_current,
            'pump_a_vibration': self.pump_a_vibration,
            'pump_a_temperature': self.pump_a_temperature,
            'pump_a_efficiency': self.pump_a_efficiency,
            'pump_a_power': self.pump_a_power,
            'pump_b_status': self.pump_b_status,
            'pump_b_flow': self.pump_b_flow,
            'pump_b_pressure': self.pump_b_pressure,
            'active_pump': self.active_pump,
            'filter_flow_rate': self.filter_flow_rate,
            'filter_pressure_drop': self.filter_pressure_drop,
            'filter_clogging': self.filter_clogging,
            'filter_efficiency': self.filter_efficiency,
            'hx_sea_water_out_temp': self.hx_sea_water_out_temp,
            'hx_process_out_temp': self.hx_process_out_temp,
            'hx_delta_t': self.hx_delta_t,
            'hx_heat_transfer': self.hx_heat_transfer,
            'discharge_temp': self.discharge_temp,
            'discharge_turbidity': self.discharge_turbidity,
            'discharge_flow': self.discharge_flow,
            'system_efficiency': self.system_efficiency,
            'energy_consumption': self.energy_consumption,
            'alarm_pump_a_overload': self.alarm_pump_a_overload,
            'alarm_pump_a_high_vibration': self.alarm_pump_a_high_vibration,
            'alarm_pump_a_high_temp': self.alarm_pump_a_high_temp,
            'alarm_filter_clogged': self.alarm_filter_clogged,
            'alarm_tank_low_level': self.alarm_tank_low_level,
            'alarm_hx_overheat': self.alarm_hx_overheat,
            'alarm_chlore_out_of_range': self.alarm_chlore_out_of_range,
            'alarm_system_error': self.alarm_system_error,
        }