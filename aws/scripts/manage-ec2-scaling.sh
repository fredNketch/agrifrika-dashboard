#!/bin/bash

# EC2 Auto Scaling management script for Agrifrika Dashboard
# Usage: ./manage-ec2-scaling.sh [action] [environment] [region]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ACTION=${1:-status}
ENVIRONMENT=${2:-production}
AWS_REGION=${3:-us-east-1}
STACK_NAME="agrifrika-${ENVIRONMENT}"
ASG_NAME="${STACK_NAME}-asg"

echo -e "${BLUE}EC2 Auto Scaling Management - ${STACK_NAME}${NC}"

# Function to show current status
show_status() {
    echo -e "${BLUE}Current Auto Scaling Group Status:${NC}"

    aws autoscaling describe-auto-scaling-groups \
        --region "$AWS_REGION" \
        --auto-scaling-group-names "$ASG_NAME" \
        --query 'AutoScalingGroups[0].[AutoScalingGroupName,MinSize,MaxSize,DesiredCapacity,Instances[].InstanceId]' \
        --output table

    echo -e "\n${BLUE}ECS Container Instances:${NC}"
    aws ecs list-container-instances \
        --region "$AWS_REGION" \
        --cluster "${STACK_NAME}-cluster" \
        --query 'containerInstanceArns' \
        --output table

    echo -e "\n${BLUE}EC2 Instances Status:${NC}"
    aws ec2 describe-instances \
        --region "$AWS_REGION" \
        --filters "Name=tag:aws:autoscaling:groupName,Values=${ASG_NAME}" \
        --query 'Reservations[*].Instances[*].[InstanceId,InstanceType,State.Name,PublicIpAddress,PrivateIpAddress]' \
        --output table

    echo -e "\n${BLUE}ECS Services:${NC}"
    aws ecs describe-services \
        --region "$AWS_REGION" \
        --cluster "${STACK_NAME}-cluster" \
        --services "${STACK_NAME}-backend" "${STACK_NAME}-frontend" \
        --query 'services[*].[serviceName,status,runningCount,desiredCount,pendingCount]' \
        --output table
}

# Function to scale out
scale_out() {
    local desired_capacity=${2:-3}
    echo -e "${YELLOW}Scaling out to ${desired_capacity} instances...${NC}"

    aws autoscaling set-desired-capacity \
        --region "$AWS_REGION" \
        --auto-scaling-group-name "$ASG_NAME" \
        --desired-capacity "$desired_capacity"

    echo -e "${GREEN}Scaling command sent. Waiting for instances...${NC}"

    # Wait for instances to be ready
    sleep 30
    show_status
}

# Function to scale in
scale_in() {
    local desired_capacity=${2:-1}
    echo -e "${YELLOW}Scaling in to ${desired_capacity} instances...${NC}"

    aws autoscaling set-desired-capacity \
        --region "$AWS_REGION" \
        --auto-scaling-group-name "$ASG_NAME" \
        --desired-capacity "$desired_capacity"

    echo -e "${GREEN}Scaling command sent. Terminating excess instances...${NC}"

    # Wait for scaling to complete
    sleep 30
    show_status
}

# Function to enable/disable auto scaling
toggle_auto_scaling() {
    local enable=${2:-true}

    if [ "$enable" = "true" ]; then
        echo -e "${BLUE}Enabling auto scaling policies...${NC}"

        # Enable scaling policies
        aws autoscaling put-scaling-policy \
            --region "$AWS_REGION" \
            --auto-scaling-group-name "$ASG_NAME" \
            --policy-name "${ASG_NAME}-scale-out" \
            --policy-type "TargetTrackingScaling" \
            --target-tracking-configuration '{
                "PredefinedMetricSpecification": {
                    "PredefinedMetricType": "ASGAverageCPUUtilization"
                },
                "TargetValue": 70.0,
                "ScaleOutCooldown": 300,
                "ScaleInCooldown": 300
            }'

        echo -e "${GREEN}Auto scaling enabled (target: 70% CPU)${NC}"
    else
        echo -e "${YELLOW}Disabling auto scaling policies...${NC}"

        # List and delete scaling policies
        POLICIES=$(aws autoscaling describe-policies \
            --region "$AWS_REGION" \
            --auto-scaling-group-name "$ASG_NAME" \
            --query 'ScalingPolicies[*].PolicyName' \
            --output text)

        for policy in $POLICIES; do
            aws autoscaling delete-policy \
                --region "$AWS_REGION" \
                --auto-scaling-group-name "$ASG_NAME" \
                --policy-name "$policy"
        done

        echo -e "${GREEN}Auto scaling disabled${NC}"
    fi
}

