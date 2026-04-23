#!/bin/bash

echo "🚀 Setting up Hermes Custom..."

# Tạo thư mục hermes
mkdir -p ~/.hermes/plugins

# Copy config
cp config/config.yaml ~/.hermes/

# Copy plugins
cp plugins/* ~/.hermes/plugins/

# Copy services
cp services/*.py ~

# Install deps
pip install redis sentence-transformers

echo "✅ Setup done!"
