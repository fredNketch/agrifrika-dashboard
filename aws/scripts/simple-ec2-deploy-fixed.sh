#!/bin/bash

set -e

RED=''
GREEN=''
YELLOW=''
BLUE=''
NC=''

ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
KEY_PAIR_NAME=${4:-agrifrika-key}

echo -e "${BLUE}Simple EC2 Deployment - Ultra Low Cost${NC}"

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

# Function to create security group
create_security_group() {
    echo -e "${BLUE}Creating security group...${NC}"
    VPC_ID=$(aws ec2 describe-vpcs \
        --region "$AWS_REGION" \
        --filters "Name=isDefault,Values=true" \
        --query 'Vpcs[0].VpcId' \
        --output text)

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
    echo -e "${BLUE}Launching t3.micro instance...${NC}"

    INSTANCE_ID=$(aws ec2 run-instances \
        --region "$AWS_REGION" \
        --image-id ami-0c02fb55956c7d316 \
        --instance-type t3.micro \
        --key-name "$KEY_PAIR_NAME" \
        --security-group-ids "$sg_id" \
        --query 'Instances[0].InstanceId' \
        --output text)

    echo -e "${GREEN}Instance launched: $INSTANCE_ID${NC}"

    if [ -z "$INSTANCE_ID" ] || [ "$INSTANCE_ID" = "None" ]; then
        echo -e "${RED}Error: Failed to launch instance${NC}"
        return 1
    fi

    aws ec2 create-tags \
        --region "$AWS_REGION" \
        --resources "$INSTANCE_ID" \
        --tags "Key=Name,Value=agrifrika-simple" || true

    echo -e "${YELLOW}Waiting for instance to be ready...${NC}"
    aws ec2 wait instance-running --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"

    PUBLIC_IP=$(aws ec2 describe-instances \
        --region "$AWS_REGION" \
        --instance-ids "$INSTANCE_ID" \
        --query 'Reservations[0].Instances[0].PublicIpAddress' \
        --output text)

    if [ -z "$PUBLIC_IP" ] || [ "$PUBLIC_IP" = "None" ]; then
        echo -e "${RED}Error: No public IP assigned to instance${NC}"
        return 1
    fi

    echo -e "${GREEN}Instance ready: $PUBLIC_IP${NC}"
    echo "$INSTANCE_ID:$PUBLIC_IP"
}

# Function to setup application
setup_application() {
    local instance_info=$1
    local public_ip=$(echo "$instance_info" | cut -d: -f2)

    echo -e "${BLUE}Setting up application on instance...${NC}"
    sleep 60

    SETUP_SCRIPT="./setup-temp-$$.sh"
    trap "rm -f '$SETUP_SCRIPT'" EXIT

    cat > "$SETUP_SCRIPT" << 'EOF'
#!/bin/bash
sudo yum update -y
sudo yum install -y docker git

sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

cd /home/ec2-user
git clone https://github.com/fredNketch/agrifrika-dashboard.git
cd agrifrika-dashboard

sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

sudo chown -R ec2-user:ec2-user /home/ec2-user/agrifrika-dashboard

echo "Application setup completed!"
EOF

    scp -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet "$SETUP_SCRIPT" ec2-user@"$public_ip":/tmp/setup-app.sh
    ssh -i "${KEY_PAIR_NAME}.pem" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=quiet ec2-user@"$public_ip" "chmod +x /tmp/setup-app.sh && /tmp/setup-app.sh"

    echo -e "${GREEN}Application setup completed${NC}"
}

# Function to show connection info
show_connection_info() {
    local instance_info=$1
    local public_ip=$(echo "$instance_info" | cut -d: -f2)

    echo -e "\n${GREEN}Deployment completed!${NC}"
    echo -e "${BLUE}Connection Information:${NC}"
    echo -e "Application URL: http://$public_ip"
    echo -e "SSH Access: ssh -i ${KEY_PAIR_NAME}.pem ec2-user@$public_ip"
}

# Main function
main() {
    create_key_pair
    SG_ID=$(create_security_group)
    INSTANCE_INFO=$(launch_instance "$SG_ID")
    setup_application "$INSTANCE_INFO"
    show_connection_info "$INSTANCE_INFO"
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up simple EC2 deployment...${NC}"
    INSTANCE_ID=$(aws ec2 describe-instances \
        --region "$AWS_REGION" \
        --filters "Name=tag:Name,Values=agrifrika-simple" "Name=instance-state-name,Values=running,stopped" \
        --query 'Reservations[0].Instances[0].InstanceId' \
        --output text)

    if [ "$INSTANCE_ID" != "None" ] && [ -n "$INSTANCE_ID" ]; then
        aws ec2 terminate-instances --region "$AWS_REGION" --instance-ids "$INSTANCE_ID"
        echo -e "${GREEN}Instance $INSTANCE_ID terminated${NC}"
    fi

    aws ec2 delete-security-group \
        --region "$AWS_REGION" \
        --group-name "agrifrika-simple-sg" 2>/dev/null || true

    echo -e "${GREEN}Cleanup completed${NC}"
}

case "${1}" in
    "cleanup"|"destroy")
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment] [region] [domain] [key-pair-name]"
        echo "       $0 cleanup"
        ;;
    *)
        main
        ;;
esac