# Function to update launch template
update_launch_template() {
    local instance_type=${2:-t3.medium}
    echo -e "${BLUE}Updating launch template with instance type: ${instance_type}${NC}"

    LAUNCH_TEMPLATE_ID=$(aws cloudformation describe-stacks \
        --region "$AWS_REGION" \
        --stack-name "${STACK_NAME}-infrastructure" \
        --query "Stacks[0].Resources[?LogicalResourceId=='ECSLaunchTemplate'].PhysicalResourceId" \
        --output text)

    aws ec2 create-launch-template-version \
        --region "$AWS_REGION" \
        --launch-template-id "$LAUNCH_TEMPLATE_ID" \
        --source-version '$Latest' \
        --launch-template-data "{\"InstanceType\":\"${instance_type}\"}"

    # Update ASG to use new version
    aws autoscaling update-auto-scaling-group \
        --region "$AWS_REGION" \
        --auto-scaling-group-name "$ASG_NAME" \
        --launch-template "LaunchTemplateId=${LAUNCH_TEMPLATE_ID},Version=\$Latest"

    echo -e "${GREEN}Launch template updated. New instances will use ${instance_type}${NC}"
}

# Function to drain and replace instances
refresh_instances() {
    echo -e "${BLUE}Starting instance refresh...${NC}"

    aws autoscaling start-instance-refresh \
        --region "$AWS_REGION" \
        --auto-scaling-group-name "$ASG_NAME" \
        --preferences '{
            "InstanceWarmup": 300,
            "MinHealthyPercentage": 50
        }'

    echo -e "${GREEN}Instance refresh started. Monitor progress with:${NC}"
    echo -e "aws autoscaling describe-instance-refreshes --region $AWS_REGION --auto-scaling-group-name $ASG_NAME"
}

# Function to show help
show_help() {
    cat << EOF
EC2 Auto Scaling Management pour Agrifrika Dashboard

Usage: $0 [action] [environment] [region]

Actions:
  status              Afficher le statut actuel (default)
  scale-out [count]   Augmenter le nombre d'instances (default: 3)
  scale-in [count]    Diminuer le nombre d'instances (default: 1)
  auto-enable         Activer l'auto-scaling automatique
  auto-disable        Désactiver l'auto-scaling automatique
  update-type [type]  Changer le type d'instance (default: t3.medium)
  refresh             Remplacer toutes les instances avec la nouvelle config
  help                Afficher cette aide

Exemples:
  $0 status production us-east-1
  $0 scale-out 4 production us-east-1
  $0 scale-in 1 production us-east-1
  $0 update-type t3.large production us-east-1
  $0 refresh production us-east-1

Types d'instances recommandés pour votre usage (< 5 utilisateurs/jour):
  - t3.small  (2 vCPU, 2 GB)  - Recommandé pour votre cas
  - t3.medium (2 vCPU, 4 GB)  - Si croissance prévue
  - t3.large  (2 vCPU, 8 GB)  - Pour usage intensif
  - t3.nano   (2 vCPU, 0.5 GB) - Développement uniquement
EOF
}

# Main function
main() {
    case "$ACTION" in
        "status"|"")
            show_status
            ;;
        "scale-out")
            scale_out "$ACTION" "${4:-3}"
            ;;
        "scale-in")
            scale_in "$ACTION" "${4:-1}"
            ;;
        "auto-enable")
            toggle_auto_scaling "$ACTION" "true"
            ;;
        "auto-disable")
            toggle_auto_scaling "$ACTION" "false"
            ;;
        "update-type")
            update_launch_template "$ACTION" "${4:-t3.medium}"
            ;;
        "refresh")
            refresh_instances
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            echo -e "${RED}Action non reconnue: $ACTION${NC}"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main