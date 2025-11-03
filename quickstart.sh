#!/bin/bash
# Quick start script for Pretalx with OIDC

set -e

echo "=================================="
echo "Pretalx with OIDC - Quick Start"
echo "=================================="
echo ""

# Check if pretalx.cfg exists
if [ ! -f "pretalx.cfg" ]; then
    echo "❌ pretalx.cfg not found!"
    echo ""
    echo "Please create pretalx.cfg from the example:"
    echo "  cp pretalx.cfg.example pretalx.cfg"
    echo ""
    echo "Then edit pretalx.cfg with your OIDC provider settings:"
    echo "  - op_discovery_endpoint"
    echo "  - rp_client_id"
    echo "  - rp_client_secret"
    echo "  - admin_users (optional)"
    echo ""
    exit 1
fi

echo "✓ Found pretalx.cfg"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker compose build

echo ""
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "=================================="
echo "✅ Pretalx is running!"
echo "=================================="
echo ""
echo "Access pretalx at: http://localhost:8355"
echo "(or the URL configured in pretalx.cfg)"
echo ""
echo "View logs:"
echo "  docker compose logs -f"
echo ""
echo "Stop services:"
echo "  docker compose down"
echo ""
echo "Note: The first login will create your user account."
echo "If you configured admin_users, you'll get admin privileges."
echo ""
