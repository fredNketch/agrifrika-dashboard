# AGRIFRIKA Dashboard - Déploiement AWS

Guide complet pour déployer l'application Agrifrika Dashboard sur AWS avec ECS sur EC2, Application Load Balancer et services managés.

## Architecture AWS

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   CloudFront        │    │   Application       │    │   ECS sur EC2       │
│   (optionnel)       │◄──►│   Load Balancer     │◄──►│   Services          │
│                     │    │                     │    │                     │
│ • CDN global        │    │ • SSL termination   │    │ • Backend (FastAPI) │
│ • Edge caching      │    │ • Health checks     │    │ • Frontend (React)  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
         ▲                          ▲                          ▲
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    ▼
              ┌─────────────────────────────────────────────────────┐
              │              Services AWS Managés                   │
              │ • ECR (images)     • Secrets Manager (credentials)  │
              │ • CloudWatch (logs)• Certificate Manager (SSL)     │
              │ • EFS (storage)    • Route 53 (DNS)               │
              └─────────────────────────────────────────────────────┘
```

## Prérequis AWS

### 1. AWS CLI Configuration
```bash
# Installer AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configurer les credentials
aws configure
```

### 2. Permissions IAM Requises
L'utilisateur/rôle doit avoir les permissions suivantes:
- ECS (création clusters, services, task definitions)
- EC2 (VPC, subnets, security groups)
- ELB (Application Load Balancer)
- ECR (repositories d'images)
- IAM (création de rôles pour ECS)
- CloudFormation (déploiement stacks)
- Secrets Manager (gestion credentials)
- Certificate Manager (certificats SSL)
- CloudWatch (monitoring et logs)
- EFS (stockage persistant)

### 3. Structure des Fichiers AWS
```
aws/
├── cloudformation/
│   ├── infrastructure.yml      # VPC, ALB, ECS cluster, Auto Scaling Group
│   ├── services.yml           # ECS services et task definitions
│   ├── monitoring.yml         # CloudWatch dashboards et alertes
│   ├── cost-optimized.yml     # Configuration optimisée coûts (< 5 users/jour)
│   └── ec2-spot.yml          # Configuration Spot instances
├── ecs/
│   ├── task-definition-backend.json  # Task definition backend (EC2/t3.small)
│   └── task-definition-frontend.json # Task definition frontend (EC2/t3.small)
├── scripts/
│   ├── deploy-aws.sh          # Script de déploiement principal
│   ├── aws-entrypoint.sh      # Entrypoint pour containers AWS
│   ├── setup-cloudwatch.sh    # Configuration monitoring
│   ├── migrate-to-aws.sh      # Migration depuis Docker Compose
│   ├── manage-ec2-scaling.sh  # Gestion du scaling EC2
│   └── simple-ec2-deploy.sh   # Déploiement ultra-économique ($20/mois)
├── nginx/
│   └── nginx-aws.conf         # Config nginx pour tests locaux
├── docker-compose.aws.yml     # Tests locaux avec config AWS
├── LOW-TRAFFIC-OPTIMIZATION.md # Guide optimisation usage faible
└── README-AWS.md             # Cette documentation
```

## Déploiement AWS

### 1. Options de Déploiement

#### Option A: ECS Complet (Recommandé pour évolutivité)
```bash
# Déploiement ECS avec Auto Scaling
chmod +x aws/scripts/deploy-aws.sh
./aws/scripts/deploy-aws.sh production us-east-1 yourdomain.com
# Coût: ~$40-45/mois
```

#### Option B: Ultra-Économique (Recommandé pour votre usage)
```bash
# Déploiement EC2 simple pour < 5 utilisateurs/jour
chmod +x aws/scripts/simple-ec2-deploy.sh
./aws/scripts/simple-ec2-deploy.sh production us-east-1 yourdomain.com
# Coût: ~$20-25/mois
```

#### Option C: Configuration Cost-Optimized
```bash
# ECS avec instances t3.small et optimisations
aws cloudformation deploy --template-file aws/cloudformation/cost-optimized.yml
# Coût: ~$30-35/mois
```

### 2. Déploiement Étape par Étape

#### Étape 1: Déployer l'infrastructure
```bash
cd aws
aws cloudformation deploy \
  --region us-east-1 \
  --template-file cloudformation/infrastructure.yml \
  --stack-name agrifrika-infrastructure \
  --parameter-overrides Environment=production DomainName=yourdomain.com \
  --capabilities CAPABILITY_IAM
