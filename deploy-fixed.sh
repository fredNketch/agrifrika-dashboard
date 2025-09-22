#!/bin/bash

# Script de déploiement corrigé pour Agrifrika Dashboard
# Intègre toutes les corrections identifiées lors du debug

set -e

echo "🚀 Déploiement Agrifrika Dashboard avec corrections appliquées"

# Variables
ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
KEY_PAIR_NAME=${3:-agrifrika-key}

echo "Environment: $ENVIRONMENT"
echo "Region: $AWS_REGION"
echo "Key Pair: $KEY_PAIR_NAME"

# Fonction pour créer l'instance EC2
create_ec2_instance() {
    echo "📦 Création de l'instance EC2..."

    # Utilise le script simple qui fonctionne
    ./aws/scripts/simple-ec2-deploy-fixed.sh

    echo "✅ Instance EC2 créée avec succès"
}

# Fonction pour préparer les fichiers corrigés
prepare_files() {
    echo "🔧 Préparation des fichiers avec corrections..."

    # Vérifier que les scripts d'entrypoint sont dans backend/
    if [ ! -f "backend/docker-entrypoint.sh" ]; then
        echo "📋 Copie des scripts d'entrypoint..."
        cp docker-entrypoint.sh backend/
        cp aws/scripts/aws-entrypoint.sh backend/
    fi

    # Créer les répertoires de logs nécessaires
    mkdir -p logs/backend logs/nginx

    echo "✅ Fichiers préparés"
}

# Fonction pour déployer l'application
deploy_application() {
    local instance_ip=$1

    echo "🚢 Déploiement de l'application sur $instance_ip..."

    # Transférer les fichiers essentiels
    echo "📤 Transfert des fichiers de configuration..."
    scp -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no -r \
        backend/ frontend/ config/ docker-compose.prod.yml nginx/ \
        ec2-user@$instance_ip:/home/ec2-user/agrifrika-dashboard/

    # Déployer avec Docker Compose
    echo "🐳 Déploiement Docker Compose..."
    ssh -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no ec2-user@$instance_ip \
        "cd /home/ec2-user/agrifrika-dashboard && \
         mkdir -p logs/backend logs/nginx && \
         docker-compose -f docker-compose.prod.yml up -d --build"

    echo "✅ Application déployée"
}

# Fonction pour configurer SSL (après DNS)
setup_ssl() {
    local instance_ip=$1

    echo "🔒 Configuration SSL Let's Encrypt..."

    ssh -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no ec2-user@$instance_ip \
        "sudo mkdir -p /var/www/html && \
         sudo certbot certonly --webroot -w /var/www/html \
         -d dashboard.agrifrika.com --non-interactive --agree-tos \
         --email admin@agrifrika.com && \
         sudo cp /etc/letsencrypt/live/dashboard.agrifrika.com/fullchain.pem /home/ec2-user/agrifrika-dashboard/nginx/ssl/cert.pem && \
         sudo cp /etc/letsencrypt/live/dashboard.agrifrika.com/privkey.pem /home/ec2-user/agrifrika-dashboard/nginx/ssl/key.pem && \
         cd /home/ec2-user/agrifrika-dashboard && \
         docker-compose -f docker-compose.prod.yml restart nginx"

    echo "✅ SSL configuré"
}

# Fonction principale
main() {
    case "${1}" in
        "ssl")
            if [ -z "${2}" ]; then
                echo "Usage: $0 ssl <instance_ip>"
                exit 1
            fi
            setup_ssl "${2}"
            ;;
        "deploy")
            prepare_files
            create_ec2_instance
            ;;
        *)
            echo "Usage: $0 [deploy|ssl <instance_ip>]"
            echo "  deploy: Créer l'instance et déployer l'application"
            echo "  ssl <ip>: Configurer SSL sur l'instance existante"
            ;;
    esac
}

main "$@"