# Checklist de Déploiement AWS EC2 - Agrifrika Dashboard (Usage Faible)

## Préparatifs Avant Déploiement

### 1. Configuration AWS
- [ ] **AWS CLI installé et configuré**
  ```bash
  aws configure
  aws sts get-caller-identity  # Vérifier les credentials
  ```
- [ ] **Permissions IAM appropriées**
  - [ ] ECS (FullAccess ou custom policy)
  - [ ] EC2 (instances, VPC, Security Groups, Load Balancer, Auto Scaling)
  - [ ] ECR (push/pull images)
  - [ ] CloudFormation (deploy stacks)
  - [ ] Secrets Manager (manage secrets)
  - [ ] Certificate Manager (SSL certificates)
  - [ ] CloudWatch (logs et monitoring)

### 2. Préparation du Code
- [ ] **Variables d'environnement configurées**
  ```bash
  cp config/.env.template config/.env.prod
  # Éditer avec les valeurs de production
  ```
- [ ] **Credentials préparés**
  - [ ] Google Sheets API credentials (JSON)
  - [ ] Google Analytics credentials (JSON)
  - [ ] Tokens Basecamp et Facebook
- [ ] **Code testé localement**
  ```bash
  docker-compose -f docker-compose.prod.yml up -d
  curl http://localhost/health
  ```

## Déploiement AWS

### 3. Choix de la Région
- [ ] **Région AWS sélectionnée** (exemple: us-east-1)
- [ ] **Vérifier les quotas de service** (ECS, ECR, ALB, EC2 instances)
- [ ] **Note**: Configuration optimisée pour < 5 utilisateurs/jour
- [ ] **Domaine configuré** (optionnel mais recommandé)

### 4. Déploiement Infrastructure
```bash
# Option 1: Déploiement automatique
./aws/scripts/deploy-aws.sh production us-east-1 yourdomain.com

# Option 2: Déploiement manuel étape par étape
```

#### Déploiement Manuel - Étapes:
- [ ] **Créer les repositories ECR**
  ```bash
  aws ecr create-repository --repository-name agrifrika-backend
  aws ecr create-repository --repository-name agrifrika-frontend
  ```
- [ ] **Déployer l'infrastructure**
  ```bash
  aws cloudformation deploy \
    --template-file aws/cloudformation/infrastructure.yml \
    --stack-name agrifrika-infrastructure \
    --capabilities CAPABILITY_IAM
  ```
- [ ] **Build et push des images**
  ```bash
  aws ecr get-login-password | docker login --username AWS --password-stdin ECR_URI
  docker build -t agrifrika-backend ./backend/
  docker tag agrifrika-backend ECR_URI/agrifrika-backend:latest
  docker push ECR_URI/agrifrika-backend:latest
  ```
- [ ] **Configurer les secrets**
  ```bash
  aws secretsmanager put-secret-value --secret-id SECRET_ARN --secret-string '{...}'
  ```
- [ ] **Déployer les services**
  ```bash
  aws cloudformation deploy \
    --template-file aws/cloudformation/services.yml \
    --stack-name agrifrika-services \
    --capabilities CAPABILITY_IAM
  ```

### 5. Configuration DNS (si domaine)
- [ ] **Route 53 configuré** ou DNS externe
  ```bash
  # Obtenir l'ALB DNS
  aws cloudformation describe-stacks --stack-name agrifrika-infrastructure \
    --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue"

  # Configurer CNAME: yourdomain.com -> ALB_DNS
  ```
- [ ] **Certificat SSL validé** (ACM)
  ```bash
  aws acm list-certificates --certificate-statuses ISSUED
  ```

## Vérifications Post-Déploiement

### 6. Tests de Santé
- [ ] **Instances EC2 enregistrées dans ECS**
  ```bash
  aws ecs list-container-instances --cluster agrifrika-infrastructure-cluster
  aws ec2 describe-instances --filters Name=tag:aws:autoscaling:groupName,Values=agrifrika-infrastructure-asg
  ```
- [ ] **Services ECS en cours d'exécution**
  ```bash
  aws ecs describe-services --cluster agrifrika-infrastructure-cluster \
    --services agrifrika-infrastructure-backend agrifrika-infrastructure-frontend
  ```
- [ ] **Health checks passent**
  ```bash
  curl https://ALB_DNS/health
  curl https://yourdomain.com/health  # Si domaine configuré
  ```
- [ ] **Application accessible**
  ```bash
  curl https://ALB_DNS/
  curl https://yourdomain.com/  # Si domaine configuré
  ```

### 7. Monitoring et Alertes
- [ ] **CloudWatch Dashboard configuré**
  ```bash
  ./aws/scripts/setup-cloudwatch.sh agrifrika-infrastructure us-east-1
  ```
