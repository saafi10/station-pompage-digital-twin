CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS pump_data (

    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    simulation_time DOUBLE PRECISION,

    pump_active INTEGER,

    pump_flow DOUBLE PRECISION,

    pump_pressure DOUBLE PRECISION,

    pump_temperature DOUBLE PRECISION,

    pump_vibration DOUBLE PRECISION,

    pump_current DOUBLE PRECISION,

    pump_status BOOLEAN,

    pump_efficiency DOUBLE PRECISION,

    pump_power DOUBLE PRECISION,

    filter_flow DOUBLE PRECISION,

    filter_clogging DOUBLE PRECISION,

    filter_pressure_drop DOUBLE PRECISION,

    tank_level DOUBLE PRECISION,

    performance_efficiency DOUBLE PRECISION,

    energy_consumption DOUBLE PRECISION

);


SELECT create_hypertable(
    'pump_data',
    'time',
    if_not_exists => TRUE
);


CREATE TABLE IF NOT EXISTS alerts (

    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    alert_type TEXT,

    severity TEXT,

    message TEXT,

    value DOUBLE PRECISION,

    threshold DOUBLE PRECISION

);