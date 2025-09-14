#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug IoT STS Service 启动脚本
"""

import os
import sys
import logging
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('sts_service.log')
        ]
    )

def check_environment():
    """Check environment variable configuration"""
    logger = logging.getLogger(__name__)
    
    # Check required environment variables
    required_vars = ['IOT_ROLE_ARN']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Please set the following environment variables:")
        logger.error("  IOT_ROLE_ARN: CAM Role ARN")
        logger.error("Optional environment variables:")
        logger.error("  TC_SECRET_ID: Tencent Cloud SecretId")
        logger.error("  TC_SECRET_KEY: Tencent Cloud SecretKey")
        logger.error("  DEFAULT_REGION: Default region (default: ap-guangzhou)")
        return False
    
    # Check optional environment variables
    secret_id = os.getenv('TC_SECRET_ID')
    secret_key = os.getenv('TC_SECRET_KEY')
    
    if secret_id and secret_key:
        logger.info("Using Tencent Cloud credentials from environment variables")
    else:
        logger.info("Will try to use CVM/TKE bound role to get temporary credentials")
    
    logger.info(f"IOT Role ARN: {os.getenv('IOT_ROLE_ARN')}")
    logger.info(f"Default region: {os.getenv('DEFAULT_REGION', 'ap-guangzhou')}")
    
    return True

def main():
    """Main function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting PixelMug IoT STS Service...")
    
    # Check environment configuration
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    try:
        import fastapi
        import uvicorn
        from mug_service import app, FASTAPI_AVAILABLE, TENCENT_CLOUD_AVAILABLE, IOT_EXPLORER_AVAILABLE
        
        if not FASTAPI_AVAILABLE:
            logger.error("FastAPI not installed, please run: pip install fastapi uvicorn")
            sys.exit(1)
            
        if not TENCENT_CLOUD_AVAILABLE:
            logger.error("Tencent Cloud STS SDK not installed, please run: pip install tencentcloud-sdk-python-sts")
            sys.exit(1)
            
        if not IOT_EXPLORER_AVAILABLE:
            logger.error("Tencent Cloud IoT Explorer SDK not installed, please run: pip install tencentcloud-sdk-python-iotexplorer")
            sys.exit(1)
            
    except ImportError as e:
        logger.error(f"Failed to import dependencies: {e}")
        logger.error("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)
    
    # Start service
    host = os.getenv('UVICORN_HOST', '0.0.0.0')
    port = int(os.getenv('UVICORN_PORT', '8000'))
    
    logger.info(f"Starting HTTP service, listening on {host}:{port}")
    logger.info("API documentation: http://localhost:8000/docs")
    logger.info("Available endpoints:")
    logger.info("  - STS credentials: GET /sts/issue?pid=<ProductId>&dn=<DeviceName>")
    logger.info("  - Send pixel image: POST /pixel/send")
    logger.info("  - Send GIF animation: POST /gif/send")
    logger.info("  - Health check: GET /health")
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    main()