- [ ] **Alertes SNS configurées**
  - [ ] Email d'alerte configuré
  - [ ] Alertes CPU/Memory actives
  - [ ] Alertes erreurs 5XX actives
- [ ] **Logs accessibles**
  ```bash
  aws logs tail /ecs/agrifrika-infrastructure/backend --follow
  ```

### 8. Tests de Performance
- [ ] **Temps de réponse acceptable** (< 2s)
  ```bash
  curl -w "@curl-format.txt" -o /dev/null -s https://yourdomain.com/api/v1/dashboard1/complete
  ```
- [ ] **Auto-scaling fonctionnel**
  ```bash
  # Générer de la charge et vérifier le scaling
  aws ecs describe-services --cluster agrifrika-infrastructure-cluster \
    --services agrifrika-infrastructure-backend
  ```

## Configuration de Production

### 9. Secrets Management
- [ ] **Tous les secrets configurés dans AWS Secrets Manager**
  - [ ] GOOGLE_SHEETS_CREDENTIALS
  - [ ] GOOGLE_ANALYTICS_CREDENTIALS
  - [ ] BASECAMP_TOKEN
  - [ ] BASECAMP_ACCOUNT_ID
  - [ ] BASECAMP_PROJECT_ID
  - [ ] FACEBOOK_ACCESS_TOKEN
  - [ ] FACEBOOK_PAGE_ID
  - [ ] SECRET_KEY
- [ ] **Rotation des secrets planifiée** (si applicable)

### 10. Sauvegarde et Disaster Recovery
- [ ] **EFS backup configuré** (si utilisé)
  ```bash
  aws efs put-backup-policy --file-system-id fs-xxx --backup-policy Status=ENABLED
  ```
- [ ] **Images ECR avec tags multiples**
  ```bash
  # Tagger avec version et latest
  docker tag image ECR_URI/repo:v1.0.0
  docker tag image ECR_URI/repo:latest
  ```
- [ ] **Documentation des procédures de récupération**

### 11. Sécurité
- [ ] **Security Groups configurés** (ports minimaux)
- [ ] **IAM roles avec permissions minimales**
- [ ] **Chiffrement activé** (EFS, Secrets Manager, ECR)
- [ ] **SSL/TLS correctement configuré**
- [ ] **WAF configuré** (optionnel mais recommandé pour production)

## Maintenance Continue

### 12. Monitoring
- [ ] **CloudWatch Dashboard vérifié quotidiennement**
- [ ] **Alertes SNS testées et fonctionnelles**
- [ ] **Logs d'erreurs surveillés**
- [ ] **Métriques de performance suivies**

### 13. Mises à Jour
- [ ] **Processus de CI/CD configuré** (optionnel)
- [ ] **Stratégie de rollback définie**
  ```bash
  # Rollback rapide
  aws ecs update-service --cluster CLUSTER --service SERVICE \
    --task-definition FAMILY:PREVIOUS_REVISION
  ```
- [ ] **Tests automatisés en place**

### 14. Optimisation des Coûts
- [ ] **Auto-scaling EC2 configuré et testé**
- [ ] **Utilisation d'instances Spot EC2** (optionnel)
- [ ] **Retention des logs optimisée** (14 jours)
- [ ] **Surveillance des coûts AWS activée**
- [ ] **Right-sizing des instances** (t3.small pour usage faible)
- [ ] **Configuration du scaling nocturne** (arrêt 2h-7h)
- [ ] **Considérer Spot Instances** (jusqu'à 70% d'économie)

## Contacts et Ressources

### 15. Documentation
- [ ] **Guide AWS**: [aws/README-AWS.md](aws/README-AWS.md)
- [ ] **Architecture AWS**: Diagrammes mis à jour
- [ ] **Runbooks**: Procédures d'incident documentées

### 16. URLs Importantes
- **Application**: https://yourdomain.com
- **Health Check**: https://yourdomain.com/health
- **API Docs**: https://yourdomain.com/docs
- **CloudWatch**: Console AWS > CloudWatch > Dashboards
- **ECS Console**: Console AWS > ECS > Clusters

### 17. Commandes d'Urgence AWS
```bash
# Arrêt d'urgence
aws ecs update-service --cluster CLUSTER --service SERVICE --desired-count 0

# Redémarrage des services
aws ecs update-service --cluster CLUSTER --service SERVICE --force-new-deployment

# Scaling rapide
aws ecs update-service --cluster CLUSTER --service SERVICE --desired-count 3

# Rollback
aws ecs update-service --cluster CLUSTER --service SERVICE \
  --task-definition FAMILY:PREVIOUS_REVISION
```

---

**Note**: Cochez chaque élément au fur et à mesure. Ce checklist couvre le déploiement AWS complet avec toutes les bonnes pratiques de sécurité et monitoring.