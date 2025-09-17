# AGRIFRIKA Dashboard

Un système de dashboards en temps réel pour la gestion et le monitoring des KPIs d'AGRIFRIKA, comprenant des métriques financières, opérationnelles et d'engagement.

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Services      │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│   Externes      │
│                 │    │                 │    │                 │
│ • Dashboard 1   │    │ • API REST      │    │ • Google Sheets │
│ • Dashboard 2   │    │ • Swagger/OpenAPI│    │ • Basecamp      │
│ • Monitoring    │    │ • Health Checks │    │ • Facebook      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  ▼
                    ┌─────────────────────────────┐
                    │     Infrastructure          │
                    │  • Docker Compose          │
                    │  • Nginx (SSL/Reverse Proxy)│
                    │  • Logging & Monitoring     │
                    │  • Backup & Security        │
                    └─────────────────────────────┘
```

## Fonctionnalités

### Dashboard 1 - Métriques Financières
- **Default Alive**: Métriques de survie et runway
- **Cash Flow**: Suivi des flux de trésorerie
- **KPIs de croissance**: Revenus, profitabilité, projections

### Dashboard 2 - Opérationnel
- **Disponibilité équipe**: Planning et statuts en temps réel
- **Tâches Basecamp**: Synchronisation automatique des projets
- **Métriques d'engagement**: Statistiques vidéos Facebook
- **Planning hebdomadaire**: Coordination des activités

### Synchronisation Automatique
- **Basecamp → Google Sheets**: Sync bidirectionnelle toutes les heures
- **Validation des données**: Contrôle de cohérence automatique
- **Monitoring**: Alertes et logs détaillés

## Stack Technique

### Frontend
- **React 19** avec TypeScript
- **Vite** pour le build optimisé
- **Tailwind CSS** pour le styling
- **Recharts** pour les visualisations
- **Framer Motion** pour les animations

### Backend
- **FastAPI** avec Python 3.11
- **Pydantic** pour la validation des données
- **Uvicorn** serveur ASGI
- **Swagger/OpenAPI** documentation automatique

### Infrastructure

#### Déploiement Local
- **Docker** et Docker Compose
- **Nginx** reverse proxy avec SSL
- **Let's Encrypt** certificats automatiques
- **Logrotate** gestion des logs

#### Déploiement AWS (Production)
- **ECS sur EC2** avec Auto Scaling pour les conteneurs
- **Application Load Balancer** avec SSL termination
- **AWS Certificate Manager** certificats automatiques
- **CloudWatch** monitoring et logs centralisés
- **AWS Secrets Manager** gestion sécurisée des credentials
- **EFS** stockage persistant
- **Auto Scaling Group** gestion automatique des instances

### Services Externes
- **Google Sheets API** pour les données de planification
- **Basecamp API** pour la gestion de projets
- **Facebook Graph API** pour les métriques d'engagement

## Installation et Déploiement

### Déploiement Local (Docker Compose)

#### Prérequis
- Docker et Docker Compose
- Domaine avec DNS configuré (optionnel pour SSL)
- Credentials pour les APIs externes

### Déploiement AWS (Production Recommandé)

#### Prérequis AWS
- AWS CLI configuré
- Permissions IAM appropriées
- Docker pour build des images
- Domaine configuré (optionnel)

Voir [Guide AWS](aws/README-AWS.md) pour les instructions détaillées.

### Déploiement Local Rapide

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd agrifrika-dashboard
   ```

2. **Configuration de sécurité**
   ```bash
   # Chiffrer les credentials
   ./scripts/encrypt-credentials.sh

   # Configurer les variables d'environnement
   cp config/.env.template config/.env.prod
   # Éditer config/.env.prod avec vos valeurs
   ```

3. **SSL et certificats**
   ```bash
   # Avec domaine personnalisé
   ./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com

   # Ou certificats auto-signés pour les tests
   ./scripts/setup-ssl.sh
   ```

