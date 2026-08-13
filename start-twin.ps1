# start-twin.ps1
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🚀 DÉMARRAGE DU JUMEAU NUMÉRIQUE" -ForegroundColor Cyan
Write-Host "   Station de Pompage - Architecture MQTT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Nettoyer les conteneurs existants
Write-Host "🧹 Nettoyage..." -ForegroundColor Yellow
docker-compose down -v

# Construire les images
Write-Host "📦 Construction des images..." -ForegroundColor Yellow
docker-compose build

# Démarrer les services
Write-Host "▶️ Démarrage des services..." -ForegroundColor Yellow
docker-compose up -d

# Attendre le démarrage
Write-Host "⏳ Attente du démarrage..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Vérifier les services
Write-Host ""
Write-Host "📊 État des services:" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "✅ Jumeau Numérique opérationnel!" -ForegroundColor Green
Write-Host ""
Write-Host "🔗 Accès:" -ForegroundColor Yellow
Write-Host "  • OPC UA Server: opc.tcp://localhost:4840" -ForegroundColor Gray
Write-Host "  • MQTT Broker: localhost:1883" -ForegroundColor Gray
Write-Host "  • Node-RED: http://localhost:1880" -ForegroundColor Gray
Write-Host "  • Grafana: http://localhost:3000 (admin/admin)" -ForegroundColor Gray
Write-Host "  • TimescaleDB: localhost:5432" -ForegroundColor Gray

Write-Host ""
Write-Host "📝 Commandes utiles:" -ForegroundColor Yellow
Write-Host "  • Logs: docker logs digital-twin -f" -ForegroundColor Gray
Write-Host "  • Écouter MQTT: docker exec -it mqtt-broker mosquitto_sub -t 'pompage/#' -v" -ForegroundColor Gray
Write-Host "  • Arrêter: docker-compose down" -ForegroundColor Gray
