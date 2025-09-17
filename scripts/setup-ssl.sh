#!/bin/bash

# Script de configuration SSL automatique pour Agrifrika Dashboard
# Support Let's Encrypt et certificats auto-signés
# Usage: ./setup-ssl.sh [domain] [email]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

DOMAIN=$1
EMAIL=$2
SSL_DIR="./nginx/ssl"
COMPOSE_FILE="docker-compose.prod.yml"

echo -e "${BLUE}🔐 Configuration SSL pour Agrifrika Dashboard${NC}"

# Créer le dossier SSL
mkdir -p "$SSL_DIR"

# Fonction pour créer des certificats auto-signés
create_self_signed() {
    echo -e "${YELLOW}📝 Création de certificats auto-signés...${NC}"

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_DIR/key.pem" \
        -out "$SSL_DIR/cert.pem" \
        -subj "/C=US/ST=State/L=City/O=Agrifrika/CN=${DOMAIN:-localhost}" \
        -addext "subjectAltName=DNS:${DOMAIN:-localhost},DNS:www.${DOMAIN:-localhost},IP:127.0.0.1"

    chmod 600 "$SSL_DIR"/*.pem
    echo -e "${GREEN}✅ Certificats auto-signés créés${NC}"
}

# Fonction pour obtenir des certificats Let's Encrypt
setup_letsencrypt() {
    local domain=$1
    local email=$2

    echo -e "${BLUE}🔒 Configuration Let's Encrypt pour $domain${NC}"

    # Vérifier si certbot est installé
    if ! command -v certbot &> /dev/null; then
        echo -e "${YELLOW}📦 Installation de certbot...${NC}"

        # Détecter l'OS et installer certbot
        if [[ -f /etc/os-release ]]; then
            . /etc/os-release
            case $ID in
                ubuntu|debian)
                    sudo apt-get update
                    sudo apt-get install -y certbot
                    ;;
                centos|rhel|fedora)
                    sudo yum install -y certbot || sudo dnf install -y certbot
                    ;;
                amzn)
                    sudo yum install -y certbot
                    ;;
                alpine)
                    sudo apk add --no-cache certbot
                    ;;
                *)
                    echo -e "${RED}❌ OS non supporté pour l'installation automatique de certbot${NC}"
                    echo -e "${YELLOW}Veuillez installer certbot manuellement${NC}"
                    return 1
                    ;;
            esac
        fi
    fi

    # Arrêter nginx temporairement si il tourne
    echo -e "${YELLOW}⏹️ Arrêt temporaire des services...${NC}"
    docker-compose -f "$COMPOSE_FILE" down nginx 2>/dev/null || true

    # Obtenir le certificat avec mode standalone
    echo -e "${BLUE}🔐 Obtention du certificat SSL...${NC}"
    sudo certbot certonly --standalone \
        -d "$domain" \
        --non-interactive \
        --agree-tos \
        --email "$email" \
        --preferred-challenges http

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Certificat Let's Encrypt obtenu${NC}"

        # Copier les certificats
        sudo cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$SSL_DIR/cert.pem"
        sudo cp "/etc/letsencrypt/live/$domain/privkey.pem" "$SSL_DIR/key.pem"

        # Ajuster les permissions
        sudo chown $(whoami):$(whoami) "$SSL_DIR"/*.pem
        chmod 600 "$SSL_DIR"/*.pem

        # Configurer le renouvellement automatique
        setup_auto_renewal "$domain"

        echo -e "${GREEN}✅ Certificats copiés et configurés${NC}"
    else
        echo -e "${RED}❌ Échec de l'obtention du certificat Let's Encrypt${NC}"
        echo -e "${YELLOW}Utilisation des certificats auto-signés en fallback${NC}"
        create_self_signed
    fi
}

# Fonction pour configurer le renouvellement automatique
setup_auto_renewal() {
    local domain=$1

    echo -e "${BLUE}🔄 Configuration du renouvellement automatique...${NC}"

    # Créer le script de renouvellement
    cat > "/tmp/renew-ssl.sh" << EOF
#!/bin/bash
# Script de renouvellement SSL pour Agrifrika Dashboard

# Renouveler le certificat
certbot renew --quiet

# Si le renouvellement réussit, redémarrer nginx
if [ \$? -eq 0 ]; then
    # Copier les nouveaux certificats
    cp "/etc/letsencrypt/live/$domain/fullchain.pem" "$PWD/$SSL_DIR/cert.pem"
    cp "/etc/letsencrypt/live/$domain/privkey.pem" "$PWD/$SSL_DIR/key.pem"

    # Redémarrer nginx
    cd "$PWD"
    docker-compose -f "$COMPOSE_FILE" restart nginx

    echo "Certificats SSL renouvelés et nginx redémarré"
fi
EOF

    sudo mv "/tmp/renew-ssl.sh" "/etc/ssl/renew-agrifrika-ssl.sh"
    sudo chmod +x "/etc/ssl/renew-agrifrika-ssl.sh"

    # Ajouter la tâche cron
    (sudo crontab -l 2>/dev/null; echo "0 3 * * 0 /etc/ssl/renew-agrifrika-ssl.sh") | sudo crontab -

    echo -e "${GREEN}✅ Renouvellement automatique configuré (tous les dimanches à 3h)${NC}"
}

# Fonction principale
main() {
    if [ -n "$DOMAIN" ] && [ -n "$EMAIL" ]; then
        echo -e "${BLUE}Domaine: $DOMAIN${NC}"
        echo -e "${BLUE}Email: $EMAIL${NC}"

        # Vérifier que le domaine pointe vers ce serveur
        echo -e "${YELLOW}🔍 Vérification DNS...${NC}"
        CURRENT_IP=$(curl -s http://checkip.amazonaws.com/ || curl -s http://ipinfo.io/ip || echo "unknown")
        DOMAIN_IP=$(dig +short "$DOMAIN" | tail -n1)

        if [ "$CURRENT_IP" = "$DOMAIN_IP" ]; then
            echo -e "${GREEN}✅ DNS configuré correctement${NC}"
            setup_letsencrypt "$DOMAIN" "$EMAIL"
        else
            echo -e "${YELLOW}⚠️ Le domaine ne pointe pas vers ce serveur${NC}"
            echo -e "${YELLOW}IP du serveur: $CURRENT_IP${NC}"
            echo -e "${YELLOW}IP du domaine: $DOMAIN_IP${NC}"
            echo -e "${YELLOW}Utilisation des certificats auto-signés${NC}"
            create_self_signed
        fi
    else
        echo -e "${YELLOW}⚠️ Domaine ou email non spécifié${NC}"
        echo -e "${YELLOW}Usage: $0 <domain> <email>${NC}"
        echo -e "${YELLOW}Création de certificats auto-signés pour les tests...${NC}"
        create_self_signed
    fi
}

# Configuration post-SSL
post_ssl_setup() {
    echo -e "${BLUE}🔧 Configuration post-SSL...${NC}"

    # Vérifier les certificats
    if [ -f "$SSL_DIR/cert.pem" ] && [ -f "$SSL_DIR/key.pem" ]; then
        echo -e "${GREEN}✅ Certificats SSL présents${NC}"

        # Afficher les informations du certificat
        echo -e "${BLUE}📋 Informations du certificat:${NC}"
        openssl x509 -in "$SSL_DIR/cert.pem" -text -noout | grep -E "(Subject:|Not After :|DNS:|IP Address:)" || true

        # Tester la configuration
        echo -e "${BLUE}🧪 Test de la configuration SSL...${NC}"
        if openssl x509 -in "$SSL_DIR/cert.pem" -checkend 86400 > /dev/null; then
            echo -e "${GREEN}✅ Certificat valide (expire dans plus de 24h)${NC}"
        else
            echo -e "${YELLOW}⚠️ Certificat expire bientôt${NC}"
        fi
    else
        echo -e "${RED}❌ Certificats SSL manquants${NC}"
        exit 1
    fi
}

# Exécution
main
post_ssl_setup

echo -e "${GREEN}🎉 Configuration SSL terminée!${NC}"
echo -e "${BLUE}📋 Prochaines étapes:${NC}"
echo -e "   1. Démarrez les services: docker-compose -f $COMPOSE_FILE up -d"
echo -e "   2. Testez HTTPS: https://${DOMAIN:-localhost}"
echo -e "   3. Vérifiez les logs: docker-compose -f $COMPOSE_FILE logs nginx"

if [ -n "$DOMAIN" ]; then
    echo -e "${YELLOW}📝 Notes importantes:${NC}"
    echo -e "   - Le renouvellement automatique est configuré"
    echo -e "   - Vérifiez les permissions des certificats"
    echo -e "   - Configurez votre pare-feu pour les ports 80/443"
fi