#!/bin/bash

# Simple EC2 deployment for ultra-low cost setup
# Single t3.small instance with Docker Compose
# Estimated cost: ~$20/month total

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
KEY_PAIR_NAME=${4:-agrifrika-key}

echo -e "${BLUE}Simple EC2 Deployment - Ultra Low Cost${NC}"
echo -e "Cost estimate: ~$20/month for single t3.small instance"

# Function to create key pair if it doesn't exist
create_key_pair() {
    echo -e "${BLUE}Checking SSH key pair...${NC}"

    if ! aws ec2 describe-key-pairs --region "$AWS_REGION" --key-names "$KEY_PAIR_NAME" &>/dev/null; then
        echo -e "${YELLOW}Creating new key pair: $KEY_PAIR_NAME${NC}"
        aws ec2 create-key-pair \
            --region "$AWS_REGION" \
            --key-name "$KEY_PAIR_NAME" \
            --query 'KeyMaterial' \
            --output text > "${KEY_PAIR_NAME}.pem"
        chmod 400 "${KEY_PAIR_NAME}.pem"
        echo -e "${GREEN}Key pair created: ${KEY_PAIR_NAME}.pem${NC}"
    else
        echo -e "${GREEN}Key pair already exists: $KEY_PAIR_NAME${NC}"
    fi
}

