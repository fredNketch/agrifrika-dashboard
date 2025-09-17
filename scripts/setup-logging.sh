#!/bin/bash

# Script de configuration de la rotation des logs pour Agrifrika Dashboard
# Usage: ./setup-logging.sh

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📝 Configuration de la rotation des logs Agrifrika Dashboard${NC}"

# Créer les répertoires de logs
create_log_directories() {
    echo -e "${BLUE}📁 Création des répertoires de logs...${NC}"

    # Répertoires locaux
    mkdir -p logs/
    mkdir -p backend/logs/
    mkdir -p nginx/logs/

    # Répertoires système
    sudo mkdir -p /var/log/agrifrika
    sudo mkdir -p /var/log/docker-logs

    # Permissions
    sudo chown -R $(whoami):$(whoami) logs/
    sudo chmod 755 /var/log/agrifrika

    echo -e "${GREEN}✅ Répertoires de logs créés${NC}"
}

# Installer logrotate si nécessaire
install_logrotate() {
    if ! command -v logrotate &> /dev/null; then
        echo -e "${YELLOW}📦 Installation de logrotate...${NC}"

        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            case $ID in
                ubuntu|debian)
                    sudo apt-get update
                    sudo apt-get install -y logrotate
                    ;;
                centos|rhel|fedora)
                    sudo yum install -y logrotate || sudo dnf install -y logrotate
                    ;;
                amzn)
                    sudo yum install -y logrotate
                    ;;
                alpine)
                    sudo apk add --no-cache logrotate
                    ;;
                *)
                    echo -e "${YELLOW}⚠️ OS non détecté, vérifiez que logrotate est installé${NC}"
                    ;;
            esac
        fi

        echo -e "${GREEN}✅ logrotate installé${NC}"
    else
        echo -e "${GREEN}✅ logrotate déjà présent${NC}"
    fi
}

# Configurer logrotate
setup_logrotate() {
    echo -e "${BLUE}⚙️ Configuration de logrotate...${NC}"

    # Copier la configuration
    sudo cp config/logrotate.conf /etc/logrotate.d/agrifrika

    # Vérifier la configuration
    sudo logrotate -d /etc/logrotate.d/agrifrika

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Configuration logrotate valide${NC}"
    else
        echo -e "${RED}❌ Erreur dans la configuration logrotate${NC}"
        exit 1
    fi

    # Tester la rotation
    echo -e "${BLUE}🧪 Test de la rotation...${NC}"
    sudo logrotate -f /etc/logrotate.d/agrifrika

    echo -e "${GREEN}✅ Logrotate configuré${NC}"
}

# Configurer Docker pour la limitation des logs
configure_docker_logging() {
    echo -e "${BLUE}🐳 Configuration des logs Docker...${NC}"

    # Créer le fichier de configuration Docker daemon s'il n'existe pas
    DOCKER_DAEMON_FILE="/etc/docker/daemon.json"

    if [ ! -f "$DOCKER_DAEMON_FILE" ]; then
        sudo mkdir -p /etc/docker
        sudo tee "$DOCKER_DAEMON_FILE" > /dev/null << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "50m",
        "max-file": "10",
        "compress": "true"
    }
}
EOF
    else
        # Backup et mise à jour
        sudo cp "$DOCKER_DAEMON_FILE" "${DOCKER_DAEMON_FILE}.backup"

        # Utiliser jq pour mettre à jour si disponible, sinon créer un nouveau fichier
        if command -v jq &> /dev/null; then
            sudo jq '.["log-driver"] = "json-file" | .["log-opts"] = {"max-size": "50m", "max-file": "10", "compress": "true"}' \
                "$DOCKER_DAEMON_FILE" > /tmp/daemon.json
            sudo mv /tmp/daemon.json "$DOCKER_DAEMON_FILE"
        else
            echo -e "${YELLOW}⚠️ jq non disponible, veuillez configurer manuellement ${DOCKER_DAEMON_FILE}${NC}"
            echo -e "${BLUE}Configuration recommandée:${NC}"
            cat << EOF
{
    "log-driver": "json-file",
    "log-opts": {
        "max-size": "50m",
        "max-file": "10",
        "compress": "true"
    }
}
EOF
        fi
    fi

    echo -e "${GREEN}✅ Configuration Docker logs mise à jour${NC}"
    echo -e "${YELLOW}⚠️ Redémarrage de Docker requis pour appliquer les changements${NC}"
}

