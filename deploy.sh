#!/bin/bash

# Agrifrika Dashboard - AWS EC2 Deployment Script
# Usage: ./deploy.sh [production|staging]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default environment
ENV=${1:-production}

echo -e "${BLUE}🚀 Agrifrika Dashboard Deployment - Environment: $ENV${NC}"

# Check if docker and docker-compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Function to install Docker on Ubuntu/Amazon Linux
install_docker() {
    echo -e "${YELLOW}📦 Installing Docker...${NC}"

    # Detect OS
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        OS=$NAME
    fi

    if [[ "$OS" == *"Amazon Linux"* ]]; then
        sudo yum update -y
        sudo yum install -y docker
        sudo service docker start
        sudo usermod -a -G docker $USER

        # Install Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose

    elif [[ "$OS" == *"Ubuntu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y docker.io docker-compose
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -a -G docker $USER
    fi

    echo -e "${GREEN}✅ Docker installed successfully${NC}"
}

# Function to setup SSL with Let's Encrypt
setup_ssl() {
    local domain=$1
    local email=${2:-"admin@$domain"}

    echo -e "${BLUE}🔐 Setting up SSL certificate for $domain${NC}"

    # Use dedicated SSL setup script
    if [[ -f "./scripts/setup-ssl.sh" ]]; then
        ./scripts/setup-ssl.sh "$domain" "$email"
    else
        echo -e "${YELLOW}⚠️ SSL setup script not found, creating self-signed certificate${NC}"
        mkdir -p ./nginx/ssl
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ./nginx/ssl/key.pem \
            -out ./nginx/ssl/cert.pem \
            -subj "/CN=${domain:-localhost}"
    fi

    echo -e "${GREEN}✅ SSL certificate configured${NC}"
}

# Function to create production environment file
create_env_file() {
    echo -e "${BLUE}📝 Creating environment configuration...${NC}"

    if [[ ! -f "./config/.env.prod" ]]; then
        cp ./config/.env ./config/.env.prod

        # Update for production
        sed -i 's/DEBUG=true/DEBUG=false/' ./config/.env.prod
        sed -i 's/ENV=development/ENV=production/' ./config/.env.prod

        echo -e "${YELLOW}⚠️  Please review and update ./config/.env.prod with production values${NC}"
        echo -e "${YELLOW}   Pay special attention to database URLs and API keys${NC}"
    fi
}

# Function to setup firewall
setup_firewall() {
    echo -e "${BLUE}🔥 Configuring firewall...${NC}"

    # Enable UFW and allow necessary ports
    if command -v ufw &> /dev/null; then
        sudo ufw --force reset
        sudo ufw default deny incoming
        sudo ufw default allow outgoing
        sudo ufw allow ssh
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw --force enable
        echo -e "${GREEN}✅ Firewall configured${NC}"
    fi
}

# Function to optimize system for production
optimize_system() {
    echo -e "${BLUE}⚡ Optimizing system for production...${NC}"

    # Increase file limits
    sudo tee -a /etc/security/limits.conf > /dev/null <<EOF
* soft nofile 65536
* hard nofile 65536
EOF

    # Optimize kernel parameters
    sudo tee -a /etc/sysctl.conf > /dev/null <<EOF
# Network optimizations
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.core.netdev_max_backlog = 5000
vm.swappiness = 10
EOF

    sudo sysctl -p

    echo -e "${GREEN}✅ System optimized${NC}"
}

# Function to setup monitoring and logging
setup_monitoring() {
    echo -e "${BLUE}📊 Setting up basic monitoring...${NC}"

    # Create log rotation config
    sudo tee /etc/logrotate.d/agrifrika > /dev/null <<EOF
/var/log/agrifrika/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 644 $USER $USER
    postrotate
        docker-compose -f /home/$USER/agrifrika/docker-compose.prod.yml restart nginx > /dev/null 2>&1 || true
    endscript
}
EOF

    # Create monitoring directory
    mkdir -p /var/log/agrifrika

    echo -e "${GREEN}✅ Basic monitoring setup complete${NC}"
}

# Function to deploy application
deploy_application() {
    echo -e "${BLUE}🚀 Deploying application...${NC}"

    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

    # Remove old images
    docker system prune -f

    # Build and start containers
    docker-compose -f docker-compose.prod.yml build --no-cache
    docker-compose -f docker-compose.prod.yml up -d

    # Wait for services to be healthy
    echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
    sleep 30

    # Check service health
    if docker-compose -f docker-compose.prod.yml ps | grep -q "unhealthy\|Exit"; then
        echo -e "${RED}❌ Some services are unhealthy. Check logs:${NC}"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi

    echo -e "${GREEN}✅ Application deployed successfully${NC}"
}

# Function to show deployment summary
show_summary() {
    local external_ip=$(curl -s http://checkip.amazonaws.com/)

    echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}📋 Deployment Summary:${NC}"
    echo -e "   Environment: $ENV"
    echo -e "   External IP: $external_ip"
    echo -e "   Application URL: https://$external_ip (or your domain)"
    echo -e "   Health Check: https://$external_ip/health"

    echo -e "\n${YELLOW}📝 Next Steps:${NC}"
    echo -e "   1. Configure your domain's DNS to point to $external_ip"
    echo -e "   2. Run SSL setup: ./deploy.sh ssl yourdomain.com"
    echo -e "   3. Review logs: docker-compose -f docker-compose.prod.yml logs"
    echo -e "   4. Monitor: docker-compose -f docker-compose.prod.yml ps"

    echo -e "\n${BLUE}🔧 Useful Commands:${NC}"
    echo -e "   Restart: docker-compose -f docker-compose.prod.yml restart"
    echo -e "   Logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo -e "   Stop: docker-compose -f docker-compose.prod.yml down"
    echo -e "   Update: git pull && ./deploy.sh"
}

# Main deployment flow
main() {
    case $1 in
        "install")
            install_docker
            ;;
        "ssl")
            setup_ssl $2
            ;;
        "production"|"staging"|"")
            create_env_file
            setup_firewall
            optimize_system
            setup_monitoring
            deploy_application
            show_summary
            ;;
        *)
            echo -e "${RED}Usage: $0 [production|staging|install|ssl domain.com]${NC}"
            exit 1
            ;;
    esac
}

# Run main function
main $@