#!/bin/bash

# AWS ECS entrypoint script for Agrifrika Dashboard
# Replaces docker-entrypoint.sh for AWS deployment

set -e

echo "Agrifrika Dashboard - AWS ECS Initialization..."

# Install AWS CLI if not present
if ! command -v aws &> /dev/null; then
    echo "Installing AWS CLI..."
    pip install awscli
fi

# Function to get secret from AWS Secrets Manager
get_secret() {
    local secret_name=$1
    local key=$2

    if [ -n "$secret_name" ]; then
        echo "Retrieving secret: $secret_name"
        aws secretsmanager get-secret-value \
            --region "${AWS_DEFAULT_REGION:-us-east-1}" \
            --secret-id "$secret_name" \
            --query SecretString \
            --output text | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(data.get('$key', ''))
"
    fi
}

# Function to create credentials file from secrets
create_credentials_file() {
    local secret_content=$1
    local output_file=$2

    if [ -n "$secret_content" ] && [ "$secret_content" != "null" ] && [ "$secret_content" != "" ]; then
        echo "Creating credentials file: $output_file"
        mkdir -p "$(dirname $output_file)"
        echo "$secret_content" > "$output_file"
        chmod 600 "$output_file"
        echo "Credentials file created: $output_file"
    else
        echo "Warning: No credentials found for $output_file"
    fi
}

# Get secrets from AWS Secrets Manager
if [ -n "$AWS_SECRET_NAME" ]; then
    echo "Retrieving application secrets from AWS Secrets Manager..."

    # Google Sheets credentials
    GOOGLE_SHEETS_CREDS=$(get_secret "$AWS_SECRET_NAME" "GOOGLE_SHEETS_CREDENTIALS")
    create_credentials_file "$GOOGLE_SHEETS_CREDS" "/app/config/credentials/google-sheets-new-credentials.json"

    # Google Analytics credentials
    GOOGLE_ANALYTICS_CREDS=$(get_secret "$AWS_SECRET_NAME" "GOOGLE_ANALYTICS_CREDENTIALS")
    create_credentials_file "$GOOGLE_ANALYTICS_CREDS" "/app/config/credentials/google-analytics-credentials.json"

    # Set environment variables from secrets
    export BASECAMP_TOKEN=$(get_secret "$AWS_SECRET_NAME" "BASECAMP_TOKEN")
    export BASECAMP_ACCOUNT_ID=$(get_secret "$AWS_SECRET_NAME" "BASECAMP_ACCOUNT_ID")
    export BASECAMP_PROJECT_ID=$(get_secret "$AWS_SECRET_NAME" "BASECAMP_PROJECT_ID")
    export FACEBOOK_ACCESS_TOKEN=$(get_secret "$AWS_SECRET_NAME" "FACEBOOK_ACCESS_TOKEN")
    export FACEBOOK_PAGE_ID=$(get_secret "$AWS_SECRET_NAME" "FACEBOOK_PAGE_ID")
    export SECRET_KEY=$(get_secret "$AWS_SECRET_NAME" "SECRET_KEY")

    echo "Application secrets loaded from AWS Secrets Manager"
else
    echo "Warning: AWS_SECRET_NAME not provided. Using local credentials if available."
fi

# Set up CloudWatch logging if AWS_REGION is available
if [ -n "$AWS_DEFAULT_REGION" ]; then
    export LOG_DRIVER="awslogs"
    export LOG_GROUP="/ecs/${ECS_CLUSTER_NAME:-agrifrika}/backend"
    echo "CloudWatch logging configured for region: $AWS_DEFAULT_REGION"
fi

# Create necessary directories
mkdir -p /app/logs /app/data

# Set proper permissions
chmod 755 /app/logs /app/data

echo "AWS ECS initialization completed. Starting application..."

# Execute the main command
exec "$@"