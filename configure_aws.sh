#!/bin/bash

echo "=================================================="
echo "          AWS Credentials Configurator            "
echo "=================================================="
read -p "Enter AWS Access Key ID: " aws_access_key
read -sp "Enter AWS Secret Access Key: " aws_secret_key
echo ""
read -p "Enter AWS Region [us-east-1]: " aws_region
aws_region=${aws_region:-us-east-1}

# Create ~/.aws directory if it doesn't exist
mkdir -p ~/.aws

# Write credentials file
cat <<EOF > ~/.aws/credentials
[default]
aws_access_key_id = $aws_access_key
aws_secret_access_key = $aws_secret_key
EOF

# Write config file
cat <<EOF > ~/.aws/config
[default]
region = $aws_region
output = json
EOF

echo "=================================================="
echo "✔ AWS Credentials configured successfully at ~/.aws/config and ~/.aws/credentials"
echo "=================================================="