```

#### Étape 2: Créer les repositories ECR
```bash
# Backend
aws ecr create-repository \
  --region us-east-1 \
  --repository-name agrifrika-backend \
  --image-scanning-configuration scanOnPush=true

# Frontend
aws ecr create-repository \
  --region us-east-1 \
  --repository-name agrifrika-frontend \
  --image-scanning-configuration scanOnPush=true
```

#### Étape 3: Build et push des images
```bash
# Obtenir le token ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

# Build backend
docker build -t agrifrika-backend ./backend/
docker tag agrifrika-backend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-backend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-backend:latest

# Build frontend
docker build -t agrifrika-frontend ./frontend/
docker tag agrifrika-frontend:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-frontend:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-frontend:latest
```

#### Étape 4: Configurer les secrets
```bash
# Obtenir l'ARN du secret
SECRET_ARN=$(aws cloudformation describe-stacks \
  --region us-east-1 \
  --stack-name agrifrika-infrastructure \
  --query "Stacks[0].Outputs[?OutputKey=='ApplicationSecrets'].OutputValue" \
  --output text)

# Mettre à jour les secrets
aws secretsmanager put-secret-value \
  --region us-east-1 \
  --secret-id "$SECRET_ARN" \
  --secret-string '{
    "GOOGLE_SHEETS_CREDENTIALS": "contenu-du-fichier-json",
    "GOOGLE_ANALYTICS_CREDENTIALS": "contenu-du-fichier-json",
    "BASECAMP_TOKEN": "votre-token",
    "BASECAMP_ACCOUNT_ID": "votre-account-id",
    "BASECAMP_PROJECT_ID": "votre-project-id",
    "FACEBOOK_ACCESS_TOKEN": "votre-facebook-token",
    "FACEBOOK_PAGE_ID": "votre-page-id",
    "SECRET_KEY": "votre-cle-secrete-forte"
  }'
```

#### Étape 5: Déployer les services
```bash
aws cloudformation deploy \
  --region us-east-1 \
  --template-file cloudformation/services.yml \
  --stack-name agrifrika-services \
  --parameter-overrides \
    StackName=agrifrika-infrastructure \
    Environment=production \
    ECRRepositoryURI=123456789012.dkr.ecr.us-east-1.amazonaws.com \
  --capabilities CAPABILITY_IAM
```

## Configuration DNS

### Route 53 (Recommandé)
```bash
# Créer la zone hébergée
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s)

# Obtenir l'ALB DNS
ALB_DNS=$(aws cloudformation describe-stacks \
  --region us-east-1 \
  --stack-name agrifrika-infrastructure \
  --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
  --output text)

# Créer l'enregistrement CNAME
aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456789 \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "yourdomain.com",
        "Type": "CNAME",
        "TTL": 300,
        "ResourceRecords": [{"Value": "'$ALB_DNS'"}]
      }
    }]
  }'
```

## Monitoring et Logs

### CloudWatch Dashboards
```bash
# Configurer le monitoring
./aws/scripts/setup-cloudwatch.sh agrifrika-infrastructure us-east-1
```

### Consultation des Logs
```bash
# Logs en temps réel
aws logs tail /ecs/agrifrika-infrastructure/backend --follow --region us-east-1
aws logs tail /ecs/agrifrika-infrastructure/frontend --follow --region us-east-1

# Logs par période
aws logs filter-log-events \
  --region us-east-1 \
  --log-group-name /ecs/agrifrika-infrastructure/backend \
  --start-time $(date -d '1 hour ago' +%s)000
