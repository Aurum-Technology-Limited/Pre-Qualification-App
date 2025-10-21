#!/bin/bash

# Fraser Finance - Health Check Script
# This script verifies all services are running correctly

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         FRASER FINANCE - HEALTH CHECK                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Backend
echo -n "🔍 Checking Backend API... "
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/api/health)
if [ "$BACKEND_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $BACKEND_STATUS)${NC}"
fi

# Check Frontend
echo -n "🔍 Checking Frontend... "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" -eq 200 ]; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $FRONTEND_STATUS)${NC}"
fi

# Check MongoDB
echo -n "🔍 Checking MongoDB... "
MONGO_STATUS=$(sudo supervisorctl status mongodb | grep -c "RUNNING")
if [ "$MONGO_STATUS" -eq 1 ]; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Service Status:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
sudo supervisorctl status | grep -E "(backend|frontend|mongodb)"
echo ""

# Test Backend API
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "API Response Test:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
curl -s http://localhost:8001/api/health | python3 -m json.tool
echo ""

# List recent certificates
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Recent Certificates:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
CERT_COUNT=$(curl -s http://localhost:8001/api/certificates?limit=5 | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['count'])")
echo "Total Certificates Generated: $CERT_COUNT"
echo ""

# Access URLs
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Access URLs:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Frontend:    http://localhost:3000"
echo "Backend API: http://localhost:8001/api/health"
echo "API Docs:    http://localhost:8001/docs"
echo ""

echo -e "${GREEN}✓ Health check completed!${NC}"