4. **Gestion des logs**
   ```bash
   ./scripts/setup-logging.sh
   ```

5. **Déploiement local**
   ```bash
   ./deploy.sh production
   ```

### Déploiement AWS Production

1. **Préparer AWS**
   ```bash
   aws configure  # Configurer credentials
   ```

2. **Déploiement automatique sur EC2**
   ```bash
   chmod +x aws/scripts/deploy-aws.sh
   ./aws/scripts/deploy-aws.sh production us-east-1 votre-domaine.com
   ```

3. **Configuration des secrets**
   - Aller dans AWS Secrets Manager
   - Mettre à jour les credentials dans le secret créé
   - Voir [Guide AWS](aws/README-AWS.md) pour les détails

### Configuration Avancée

#### Variables d'environnement principales

```bash
# Base
ENV=production
DEBUG=false
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=["https://yourdomain.com"]

# Google Sheets API
GOOGLE_SHEETS_CREDENTIALS_PATH=/app/config/credentials/google-sheets-new-credentials.json
PLANNING_SHEET_ID=votre_sheet_id

# Basecamp API
BASECAMP_ACCESS_TOKEN=votre_token
BASECAMP_ACCOUNT_ID=votre_account_id
BASECAMP_PROJECT_ID=votre_project_id

# Facebook API (optionnel)
FACEBOOK_ACCESS_TOKEN=votre_facebook_token
FACEBOOK_PAGE_ID=votre_page_id
```

#### Sécurité

Le projet implémente plusieurs couches de sécurité :

- **Chiffrement des credentials** avec AES-256-CBC
- **Certificats SSL** automatiques avec Let's Encrypt
- **Headers de sécurité** configurés dans Nginx
- **Utilisateurs non-root** dans les conteneurs Docker
- **Validation des inputs** avec Pydantic
- **Rate limiting** sur les endpoints sensibles

## API Documentation

### Endpoints Principaux

#### Health & Monitoring
- `GET /health` - Vérification rapide de santé
- `GET /health/detailed` - Diagnostic complet
- `GET /health/credentials` - Validation des credentials

#### Dashboard Data
- `GET /api/v1/dashboard1/complete` - Données financières complètes
- `GET /api/v1/dashboard2/complete` - Données opérationnelles complètes

#### Synchronisation
- `GET /api/v1/sync/status` - Statut du service de sync
- `POST /api/v1/sync/execute` - Synchronisation manuelle

### Documentation Interactive

- **Swagger UI**: `https://yourdomain.com/docs`
- **ReDoc**: `https://yourdomain.com/redoc`

## Monitoring et Maintenance

### Logs et Métriques

```bash
# Voir les logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Statut des services
docker-compose -f docker-compose.prod.yml ps

# Métriques système
tail -f logs/metrics/system-metrics.log
```

### Health Checks

L'application expose plusieurs endpoints de monitoring :

- **API Health**: `https://yourdomain.com/health`
- **Services Status**: Validation automatique des APIs externes
- **System Metrics**: Collecte des métriques CPU, mémoire, disque

### Maintenance Automatique

- **Rotation des logs**: Quotidienne via logrotate
- **Nettoyage automatique**: Hebdomadaire via cron
- **Renouvellement SSL**: Automatique avec Let's Encrypt
- **Synchronisation**: Toutes les heures entre Basecamp et Google Sheets

## Développement

### Setup Local

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

### Scripts Utiles

```bash
# Tests
npm test                              # Frontend
pytest                              # Backend

# Linting
npm run lint                         # Frontend
flake8 app/                         # Backend

# Build
npm run build                       # Frontend
docker build -t agrifrika-backend .  # Backend
```

### Structure du Projet

