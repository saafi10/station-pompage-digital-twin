#!/bin/bash
# Test script for Digital Twin

echo "Testing Digital Twin System..."

# Test MQTT broker
echo "Testing MQTT Broker..."
docker exec mosquitto mosquitto_pub -t test -m "hello" -q 1

# Test database connection
echo "Testing TimescaleDB..."
docker exec timescaledb psql -U admin -d pompage -c "SELECT 1;"

# Test data insertion
echo "Inserting test data..."
docker exec timescaledb psql -U admin -d pompage -c "INSERT INTO pump_data (time, pump_id, pressure, flow_rate, temperature) VALUES (NOW(), 1, 3.5, 120.5, 25.3);"

echo "System test complete!"
