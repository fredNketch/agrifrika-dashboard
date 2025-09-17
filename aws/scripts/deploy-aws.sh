#!/bin/bash

# Agrifrika Dashboard - AWS Deployment Script
# Usage: ./deploy-aws.sh [environment] [region] [domain]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Parameters
ENVIRONMENT=${1:-production}
AWS_REGION=${2:-us-east-1}
DOMAIN_NAME=${3:-""}
STACK_NAME="agrifrika-${ENVIRONMENT}"

echo -e "${BLUE}AWS EC2 Deployment - Agrifrika Dashboard${NC}"
echo -e "Environment: ${ENVIRONMENT}"
echo -e "Region: ${AWS_REGION}"
echo -e "Stack: ${STACK_NAME}"
echo -e "Compute: ECS on EC2 (Auto Scaling)"
if [ -n "$DOMAIN_NAME" ]; then
    echo -e "Domain: ${DOMAIN_NAME}"
fi

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"

    if ! command -v aws &> /dev/null; then
        echo -e "${RED}AWS CLI not found. Please install it first.${NC}"
        exit 1
    fi

    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker not found. Please install it first.${NC}"
        exit 1
    fi

    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        echo -e "${RED}AWS credentials not configured. Run 'aws configure' first.${NC}"
        exit 1
    fi

    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Create ECR repositories
create_ecr_repositories() {
    echo -e "${BLUE}Creating ECR repositories...${NC}"

    # Backend repository
    aws ecr describe-repositories --region "$AWS_REGION" --repository-names "${STACK_NAME}-backend" &> /dev/null || \
    aws ecr create-repository \
        --region "$AWS_REGION" \
        --repository-name "${STACK_NAME}-backend" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

    # Frontend repository
    aws ecr describe-repositories --region "$AWS_REGION" --repository-names "${STACK_NAME}-frontend" &> /dev/null || \
    aws ecr create-repository \
        --region "$AWS_REGION" \
        --repository-name "${STACK_NAME}-frontend" \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256

    echo -e "${GREEN}ECR repositories created${NC}"
}

# Build and push Docker images
build_and_push_images() {
    echo -e "${BLUE}Building and pushing Docker images...${NC}"

    # Get ECR login token
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Build and push backend
    echo -e "${YELLOW}Building backend image...${NC}"
    docker build -t "${STACK_NAME}-backend" ./backend/
    docker tag "${STACK_NAME}-backend:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${STACK_NAME}-backend:latest"
    docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${STACK_NAME}-backend:latest"

    # Build and push frontend
    echo -e "${YELLOW}Building frontend image...${NC}"
    docker build -t "${STACK_NAME}-frontend" ./frontend/
    docker tag "${STACK_NAME}-frontend:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${STACK_NAME}-frontend:latest"
    docker push "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${STACK_NAME}-frontend:latest"

    echo -e "${GREEN}Images built and pushed to ECR${NC}"
}

# Deploy infrastructure
deploy_infrastructure() {
    echo -e "${BLUE}Deploying infrastructure stack...${NC}"

    local params=""
    if [ -n "$DOMAIN_NAME" ]; then
        params="ParameterKey=DomainName,ParameterValue=${DOMAIN_NAME}"
    fi

    aws cloudformation deploy \
        --region "$AWS_REGION" \
        --template-file aws/cloudformation/infrastructure.yml \
        --stack-name "${STACK_NAME}-infrastructure" \
        --parameter-overrides Environment="$ENVIRONMENT" $params \
        --capabilities CAPABILITY_IAM \
        --tags Environment="$ENVIRONMENT" Application=agrifrika-dashboard

    echo -e "${GREEN}Infrastructure deployed${NC}"
}

# Deploy services
deploy_services() {
    echo -e "${BLUE}Deploying ECS services...${NC}"

    aws cloudformation deploy \
        --region "$AWS_REGION" \
        --template-file aws/cloudformation/services.yml \
        --stack-name "${STACK_NAME}-services" \
        --parameter-overrides \
            StackName="${STACK_NAME}-infrastructure" \
            Environment="$ENVIRONMENT" \
            ECRRepositoryURI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com" \
        --capabilities CAPABILITY_IAM \
        --tags Environment="$ENVIRONMENT" Application=agrifrika-dashboard

    echo -e "${GREEN}Services deployed${NC}"
}