```
agrifrika-dashboard/
├── backend/                     # API FastAPI
│   ├── app/
│   │   ├── api/                # Routes API
│   │   ├── core/               # Configuration
│   │   ├── models/             # Modèles Pydantic
│   │   ├── schemas/            # Schémas OpenAPI
│   │   ├── services/           # Logique métier
│   │   └── main.py            # Point d'entrée
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                    # Application React
│   ├── src/
│   │   ├── components/         # Composants React
│   │   ├── hooks/              # Hooks personnalisés
│   │   ├── services/           # Appels API
│   │   └── main.tsx           # Point d'entrée
│   ├── Dockerfile
│   └── package.json
├── nginx/                       # Configuration reverse proxy
│   └── nginx.conf
├── config/                      # Configuration globale
│   ├── .env.prod               # Variables production
│   └── credentials/            # Credentials chiffrés
├── scripts/                     # Scripts de déploiement
│   ├── deploy.sh
│   ├── encrypt-credentials.sh
│   ├── setup-ssl.sh
│   └── setup-logging.sh
├── docker-compose.prod.yml      # Orchestration production
└── README.md
```

## Troubleshooting

### Problèmes Courants

**Services ne démarrent pas**
```bash
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml build --no-cache
```

**Erreurs SSL**
```bash
./scripts/setup-ssl.sh yourdomain.com
```

**Problèmes de synchronisation**
```bash
# Vérifier le statut
curl https://yourdomain.com/api/v1/sync/status

# Synchronisation manuelle
curl -X POST https://yourdomain.com/api/v1/sync/execute
```

**Manque d'espace disque**
```bash
docker system prune -a
/usr/local/bin/agrifrika-cleanup-logs.sh
```

### Logs de Debug

```bash
# Logs application
docker-compose -f docker-compose.prod.yml logs backend

# Logs Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Logs système
sudo journalctl -u docker

# Métriques de performance
tail -f logs/metrics/system-metrics.log
```

## Sécurité

### Mesures Implémentées

- **Chiffrement**: Credentials chiffrés avec AES-256-CBC
- **HTTPS**: SSL/TLS avec certificats Let's Encrypt
- **Headers sécurisés**: HSTS, CSP, X-Frame-Options
- **Rate limiting**: Protection contre les attaques DDoS
- **Validation inputs**: Sanitisation avec Pydantic
- **Conteneurs sécurisés**: Utilisateurs non-root, volumes read-only

### Checklist Sécurité

- [ ] Credentials chiffrés et clé maître sauvegardée
- [ ] Certificats SSL valides et renouvellement automatique
- [ ] Variables d'environnement sécurisées
- [ ] Firewall configuré (ports 22, 80, 443 uniquement)
- [ ] Logs de sécurité activés
- [ ] Sauvegardes régulières

## Performance

### Optimisations

- **Cache**: TTL configuré pour les APIs externes
- **Compression**: Gzip activé sur Nginx
- **Requêtes parallèles**: asyncio.gather pour les appels API
- **Build optimisé**: Vite avec tree-shaking
- **Docker multi-stage**: Images légères en production

### Métriques

- **Temps de réponse**: < 2s pour les dashboards complets
- **Consommation mémoire**: < 512MB par conteneur
- **CPU**: < 50% en charge normale
- **Stockage**: Rotation automatique des logs

## Contribution

### Guidelines

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. **Commit** les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. **Push** vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. **Créer** une Pull Request

### Standards

- **Code style**: ESLint pour TypeScript, Black pour Python
- **Tests**: Coverage > 80%
- **Documentation**: Swagger pour API, JSDoc pour composants
- **Commits**: Conventional Commits format

## Licence

MIT License - voir le fichier [LICENSE](LICENSE) pour les détails.

## Support

### Contacts
- **Email technique**: tech@agrifrika.com
- **Documentation**: https://yourdomain.com/docs
- **Issues**: GitHub Issues

### Ressources
- **Status page**: https://yourdomain.com/health
- **API docs**: https://yourdomain.com/docs
- **Monitoring**: https://yourdomain.com/metrics

---

**Version**: 1.0.0
**Dernière mise à jour**: $(date -u +"%Y-%m-%dT%H:%M:%SZ")
**Environnement**: Production Ready