#!/bin/bash
# Script to securely update OpenAI API key on the instance

echo "This script will update the OpenAI API key on the deployment instance."
echo ""
read -sp "Enter your OpenAI API key: " API_KEY
echo ""

if [ -z "$API_KEY" ]; then
    echo "Error: API key cannot be empty"
    exit 1
fi

# Read current .env file
COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && cat .env\"]" \
  --query 'Command.CommandId' \
  --output text)

sleep 3
CURRENT_ENV=$(aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'StandardOutputContent' \
  --output text)

# Replace the OPENAI_API_KEY line
UPDATED_ENV=$(echo "$CURRENT_ENV" | sed "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=$API_KEY|")

# Base64 encode and send back
ENV_B64=$(echo "$UPDATED_ENV" | base64)

COMMAND_ID=$(aws ssm send-command \
  --instance-ids i-05f785a26aaaf9f30 \
  --document-name "AWS-RunShellScript" \
  --parameters "commands=[\"cd /opt/hibid-email-mvp && echo '$ENV_B64' | base64 -d > .env && chmod 600 .env && echo 'API key updated successfully'\"]" \
  --query 'Command.CommandId' \
  --output text)

echo "Updating API key on instance..."
sleep 5

STATUS=$(aws ssm get-command-invocation \
  --command-id $COMMAND_ID \
  --instance-id i-05f785a26aaaf9f30 \
  --query 'Status' \
  --output text)

if [ "$STATUS" = "Success" ]; then
    echo "✅ API key updated successfully!"
    echo "Restarting backend container to apply changes..."
    
    # Restart backend container
    COMMAND_ID=$(aws ssm send-command \
      --instance-ids i-05f785a26aaaf9f30 \
      --document-name "AWS-RunShellScript" \
      --parameters 'commands=["cd /opt/hibid-email-mvp && docker-compose -f docker-compose.prod.yml restart backend"]' \
      --query 'Command.CommandId' \
      --output text)
    
    sleep 10
    RESTART_STATUS=$(aws ssm get-command-invocation \
      --command-id $COMMAND_ID \
      --instance-id i-05f785a26aaaf9f30 \
      --query 'Status' \
      --output text)
    
    if [ "$RESTART_STATUS" = "Success" ]; then
        echo "✅ Backend container restarted successfully!"
        echo ""
        echo "The API key is now active. You can test the AI features."
    else
        echo "⚠️  API key updated but restart failed. You may need to restart manually."
    fi
else
    echo "❌ Failed to update API key. Status: $STATUS"
    exit 1
fi
