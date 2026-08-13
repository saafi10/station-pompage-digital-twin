# Station de Pompage - Digital Twin

## Architecture IoT
- **Node-RED**: Orchestration des flux et client MQTT
- **Mosquitto**: Broker MQTT pour communication IoT
- **TimescaleDB**: Base de données temps-réel
- **Grafana**: Visualisation et tableaux de bord

## Démarrage Rapide
\\\ash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter tous les services
docker-compose down
\\\

## Accès
- Node-RED: http://localhost:1880
- Grafana: http://localhost:3000 (admin/admin)
- MQTT Broker: localhost:1883
- TimescaleDB: localhost:5432
