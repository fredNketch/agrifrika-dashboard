#!/bin/bash

# Migration script from Docker Compose to AWS ECS
# Usage: ./migrate-to-aws.sh [environment] [region] [domain]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
DOMAIN_NAME=${3:-""}

echo -e "${BLUE}Migration Docker Compose vers AWS ECS${NC}"

# Function to export secrets to AWS
export_secrets_to_aws() {
    echo -e "${BLUE}Migration des secrets vers AWS Secrets Manager...${NC}"

    # Check if encrypted credentials exist
    if [ -d "config/credentials-secure" ] && [ -f "config/credentials-secure/master.key" ]; then
        echo -e "${YELLOW}Credentials chiffrés détectés. Déchiffrement...${NC}"

        # Decrypt credentials temporarily
        mkdir -p /tmp/agrifrika-migration

        # Decrypt Google Sheets credentials
        if [ -f "config/credentials-secure/google-sheets-new-credentials.json.enc" ]; then
            openssl enc -aes-256-cbc -d \
                -in "config/credentials-secure/google-sheets-new-credentials.json.enc" \
                -out "/tmp/agrifrika-migration/google-sheets.json" \
                -pass file:config/credentials-secure/master.key
        fi

        # Decrypt Google Analytics credentials
        if [ -f "config/credentials-secure/google-analytics-credentials.json.enc" ]; then
            openssl enc -aes-256-cbc -d \
                -in "config/credentials-secure/google-analytics-credentials.json.enc" \
                -out "/tmp/agrifrika-migration/google-analytics.json" \
                -pass file:config/credentials-secure/master.key
        fi

        # Extract other secrets from .env
        if [ -f "config/.env.prod" ]; then
            source config/.env.prod
        fi

    elif [ -d "config/credentials" ]; then
        echo -e "${YELLOW}Credentials non chiffrés détectés. Utilisation directe...${NC}"
        cp config/credentials/*.json /tmp/agrifrika-migration/ 2>/dev/null || true

        if [ -f "config/.env.prod" ]; then
            source config/.env.prod
        fi
    else
        echo -e "${RED}Aucun credential trouvé. Migration manuelle nécessaire.${NC}"
        return 1
    fi

    # Get the secret ARN from infrastructure stack
    SECRET_ARN=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "agrifrika-${ENVIRONMENT}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='ApplicationSecrets'].OutputValue" \
        --output text 2>/dev/null)

    if [ -z "$SECRET_ARN" ]; then
        echo -e "${RED}Infrastructure stack non trouvé. Déployez d'abord l'infrastructure.${NC}"
        return 1
    fi

    # Build the secrets JSON
    SECRETS_JSON="{"

    # Add Google credentials
    if [ -f "/tmp/agrifrika-migration/google-sheets.json" ]; then
        GOOGLE_SHEETS_CONTENT=$(cat /tmp/agrifrika-migration/google-sheets.json | jq -c .)
        SECRETS_JSON="$SECRETS_JSON\"GOOGLE_SHEETS_CREDENTIALS\": $GOOGLE_SHEETS_CONTENT,"
    fi

    if [ -f "/tmp/agrifrika-migration/google-analytics.json" ]; then
        GOOGLE_ANALYTICS_CONTENT=$(cat /tmp/agrifrika-migration/google-analytics.json | jq -c .)
        SECRETS_JSON="$SECRETS_JSON\"GOOGLE_ANALYTICS_CREDENTIALS\": $GOOGLE_ANALYTICS_CONTENT,"
    fi

    # Add other secrets
    [ -n "$BASECAMP_TOKEN" ] && SECRETS_JSON="$SECRETS_JSON\"BASECAMP_TOKEN\": \"$BASECAMP_TOKEN\","
    [ -n "$BASECAMP_ACCOUNT_ID" ] && SECRETS_JSON="$SECRETS_JSON\"BASECAMP_ACCOUNT_ID\": \"$BASECAMP_ACCOUNT_ID\","
    [ -n "$BASECAMP_PROJECT_ID" ] && SECRETS_JSON="$SECRETS_JSON\"BASECAMP_PROJECT_ID\": \"$BASECAMP_PROJECT_ID\","
    [ -n "$FACEBOOK_ACCESS_TOKEN" ] && SECRETS_JSON="$SECRETS_JSON\"FACEBOOK_ACCESS_TOKEN\": \"$FACEBOOK_ACCESS_TOKEN\","
    [ -n "$FACEBOOK_PAGE_ID" ] && SECRETS_JSON="$SECRETS_JSON\"FACEBOOK_PAGE_ID\": \"$FACEBOOK_PAGE_ID\","

    # Generate strong secret key
    SECRET_KEY=$(openssl rand -base64 32)
    SECRETS_JSON="$SECRETS_JSON\"SECRET_KEY\": \"$SECRET_KEY\""

    SECRETS_JSON="$SECRETS_JSON}"

    # Upload to AWS Secrets Manager
    echo -e "${BLUE}Upload des secrets vers AWS Secrets Manager...${NC}"
    aws secretsmanager put-secret-value \
        --region "$AWS_REGION" \
        --secret-id "$SECRET_ARN" \
        --secret-string "$SECRETS_JSON"

    echo -e "${GREEN}Secrets migrés vers AWS Secrets Manager${NC}"

    # Cleanup temporary files
    rm -rf /tmp/agrifrika-migration
}

# Function to validate migration
validate_migration() {
    echo -e "${BLUE}Validation de la migration...${NC}"

    STACK_NAME="agrifrika-${ENVIRONMENT}"

    # Check ECS services
    echo -e "${YELLOW}Vérification des services ECS...${NC}"
    aws ecs describe-services \
        --region "$AWS_REGION" \
        --cluster "${STACK_NAME}-cluster" \
        --services "${STACK_NAME}-backend" "${STACK_NAME}-frontend" \
        --query 'services[*].[serviceName,status,runningCount,desiredCount]' \
        --output table

    # Wait for services to be stable
    echo -e "${YELLOW}Attente de la stabilisation des services...${NC}"
    aws ecs wait services-stable \
        --region "$AWS_REGION" \
        --cluster "${STACK_NAME}-cluster" \
        --services "${STACK_NAME}-backend" "${STACK_NAME}-frontend"

    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
        --output text)

    # Test health endpoint
    echo -e "${YELLOW}Test du health check...${NC}"
    for i in {1..5}; do
        if curl -f -s "https://${ALB_DNS}/health" > /dev/null; then
            echo -e "${GREEN}Health check OK${NC}"
            break
        else
            echo -e "${YELLOW}Tentative $i/5 - Attente...${NC}"
            sleep 10
        fi
    done

    # Test frontend
    echo -e "${YELLOW}Test du frontend...${NC}"
    if curl -f -s "https://${ALB_DNS}/" > /dev/null; then
        echo -e "${GREEN}Frontend accessible${NC}"
    else
        echo -e "${RED}Frontend non accessible${NC}"
    fi

    echo -e "${GREEN}Validation terminée${NC}"
}

# Function to create migration report
create_migration_report() {
    echo -e "${BLUE}Création du rapport de migration...${NC}"

    STACK_NAME="agrifrika-${ENVIRONMENT}"
    REPORT_FILE="aws-migration-report-$(date +%Y%m%d-%H%M%S).md"

    cat > "$REPORT_FILE" << EOF
# Rapport de Migration AWS - Agrifrika Dashboard

**Date**: $(date)
**Environnement**: $ENVIRONMENT
**Région AWS**: $AWS_REGION
**Domaine**: ${DOMAIN_NAME:-"Non configuré"}

## Ressources Créées

### CloudFormation Stacks
- Infrastructure: ${STACK_NAME}-infrastructure
- Services: ${STACK_NAME}-services
- Monitoring: ${STACK_NAME}-monitoring (si déployé)

### ECS
- Cluster: ${STACK_NAME}-cluster
- Service Backend: ${STACK_NAME}-backend
- Service Frontend: ${STACK_NAME}-frontend

### Load Balancer
EOF

    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
        --output text 2>/dev/null || echo "Non trouvé")

    cat >> "$REPORT_FILE" << EOF
- ALB DNS: $ALB_DNS
- URL Application: https://$ALB_DNS

### Secrets Manager
EOF

    # Get secrets ARN
    SECRET_ARN=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='ApplicationSecrets'].OutputValue" \
        --output text 2>/dev/null || echo "Non trouvé")

    cat >> "$REPORT_FILE" << EOF
- Secret ARN: $SECRET_ARN

## Prochaines Étapes

1. Configurer DNS pour pointer vers: $ALB_DNS
2. Vérifier le certificat SSL dans AWS Certificate Manager
3. Configurer le monitoring CloudWatch
4. Tester la charge et l'auto-scaling
5. Arrêter l'ancien déploiement Docker Compose

## Commandes Utiles

\`\`\`bash
# Voir les logs
aws logs tail /ecs/${STACK_NAME}/backend --follow --region $AWS_REGION

# Redémarrer les services
aws ecs update-service --cluster ${STACK_NAME}-cluster --service ${STACK_NAME}-backend --force-new-deployment --region $AWS_REGION

# Vérifier les métriques
aws cloudwatch get-metric-statistics --namespace AWS/ECS --metric-name CPUUtilization --region $AWS_REGION
\`\`\`

## Rollback vers Docker Compose

En cas de problème, vous pouvez revenir au déploiement Docker Compose:

\`\`\`bash
# Arrêter les services AWS
aws ecs update-service --cluster ${STACK_NAME}-cluster --service ${STACK_NAME}-backend --desired-count 0
aws ecs update-service --cluster ${STACK_NAME}-cluster --service ${STACK_NAME}-frontend --desired-count 0

# Redémarrer Docker Compose
docker-compose -f docker-compose.prod.yml up -d
\`\`\`
EOF

    echo -e "${GREEN}Rapport de migration créé: $REPORT_FILE${NC}"
}

# Main migration function
main() {
    echo -e "${BLUE}Début de la migration vers AWS${NC}"

    # Check if infrastructure exists
    if ! aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "agrifrika-${ENVIRONMENT}-infrastructure" &> /dev/null; then
        echo -e "${RED}Infrastructure AWS non trouvée. Exécutez d'abord:${NC}"
        echo -e "./aws/scripts/deploy-aws.sh $ENVIRONMENT $AWS_REGION $DOMAIN_NAME"
        exit 1
    fi

    export_secrets_to_aws
    validate_migration
    create_migration_report

    echo -e "${GREEN}Migration terminée avec succès!${NC}"
}

# Help function
show_help() {
    cat << EOF
Migration Docker Compose vers AWS ECS

Usage: $0 [environment] [region] [domain]

Arguments:
  environment  Environment target (default: production)
  region       Région AWS (default: us-east-1)
  domain       Nom de domaine (optionnel)

Exemples:
  $0 production us-east-1 agrifrika.com
  $0 staging us-west-2
  $0 production

Prérequis:
  - AWS CLI configuré
  - Infrastructure AWS déployée
  - Credentials locaux disponibles
EOF
}

# Handle arguments
case "${1}" in
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        main
        ;;
esac