```

### Métriques Importantes
- **ECS Services**: CPU, Memory, Task Count
- **Application Load Balancer**: Response Time, Request Count, Error Rates
- **Custom Metrics**: Application-specific metrics via CloudWatch API

## Gestion des Secrets

### AWS Secrets Manager
```bash
# Lister les secrets
aws secretsmanager list-secrets --region us-east-1

# Mettre à jour un secret
aws secretsmanager update-secret \
  --region us-east-1 \
  --secret-id "agrifrika-production/application-secrets" \
  --secret-string '{"BASECAMP_TOKEN": "nouveau-token"}'

# Récupérer un secret
aws secretsmanager get-secret-value \
  --region us-east-1 \
  --secret-id "agrifrika-production/application-secrets"
```

### Migration des Credentials Existants
```bash
# Depuis les credentials chiffrés locaux
./scripts/encrypt-credentials.sh  # Si pas déjà fait

# Extraire et uploader vers AWS
GOOGLE_SHEETS_CREDS=$(cat config/credentials/google-sheets-new-credentials.json)
aws secretsmanager put-secret-value \
  --secret-id "$SECRET_ARN" \
  --secret-string "{\"GOOGLE_SHEETS_CREDENTIALS\": \"$GOOGLE_SHEETS_CREDS\"}"
```

## Mise à Jour et Maintenance

### Déploiement d'une Nouvelle Version
```bash
# Build et push nouvelle image
docker build -t agrifrika-backend:v2.0 ./backend/
docker tag agrifrika-backend:v2.0 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-backend:v2.0
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/agrifrika-backend:v2.0

# Mettre à jour le service
aws ecs update-service \
  --cluster agrifrika-infrastructure-cluster \
  --service agrifrika-infrastructure-backend \
  --force-new-deployment
```

### Rolling Back
```bash
# Revenir à la version précédente
aws ecs update-service \
  --cluster agrifrika-infrastructure-cluster \
  --service agrifrika-infrastructure-backend \
  --task-definition agrifrika-backend:PREVIOUS_REVISION
```

### Scaling Manuel
```bash
# Augmenter le nombre d'instances EC2
aws autoscaling set-desired-capacity \
  --auto-scaling-group-name agrifrika-infrastructure-asg \
  --desired-capacity 3

# Augmenter le nombre de tasks ECS
aws ecs update-service \
  --cluster agrifrika-infrastructure-cluster \
  --service agrifrika-infrastructure-backend \
  --desired-count 3

# Utiliser le script de gestion
./aws/scripts/manage-ec2-scaling.sh scale-out 4
```

## Optimisations de Coûts

### 1. Auto Scaling EC2
Les instances EC2 sont gérées par un Auto Scaling Group avec scaling automatique basé sur la charge ECS.

### 2. Auto Scaling
Auto scaling configuré basé sur CPU (seuil 70%).

### 3. Log Retention
Logs CloudWatch avec rétention de 14 jours pour optimiser les coûts.

### 4. Ressources Dimensionnées (Usage Faible)
- Instances EC2: t3.small (2 vCPU, 2 GB RAM) - optimisé pour < 5 utilisateurs/jour
- Auto Scaling: 1-2 instances maximum
- Backend: 256 CPU units, 512 MB RAM par conteneur
- Frontend: 128 CPU units, 256 MB RAM par conteneur
- Scaling plus conservateur avec cooldowns plus longs

## Tests Locaux avec Configuration AWS

```bash
# Test en local avec la configuration AWS
cd aws
docker-compose -f docker-compose.aws.yml up -d

# Vérifier les services
docker-compose -f docker-compose.aws.yml ps
docker-compose -f docker-compose.aws.yml logs -f
```

## Sécurité AWS

### Network Security
- VPC dédiée avec subnets publics
- Security Groups restrictifs
- Communication interne uniquement

### Secrets Management
- AWS Secrets Manager pour tous les credentials
- Rotation automatique disponible
- Chiffrement au repos et en transit

### Monitoring de Sécurité
- CloudTrail pour l'audit des actions
- GuardDuty pour la détection de menaces (optionnel)
- Config Rules pour la conformité (optionnel)

## Dépannage

### Services ne démarrent pas
```bash
# Vérifier les logs ECS
aws ecs describe-services \
  --cluster agrifrika-infrastructure-cluster \
  --services agrifrika-infrastructure-backend