# Function to create simple security group
create_security_group() {
    echo -e "${BLUE}Creating security group...${NC}"

    # Get default VPC
    VPC_ID=$(aws ec2 describe-vpcs \
        --region "$AWS_REGION" \
        --filters "Name=isDefault,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text)

    # Create security group
    SG_ID=$(aws ec2 create-security-group \
        --region "$AWS_REGION" \
        --group-name "agrifrika-simple-sg" \
        --description "Simple security group for Agrifrika" \
        --vpc-id "$VPC_ID" \
        --query 'GroupId' \
        --output text 2>/dev/null || \
    aws ec2 describe-security-groups \
        --region "$AWS_REGION" \
        --group-names "agrifrika-simple-sg" \
        --query 'SecurityGroups[0].GroupId' \
        --output text)

    # Add rules
    aws ec2 authorize-security-group-ingress \
        --region "$AWS_REGION" \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 2>/dev/null || true

    aws ec2 authorize-security-group-ingress \
        --region "$AWS_REGION" \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 80 \
        --cidr 0.0.0.0/0 2>/dev/null || true

    aws ec2 authorize-security-group-ingress \
        --region "$AWS_REGION" \
        --group-id "$SG_ID" \
        --protocol tcp \
        --port 443 \
        --cidr 0.0.0.0/0 2>/dev/null || true

    echo -e "${GREEN}Security group ready: $SG_ID${NC}"
    echo "$SG_ID"
}

# Function to launch EC2 instance
launch_instance() {
    local sg_id=$1

    echo -e "${BLUE}Launching t3.small instance...${NC}"

    # Create user data script
    cat > /tmp/user-data.sh << 'EOF'
#!/bin/bash
yum update -y
yum install -y docker git

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker
systemctl start docker
systemctl enable docker
usermod -a -G docker ec2-user

# Clone and setup application
cd /home/ec2-user
git clone https://github.com/your-repo/agrifrika-dashboard.git
cd agrifrika-dashboard

# Setup application (will be completed by SSH)
chown -R ec2-user:ec2-user /home/ec2-user/agrifrika-dashboard
EOF

    # Launch instance
    INSTANCE_ID=$(aws ec2 run-instances \
        --region "$AWS_REGION" \
        --image-id ami-0c02fb55956c7d316 \
        --instance-type t3.small \
        --key-name "$KEY_PAIR_NAME" \
        --security-group-ids "$sg_id" \
        --user-data file:///tmp/user-data.sh \
        --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=agrifrika-simple},{Key=Environment,Value=$ENVIRONMENT},{Key=CostOptimized,Value=true}]" \
        --query 'Instances[0].InstanceId' \
        --output text)

    echo -e "${GREEN}Instance launched: $INSTANCE_ID${NC}"

    # Wait for instance to be running
    echo -e "${YELLOW}Waiting for instance to be ready...${NC}"
    aws ec2 wait instance-running --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"

    # Get public IP
    PUBLIC_IP=$(aws ec2 describe-instances \
        --region "$AWS_REGION" \
        --instance-ids "$INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)

    echo -e "${GREEN}Instance ready: $PUBLIC_IP${NC}"
    echo "$INSTANCE_ID:$PUBLIC_IP"
}

# Function to setup application on instance
setup_application() {
    local instance_info=$1
    local instance_id=$(echo "$instance_info" | cut -d: -f1)
    local public_ip=$(echo "$instance_info" | cut -d: -f2)

    echo -e "${BLUE}Setting up application on instance...${NC}"

    # Wait a bit more for SSH to be ready
    sleep 60

    # Create setup script
    cat > /tmp/setup-app.sh << 'EOF'
#!/bin/bash
cd /home/ec2-user/agrifrika-dashboard

# Copy configuration template
cp config/.env.template config/.env.prod

# Update for single instance deployment
sed -i 's/DEBUG=true/DEBUG=false/' config/.env.prod
sed -i 's/ENV=development/ENV=production/' config/.env.prod

# Setup SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout nginx/ssl/key.pem \
    -out nginx/ssl/cert.pem \
    -subj "/CN=localhost"

# Deploy with Docker Compose
docker-compose -f docker-compose.prod.yml up -d

echo "Application deployed successfully!"
echo "Access at: http://$(curl -s http://checkip.amazonaws.com/)"
EOF

    # Copy and execute setup script
    scp -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no /tmp/setup-app.sh ec2-user@"$public_ip":/tmp/
    ssh -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no ec2-user@"$public_ip" "chmod +x /tmp/setup-app.sh && /tmp/setup-app.sh"

    echo -e "${GREEN}Application setup completed${NC}"
}

# Function to show connection info
show_connection_info() {
    local instance_info=$1
    local public_ip=$(echo "$instance_info" | cut -d: -f2)

    echo -e "\n${GREEN}Deployment completed!${NC}"
    echo -e "${BLUE}Connection Information:${NC}"
    echo -e "Application URL: https://$public_ip"
    echo -e "Health Check: https://$public_ip/health"
    echo -e "SSH Access: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@$public_ip"

    echo -e "\n${YELLOW}Cost Optimization Notes:${NC}"
    echo -e "- Single t3.small instance: ~$15/month"
    echo -e "- No ALB cost (direct access)"
    echo -e "- Minimal AWS services usage"
    echo -e "- Total estimated: $20-25/month"

    echo -e "\n${BLUE}Management Commands:${NC}"
    echo -e "Stop instance (save costs): aws ec2 stop-instances --instance-ids $(echo "$instance_info" | cut -d: -f1)"
    echo -e "Start instance: aws ec2 start-instances --instance-ids $(echo "$instance_info" | cut -d: -f1)"
    echo -e "Application logs: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@$public_ip 'docker-compose -f agrifrika-dashboard/docker-compose.prod.yml logs'"
}

# Function to create scheduled start/stop
setup_scheduled_scaling() {
    local instance_id=$1

    echo -e "${BLUE}Setting up scheduled start/stop...${NC}"

    # Create Lambda function for instance management
    cat > /tmp/instance-scheduler.py << 'EOF'
import boto3
import json

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    action = event.get('action', 'stop')
    instance_id = event.get('instance_id')

    if action == 'stop':
        ec2.stop_instances(InstanceIds=[instance_id])
    elif action == 'start':
        ec2.start_instances(InstanceIds=[instance_id])

    return {'statusCode': 200, 'body': f'Instance {instance_id} {action} initiated'}
EOF

    # Note: Full Lambda setup would require additional IAM roles and EventBridge rules
    echo -e "${YELLOW}Manual scheduling recommended for simplicity:${NC}"
    echo -e "- Stop: aws ec2 stop-instances --instance-ids $instance_id"
    echo -e "- Start: aws ec2 start-instances --instance-ids $instance_id"
}

# Main function
main() {
    create_key_pair
    SG_ID=$(create_security_group)
    INSTANCE_INFO=$(launch_instance "$SG_ID")
    setup_application "$INSTANCE_INFO"
    show_connection_info "$INSTANCE_INFO"

    # Optional: setup scheduled scaling
    INSTANCE_ID=$(echo "$INSTANCE_INFO" | cut -d: -f1)
    setup_scheduled_scaling "$INSTANCE_ID"
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up simple EC2 deployment...${NC}"

    # Find and terminate instance
    INSTANCE_ID=$(aws ec2 describe-instances \
        --region "$AWS_REGION" \
        --filters "Name=tag:Name,Values=agrifrika-simple" "Name=instance-state-name,Values=running,stopped" \
        --query 'Reservations[0].Instances[0].InstanceId' \
        --output text)

    if [ "$INSTANCE_ID" != "None" ] && [ -n "$INSTANCE_ID" ]; then
        aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
        echo -e "${GREEN}Instance $INSTANCE_ID terminated${NC}"
    fi

    # Delete security group
    aws ec2 delete-security-group \
        --region "$AWS_REGION" \
        --group-name "agrifrika-simple-sg" 2>/dev/null || true

    echo -e "${GREEN}Cleanup completed${NC}"
}

# Handle arguments
case "${1}" in
    "cleanup"|"destroy")
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment] [region] [domain] [key-pair-name]"
        echo "       $0 cleanup"
        echo ""
        echo "Simple single-instance deployment for ultra-low cost"
        echo "Estimated cost: ~$20/month"
        ;;
    *)
        main
        ;;
esac