-- Table simple pour les tests
CREATE TABLE IF NOT EXISTS pump_data (
    time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pump_id INTEGER NOT NULL,
    pressure FLOAT,
    flow_rate FLOAT,
    temperature FLOAT,
    vibration FLOAT,
    power_consumption FLOAT,
    status VARCHAR(50)
);

-- Créer l'hypertable
SELECT create_hypertable('pump_data', 'time', if_not_exists => TRUE);
