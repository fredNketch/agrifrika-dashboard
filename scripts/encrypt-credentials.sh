#!/bin/bash

# Script de chiffrement des credentials pour Agrifrika Dashboard
# Usage: ./encrypt-credentials.sh

set -e

CREDENTIALS_DIR="config/credentials"
SECURE_DIR="config/credentials-secure"
ENV_FILE="config/.env"

echo "Chiffrement des credentials Agrifrika Dashboard..."

# Vérifier que les dossiers existent
if [ ! -d "$CREDENTIALS_DIR" ]; then
    echo "Erreur: Le dossier $CREDENTIALS_DIR n'existe pas"
    exit 1
fi

# Créer le dossier sécurisé
mkdir -p "$SECURE_DIR"

# Générer une clé de chiffrement si elle n'existe pas
if [ ! -f "$SECURE_DIR/master.key" ]; then
    echo "Génération de la clé maître..."
    openssl rand -base64 32 > "$SECURE_DIR/master.key"
    chmod 600 "$SECURE_DIR/master.key"
    echo "Clé maître générée dans $SECURE_DIR/master.key"
fi

# Chiffrer les fichiers JSON de credentials
for file in "$CREDENTIALS_DIR"/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "Chiffrement de $filename..."

        # Chiffrer avec AES-256-CBC
        openssl enc -aes-256-cbc -salt -in "$file" \
            -out "$SECURE_DIR/${filename}.enc" \
            -pass file:"$SECURE_DIR/master.key"

        echo "✓ $filename chiffré -> ${filename}.enc"
    fi
done

# Créer un script de déchiffrement
cat > "$SECURE_DIR/decrypt.sh" << 'EOF'
#!/bin/bash
# Script de déchiffrement des credentials
# Usage: ./decrypt.sh [filename.json]

SECURE_DIR="config/credentials-secure"
OUTPUT_DIR="config/credentials"

if [ -z "$1" ]; then
    echo "Usage: $0 <filename.json>"
    echo "Fichiers disponibles:"
    ls -1 "$SECURE_DIR"/*.enc | sed 's/.*\///;s/\.enc$//'
    exit 1
fi

ENCRYPTED_FILE="$SECURE_DIR/$1.enc"
OUTPUT_FILE="$OUTPUT_DIR/$1"

if [ ! -f "$ENCRYPTED_FILE" ]; then
    echo "Erreur: Fichier $ENCRYPTED_FILE non trouvé"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

openssl enc -aes-256-cbc -d -in "$ENCRYPTED_FILE" \
    -out "$OUTPUT_FILE" \
    -pass file:"$SECURE_DIR/master.key"

echo "Fichier déchiffré: $OUTPUT_FILE"
EOF

chmod +x "$SECURE_DIR/decrypt.sh"

# Créer un script de chiffrement des variables d'environnement
cat > "$SECURE_DIR/encrypt-env.sh" << 'EOF'
#!/bin/bash
# Chiffrement des variables d'environnement sensibles

SECURE_DIR="config/credentials-secure"
ENV_FILE="config/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Erreur: Fichier $ENV_FILE non trouvé"
    exit 1
fi

# Chiffrer le fichier .env
openssl enc -aes-256-cbc -salt -in "$ENV_FILE" \
    -out "$SECURE_DIR/.env.enc" \
    -pass file:"$SECURE_DIR/master.key"

echo "✓ Fichier .env chiffré -> .env.enc"
EOF

chmod +x "$SECURE_DIR/encrypt-env.sh"

# Créer un script de déchiffrement pour .env
cat > "$SECURE_DIR/decrypt-env.sh" << 'EOF'
#!/bin/bash
# Déchiffrement des variables d'environnement

SECURE_DIR="config/credentials-secure"
OUTPUT_FILE="config/.env.prod"

if [ ! -f "$SECURE_DIR/.env.enc" ]; then
    echo "Erreur: Fichier .env.enc non trouvé"
    exit 1
fi

openssl enc -aes-256-cbc -d -in "$SECURE_DIR/.env.enc" \
    -out "$OUTPUT_FILE" \
    -pass file:"$SECURE_DIR/master.key"

echo "Variables d'environnement déchiffrées: $OUTPUT_FILE"
EOF

chmod +x "$SECURE_DIR/decrypt-env.sh"

# Chiffrer le fichier .env
if [ -f "$ENV_FILE" ]; then
    echo "Chiffrement du fichier .env..."
    "$SECURE_DIR/encrypt-env.sh"
fi

echo ""
echo "✅ Chiffrement terminé!"
echo ""
echo "IMPORTANT:"
echo "1. Sauvegardez la clé maître: $SECURE_DIR/master.key"
echo "2. Supprimez les fichiers originaux après vérification"
echo "3. Ajoutez la clé maître aux secrets de votre système de déploiement"
echo ""
echo "Scripts disponibles:"
echo "- $SECURE_DIR/decrypt.sh <filename.json> - Déchiffrer un credential"
echo "- $SECURE_DIR/decrypt-env.sh - Déchiffrer les variables d'environnement"
echo ""
echo "Pour le déploiement, utilisez la variable d'environnement MASTER_KEY"
echo "ou montez la clé via un volume Docker secret."