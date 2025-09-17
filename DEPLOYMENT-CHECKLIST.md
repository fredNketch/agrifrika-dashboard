# Checklist de Déploiement - Agrifrika Dashboard

## Préparatifs Avant Déploiement

### 1. Sécurité
- [ ] **Chiffrer les credentials sensibles**
  ```bash
  ./scripts/encrypt-credentials.sh
  ```
- [ ] **Configurer les variables d'environnement**
  - [ ] Mettre à jour `config/.env.prod` avec vos valeurs
  - [ ] Changer `SECRET_KEY` par une valeur unique
  - [ ] Configurer `ALLOWED_ORIGINS` avec votre domaine
- [ ] **Sauvegarder la clé maître** dans un endroit sûr
- [ ] **Supprimer les credentials non chiffrés** après vérification

### 2. Configuration SSL
- [ ] **Avec domaine personnalisé:**
  ```bash
  ./scripts/setup-ssl.sh yourdomain.com admin@yourdomain.com
  ```
- [ ] **Test local (certificats auto-signés):**
  ```bash
  ./scripts/setup-ssl.sh
  ```

### 3. Logging et Monitoring
- [ ] **Configurer la rotation des logs:**
  ```bash
  ./scripts/setup-logging.sh
  ```
- [ ] **Créer les répertoires de logs:**
  ```bash
  mkdir -p logs/{backend,nginx,metrics}
  ```

## Déploiement

### 4. Installation Docker (si nécessaire)
```bash
./deploy.sh install
```

### 5. Déploiement Production
```bash
./deploy.sh production
```

### 6. Configuration SSL Post-Déploiement
```bash
# Si vous avez un domaine
./deploy.sh ssl yourdomain.com
```

## Vérifications Post-Déploiement

### 7. Tests de Santé
- [ ] **Backend:** `curl https://yourdomain.com/api/health`
- [ ] **Frontend:** `curl https://yourdomain.com/`
- [ ] **Certificats SSL:** Vérifier l'expiration dans le navigateur

### 8. Monitoring des Services
```bash
# Statut des conteneurs
docker-compose -f docker-compose.prod.yml ps

# Logs en temps réel
docker-compose -f docker-compose.prod.yml logs -f

# Métriques système
tail -f logs/metrics/system-metrics.log
```

### 9. Tests de Performance
- [ ] **Temps de réponse acceptable** (< 2s)
- [ ] **Gestion de la charge** (test avec ab ou similaire)
- [ ] **Consommation mémoire/CPU** raisonnable

## Maintenance

### 10. Rotation des Logs
```bash
# Test manuel
sudo logrotate -f /etc/logrotate.d/agrifrika

# Nettoyage manuel
/usr/local/bin/agrifrika-cleanup-logs.sh
```

### 11. Renouvellement SSL
```bash
# Manuel (Let's Encrypt)
sudo certbot renew

# Le renouvellement automatique est configuré via cron
```

### 12. Mise à Jour de l'Application
```bash
git pull
./deploy.sh production
```

## Sécurité Continue

### 13. Surveillance
- [ ] **Logs d'erreurs:** Vérifier quotidiennement
- [ ] **Certificats SSL:** Surveiller l'expiration
- [ ] **Mises à jour sécurité:** Système et dépendances

### 14. Sauvegardes
- [ ] **Configuration:** Sauvegarder `config/` régulièrement
- [ ] **Logs critiques:** Archiver selon la politique de rétention
- [ ] **Clé maître:** Sauvegarder dans un coffre-fort sécurisé

## Dépannage

### 15. Problèmes Courants

**Services ne démarrent pas:**
```bash
docker-compose -f docker-compose.prod.yml logs
docker-compose -f docker-compose.prod.yml build --no-cache
```

**Erreurs SSL:**
```bash
./scripts/setup-ssl.sh yourdomain.com
```

**Problèmes de permissions:**
```bash
sudo chown -R $(whoami):$(whoami) logs/
chmod -R 755 logs/
```

**Manque d'espace disque:**
```bash
docker system prune -a
/usr/local/bin/agrifrika-cleanup-logs.sh
```

## Contacts d'Urgence

### 16. Informations Importantes
- **URL Application:** `https://yourdomain.com`
- **Health Check:** `https://yourdomain.com/health`
- **Logs:** `/var/log/agrifrika/`
- **Scripts:** `./scripts/`

### 17. Commandes d'Urgence
```bash
# Arrêt d'urgence
docker-compose -f docker-compose.prod.yml down

# Redémarrage complet
docker-compose -f docker-compose.prod.yml restart

# Rollback (si git configuré)
git checkout HEAD~1 && ./deploy.sh production
```

---

**Note:** Cochez chaque élément au fur et à mesure de sa completion. Conservez ce checklist pour les futures mises à jour.