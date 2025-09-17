# Optimisations pour Usage Faible - Agrifrika Dashboard

Configuration spécialement adaptée pour < 5 utilisateurs par jour avec focus sur l'optimisation des coûts.

## Configuration Recommandée

### Ressources Minimales
- **Instance EC2**: 1x t3.small (2 vCPU, 2 GB RAM)
- **Auto Scaling**: 1-2 instances maximum
- **Backend**: 256 CPU units, 512 MB RAM
- **Frontend**: 128 CPU units, 256 MB RAM

### Coût Mensuel Estimé: $30-35

## Scripts d'Optimisation

### 1. Déploiement Cost-Optimized
```bash
# Utiliser la stack optimisée pour coûts
aws cloudformation deploy \
  --template-file aws/cloudformation/cost-optimized.yml \
  --stack-name agrifrika-cost-optimized \
  --capabilities CAPABILITY_IAM
```

### 2. Configuration Spot Instances (Économie 70%)
```bash
# Déployer avec instances Spot
aws cloudformation deploy \
  --template-file aws/cloudformation/ec2-spot.yml \
  --stack-name agrifrika-spot \
  --parameter-overrides SpotMaxPrice=0.02 \
  --capabilities CAPABILITY_IAM
```

### 3. Scaling Programmé
```bash
# Arrêt automatique nocturne (2h-7h)
# Déjà configuré dans cost-optimized.yml

# Vérifier les schedules
aws autoscaling describe-scheduled-actions \
  --auto-scaling-group-name agrifrika-cost-asg
```

## Monitoring Adapté Usage Faible

### Alertes Ajustées
- **CPU > 60%** (au lieu de 80%) - scaling plus précoce
- **Memory > 75%** (au lieu de 85%)
- **Response time > 3s** (plus tolérant)
- **Coût mensuel > $50** - alerte budget

### Métriques Importantes
```bash
# Vérifier l'utilisation actuelle
aws cloudwatch get-metric-statistics \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 3600 \
  --statistics Average,Maximum
```

## Options d'Économie Supplémentaires

### 1. Reserved Instances (Si Usage Prévisible)
```bash
# Acheter une Reserved Instance t3.small (1 an)
# Économie: ~40% sur le coût de l'instance
aws ec2 purchase-reserved-instances-offering \
  --reserved-instances-offering-id [offering-id] \
  --instance-count 1
```

### 2. CloudWatch Logs Optimisés
```bash
# Réduire la rétention à 7 jours pour économiser
aws logs put-retention-policy \
  --log-group-name /ecs/agrifrika-infrastructure/backend \
  --retention-in-days 7
```

### 3. Application Load Balancer Alternatives
Pour un usage très faible, considérer:
- **Network Load Balancer**: Plus économique pour peu de connexions
- **CloudFront + S3**: Pour le frontend statique seulement
- **Direct EC2**: Éliminer l'ALB complètement (moins sécurisé)

## Configuration Ultra-Économique

### Single Instance Setup
```bash
# Configuration pour 1 seule instance avec tous les services
# backend + frontend + nginx sur la même instance t3.small
# Coût estimé: ~$20/mois total
```

### Docker Compose sur EC2
```bash
# Alternative: Déployer docker-compose directement sur EC2
# Sans ECS, juste Docker Compose sur instance unique
# Script: aws/scripts/simple-ec2-deploy.sh
```

## Scripts de Gestion Spécialisés

### Surveillance des Coûts
```bash
# Vérifier les coûts actuels
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=DIMENSION,Key=SERVICE
```

### Optimisation Automatique
```bash
# Script de monitoring et optimisation
./aws/scripts/cost-optimizer.sh monitor  # Vérifier l'utilisation
./aws/scripts/cost-optimizer.sh optimize  # Appliquer optimisations
```

## Recommandations Spécifiques

### Pour Votre Usage (< 5 utilisateurs/jour)

1. **Instance unique t3.small** avec arrêt nocturne
2. **Spot Instance** pour économiser 70%
3. **Logs réduits** à 7 jours de rétention
4. **Monitoring minimal** - alertes essentielles seulement
5. **Considérer EC2 simple** au lieu d'ECS si pas de scaling prévu

### Migration Progressive
1. **Phase 1**: Démarrer avec configuration standard
2. **Phase 2**: Analyser l'utilisation après 1 semaine
3. **Phase 3**: Migrer vers Spot si stable
4. **Phase 4**: Implémenter scaling nocturne

---

Cette configuration devrait  permettre de rester sous $35/mois tout en maintenant une architecture professionnelle et scalable.