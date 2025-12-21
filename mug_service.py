#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PixelMug Smart Mug Tencent Cloud IoT Control Service
Provides device control functionality via Tencent Cloud IoT Explorer API
"""

import json
import uuid
import datetime
import logging
import base64
import re
import io
import os
import hashlib
from typing import Dict, Any, Optional, Union, List, Tuple

# 导入颜色生成器模块
try:
    from . import color_generator
except ImportError:
    # 如果相对导入失败，尝试绝对导入（适用于直接运行脚本的情况）
    import color_generator

# 腾讯云STS相关依赖
try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.sts.v20180813 import sts_client, models as sts_models
    TENCENT_CLOUD_AVAILABLE = True
except ImportError:
    TENCENT_CLOUD_AVAILABLE = False

# 腾讯云IoT Explorer相关依赖
try:
    from tencentcloud.iotexplorer.v20190423 import iotexplorer_client, models as iot_models
    IOT_EXPLORER_AVAILABLE = True
except ImportError:
    IOT_EXPLORER_AVAILABLE = False

# 腾讯云COS相关依赖
try:
    from qcloud_cos import CosConfig, CosS3Client
    COS_AVAILABLE = True
except ImportError:
    COS_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class MugService:
    """PixelMug service core class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_help(self) -> Dict[str, Any]:
        """Return service help information"""
        return {
            "service": "mcp_pixel_mug",
            "version": "2.0.0",
            "description": "PixelMug Smart Mug Tencent Cloud IoT Control Interface (Alaya MCP)",
            "methods": [
                {
                    "name": "help",
                    "description": "Get service help information",
                    "params": {}
                },
                {
                    "name": "issue_sts", 
                    "description": "Issue Tencent Cloud IoT STS temporary access credentials",
                    "params": {
                        "product_id": "Product ID, e.g.: ABC123DEF",
                        "device_name": "Device name, e.g.: mug_001"
                    }
                },
                {
                    "name": "send_pixel_image",
                    "description": "Send pixel image to device via Tencent Cloud IoT with optional COS upload",
                    "params": {
                        "product_id": "Product ID",
                        "device_name": "Device name",
                        "image_data": "Base64 encoded image or pixel matrix",
                        "target_width": "Target width (optional, default: 16)",
                        "target_height": "Target height (optional, default: 16)",
                        "use_cos": "Enable COS upload (optional, default: True)",
                        "ttl_sec": "COS signed URL TTL in seconds (optional, default: 900)"
                    }
                },
                {
                    "name": "send_gif_animation",
                    "description": "Send GIF pixel animation to device via Tencent Cloud IoT with optional COS upload",
                    "params": {
                        "product_id": "Product ID",
                        "device_name": "Device name", 
                        "gif_data": "Base64 encoded GIF, frame array, or palette format",
                        "frame_delay": "Delay between frames in ms (optional, default: 100)",
                        "loop_count": "Number of loops (optional, default: 0 for infinite)",
                        "target_width": "Target width (optional, default: 16)",
                        "target_height": "Target height (optional, default: 16)",
                        "use_cos": "Enable COS upload (optional, default: True)",
                        "ttl_sec": "COS signed URL TTL in seconds (optional, default: 900)",
                        "sta_port": "Port for device communication (optional, default: 80)"
                    }
                },
                {
                    "name": "convert_image_to_pixels",
                    "description": "Convert base64 image to pixel matrix for display",
                    "params": {
                        "image_data": "Base64 encoded image (PNG/JPEG)",
                        "target_width": "Target width for pixel matrix (optional, default: 16)",
                        "target_height": "Target height for pixel matrix (optional, default: 16)",
                        "resize_method": "Resize method: nearest/bilinear/bicubic (optional, default: nearest)"
                    }
                },
                {
                    "name": "get_device_status",
                    "description": "Query device online status and basic information",
                    "params": {
                        "product_id": "Product ID, e.g.: ABC123DEF",
                        "device_name": "Device name, e.g.: mug_001"
                    }
                },
                {
                    "name": "send_display_text",
                    "description": "Send text to display on smart mug screen via CallDeviceActionAsync",
                    "params": {
                        "product_id": "Product ID, e.g.: H3PI4FBTV5",
                        "device_name": "Device name, e.g.: mug_001",
                        "text": "Text to display (0-200 characters, empty string allowed)"
                    }
                }
            ],
            "supported_actions": [
                {"action": "send_pixel_image", "description": "Send pixel image via Tencent Cloud IoT", "params": {"image_data": "Pixel data or base64 image", "width": "Image width", "height": "Image height"}},
                {"action": "run_display_gif", "description": "Send GIF animation via Tencent Cloud IoT with device model parameters", "params": {"sta_file_name": "GIF filename", "sta_file_len": "File size in bytes", "sta_file_url": "COS download URL", "sta_port": "Communication port"}},
                {"action": "send_display_text", "description": "Send text to display on smart mug screen via CallDeviceActionAsync", "params": {"text": "Text to display (0-200 characters, empty string allowed)"}}
            ],
            "pixel_art_examples": self._generate_pixel_examples(),
            "pixel_art_formats": {
                "2d_array": "Array of arrays with hex colors: [[\"#FF0000\", \"#00FF00\"], [\"#0000FF\", \"#FFFFFF\"]]",
                "rgb_array": "Array of arrays with RGB tuples: [[[255,0,0], [0,255,0]], [[0,0,255], [255,255,255]]]",
                "base64": "Base64 encoded image data (PNG/JPEG)",
                "palette_based": "Palette-based format with color indices: {\"palette\": [\"#ffffff\", \"#ff0000\"], \"pixels\": [[0,1], [1,0]]}"
            }
        }
    
    def issue_sts(self, product_id: str, device_name: str) -> Dict[str, Any]:
        """Issue Tencent Cloud IoT STS temporary access credentials for ALAYA network"""
        try:
            # Check if Tencent Cloud SDK is available
            if not TENCENT_CLOUD_AVAILABLE:
                raise ImportError("Tencent Cloud SDK not installed, please install tencentcloud-sdk-python-sts")
            
            # Get configuration from environment variables
            role_arn = os.getenv("IOT_ROLE_ARN")
            if not role_arn:
                raise ValueError("Environment variable IOT_ROLE_ARN is not set")
            
            # Log the role ARN being used for debugging
            self.logger.info(f"Using role ARN: {role_arn}")
            
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            
            # Get base credentials for STS call
            base_cred = self._get_base_credentials()
            
            # Configure HTTP and Client Profile
            httpProfile = HttpProfile()
            httpProfile.endpoint = "sts.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # Create STS client
            client = sts_client.StsClient(base_cred, region, clientProfile)
            
            # Build session policy to limit permissions to single device
            session_policy = self._build_session_policy(product_id, device_name)
            
            # Create AssumeRole request with complete common parameters
            req = sts_models.AssumeRoleRequest()
            params = {
                "Action": "AssumeRole",
                "Version": "2018-08-13",
                "Region": region,
                "RoleArn": role_arn,
                "RoleSessionName": f"iot-device-{product_id}-{device_name}-{int(datetime.datetime.now().timestamp())}",
                "DurationSeconds": 900,  # 15 minutes
                "Policy": session_policy
            }
            req.from_json_string(json.dumps(params))
            
            # Call AssumeRole API
            resp = client.AssumeRole(req)
            
            # Extract credentials from response
            credentials = resp.Credentials
            result = {
                "tmpSecretId": credentials.TmpSecretId,
                "tmpSecretKey": credentials.TmpSecretKey,
                "token": credentials.Token,
                "expiredTime": resp.ExpiredTime,
                "expiration": resp.Expiration,
                "region": region,
                "product_id": product_id,
                "device_name": device_name,
                "issued_at": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            self.logger.info(f"Successfully issued STS credentials for device {product_id}/{device_name}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Failed to issue STS credentials: {error_msg}")
            
            # Get caller identity for debugging
            caller_info = self._get_caller_identity()
            self.logger.info(f"Caller identity: {caller_info}")
            
            # Provide specific guidance for common STS errors
            if "role not exist" in error_msg.lower():
                raise ValueError(f"Role assumption failed: 'role not exist'. "
                               f"This typically means: 1) The role '{role_arn}' exists but the sub-account lacks permission to assume it, "
                               f"2) The role's trust policy doesn't allow this sub-account to assume it, "
                               f"3) The sub-account doesn't have sts:AssumeRole permission. "
                               f"Caller info: {caller_info}. "
                               f"Please check the role's trust policy in CAM console and ensure it includes the sub-account UIN.")
            elif "access denied" in error_msg.lower():
                raise ValueError(f"Access denied. Please check sub-account permissions for sts:AssumeRole. Caller info: {caller_info}")
            elif "invalid role" in error_msg.lower():
                raise ValueError(f"Invalid role ARN format: {role_arn}")
            else:
                raise
    
    def _get_base_credentials(self):
        """Get base credentials for Tencent Cloud operations
        
        This method is used for various Tencent Cloud operations including:
        - STS AssumeRole calls
        - IoT Explorer operations
        - COS operations
        - Caller identity verification
        
        Priority: Sub-account keys > Main account keys
        """
        try:
            # Use explicit AK/SK from environment variables
            secret_id = os.getenv("TC_SECRET_ID")
            secret_key = os.getenv("TC_SECRET_KEY")
            
            if secret_id and secret_key:
                # Check if it's sub-account or main account
                account_type = self._detect_account_type(secret_id)
                self.logger.info(f"Using {account_type} credentials from environment variables")
                return credential.Credential(secret_id, secret_key)
            else:
                raise ValueError("No base credentials available. Please set TC_SECRET_ID and TC_SECRET_KEY environment variables.")
                
        except Exception as e:
            self.logger.error(f"Failed to get base credentials: {str(e)}")
            raise ValueError("Unable to get base credentials for Tencent Cloud operations")
    
    def _detect_account_type(self, secret_id: str) -> str:
        """Detect if the secret_id belongs to main account or sub-account"""
        try:
            # Sub-account secret_id typically starts with specific patterns
            # This is a heuristic detection, actual implementation may vary
            if secret_id.startswith("AKID") and len(secret_id) > 20:
                # This is a rough heuristic - in practice you might need to call
                # GetCallerIdentity API to determine the actual account type
                return "sub-account"
            else:
                return "main-account"
        except Exception:
            return "unknown-account"
    
    def _get_caller_identity(self) -> Dict[str, Any]:
        """Get caller identity information for debugging STS issues"""
        try:
            if not TENCENT_CLOUD_AVAILABLE:
                return {"error": "Tencent Cloud SDK not available"}
            
            # Get base credentials
            base_cred = self._get_base_credentials()
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            
            # Create STS client
            httpProfile = HttpProfile()
            httpProfile.endpoint = "sts.tencentcloudapi.com"
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = sts_client.StsClient(base_cred, region, clientProfile)
            
            # Call GetCallerIdentity
            req = sts_models.GetCallerIdentityRequest()
            resp = client.GetCallerIdentity(req)
            
            return {
                "arn": resp.Arn,
                "account_id": resp.AccountId,
                "user_id": resp.UserId,
                "principal_id": resp.PrincipalId
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get caller identity: {str(e)}")
            return {"error": str(e)}
    
    def _get_tencent_credentials(self, sts_credentials: Dict[str, Any] = None, use_direct_credentials: bool = False):
        """Get Tencent Cloud credentials for ALAYA network operations
        
        Args:
            sts_credentials: STS temporary credentials (preferred for ALAYA network)
            use_direct_credentials: If True, use sub-account credentials directly without STS
        """
        try:
            if sts_credentials and not use_direct_credentials:
                # Use STS temporary credentials (preferred for ALAYA network)
                self.logger.info("Using STS temporary credentials for ALAYA network operations")
                return credential.Credential(
                    sts_credentials["tmpSecretId"],
                    sts_credentials["tmpSecretKey"],
                    sts_credentials["token"]
                )
            elif use_direct_credentials:
                # Use sub-account credentials directly
                self.logger.info("Using sub-account credentials directly (bypassing STS)")
                return self._get_base_credentials()
            else:
                # This should not happen in ALAYA network - all operations should use STS
                raise ValueError("STS credentials required for ALAYA network operations")
                
        except Exception as e:
            self.logger.error(f"Failed to get Tencent Cloud credentials: {str(e)}")
            raise ValueError("Unable to get Tencent Cloud credentials for ALAYA network")
    
    def _build_session_policy(self, product_id: str, device_name: str) -> str:
        """Build session policy to limit permissions to single device and COS operations
        
        Note: This policy further restricts the permissions of the STS temporary credentials.
        The actual permissions come from the role being assumed (IOT_ROLE_ARN).
        """
        # Get COS configuration from environment variables
        cos_region = os.getenv("COS_REGION", "ap-guangzhou")
        cos_owner_uin = os.getenv("COS_OWNER_UIN")
        cos_bucket_name = os.getenv("COS_BUCKET_NAME")
        
        # Build COS resource ARN if COS is configured
        # Note: cos_owner_uin should be the UIN of the account that owns the COS bucket
        # This could be the main account UIN or sub-account UIN depending on your setup
        cos_resources = []
        if cos_owner_uin and cos_bucket_name:
            cos_resource_arn = f"qcs::cos:{cos_region}:uid/{cos_owner_uin}:{cos_bucket_name}/pmug/{device_name}/*"
            cos_resources.append(cos_resource_arn)
            self.logger.info(f"Added COS resource ARN: {cos_resource_arn}")
            self.logger.info(f"COS Owner UIN: {cos_owner_uin} (should be the account UIN that owns the COS bucket)")
        else:
            self.logger.warning("COS not configured: COS_OWNER_UIN or COS_BUCKET_NAME not set, skipping COS permissions")
        
        policy = {
            "version": "2.0",
            "statement": [
                {
                    "effect": "allow",
                    "action": [
                        "iotcloud:UpdateDeviceShadow",
                        "iotcloud:PublishMessage",
                        "iotcloud:CallDeviceActionAsync"
                    ],
                    "resource": [
                        f"qcs::iotcloud:::productId/{product_id}/device/{device_name}"
                    ]
                }
            ]
        }
        
        # Add COS permissions if COS is configured
        if cos_resources:
            policy["statement"].append({
                "effect": "allow",
                "action": [
                    "name/cos:PutObject",
                    "name/cos:GetObject"
                ],
                "resource": cos_resources
            })
        
        return json.dumps(policy)
    
    def _authorize(self, user_id: str, product_id: str, device_name: str) -> bool:
        """
        Simple authorization method for ALAYA protocol
        ALAYA is a protocol standard, no additional validation needed
        DApp directly assembles stdio parameters
        """
        try:
            # 基本参数验证
            if not product_id or not device_name:
                self.logger.error("Missing required parameters: product_id and device_name")
                return False
            
            # ALAYA协议标准：直接接受DApp组装的参数
            self.logger.info(f"Device {product_id}/{device_name} authorized for user {user_id} via ALAYA protocol")
            return True
                
        except Exception as e:
            self.logger.error(f"Error during device authorization: {str(e)}")
            return False
    

    def _create_iot_client_with_sts(self, sts_credentials: Dict[str, Any] = None, use_direct_credentials: bool = False):
        """Create Tencent Cloud IoT Explorer client with STS temporary credentials or direct sub-account credentials"""
        try:
            # Check if IoT Explorer SDK is available
            if not IOT_EXPLORER_AVAILABLE:
                raise ImportError("Tencent Cloud IoT Explorer SDK not installed, please install tencentcloud-sdk-python-iotexplorer")
            
            # Create credentials
            if use_direct_credentials:
                # Use sub-account credentials directly
                cred = self._get_base_credentials()
                region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
                self.logger.info(f"Using sub-account credentials directly for IoT operations in region {region}")
            else:
                # Use STS temporary credentials
                cred = credential.Credential(
                    sts_credentials["tmpSecretId"],
                    sts_credentials["tmpSecretKey"],
                    sts_credentials["token"]
                )
                region = sts_credentials["region"]
                self.logger.info(f"Using STS temporary credentials for IoT operations in region {region}")
            
            # Configure HTTP and Client Profile
            httpProfile = HttpProfile()
            httpProfile.endpoint = "iotexplorer.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # Create IoT Explorer client
            client = iotexplorer_client.IotexplorerClient(cred, region, clientProfile)
            
            self.logger.info(f"Successfully created IoT Explorer client for region {region}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create IoT Explorer client: {str(e)}")
            raise

    def _push_asset_to_cos(self, product_id: str, device_name: str, asset_data: bytes, 
                          asset_kind: str, file_name: str, metadata: Dict[str, Any], 
                          ttl_sec: int = 300, use_direct_credentials: bool = True) -> Dict[str, Any]:
        """Push asset to COS and get signed URL with proper key pattern and metadata
        
        Args:
            product_id: Product ID
            device_name: Device name
            asset_data: Asset data bytes
            asset_kind: Asset kind ("pixel-json" or "gif")
            file_name: File name without extension (e.g., "gif_asset_1765780420")
            metadata: Asset metadata
            ttl_sec: TTL in seconds
            use_direct_credentials: Use direct credentials flag
            
        Returns:
            Dict containing key, url, file_name (with extension), and other asset info
        """
        try:
            if not COS_AVAILABLE:
                raise ImportError("Tencent Cloud COS SDK not installed, please install tencentcloud-sdk-python-cos")
            
            # 1. Always use direct credentials for COS operations in stdio mode
            # STS is not needed for COS operations and may fail due to role permissions
            cred = self._get_base_credentials()
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            sts_info = {
                "tmpSecretId": cred.secret_id,
                "tmpSecretKey": cred.secret_key,
                "token": None,  # No token for direct credentials
                "region": region
            }
            self.logger.info("Using sub-account credentials directly for COS operations (stdio mode)")
            
            # 2. Generate COS client
            cos_config = CosConfig(
                Region=sts_info["region"],
                SecretId=sts_info["tmpSecretId"],
                SecretKey=sts_info["tmpSecretKey"],
                Token=sts_info.get("token"),  # Token may be None for direct credentials
                Scheme="https"
            )
            
            # Single-AZ bucket configuration (no multi-AZ support needed)
            cos_client = CosS3Client(cos_config)
            
            # 3. Generate SHA256 hash and key with new pattern
            sha256 = hashlib.sha256(asset_data).hexdigest()
            sha8 = sha256[:8]  # First 8 characters of SHA256
            current_date = datetime.datetime.utcnow().strftime("%Y%m")
            
            # Determine file extension based on asset kind
            if asset_kind == "pixel-json":
                ext = "json"
            elif asset_kind == "gif":
                ext = "gif"
            else:
                ext = "json"
            
            # Key pattern: pmug/{deviceName}/{YYYYMM}/{file_name}-{sha8}.{ext}
            # file_name is passed from external, ensuring uniqueness
            key = f"pmug/{device_name}/{current_date}/{file_name}-{sha8}.{ext}"
            
            # Generate full file name with extension for sta_file_name
            full_file_name = f"{file_name}-{sha8}.{ext}"
            
            # 4. Set Content-Type based on asset kind
            content_type = "application/vnd.pmug.pixel+json" if asset_kind == "pixel-json" else "image/gif"
            
            # 5. Prepare metadata
            cos_metadata = {
                "x-cos-meta-sha256": sha256,
                "x-cos-meta-width": str(metadata.get("width", 0)),
                "x-cos-meta-height": str(metadata.get("height", 0)),
                "x-cos-meta-frames": str(metadata.get("frame_count", 1)),
                "x-cos-meta-file-name": file_name,
                "x-cos-meta-device-name": device_name,
                "x-cos-meta-product-id": product_id
            }
            
            # 6. Upload to COS with metadata and cache headers
            bucket_name = os.getenv("COS_BUCKET_NAME", "pixelmug-assets")
            cos_client.put_object(
                Bucket=bucket_name,
                Body=asset_data,
                Key=key,
                ContentType=content_type,
                Metadata=cos_metadata,
                CacheControl="public, max-age=31536000, immutable",
                StorageClass="STANDARD"
            )
            
            # 7. Generate public read URL
            get_url = cos_client.get_object_url(
                Bucket=bucket_name,
                Key=key
            )
            
            # 8. Calculate expiration timestamp
            expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_sec)).timestamp())
            
            return {
                "key": key,
                "sha256": sha256,
                "sha8": sha8,
                "file_name": full_file_name,  # Full file name with extension: {file_name}-{sha8}.{ext}
                "url": get_url,
                "bytes": len(asset_data),
                "width": metadata.get("width", 0),
                "height": metadata.get("height", 0),
                "frames": metadata.get("frame_count", 1),
                "expiresAt": expires_at,
                "contentType": content_type
            }
            
        except Exception as e:
            self.logger.error(f"Failed to push asset to COS: {str(e)}")
            raise

    def send_pixel_image(self, product_id: str, device_name: str, image_data: Union[str, List, Dict], 
                        target_width: int = 16, target_height: int = 16, 
                        use_cos: bool = True, ttl_sec: int = 900, use_direct_credentials: bool = True) -> Dict[str, Any]:
        """Send pixel image to device via Tencent Cloud IoT Explorer with optional COS upload"""
        try:
            # Create IoT client with direct credentials for stdio mode
            client = self._create_iot_client_with_sts(use_direct_credentials=use_direct_credentials)
            
            # Process image data
            if isinstance(image_data, str):
                # If it's base64 encoded image, convert to pixel matrix
                conversion_result = self.convert_image_to_pixels(image_data, target_width, target_height)
                pixel_matrix = conversion_result["pixel_matrix"]
                width = conversion_result["width"]
                height = conversion_result["height"]
            elif isinstance(image_data, dict) and "pixels" in image_data:
                # If it's palette-based pixel art format
                palette_result = self._process_palette_pixel_art(image_data, target_width, target_height)
                pixel_matrix = palette_result["pixel_matrix"]
                width = palette_result["width"]
                height = palette_result["height"]
            else:
                # If it's already a pixel matrix
                pixel_matrix = image_data
                width = target_width
                height = target_height
                
            # Validate pixel matrix
            self._validate_pixel_pattern(pixel_matrix, width, height)
            
            # Convert pixel matrix to single frame GIF for display
            # Since device only supports GIF action, we'll create a single frame GIF
            frames = [{
                "frame_index": 0,
                "pixel_matrix": pixel_matrix,
                "duration": 1000  # 1 second display
            }]
            
            # Create GIF from single frame
            gif_bytes = self._create_gif_from_frames(frames, 1000, 0)  # No loop
            
            # Prepare asset data for COS upload if enabled (only upload GIF, not JSON)
            asset_info = None
            if use_cos:
                try:
                    # Generate file_name with unified logic: pixel_{timestamp}
                    timestamp = int(datetime.datetime.utcnow().timestamp())
                    file_name = f"pixel_asset_{timestamp}"
                    
                    # Prepare metadata
                    metadata = {
                        "width": width,
                        "height": height,
                        "frame_count": 1
                    }
                    
                    # Upload GIF to COS (not JSON)
                    asset_info = self._push_asset_to_cos(product_id, device_name, gif_bytes, "gif", file_name, metadata, ttl_sec, use_direct_credentials)
                    self.logger.info(f"Successfully uploaded pixel image GIF to COS: {asset_info['key']}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload to COS, falling back to direct transmission: {str(e)}")
                    use_cos = False
            
            # Prepare input parameters for GIF action according to device model
            if use_cos and asset_info:
                # Use COS upload for GIF
                # Determine port based on URL protocol
                url = asset_info["url"]
                if url.startswith("https://"):
                    port = 443
                else:
                    port = 80
                
                # Use the file_name from asset_info which matches the COS URL filename
                input_params = {
                    "sta_file_name": asset_info["file_name"],  # This matches the filename in COS URL
                    "sta_file_len": len(gif_bytes),
                    "sta_file_url": url,
                    "sta_port": port
                }
                delivery_method = "cos"
            else:
                # For direct transmission, use device model parameters
                temp_filename = f"pixel_{int(datetime.datetime.utcnow().timestamp())}.gif"
                
                input_params = {
                    "sta_file_name": temp_filename,
                    "sta_file_len": len(gif_bytes),
                    "sta_file_url": "direct_transmission",  # Placeholder for direct transmission
                    "sta_port": 80
                }
                delivery_method = "direct"
            
            # Create CallDeviceActionAsync request with complete common parameters
            req = iot_models.CallDeviceActionAsyncRequest()
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                "ActionId": "run_display_gif",  # Use existing GIF action
                "InputParams": json.dumps(input_params),
                # Add common parameters as per Tencent Cloud API documentation
                "Region": region,
                "Version": "2019-04-23"  # IoT Explorer API version
            }
            req.from_json_string(json.dumps(params))
            
            # Send request to device
            resp = client.CallDeviceActionAsync(req)
            
            result = {
                "status": "success",
                "client_token": resp.ClientToken,
                "call_status": resp.Status,
                "request_id": resp.RequestId,
                "product_id": product_id,
                "device_name": device_name,
                "action_id": "run_display_gif",  # Updated to use GIF action
                "image_info": {
                    "width": width,
                    "height": height,
                    "total_pixels": width * height,
                    "converted_to_gif": True,
                    "frame_count": 1
                },
                "delivery_method": delivery_method,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            # Add COS asset info to result if available
            if use_cos and asset_info:
                result["asset"] = asset_info
            
            self.logger.info(f"Successfully sent pixel image to device {product_id}/{device_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send pixel image: {str(e)}")
            raise

    def _process_gif_to_frames(self, gif_data: str, target_width: int = 16, target_height: int = 16) -> List[Dict]:
        """Process GIF data to frame array"""
        try:
            if not PIL_AVAILABLE:
                raise ImportError("PIL not available for GIF processing")
                
            # Decode base64 GIF data
            gif_bytes = base64.b64decode(gif_data)
            
            # Open GIF with PIL
            gif_image = Image.open(io.BytesIO(gif_bytes))
            
            frames = []
            frame_index = 0
            
            try:
                while True:
                    # Get current frame
                    frame = gif_image.copy()
                    
                    # Convert to RGB if necessary
                    if frame.mode != 'RGB':
                        frame = frame.convert('RGB')
                    
                    # Resize frame
                    resized_frame = frame.resize((target_width, target_height), Image.NEAREST)
                    
                    # Convert to pixel matrix
                    pixel_matrix = []
                    for y in range(target_height):
                        row = []
                        for x in range(target_width):
                            r, g, b = resized_frame.getpixel((x, y))
                            hex_color = f"#{r:02x}{g:02x}{b:02x}"
                            row.append(hex_color)
                        pixel_matrix.append(row)
                    
                    # Get frame duration (default 100ms if not specified)
                    duration = gif_image.info.get('duration', 100)
                    
                    frames.append({
                        "frame_index": frame_index,
                        "pixel_matrix": pixel_matrix,
                        "duration": duration
                    })
                    
                    frame_index += 1
                    gif_image.seek(gif_image.tell() + 1)
                    
            except EOFError:
                # End of frames
                pass
            
            self.logger.info(f"Processed GIF into {len(frames)} frames")
            return frames
            
        except Exception as e:
            self.logger.error(f"Failed to process GIF: {str(e)}")
            raise

    def _create_gif_from_frames(self, frames: List[Dict], frame_delay: int = 100, loop_count: int = 0) -> bytes:
        """Create GIF file bytes from frame data"""
        try:
            if not PIL_AVAILABLE:
                raise ImportError("PIL not available for GIF creation")
            
            if not frames:
                raise ValueError("No frames provided for GIF creation")
            
            # Get dimensions from first frame
            first_frame = frames[0]
            pixel_matrix = first_frame["pixel_matrix"]
            height = len(pixel_matrix)
            width = len(pixel_matrix[0]) if pixel_matrix else 0
            
            # Create PIL images for each frame
            pil_frames = []
            durations = []
            
            self.logger.info(f"Creating GIF from {len(frames)} frames, width={width}, height={height}")
            
            for idx, frame in enumerate(frames):
                pixel_matrix = frame["pixel_matrix"]
                duration = frame.get("duration", frame_delay)
                
                # Convert duration from milliseconds to seconds (PIL uses seconds)
                # PIL expects duration in milliseconds, but we'll use it as-is
                # Actually, PIL's duration parameter expects milliseconds
                duration_ms = duration
                
                # Create PIL image from pixel matrix
                # Use 'P' mode (palette) for better GIF compatibility
                img = Image.new('RGB', (width, height))
                
                for y in range(height):
                    for x in range(width):
                        color_hex = pixel_matrix[y][x]
                        # Convert hex color to RGB
                        if color_hex.startswith('#'):
                            color_hex = color_hex[1:]
                        r = int(color_hex[0:2], 16)
                        g = int(color_hex[2:4], 16)
                        b = int(color_hex[4:6], 16)
                        img.putpixel((x, y), (r, g, b))
                
                # Convert to palette mode BEFORE appending
                # This is critical for multi-frame GIFs - each frame must be in palette mode
                # Convert each frame to palette mode independently
                img_p = img.quantize()
                
                # Make a copy to ensure frame independence
                img_copy = img_p.copy()
                
                pil_frames.append(img_copy)
                durations.append(duration_ms)
                
                # Log first few pixels to verify frames are different
                if idx < 3:
                    sample_pixels = []
                    for sy in range(min(3, height)):
                        for sx in range(min(3, width)):
                            sample_pixels.append(pixel_matrix[sy][sx])
                    self.logger.debug(f"Frame {idx}: duration={duration_ms}ms, size={img_copy.size}, mode={img_copy.mode}, sample_pixels={sample_pixels[:9]}")
                else:
                    self.logger.debug(f"Frame {idx}: duration={duration_ms}ms, size={img_copy.size}, mode={img_copy.mode}")
            
            self.logger.info(f"Created {len(pil_frames)} PIL images, durations: {durations}")
            
            # Verify frames are different by comparing all frames
            if len(pil_frames) > 1:
                all_frames_identical = True
                frame0_data = list(pil_frames[0].getdata())
                
                for idx in range(1, len(pil_frames)):
                    frame_data = list(pil_frames[idx].getdata())
                    if frame0_data != frame_data:
                        all_frames_identical = False
                        self.logger.info(f"Frame {idx} is different from frame 0")
                        break
                
                if all_frames_identical:
                    self.logger.error("CRITICAL: All frames are IDENTICAL! PIL will optimize them into a single frame.")
                    self.logger.error("This is a data issue - all frames have the same pixel values.")
                    # Check if all pixels are the same color
                    unique_colors = set(frame0_data)
                    if len(unique_colors) == 1:
                        self.logger.error(f"All pixels in all frames are the same color: {unique_colors}")
                else:
                    # Check first two frames
                    frame1_data = list(pil_frames[1].getdata())
                    frames_are_different = frame0_data != frame1_data
                    self.logger.info(f"Frame comparison: frames 0 and 1 are {'different' if frames_are_different else 'IDENTICAL'}")
            
            # Create GIF
            gif_buffer = io.BytesIO()
            
            # Save as GIF with proper parameters
            # Note: PIL's duration parameter expects milliseconds
            append_images = pil_frames[1:] if len(pil_frames) > 1 else []
            
            # Always use list for duration to ensure each frame gets its own duration
            # Even if all durations are the same, using a list is more reliable
            duration_value = durations
            self.logger.info(f"Using duration list: {durations}")
            
            # Try multiple save strategies if first one fails
            save_kwargs = {
                'format': 'GIF',
                'save_all': True,
                'append_images': append_images,
                'duration': duration_value,  # Always use list
                'loop': loop_count if loop_count > 0 else 0,  # 0 means infinite loop
                'optimize': False  # Disable optimization to ensure all frames are saved
            }
            
            self.logger.info(f"Saving GIF: {len(pil_frames)} frames, duration={duration_value}, loop={save_kwargs['loop']}, append_images={len(append_images)}")
            
            # Save first frame with all other frames appended
            try:
                pil_frames[0].save(gif_buffer, **save_kwargs)
            except Exception as e:
                self.logger.error(f"Failed to save GIF with standard method: {str(e)}")
                # Try without disposal parameter
                save_kwargs_no_disposal = save_kwargs.copy()
                if 'disposal' in save_kwargs_no_disposal:
                    del save_kwargs_no_disposal['disposal']
                self.logger.info("Retrying without disposal parameter...")
                pil_frames[0].save(gif_buffer, **save_kwargs_no_disposal)
            
            gif_bytes = gif_buffer.getvalue()
            gif_buffer.close()
            
            # Verify the GIF was created correctly by checking if we can read it back
            if PIL_AVAILABLE and len(gif_bytes) > 0:
                try:
                    verify_img = Image.open(io.BytesIO(gif_bytes))
                    frame_count = 0
                    try:
                        while True:
                            verify_img.seek(frame_count)
                            frame_count += 1
                    except EOFError:
                        pass
                    self.logger.info(f"Created GIF with {len(frames)} input frames, {frame_count} frames in output file, {len(gif_bytes)} bytes")
                    if frame_count != len(frames):
                        self.logger.warning(f"Frame count mismatch: expected {len(frames)} frames, but GIF contains {frame_count} frames")
                except Exception as e:
                    self.logger.warning(f"Could not verify GIF frame count: {str(e)}")
            else:
                self.logger.info(f"Created GIF with {len(frames)} frames, {len(gif_bytes)} bytes")
            return gif_bytes
            
        except Exception as e:
            self.logger.error(f"Failed to create GIF from frames: {str(e)}")
            raise

    def send_gif_animation(self, product_id: str, device_name: str, gif_data: Union[str, List, Dict], 
                          frame_delay: int = 100, loop_count: int = 0, 
                          target_width: int = 16, target_height: int = 16,
                          use_cos: bool = True, ttl_sec: int = 900, sta_port: int = 80, use_direct_credentials: bool = True) -> Dict[str, Any]:
        """Send GIF pixel animation to device via Tencent Cloud IoT Explorer with optional COS upload"""
        try:
            # Create IoT client with direct credentials for stdio mode
            client = self._create_iot_client_with_sts(use_direct_credentials=use_direct_credentials)
            
            # Process GIF data
            frames = None
            gif_bytes = None
            
            self.logger.info(f"Processing GIF data, type: {type(gif_data).__name__}")
            
            if isinstance(gif_data, str):
                # If it's base64 encoded GIF, we can use it directly or process to frames
                self.logger.info("Branch: gif_data is string, attempting base64 decode")
                try:
                    # Try to decode as base64 GIF first
                    gif_bytes = base64.b64decode(gif_data)
                    self.logger.info(f"Successfully decoded base64, size: {len(gif_bytes)} bytes")
                    
                    # Validate it's a GIF by trying to open it
                    if PIL_AVAILABLE:
                        test_img = Image.open(io.BytesIO(gif_bytes))
                        self.logger.info(f"Image opened successfully, format: {test_img.format}")
                        if test_img.format != 'GIF':
                            # Not a GIF, process as frames
                            self.logger.warning(f"Image format is {test_img.format}, not GIF. Processing as frames")
                            frames = self._process_gif_to_frames(gif_data, target_width, target_height)
                            gif_bytes = None
                            self.logger.info(f"Processed to frames, frame count: {len(frames) if frames else 0}")
                        else:
                            self.logger.info("Valid GIF format detected, using gif_bytes directly")
                    else:
                        self.logger.warning("PIL not available, cannot validate GIF format. Assuming valid GIF")
                except Exception as e:
                    # If base64 decode fails, treat as frame data
                    self.logger.warning(f"Base64 decode failed: {str(e)}, treating as frame data")
                    frames = self._process_gif_to_frames(gif_data, target_width, target_height)
                    self.logger.info(f"Processed to frames, frame count: {len(frames) if frames else 0}")
            elif isinstance(gif_data, dict) and "frames" in gif_data:
                # If it's palette-based GIF format
                self.logger.info("Branch: gif_data is dict with 'frames' key, processing as palette-based GIF format")
                frames = self._process_palette_gif_animation(gif_data, target_width, target_height)
                self.logger.info(f"Processed palette-based GIF, frame count: {len(frames) if frames else 0}")
            elif isinstance(gif_data, list):
                # If it's already frame array
                self.logger.info(f"Branch: gif_data is list, treating as frame array")
                
                # Validate frame structure
                if len(gif_data) == 0:
                    raise ValueError("gif_data list is empty")
                
                # Check first frame structure
                first_frame = gif_data[0]
                if not isinstance(first_frame, dict):
                    raise ValueError(f"Frame must be a dict, got {type(first_frame).__name__}")
                
                if "pixel_matrix" not in first_frame:
                    raise ValueError("Frame missing required 'pixel_matrix' field")
                
                self.logger.info(f"Frame array structure validated: {len(gif_data)} frames")
                self.logger.info(f"First frame keys: {list(first_frame.keys())}")
                self.logger.info(f"First frame has duration: {'duration' in first_frame}")
                
                frames = gif_data
                self.logger.info(f"Using frames directly, frame count: {len(frames)}")
                
                # Log frame details
                for idx, frame in enumerate(frames):
                    frame_duration = frame.get("duration", "not set")
                    pixel_matrix = frame.get("pixel_matrix", [])
                    matrix_height = len(pixel_matrix) if pixel_matrix else 0
                    matrix_width = len(pixel_matrix[0]) if pixel_matrix and len(pixel_matrix) > 0 else 0
                    self.logger.debug(f"Frame {idx}: duration={frame_duration}, size={matrix_width}x{matrix_height}")
            else:
                # Unknown type
                raise ValueError(f"Unsupported gif_data type: {type(gif_data).__name__}, expected str, dict, or list")
                
            # Validate we have either frames or GIF bytes
            self.logger.info(f"Validation: frames={frames is not None}, gif_bytes={gif_bytes is not None}")
            if not frames and not gif_bytes:
                self.logger.error("No valid GIF data found: both frames and gif_bytes are None")
                raise ValueError("No valid GIF data found")
            else:
                if frames:
                    self.logger.info(f"Using frames data, count: {len(frames)}")
                if gif_bytes:
                    self.logger.info(f"Using gif_bytes data, size: {len(gif_bytes)} bytes")
            
            # Prepare asset data for COS upload if enabled
            asset_info = None
            # Prepare input parameters according to device model
            self.logger.info(f"use_cos: {use_cos} - asset_info: {asset_info}")
            if use_cos:
                try:
                    # Generate file_name with unified logic: gif_asset_{timestamp}
                    timestamp = int(datetime.datetime.utcnow().timestamp())
                    file_name = f"gif_asset_{timestamp}"
                    
                    # Create GIF file if we have frames
                    if frames and not gif_bytes:
                        gif_bytes = self._create_gif_from_frames(frames, frame_delay, loop_count)
                    
                    # Prepare metadata
                    metadata = {
                        "width": target_width,
                        "height": target_height,
                        "frame_count": len(frames) if frames else 1
                    }
                    
                    # Upload actual GIF file to COS
                    asset_info = self._push_asset_to_cos(product_id, device_name, gif_bytes, "gif", file_name, metadata, ttl_sec, use_direct_credentials)
                    self.logger.info(f"Successfully uploaded GIF file to COS: {asset_info['key']}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload to COS, falling back to direct transmission: {str(e)}")
                    use_cos = False
            
            
            if use_cos and asset_info:
                # Use device model parameters: sta_file_name, sta_file_len, sta_file_url, sta_port
                # Determine port based on URL protocol
                self.logger.info(f"COS success - asset_info: {asset_info}")
                url = asset_info["url"]
                if url.startswith("https://"):
                    port = 443
                else:
                    port = 80
                
                # Use the file_name from asset_info which matches the COS URL filename
                input_params = {
                    "sta_file_name": asset_info["file_name"],  # This matches the filename in COS URL: {file_name}-{sha8}.gif
                    "sta_file_len": asset_info["bytes"],
                    "sta_file_url": url,
                    "sta_port": port
                }
                self.logger.info(f"COS success URL: {url}")
                delivery_method = "cos"
            else:
                # For direct transmission, we need to create a temporary GIF and upload it
                # Since device model only accepts COS parameters, we'll create a minimal GIF
                self.logger.info(f"COS failed - frames: {frames}")
                if not frames:
                    raise ValueError("Cannot send GIF without frames when COS is disabled")
                
                # Create GIF from frames
                gif_bytes = self._create_gif_from_frames(frames, frame_delay, loop_count)
                
                # For direct transmission, we'll use a simple approach
                # Generate a temporary filename
                temp_filename = f"temp_gif_{int(datetime.datetime.utcnow().timestamp())}.gif"
                
                input_params = {
                    "sta_file_name": temp_filename,
                    "sta_file_len": len(gif_bytes),
                    "sta_file_url": "direct_transmission",  # Placeholder for direct transmission
                    "sta_port": 80
                }
                delivery_method = "direct"
            
            # Create CallDeviceActionAsync request with complete common parameters
            req = iot_models.CallDeviceActionAsyncRequest()
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                "ActionId": "run_display_gif",  # Use device model action ID
                "InputParams": json.dumps(input_params),
                # Add common parameters as per Tencent Cloud API documentation
                "Region": region,
                "Version": "2019-04-23"  # IoT Explorer API version
            }
            req.from_json_string(json.dumps(params))
            
            # Send request to device
            resp = client.CallDeviceActionAsync(req)
            
            result = {
                "status": "success",
                "client_token": resp.ClientToken,
                "call_status": resp.Status,
                "request_id": resp.RequestId,
                "product_id": product_id,
                "device_name": device_name,
                "action_id": "run_display_gif",
                "animation_info": {
                    "frame_count": len(frames) if frames else 1,
                    "frame_delay": frame_delay,
                    "loop_count": loop_count,
                    "width": target_width,
                    "height": target_height,
                    "total_pixels": target_width * target_height
                },
                "delivery_method": delivery_method,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            # Add COS asset info to result if available
            if use_cos and asset_info:
                result["asset"] = asset_info
            
            self.logger.info(f"Successfully sent GIF animation to device {product_id}/{device_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send GIF animation: {str(e)}")
            raise

    def _process_palette_gif_animation(self, gif_data: Dict[str, Any], target_width: int, target_height: int) -> List[Dict]:
        """Process palette-based GIF animation format to frame array"""
        try:
            # Extract data from GIF format
            title = gif_data.get("title", "unknown")
            description = gif_data.get("description", "")
            width = gif_data.get("width", target_width)
            height = gif_data.get("height", target_height)
            palette = gif_data.get("palette", [])
            frames_data = gif_data.get("frames", [])
            frame_delay = gif_data.get("frame_delay", 100)
            loop_count = gif_data.get("loop_count", 0)
            
            # Validate palette
            if not palette or len(palette) == 0:
                raise ValueError("Palette cannot be empty")
            
            if len(palette) > 16:
                raise ValueError("Palette cannot have more than 16 colors")
            
            # Validate palette colors
            for i, color in enumerate(palette):
                if not isinstance(color, str) or not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    raise ValueError(f"Invalid color format in palette at index {i}: {color}")
            
            # Process frames
            frames = []
            for frame_idx, frame_data in enumerate(frames_data):
                if not isinstance(frame_data, dict):
                    raise ValueError(f"Frame {frame_idx} is not a dictionary")
                
                frame_pixels = frame_data.get("pixels", [])
                frame_duration = frame_data.get("duration", frame_delay)
                
                # Validate frame pixels
                if not frame_pixels or len(frame_pixels) != height:
                    raise ValueError(f"Frame {frame_idx} pixels height {len(frame_pixels)} doesn't match specified height {height}")
                
                # Convert palette indices to hex colors for this frame
                pixel_matrix = []
                for row_idx, row in enumerate(frame_pixels):
                    if not isinstance(row, list):
                        raise ValueError(f"Frame {frame_idx} row {row_idx} is not a list")
                    
                    if len(row) != width:
                        raise ValueError(f"Frame {frame_idx} row {row_idx} width {len(row)} doesn't match specified width {width}")
                    
                    pixel_row = []
                    for col_idx, pixel_index in enumerate(row):
                        if not isinstance(pixel_index, int) or pixel_index < 0 or pixel_index >= len(palette):
                            raise ValueError(f"Invalid pixel index in frame {frame_idx} at [{row_idx}][{col_idx}]: {pixel_index}")
                        
                        # Get color from palette
                        color = palette[pixel_index]
                        pixel_row.append(color)
                    
                    pixel_matrix.append(pixel_row)
                
                frames.append({
                    "frame_index": frame_idx,
                    "pixel_matrix": pixel_matrix,
                    "duration": frame_duration
                })
            
            return frames
            
        except Exception as e:
            self.logger.error(f"Failed to process palette GIF animation: {str(e)}")
            raise

    def _process_palette_pixel_art(self, pixel_art_data: Dict[str, Any], target_width: int, target_height: int) -> Dict[str, Any]:
        """Process palette-based pixel art format to hex color matrix"""
        try:
            # Extract data from pixel art format
            title = pixel_art_data.get("title", "unknown")
            description = pixel_art_data.get("description", "")
            width = pixel_art_data.get("width", target_width)
            height = pixel_art_data.get("height", target_height)
            palette = pixel_art_data.get("palette", [])
            pixels = pixel_art_data.get("pixels", [])
            
            # Validate palette
            if not palette or len(palette) == 0:
                raise ValueError("Palette cannot be empty")
            
            if len(palette) > 16:
                raise ValueError("Palette cannot have more than 16 colors")
            
            # Validate palette colors
            for i, color in enumerate(palette):
                if not isinstance(color, str) or not re.match(r'^#[0-9A-Fa-f]{6}$', color):
                    raise ValueError(f"Invalid color format in palette at index {i}: {color}")
            
            # Validate pixels array
            if not pixels or len(pixels) != height:
                raise ValueError(f"Pixels array height {len(pixels)} doesn't match specified height {height}")
            
            # Convert palette indices to hex colors
            pixel_matrix = []
            for row_idx, row in enumerate(pixels):
                if not isinstance(row, list):
                    raise ValueError(f"Pixels row {row_idx} is not a list")
                
                if len(row) != width:
                    raise ValueError(f"Pixels row {row_idx} width {len(row)} doesn't match specified width {width}")
                
                pixel_row = []
                for col_idx, pixel_index in enumerate(row):
                    if not isinstance(pixel_index, int) or pixel_index < 0 or pixel_index >= len(palette):
                        raise ValueError(f"Invalid pixel index at [{row_idx}][{col_idx}]: {pixel_index}")
                    
                    # Get color from palette
                    color = palette[pixel_index]
                    pixel_row.append(color)
                
                pixel_matrix.append(pixel_row)
            
            return {
                "pixel_matrix": pixel_matrix,
                "width": width,
                "height": height,
                "palette": palette,
                "title": title,
                "description": description,
                "format": "palette-based"
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process palette pixel art: {str(e)}")
            raise

    def _validate_pixel_pattern(self, pattern: Union[List, str], width: int, height: int) -> bool:
        """Validate pixel art pattern"""
        if isinstance(pattern, str):
            # Base64 encoded image
            try:
                decoded = base64.b64decode(pattern)
                # Basic validation - should have reasonable size
                if len(decoded) < width * height or len(decoded) > width * height * 4:
                    raise ValueError("Base64 pattern size doesn't match dimensions")
                return True
            except Exception as e:
                raise ValueError(f"Invalid base64 pattern: {str(e)}")
        
        elif isinstance(pattern, list):
            # 2D array of colors
            if len(pattern) != height:
                raise ValueError(f"Pattern height {len(pattern)} doesn't match specified height {height}")
            
            for row_idx, row in enumerate(pattern):
                if not isinstance(row, list):
                    raise ValueError(f"Row {row_idx} is not a list")
                if len(row) != width:
                    raise ValueError(f"Row {row_idx} width {len(row)} doesn't match specified width {width}")
                
                for col_idx, pixel in enumerate(row):
                    if isinstance(pixel, str):
                        # Hex color validation
                        if not re.match(r'^#[0-9A-Fa-f]{6}$', pixel):
                            raise ValueError(f"Invalid color format at [{row_idx}][{col_idx}]: {pixel}")
                    elif isinstance(pixel, (list, tuple)):
                        # RGB/RGBA values
                        if len(pixel) not in [3, 4]:
                            raise ValueError(f"Invalid RGB/RGBA format at [{row_idx}][{col_idx}]: {pixel}")
                        for component in pixel:
                            if not isinstance(component, int) or component < 0 or component > 255:
                                raise ValueError(f"Invalid RGB component at [{row_idx}][{col_idx}]: {component}")
                    else:
                        raise ValueError(f"Invalid pixel format at [{row_idx}][{col_idx}]: {type(pixel)}")
            return True
        
        else:
            raise ValueError("Pattern must be a 2D array or base64 string")

    def _generate_pixel_examples(self) -> Dict[str, Any]:
        """Generate pixel art examples for documentation"""
        return {
            "smiley_face": {
                "description": "8x8 smiley face",
                "pattern": [
                    ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#000000", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#000000", "#000000", "#000000", "#000000", "#FFFF00", "#FFFF00"],
                    ["#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00"],
                    ["#000000", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#FFFF00", "#000000"]
                ],
                "width": 8,
                "height": 8
            },
            "heart": {
                "description": "8x8 heart shape",
                "pattern": [
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000"],
                    ["#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000"],
                    ["#000000", "#000000", "#FF0000", "#FF0000", "#FF0000", "#FF0000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#FF0000", "#FF0000", "#000000", "#000000", "#000000"]
                ],
                "width": 8,
                "height": 8
            },
            "coffee_cup": {
                "description": "8x8 coffee cup",
                "pattern": [
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#FFFFFF", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#FFFFFF", "#000000"],
                    ["#000000", "#8B4513", "#654321", "#654321", "#654321", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000"],
                    ["#000000", "#000000", "#8B4513", "#8B4513", "#8B4513", "#000000", "#000000", "#000000"],
                    ["#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000", "#000000"]
                ],
                "width": 8,
                "height": 8
            },
            "palette_example": {
                "description": "4x4 palette-based example",
                "palette_format": {
                    "title": "sample_image",
                    "description": "Converted from sample_image.jpg",
                    "width": 4,
                    "height": 4,
                    "palette": ["#ffffff", "#ff0000", "#00ff00", "#0000ff"],
                    "pixels": [
                        [0, 1, 1, 0],
                        [1, 2, 2, 1],
                        [1, 3, 3, 1],
                        [0, 1, 1, 0]
                    ]
                }
            }
        }

    def validate_device_params(self, action: str, params: Dict[str, Any]) -> bool:
        """Validate device operation parameters"""
        validation_rules = {
            "display_pixel_image": {
                "required": ["pixel_data", "width", "height"],
                "pixel_data": {"type": list, "description": "2D array of pixel colors"},
                "width": {"type": int, "min": 1, "max": 128},
                "height": {"type": int, "min": 1, "max": 128}
            },
            "display_gif_animation": {
                "required": ["frames", "width", "height"],
                "frames": {"type": list, "description": "Array of frame data"},
                "width": {"type": int, "min": 1, "max": 128},
                "height": {"type": int, "min": 1, "max": 128},
                "frame_delay": {"type": int, "min": 10, "max": 5000, "default": 100},
                "loop_count": {"type": int, "min": 0, "max": 1000, "default": 0}
            },
            "run_display_text": {
                "required": ["set_text"],
                "set_text": {"type": str, "min_length": 0, "max_length": 200, "description": "Text to display on screen"}
            }
        }
        
        if action not in validation_rules:
            return False
            
        rules = validation_rules[action]
        
        # Check required parameters
        for required_param in rules["required"]:
            if required_param not in params:
                raise ValueError(f"Missing required parameter: {required_param}")
        
        # Validate parameter types and values
        for param_name, param_value in params.items():
            if param_name in rules:
                rule = rules[param_name]
                
                # Type checking (handle tuple types for pixel_art)
                if "type" in rule:
                    expected_type = rule["type"]
                    if isinstance(expected_type, tuple):
                        # Multiple allowed types (for pixel_art pattern)
                        if not isinstance(param_value, expected_type):
                            type_names = [t.__name__ for t in expected_type]
                            raise ValueError(f"Parameter {param_name} type error, expected one of: {type_names}")
                    else:
                        if not isinstance(param_value, expected_type):
                            raise ValueError(f"Parameter {param_name} type error, expected {expected_type.__name__}")
                
                # Range checking for numbers
                if isinstance(param_value, int):
                    if "min" in rule and param_value < rule["min"]:
                        raise ValueError(f"Parameter {param_name} value too small, minimum: {rule['min']}")
                    if "max" in rule and param_value > rule["max"]:
                        raise ValueError(f"Parameter {param_name} value too large, maximum: {rule['max']}")
                
                # Length checking for strings
                if isinstance(param_value, str):
                    if "min_length" in rule and len(param_value) < rule["min_length"]:
                        raise ValueError(f"Parameter {param_name} too short, minimum length: {rule['min_length']}")
                    if "max_length" in rule and len(param_value) > rule["max_length"]:
                        raise ValueError(f"Parameter {param_name} too long, maximum length: {rule['max_length']}")
                    if "choices" in rule and param_value not in rule["choices"]:
                        raise ValueError(f"Parameter {param_name} invalid value, valid choices: {rule['choices']}")
        
        # Special validation for display_pixel_image
        if action == "display_pixel_image":
            pixel_data = params.get("pixel_data")
            width = params.get("width")
            height = params.get("height")
            
            if pixel_data is not None and width is not None and height is not None:
                self._validate_pixel_pattern(pixel_data, width, height)
        
        return True

    def convert_image_to_pixels(self, image_data: str, target_width: int = 16, target_height: int = 16, resize_method: str = "nearest") -> Dict[str, Any]:
        """Convert base64 image to pixel matrix"""
        try:
            # Validate parameters
            if target_width < 1 or target_width > 128:
                raise ValueError("target_width must be between 1 and 128")
            if target_height < 1 or target_height > 128:
                raise ValueError("target_height must be between 1 and 128")
            if resize_method not in ["nearest", "bilinear", "bicubic"]:
                raise ValueError("resize_method must be one of: nearest, bilinear, bicubic")
            
            # Check if PIL is available
            if not PIL_AVAILABLE:
                # Fallback: Return a simple pattern if PIL is not available
                self.logger.warning("PIL not available, using fallback pattern generation")
                return self._generate_fallback_pattern(target_width, target_height, image_data)
            
            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data)
            except Exception as e:
                raise ValueError(f"Invalid base64 image data: {str(e)}")
            
            # Open image with PIL
            try:
                image = Image.open(io.BytesIO(image_bytes))
            except Exception as e:
                raise ValueError(f"Cannot open image: {str(e)}")
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize image to target dimensions
            resize_filters = {
                "nearest": Image.NEAREST,
                "bilinear": Image.BILINEAR, 
                "bicubic": Image.BICUBIC
            }
            
            resized_image = image.resize((target_width, target_height), resize_filters[resize_method])
            
            # Convert to pixel matrix
            pixel_matrix = []
            for y in range(target_height):
                row = []
                for x in range(target_width):
                    r, g, b = resized_image.getpixel((x, y))
                    hex_color = f"#{r:02x}{g:02x}{b:02x}"
                    row.append(hex_color)
                pixel_matrix.append(row)
            
            # Get original image info
            original_size = image.size
            
            result = {
                "pixel_matrix": pixel_matrix,
                "width": target_width,
                "height": target_height,
                "original_size": {
                    "width": original_size[0],
                    "height": original_size[1]
                },
                "resize_method": resize_method,
                "total_pixels": target_width * target_height,
                "format_info": {
                    "original_mode": image.mode,
                    "converted_mode": "RGB",
                    "pixel_format": "hex_colors"
                }
            }
            
            self.logger.info(f"Successfully converted image from {original_size} to {target_width}x{target_height} pixel matrix")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to convert image to pixels: {str(e)}")
            raise

    def get_device_status(self, product_id: str, device_name: str, use_direct_credentials: bool = True) -> Dict[str, Any]:
        """Query device online status and basic information"""
        try:
            # Create IoT client with direct credentials for stdio mode
            client = self._create_iot_client_with_sts(use_direct_credentials=use_direct_credentials)
            
            # Create DescribeDevice request with complete common parameters
            req = iot_models.DescribeDeviceRequest()
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                # Add common parameters as per Tencent Cloud API documentation
                "Region": region,
                "Version": "2019-04-23"  # IoT Explorer API version
            }
            req.from_json_string(json.dumps(params))
            
            # Send request to get device status
            resp = client.DescribeDevice(req)
            
            result = {
                "status": "success",
                "product_id": product_id,
                "device_name": device_name,
                "device_status": {
                    "online": resp.Device.Status == 1,  # 1表示在线
                    "last_online_time": getattr(resp.Device, 'FirstOnlineTime', None),
                    "last_offline_time": getattr(resp.Device, 'LastOfflineTime', None),
                    "client_ip": getattr(resp.Device, 'ClientIP', None),
                    "device_cert": getattr(resp.Device, 'DeviceCert', None),
                    "device_secret": getattr(resp.Device, 'DeviceSecret', None),
                    "enable_state": getattr(resp.Device, 'EnableState', None),
                    "device_type": getattr(resp.Device, 'DeviceType', None),
                    "product_name": getattr(resp.Device, 'ProductName', None)
                },
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            self.logger.info(f"Successfully queried device status for {product_id}/{device_name}")
            self.logger.info(f"Device status: {resp}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get device status: {str(e)}")
            raise

    def send_display_text(self, product_id: str, device_name: str, text: str, use_direct_credentials: bool = True) -> Dict[str, Any]:
        """Send text to display on smart mug screen via CallDeviceActionAsync
        
        Args:
            product_id: Product ID
            device_name: Device name
            text: Text to display
            use_direct_credentials: If True, use sub-account credentials directly without STS
        """
        try:
            # 1. Handle text input (could be str or bytes)
            processed_text = None
            if isinstance(text, bytes):
                # If input is bytes, try to decode with common encodings
                for encoding in ['utf-8', 'gbk', 'gb2312', 'big5', 'latin1', 'cp1252']:
                    try:
                        processed_text = text.decode(encoding)
                        self.logger.info(f"Decoded bytes using encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if processed_text is None:
                    # If all encodings fail, use UTF-8 with error handling
                    processed_text = text.decode('utf-8', errors='ignore')
                    self.logger.warning("Failed to decode with common encodings, using UTF-8 with error handling")
            elif isinstance(text, str):
                # If input is already a string, use it directly
                processed_text = text
            else:
                raise ValueError("Text must be a string or bytes")
            
            # 2. Check and truncate text length to ensure < 200 characters
            original_length = len(processed_text)
            if len(processed_text) >= 200:
                processed_text = processed_text[:199]  # Truncate to ensure < 200
                self.logger.warning(f"Text length {original_length} exceeds 200, truncated to {len(processed_text)} characters")
            
            # 3. Ensure text is in UTF-8 format and encode to base64
            # Convert to UTF-8 bytes (handles any remaining encoding issues)
            try:
                text_utf8_bytes = processed_text.encode('utf-8')
            except UnicodeEncodeError:
                # If encoding fails, use error handling
                text_utf8_bytes = processed_text.encode('utf-8', errors='ignore')
                self.logger.warning("Some characters were ignored during UTF-8 encoding")
            
            # Base64 encode the UTF-8 bytes
            text_base64 = base64.b64encode(text_utf8_bytes).decode('utf-8')
            
            # Create IoT client with direct credentials for stdio mode
            client = self._create_iot_client_with_sts(use_direct_credentials=use_direct_credentials)
            region = os.getenv("DEFAULT_REGION", "ap-guangzhou")
            
            # 生成随机颜色对（鲜亮显眼的文本颜色和对比鲜明的背景颜色）
            text_color, bg_color = color_generator.generate_color_pair()
            
            # Prepare input parameters for device action
            # Use base64 encoded text for set_text
            input_params = {
                "set_text": text_base64,
                "set_text_count": len(processed_text),  # Use original text length (after truncation)
                "set_text_color": text_color,
                "set_text_dir": 1,
                "set_text_speed": 30,
                "set_text_bg_color": bg_color,

            }
            
            # Create CallDeviceActionAsync request
            req = iot_models.CallDeviceActionAsyncRequest()
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                "ActionId": "run_display_text",
                "InputParams": json.dumps(input_params),
                # Add common parameters as per Tencent Cloud API documentation
                "Region": region,
                "Version": "2019-04-23",  # IoT Explorer API version
            }
            
            # No token needed for direct credentials
            
            req.from_json_string(json.dumps(params))
            
            # Send request to device
            resp = client.CallDeviceActionAsync(req)
            
            result = {
                "status": "success",
                "client_token": resp.ClientToken,
                "call_status": resp.Status,
                "request_id": resp.RequestId,
                "product_id": product_id,
                "device_name": device_name,
                "action_id": "run_display_text",
                "text_info": {
                    "text": processed_text,  # Processed text (after truncation and encoding conversion)
                    "original_length": original_length if original_length != len(processed_text) else None,
                    "length": len(processed_text),
                    "max_length": 200,
                    "is_base64_encoded": True,
                    "encoding": "utf-8"
                },
                "credential_type": "direct_subaccount" if use_direct_credentials else "sts_temporary",
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            self.logger.info(f"Successfully sent display text to device {product_id}/{device_name}: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to send display text: {str(e)}")
            raise

    def _generate_fallback_pattern(self, width: int, height: int, image_data: str) -> Dict[str, Any]:
        """Generate a fallback pattern when PIL is not available"""
        # Generate a simple hash-based pattern from the image data
        import hashlib
        
        # Create a hash from the image data
        hash_obj = hashlib.md5(image_data.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Generate colors based on hash
        colors = []
        for i in range(0, len(hash_hex), 6):
            color_hex = hash_hex[i:i+6]
            if len(color_hex) == 6:
                colors.append(f"#{color_hex}")
        
        # If we don't have enough colors, repeat them
        while len(colors) < width * height:
            colors.extend(colors)
        
        # Create pixel matrix
        pixel_matrix = []
        color_index = 0
        for y in range(height):
            row = []
            for x in range(width):
                row.append(colors[color_index % len(colors)])
                color_index += 1
            pixel_matrix.append(row)
        
        return {
            "pixel_matrix": pixel_matrix,
            "width": width,
            "height": height,
            "original_size": {"width": "unknown", "height": "unknown"},
            "resize_method": "fallback_hash",
            "total_pixels": width * height,
            "format_info": {
                "original_mode": "unknown",
                "converted_mode": "hash_based",
                "pixel_format": "hex_colors"
            },
            "warning": "PIL not available, generated pattern from image hash"
        }

# Service instance
mug_service = MugService()

# FastAPI Application (Optional - only needed for HTTP mode)
# ALAYA network uses stdio mode, FastAPI is not required
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import JSONResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Note: ALAYA network uses stdio mode, FastAPI endpoints are optional
if FASTAPI_AVAILABLE:
    app = FastAPI(title="PixelMug IoT STS Service (Alaya MCP)", version="2.0.0")
    
    @app.get("/sts/issue")
    async def issue_sts_endpoint(
        pid: str = Query(..., description="Product ID"),
        dn: str = Query(..., description="Device name"),
        user_id: str = Query("default_user", description="User ID (for authorization)")
    ):
        """
        Issue Tencent Cloud IoT STS temporary access credentials
        
        Args:
            pid: Product ID
            dn: Device name  
            user_id: User ID (for authorization)
            
        Returns:
            JSON containing: tmpSecretId, tmpSecretKey, token, expiration, region
        """
        try:
            # Parameter validation
            if not pid or not dn:
                raise HTTPException(
                    status_code=400, 
                    detail="Missing parameters: pid (Product ID) and dn (Device name) are required"
                )
            
            # User authorization
            if not mug_service._authorize(user_id, pid, dn):
                raise HTTPException(
                    status_code=403,
                    detail=f"User {user_id} has no permission to access device {pid}/{dn}"
                )
            
            # Issue STS temporary credentials
            result = mug_service.issue_sts(pid, dn)
            
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "STS credentials issued successfully",
                    "data": result
                }
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except ValueError as e:
            # Parameter error or configuration error
            raise HTTPException(
                status_code=400,
                detail=f"Parameter error: {str(e)}"
            )
        except ImportError as e:
            # SDK missing
            raise HTTPException(
                status_code=500,
                detail=f"Service configuration error: {str(e)}"
            )
        except Exception as e:
            # Other server errors
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    @app.post("/pixel/send")
    async def send_pixel_image_endpoint(
        pid: str = Query(..., description="Product ID"),
        dn: str = Query(..., description="Device name"),
        image_data: str = Query(..., description="Base64 encoded image or pixel matrix JSON"),
        width: int = Query(16, description="Target width"),
        height: int = Query(16, description="Target height"),
        use_cos: bool = Query(True, description="Enable COS upload"),
        ttl_sec: int = Query(900, description="COS signed URL TTL in seconds"),
        user_id: str = Query("default_user", description="User ID (for authorization)")
    ):
        """
        Send pixel image to device via Tencent Cloud IoT
        
        Args:
            pid: Product ID
            dn: Device name
            image_data: Base64 encoded image or JSON encoded pixel matrix
            width: Target width (default: 16)
            height: Target height (default: 16)
            user_id: User ID (for authorization)
            
        Returns:
            JSON containing device response information
        """
        try:
            # Parameter validation
            if not pid or not dn or not image_data:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameters: pid, dn, and image_data are required"
                )
            
            # User authorization
            if not mug_service._authorize(user_id, pid, dn):
                raise HTTPException(
                    status_code=403,
                    detail=f"User {user_id} has no permission to access device {pid}/{dn}"
                )
            
            # Try to parse as JSON first (pixel matrix), otherwise treat as base64 image
            try:
                parsed_data = json.loads(image_data)
                image_input = parsed_data
            except json.JSONDecodeError:
                image_input = image_data
            
            # Send pixel image to device
            result = mug_service.send_pixel_image(pid, dn, image_input, width, height, use_cos, ttl_sec)
            
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "Pixel image sent successfully",
                    "data": result
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send pixel image: {str(e)}"
            )
    
    @app.post("/gif/send")
    async def send_gif_animation_endpoint(
        pid: str = Query(..., description="Product ID"),
        dn: str = Query(..., description="Device name"),
        gif_data: str = Query(..., description="Base64 encoded GIF, frame array JSON, or palette format"),
        frame_delay: int = Query(100, description="Frame delay in milliseconds"),
        loop_count: int = Query(0, description="Loop count (0 for infinite)"),
        width: int = Query(16, description="Target width"),
        height: int = Query(16, description="Target height"),
        use_cos: bool = Query(True, description="Enable COS upload"),
        ttl_sec: int = Query(900, description="COS signed URL TTL in seconds"),
        sta_port: int = Query(80, description="Port for device communication"),
        user_id: str = Query("default_user", description="User ID (for authorization)")
    ):
        """
        Send GIF pixel animation to device via Tencent Cloud IoT
        
        Args:
            pid: Product ID
            dn: Device name
            gif_data: Base64 encoded GIF, frame array JSON, or palette format
            frame_delay: Frame delay in milliseconds (default: 100)
            loop_count: Loop count, 0 for infinite (default: 0)
            width: Target width (default: 16)
            height: Target height (default: 16)
            use_cos: Enable COS upload (default: True)
            ttl_sec: COS signed URL TTL in seconds (default: 900)
            sta_port: Port for device communication (default: 80)
            user_id: User ID (for authorization)
            
        Returns:
            JSON containing device response information
        """
        try:
            # Parameter validation
            if not pid or not dn or not gif_data:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameters: pid, dn, and gif_data are required"
                )
            
            # User authorization
            if not mug_service._authorize(user_id, pid, dn):
                raise HTTPException(
                    status_code=403,
                    detail=f"User {user_id} has no permission to access device {pid}/{dn}"
                )
            
            # Try to parse as JSON first (frame array), otherwise treat as base64 GIF
            try:
                parsed_data = json.loads(gif_data)
                gif_input = parsed_data
            except json.JSONDecodeError:
                gif_input = gif_data
            
            # Send GIF animation to device
            result = mug_service.send_gif_animation(pid, dn, gif_input, frame_delay, loop_count, width, height, use_cos, ttl_sec, sta_port)
            
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "GIF animation sent successfully",
                    "data": result
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send GIF animation: {str(e)}"
            )
    
    @app.post("/text/send")
    async def send_display_text_endpoint(
        pid: str = Query(..., description="Product ID"),
        dn: str = Query(..., description="Device name"),
        text: str = Query(..., description="Text to display (max 200 characters)"),
        user_id: str = Query("default_user", description="User ID (for authorization)")
    ):
        """
        Send text to display on smart mug screen via device shadow
        
        Args:
            pid: Product ID
            dn: Device name
            text: Text to display (max 200 characters)
            user_id: User ID (for authorization)
            
        Returns:
            JSON containing device shadow response information
        """
        try:
            # Parameter validation
            if not pid or not dn or not text:
                raise HTTPException(
                    status_code=400,
                    detail="Missing required parameters: pid, dn, and text are required"
                )
            
            if len(text) > 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Text length {len(text)} exceeds maximum limit of 200 characters"
                )
            
            # User authorization
            if not mug_service._authorize(user_id, pid, dn):
                raise HTTPException(
                    status_code=403,
                    detail=f"User {user_id} has no permission to access device {pid}/{dn}"
                )
            
            # Send display text to device
            result = mug_service.send_display_text(pid, dn, text)
            
            return JSONResponse(
                status_code=200,
                content={
                    "code": 0,
                    "message": "Display text sent successfully",
                    "data": result
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send display text: {str(e)}"
            )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "mcp_pixel_mug_sts_alaya",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "tencent_cloud_sdk": TENCENT_CLOUD_AVAILABLE,
            "cos_sdk": COS_AVAILABLE,
            "iot_explorer_sdk": IOT_EXPLORER_AVAILABLE,
            "pil_available": PIL_AVAILABLE
        }
    
    @app.get("/")
    async def root():
        """Root path, return service information"""
        return {
            "service": "PixelMug IoT STS Service (Alaya MCP)",
            "version": "2.0.0",
            "description": "Tencent Cloud IoT Device Control and STS Service for Alaya Network",
            "features": [
                "STS temporary credential issuing",
                "Pixel image transmission to IoT devices with COS upload",
                "GIF animation transmission to IoT devices with COS upload",
                "Device authorization and validation",
                "COS asset management with signed URLs"
            ],
            "endpoints": {
                "issue_sts": "/sts/issue?pid=<ProductId>&dn=<DeviceName>&user_id=<UserId>",
                "send_pixel": "/pixel/send (POST)",
                "send_gif": "/gif/send (POST)",
                "send_text": "/text/send (POST)",
                "health": "/health",
                "api_docs": "/docs"
            },
            "requirements": {
                "env_vars": {
                    "IOT_ROLE_ARN": "CAM Role ARN (required)",
                    "COS_OWNER_UIN": "COS bucket owner UIN (main account or sub-account UIN that owns the bucket)",
                    "COS_BUCKET_NAME": "COS bucket name for policy (required for COS operations)",
                    "COS_REGION": "COS region (optional, default: ap-guangzhou)",
                    "TC_SECRET_ID": "Tencent Cloud SecretId (optional, can be omitted in CVM/TKE environment)",
                    "TC_SECRET_KEY": "Tencent Cloud SecretKey (optional, can be omitted in CVM/TKE environment)",
                    "DEFAULT_REGION": "Default region (optional, default: ap-guangzhou)"
                },
                "dependencies": {
                    "tencentcloud-sdk-python-sts": ">=3.0.0",
                    "tencentcloud-sdk-python-iotexplorer": ">=3.0.0",
                    "tencentcloud-sdk-python-cos": ">=5.0.0",
                    "fastapi": ">=0.68.0",
                    "Pillow": ">=8.0.0 (for image/GIF processing)"
                }
            },
            "device_actions": {
                "display_pixel_image": "Display static pixel image on device screen",
                "run_display_gif": "Display animated GIF on device screen with device model parameters (sta_file_name, sta_file_len, sta_file_url, sta_port)",
                "run_display_text": "Display text on smart mug screen via CallDeviceActionAsync"
            }
        }
else:
    print("Warning: FastAPI not installed, unable to start HTTP service")
