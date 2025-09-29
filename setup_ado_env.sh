#!/bin/bash

# Azure DevOps Environment Variables Setup
# Run this script to set up environment variables for the Product Planner application

echo "🔧 Setting up Azure DevOps Environment Variables"
echo "================================================"

# Prompt for Azure DevOps configuration
read -p "Enter your Azure DevOps Organization: " ADO_ORG
read -p "Enter your Azure DevOps Project: " ADO_PROJECT
read -s -p "Enter your Azure DevOps Personal Access Token (PAT): " ADO_PAT
echo

# Create or update .env file
ENV_FILE="../.env"
echo "Creating/updating $ENV_FILE..."

# Remove existing Azure DevOps entries if they exist
if [ -f "$ENV_FILE" ]; then
    grep -v "AZURE_DEVOPS_" "$ENV_FILE" > "${ENV_FILE}.tmp" && mv "${ENV_FILE}.tmp" "$ENV_FILE"
fi

# Add new environment variables
cat >> "$ENV_FILE" << EOF

# Azure DevOps Configuration
AZURE_DEVOPS_ORG=$ADO_ORG
AZURE_DEVOPS_PROJECT=$ADO_PROJECT
AZURE_DEVOPS_PAT=$ADO_PAT
EOF

echo "✅ Environment variables saved to $ENV_FILE"
echo
echo "📋 To use these variables:"
echo "1. Source the .env file: source ../.env"
echo "2. Or export them manually:"
echo "   export AZURE_DEVOPS_ORG=$ADO_ORG"
echo "   export AZURE_DEVOPS_PROJECT=$ADO_PROJECT" 
echo "   export AZURE_DEVOPS_PAT=***hidden***"
echo
echo "🔐 Alternative: Add to Streamlit secrets (.streamlit/secrets.toml):"
echo "[Azure DevOps]"
echo "AZURE_DEVOPS_ORG = \"$ADO_ORG\""
echo "AZURE_DEVOPS_PROJECT = \"$ADO_PROJECT\""
echo "AZURE_DEVOPS_PAT = \"***hidden***\""
echo
echo "🚀 Restart Streamlit to load the new configuration!"