# Créer un script de nettoyage des logs
create_log_cleanup_script() {
    echo -e "${BLUE}🧹 Création du script de nettoyage...${NC}"

    cat > "/tmp/cleanup-logs.sh" << 'EOF'
#!/bin/bash
# Script de nettoyage des logs Agrifrika Dashboard

LOG_RETENTION_DAYS=30
DOCKER_LOG_RETENTION_DAYS=7

echo "Nettoyage des logs anciens..."

# Nettoyer les logs applicatifs
find /var/log/agrifrika -name "*.log" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null || true
find /var/log/agrifrika -name "*.gz" -mtime +$LOG_RETENTION_DAYS -delete 2>/dev/null || true

# Nettoyer les logs Docker (conteneurs arrêtés)
docker system prune -f --volumes --filter "until=${DOCKER_LOG_RETENTION_DAYS}h" 2>/dev/null || true

# Nettoyer les logs de build
find . -name "*.log" -path "*/node_modules/*" -mtime +7 -delete 2>/dev/null || true

# Afficher l'espace disque
echo "Espace disque après nettoyage:"
df -h /var/log

echo "Nettoyage terminé"
EOF

    sudo mv "/tmp/cleanup-logs.sh" "/usr/local/bin/agrifrika-cleanup-logs.sh"
    sudo chmod +x "/usr/local/bin/agrifrika-cleanup-logs.sh"

    echo -e "${GREEN}✅ Script de nettoyage créé: /usr/local/bin/agrifrika-cleanup-logs.sh${NC}"
}

# Configurer les tâches cron
setup_cron_jobs() {
    echo -e "${BLUE}⏰ Configuration des tâches cron...${NC}"

    # Ajouter les tâches cron pour le nettoyage automatique
    (crontab -l 2>/dev/null; echo "0 2 * * 0 /usr/local/bin/agrifrika-cleanup-logs.sh") | crontab -
    (crontab -l 2>/dev/null; echo "0 1 * * * /usr/sbin/logrotate /etc/logrotate.d/agrifrika") | crontab -

    echo -e "${GREEN}✅ Tâches cron configurées:${NC}"
    echo -e "   - Nettoyage des logs: Dimanche à 2h"
    echo -e "   - Rotation des logs: Quotidienne à 1h"
}

# Configuration des logs pour le monitoring
setup_monitoring_logs() {
    echo -e "${BLUE}📊 Configuration des logs de monitoring...${NC}"

    # Créer un répertoire pour les métriques
    mkdir -p logs/metrics/

    # Script de collecte de métriques
    cat > "logs/metrics/collect-metrics.sh" << 'EOF'
#!/bin/bash
# Collecte des métriques système pour Agrifrika Dashboard

METRICS_FILE="logs/metrics/system-metrics.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Métriques système
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.2f", ($3/$2) * 100.0)}')
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

# Métriques Docker
DOCKER_CONTAINERS=$(docker ps -q | wc -l)
DOCKER_IMAGES=$(docker images -q | wc -l)

# Écrire les métriques
echo "$TIMESTAMP,cpu_usage,$CPU_USAGE,memory_usage,$MEMORY_USAGE,disk_usage,$DISK_USAGE,docker_containers,$DOCKER_CONTAINERS,docker_images,$DOCKER_IMAGES" >> "$METRICS_FILE"

# Rotation manuelle si le fichier devient trop gros (>10MB)
if [ $(stat -c%s "$METRICS_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
    mv "$METRICS_FILE" "${METRICS_FILE}.old"
    echo "timestamp,metric,value" > "$METRICS_FILE"
fi
EOF

    chmod +x logs/metrics/collect-metrics.sh

    # Ajouter la collecte de métriques au cron (toutes les 5 minutes)
    (crontab -l 2>/dev/null; echo "*/5 * * * * $PWD/logs/metrics/collect-metrics.sh") | crontab -

    echo -e "${GREEN}✅ Monitoring des métriques configuré${NC}"
}

# Fonction principale
main() {
    create_log_directories
    install_logrotate
    setup_logrotate
    configure_docker_logging
    create_log_cleanup_script
    setup_cron_jobs
    setup_monitoring_logs

    echo -e "${GREEN}🎉 Configuration des logs terminée!${NC}"
    echo -e "${BLUE}📋 Résumé:${NC}"
    echo -e "   - Rotation automatique configurée"
    echo -e "   - Nettoyage automatique configuré"
    echo -e "   - Logs Docker limités à 50MB x 10 fichiers"
    echo -e "   - Métriques système collectées toutes les 5 min"
    echo -e "   - Script de nettoyage: /usr/local/bin/agrifrika-cleanup-logs.sh"

    echo -e "${YELLOW}📝 Actions requises:${NC}"
    echo -e "   1. Redémarrez Docker: sudo systemctl restart docker"
    echo -e "   2. Vérifiez les permissions des logs"
    echo -e "   3. Testez la rotation: sudo logrotate -f /etc/logrotate.d/agrifrika"

    echo -e "${BLUE}📊 Surveillance:${NC}"
    echo -e "   - Logs: tail -f logs/*.log"
    echo -e "   - Métriques: tail -f logs/metrics/system-metrics.log"
    echo -e "   - Espace disque: df -h /var/log"
}

# Exécution
main