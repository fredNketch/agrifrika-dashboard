#!/bin/bash

# Setup CloudWatch monitoring for Agrifrika Dashboard
# Usage: ./setup-cloudwatch.sh [stack-name] [region]

set -e

STACK_NAME=${1:-agrifrika-dashboard}
AWS_REGION=${2:-us-east-1}

echo "Setting up CloudWatch monitoring for ${STACK_NAME} in ${AWS_REGION}"

# Create CloudWatch dashboard
aws cloudwatch put-dashboard \
  --region "$AWS_REGION" \
  --dashboard-name "${STACK_NAME}-monitoring" \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "AWS/ECS", "CPUUtilization", "ServiceName", "'${STACK_NAME}'-backend", "ClusterName", "'${STACK_NAME}'-cluster" ],
            [ ".", "MemoryUtilization", ".", ".", ".", "." ],
            [ ".", "CPUUtilization", "ServiceName", "'${STACK_NAME}'-frontend", "ClusterName", "'${STACK_NAME}'-cluster" ],
            [ ".", "MemoryUtilization", ".", ".", ".", "." ]
          ],
          "view": "timeSeries",
          "stacked": false,
          "region": "'${AWS_REGION}'",
          "title": "ECS Service Metrics",
          "period": 300
        }
      },
      {
        "type": "metric",
        "x": 0,
        "y": 6,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", "'$(aws elbv2 describe-load-balancers --region $AWS_REGION --names ${STACK_NAME}-alb --query LoadBalancers[0].LoadBalancerArn --output text | cut -d'/' -f2-)'", { "stat": "Average" } ],
            [ ".", "RequestCount", ".", ".", { "stat": "Sum" } ],
            [ ".", "HTTPCode_Target_2XX_Count", ".", ".", { "stat": "Sum" } ],
            [ ".", "HTTPCode_Target_4XX_Count", ".", ".", { "stat": "Sum" } ],
            [ ".", "HTTPCode_Target_5XX_Count", ".", ".", { "stat": "Sum" } ]
          ],
          "view": "timeSeries",
          "stacked": false,
          "region": "'${AWS_REGION}'",
          "title": "Application Load Balancer Metrics",
          "period": 300
        }
      }
    ]
  }'

# Create CloudWatch alarms
echo "Creating CloudWatch alarms..."

# High CPU alarm for backend
aws cloudwatch put-metric-alarm \
  --region "$AWS_REGION" \
  --alarm-name "${STACK_NAME}-backend-high-cpu" \
  --alarm-description "Backend service high CPU utilization" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:${AWS_REGION}:${AWS::AccountId}:${STACK_NAME}-alerts" \
  --dimensions Name=ServiceName,Value="${STACK_NAME}-backend" Name=ClusterName,Value="${STACK_NAME}-cluster"

# High memory alarm for backend
aws cloudwatch put-metric-alarm \
  --region "$AWS_REGION" \
  --alarm-name "${STACK_NAME}-backend-high-memory" \
  --alarm-description "Backend service high memory utilization" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 85.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions "arn:aws:sns:${AWS_REGION}:${AWS::AccountId}:${STACK_NAME}-alerts" \
  --dimensions Name=ServiceName,Value="${STACK_NAME}-backend" Name=ClusterName,Value="${STACK_NAME}-cluster"

# Response time alarm
aws cloudwatch put-metric-alarm \
  --region "$AWS_REGION" \
  --alarm-name "${STACK_NAME}-high-response-time" \
  --alarm-description "High response time on load balancer" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --threshold 2.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 3 \
  --alarm-actions "arn:aws:sns:${AWS_REGION}:${AWS::AccountId}:${STACK_NAME}-alerts" \
  --dimensions Name=LoadBalancer,Value="$(aws elbv2 describe-load-balancers --region $AWS_REGION --names ${STACK_NAME}-alb --query LoadBalancers[0].LoadBalancerArn --output text | cut -d'/' -f2-)"

# 5XX errors alarm
aws cloudwatch put-metric-alarm \
  --region "$AWS_REGION" \
  --alarm-name "${STACK_NAME}-5xx-errors" \
  --alarm-description "High rate of 5XX errors" \
  --metric-name HTTPCode_Target_5XX_Count \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 10.0 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --treat-missing-data notBreaching \
  --alarm-actions "arn:aws:sns:${AWS_REGION}:${AWS::AccountId}:${STACK_NAME}-alerts" \
  --dimensions Name=LoadBalancer,Value="$(aws elbv2 describe-load-balancers --region $AWS_REGION --names ${STACK_NAME}-alb --query LoadBalancers[0].LoadBalancerArn --output text | cut -d'/' -f2-)"

echo "CloudWatch monitoring setup completed successfully"
echo "Dashboard available at: https://console.aws.amazon.com/cloudwatch/home?region=${AWS_REGION}#dashboards:name=${STACK_NAME}-monitoring"