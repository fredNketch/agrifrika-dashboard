#!/bin/bash

# Docker entrypoint script pour déchiffrer les credentials au runtime
# Ce script est exécuté au démarrage du conteneur backend

set -e

echo "Agrifrika Dashboard - Initialisation sécurisée..."

# Vérifier si la clé maître est disponible
if [ -n "$MASTER_KEY" ]; then
    echo "Clé maître trouvée dans les variables d'environnement"
    echo "$MASTER_KEY" > /tmp/master.key
elif [ -f "/run/secrets/master_key" ]; then
    echo "Clé maître trouvée dans les secrets Docker"
    cp /run/secrets/master_key /tmp/master.key
elif [ -f "/app/config/credentials-secure/master.key" ]; then
    echo "Clé maître trouvée dans le volume monté"
    cp /app/config/credentials-secure/master.key /tmp/master.key
else
    echo "ATTENTION: Aucune clé maître trouvée. Utilisation des credentials non chiffrés si disponibles."
fi

# Fonction de déchiffrement
decrypt_file() {
    local encrypted_file=$1
    local output_file=$2

    if [ -f "$encrypted_file" ] && [ -f "/tmp/master.key" ]; then
        echo "Déchiffrement de $(basename $encrypted_file)..."
        mkdir -p "$(dirname $output_file)"
        openssl enc -aes-256-cbc -d -in "$encrypted_file" \
            -out "$output_file" \
            -pass file:/tmp/master.key
        chmod 600 "$output_file"
        echo "✓ Fichier déchiffré: $output_file"
    fi
}

# Déchiffrer les credentials Google si nécessaire
decrypt_file "/app/config/credentials-secure/google-sheets-new-credentials.json.enc" \
            "/app/config/credentials/google-sheets-new-credentials.json"

decrypt_file "/app/config/credentials-secure/google-analytics-credentials.json.enc" \
            "/app/config/credentials/google-analytics-credentials.json"

# Déchiffrer les variables d'environnement si nécessaire
if [ -f "/app/config/credentials-secure/.env.enc" ] && [ -f "/tmp/master.key" ]; then
    echo "Déchiffrement des variables d'environnement..."
    openssl enc -aes-256-cbc -d -in "/app/config/credentials-secure/.env.enc" \
        -out "/app/config/.env.runtime" \
        -pass file:/tmp/master.key

    # Charger les variables d'environnement déchiffrées
    set -a
    source /app/config/.env.runtime
    set +a

    echo "✓ Variables d'environnement chargées"
fi

# Nettoyer la clé temporaire
if [ -f "/tmp/master.key" ]; then
    rm -f /tmp/master.key
fi

echo "Initialisation terminée. Démarrage de l'application..."

# Exécuter la commande principale
exec "$@"