# Vérifier les task definitions
aws ecs describe-task-definition \
  --task-definition agrifrika-backend
```

### Problèmes de Load Balancer
```bash
# Vérifier les target groups
aws elbv2 describe-target-health \
  --target-group-arn arn:aws:elasticloadbalancing:...

# Vérifier les logs ALB
aws logs filter-log-events \
  --log-group-name /aws/elb/agrifrika-infrastructure-alb
```

### Problèmes de Secrets
```bash
# Vérifier l'accès aux secrets
aws secretsmanager get-secret-value \
  --secret-id agrifrika-production/application-secrets

# Vérifier les permissions IAM
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:role/ECSTaskRole \
  --action-names secretsmanager:GetSecretValue \
  --resource-arns arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:*
```

## Coûts Estimés (us-east-1)

### Configuration Optimisée pour < 5 Utilisateurs/Jour

#### Compute (ECS sur EC2)
- t3.small (2 vCPU, 2 GB): ~$15/mois (1 instance)
- Auto Scaling: 1-2 instances maximum
- Scaling nocturne: arrêt automatique 2h-7h (économie ~30%)

#### Load Balancer
- Application Load Balancer: ~$16/mois
- Data transfer: < $1/mois (faible trafic)

#### Stockage et Services
- EFS: ~$0.30/GB/mois (minimal)
- CloudWatch Logs: < $1/mois (faible volume)
- Secrets Manager: ~$0.40/mois
- Certificate Manager: Gratuit

#### Options d'Optimisation
- **Spot Instances**: Jusqu'à 70% d'économie (~$5/mois au lieu de $15)
- **Scaling programmé**: Arrêt nocturne (économie 8h/jour)
- **Reserved Instances**: -40% si usage prévisible

**Total estimé: $30-35/mois** (avec optimisations Spot et scaling)
**Total standard: $40-45/mois** (instances On-Demand)

## Support et Monitoring

### URLs Importantes
- Application: https://yourdomain.com
- Health Check: https://yourdomain.com/health
- API Docs: https://yourdomain.com/docs
- CloudWatch Dashboard: Console AWS > CloudWatch > Dashboards

### Alertes Configurées
- CPU > 80% pendant 10 minutes
- Memory > 85% pendant 10 minutes
- Response time > 2s pendant 15 minutes
- Erreurs 5XX > 10 en 5 minutes

### Commandes Utiles
```bash
# Statut des services
aws ecs describe-services --cluster agrifrika-infrastructure-cluster --services agrifrika-infrastructure-backend agrifrika-infrastructure-frontend

# Redémarrer un service
aws ecs update-service --cluster agrifrika-infrastructure-cluster --service agrifrika-infrastructure-backend --force-new-deployment

# Voir les métriques
aws cloudwatch get-metric-statistics \
  --namespace AWS/ECS \
  --metric-name CPUUtilization \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average \
  --dimensions Name=ServiceName,Value=agrifrika-infrastructure-backend
```

## Migration depuis Docker Compose

### Différences Principales
1. **Compute**: ECS sur EC2 avec Auto Scaling au lieu de conteneurs locaux
2. **Networking**: AWS VPC au lieu de Docker networks
3. **Load Balancing**: ALB au lieu de Nginx interne
4. **Secrets**: AWS Secrets Manager au lieu de fichiers chiffrés
5. **Logs**: CloudWatch au lieu de volumes locaux
6. **SSL**: Certificate Manager au lieu de Let's Encrypt
7. **Storage**: EFS au lieu de volumes Docker
8. **Scaling**: Auto Scaling Group EC2 au lieu de scaling manuel

### Script de Migration
Un script de migration automatique sera disponible prochainement pour faciliter la transition depuis un déploiement Docker Compose existant.

---
