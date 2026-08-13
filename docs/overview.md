# Documentation - Seawater Pumping Station Digital Twin

## Physical Architecture
1. Sea Water Intake → Screen → Sump Tank → Pumps → Filter → Heat Exchanger → Discharge

## Digital Twin Architecture
CoDeSys (Simulation) → OPC UA → Node-RED → MQTT → TimescaleDB → Grafana

## Instrumentation
- Pump A: Flow, Pressure, Current, Vibration, Temperature
- Pump B: Flow, Pressure, Current, Vibration, Temperature
- Filter: Flow, Pressure Drop, Clogging
- Heat Exchanger: In/Out Temps, Delta T, Heat Transfer
- Discharge: Temperature, Flow, Turbidity

## Access Points
- CoDeSys: Local simulation
- Node-RED: http://localhost:1880
- Grafana: http://localhost:3000
- MQTT: localhost:1883
- TimescaleDB: localhost:5432