# Setup secrets
setup_secrets() {
    echo -e "${BLUE}Setting up application secrets...${NC}"

    # Get the secrets ARN
    SECRET_ARN=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='ApplicationSecrets'].OutputValue" \
        --output text)

    echo -e "${YELLOW}Please update secrets in AWS Secrets Manager:${NC}"
    echo -e "Secret ARN: ${SECRET_ARN}"
    echo -e "Console URL: https://console.aws.amazon.com/secretsmanager/home?region=${AWS_REGION}#!/secret?name=${SECRET_ARN}"

    echo -e "${YELLOW}Required secrets:${NC}"
    echo -e "- GOOGLE_SHEETS_CREDENTIALS (JSON content)"
    echo -e "- GOOGLE_ANALYTICS_CREDENTIALS (JSON content)"
    echo -e "- BASECAMP_TOKEN"
    echo -e "- BASECAMP_ACCOUNT_ID"
    echo -e "- BASECAMP_PROJECT_ID"
    echo -e "- FACEBOOK_ACCESS_TOKEN"
    echo -e "- FACEBOOK_PAGE_ID"
    echo -e "- SECRET_KEY (auto-generated)"
}

# Wait for services to be stable
wait_for_services() {
    echo -e "${BLUE}Waiting for services to be stable...${NC}"

    aws ecs wait services-stable \
        --region "$AWS_REGION" \
        --cluster "${STACK_NAME}-cluster" \
        --services "${STACK_NAME}-backend" "${STACK_NAME}-frontend"

    echo -e "${GREEN}Services are stable${NC}"
}

# Show deployment summary
show_summary() {
    echo -e "\n${GREEN}Deployment completed successfully!${NC}"

    # Get ALB DNS
    ALB_DNS=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" \
        --output text)

    echo -e "${BLUE}Deployment Summary:${NC}"
    echo -e "Environment: ${ENVIRONMENT}"
    echo -e "Region: ${AWS_REGION}"
    echo -e "Load Balancer: ${ALB_DNS}"
    echo -e "Application URL: https://${ALB_DNS}"
    echo -e "Health Check: https://${ALB_DNS}/health"

    if [ -n "$DOMAIN_NAME" ]; then
        echo -e "Custom Domain: https://${DOMAIN_NAME}"
    fi

    echo -e "\n${YELLOW}Next Steps:${NC}"
    if [ -n "$DOMAIN_NAME" ]; then
        echo -e "1. Update DNS records to point ${DOMAIN_NAME} to ${ALB_DNS}"
        echo -e "2. Wait for certificate validation (can take up to 30 minutes)"
    echo -e "3. EC2 instances will auto-register to ECS cluster"
    fi
    echo -e "4. Update application secrets in AWS Secrets Manager"
    echo -e "5. Monitor EC2 instances: aws ec2 describe-instances --filters Name=tag:aws:autoscaling:groupName,Values=${STACK_NAME}-asg"
    echo -e "6. Monitor services: aws ecs describe-services --cluster ${STACK_NAME}-cluster --services ${STACK_NAME}-backend ${STACK_NAME}-frontend"

    echo -e "\n${BLUE}Useful Commands:${NC}"
    echo -e "Update service: aws ecs update-service --cluster ${STACK_NAME}-cluster --service ${STACK_NAME}-backend --force-new-deployment"
    echo -e "View logs: aws logs tail /ecs/${STACK_NAME}/backend --follow"
    echo -e "EC2 instances: aws ec2 describe-instances --filters Name=tag:aws:autoscaling:groupName,Values=${STACK_NAME}-asg"
    echo -e "Scale instances: aws autoscaling set-desired-capacity --auto-scaling-group-name ${STACK_NAME}-asg --desired-capacity 3"
    echo -e "CloudWatch Dashboard: https://console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:name=${STACK_NAME}-monitoring"
}

# Main deployment function
main() {
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    export AWS_ACCOUNT_ID

    check_prerequisites
    create_ecr_repositories
    build_and_push_images
    deploy_infrastructure
    deploy_services
    setup_secrets

    # Setup CloudWatch monitoring
    if [ -f "aws/scripts/setup-cloudwatch.sh" ]; then
        ./aws/scripts/setup-cloudwatch.sh "$STACK_NAME" "$AWS_REGION"
    fi

    wait_for_services
    show_summary
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up AWS resources...${NC}"

    # Delete services stack
    aws cloudformation delete-stack \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-services"

    aws cloudformation wait stack-delete-complete \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-services"

    # Delete infrastructure stack
    aws cloudformation delete-stack \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure"

    aws cloudformation wait stack-delete-complete \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure"

    echo -e "${GREEN}Cleanup completed${NC}"
}

# Handle command line arguments
case "${1}" in
    "cleanup"|"destroy")
        ENVIRONMENT=${2:-production}
        AWS_REGION=${3:-us-east-1}
        STACK_NAME="agrifrika-${ENVIRONMENT}"
        cleanup
        ;;
    "help"|"-h"|"--help")
        echo "Usage: $0 [environment] [region] [domain]"
        echo "       $0 cleanup [environment] [region]"
        echo ""
        echo "Examples:"
        echo "  $0 production us-east-1 agrifrika.com"
        echo "  $0 staging us-west-2"
        echo "  $0 cleanup production us-east-1"
        ;;
    *)
        main
        ;;
esac