#!/bin/bash

# Test get_device_status method
echo "Testing get_device_status method..."

curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_device_status",
    "params": {
      "product_id": "TEST_PRODUCT",
      "device_name": "test_device"
    },
    "id": 6
  }'

echo ""
