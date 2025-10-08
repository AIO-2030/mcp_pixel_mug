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
from typing import Dict, Any, Optional, Union, List

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
    from tencentcloud.cos import CosConfig, CosS3Client
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
                        "gif_data": "Base64 encoded GIF or frame array",
                        "frame_delay": "Delay between frames in ms (optional, default: 100)",
                        "loop_count": "Number of loops (optional, default: 0 for infinite)",
                        "target_width": "Target width (optional, default: 16)",
                        "target_height": "Target height (optional, default: 16)",
                        "use_cos": "Enable COS upload (optional, default: True)",
                        "ttl_sec": "COS signed URL TTL in seconds (optional, default: 900)"
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
                }
            ],
            "supported_actions": [
                {"action": "send_pixel_image", "description": "Send pixel image via Tencent Cloud IoT", "params": {"image_data": "Pixel data or base64 image", "width": "Image width", "height": "Image height"}},
                {"action": "send_gif_animation", "description": "Send GIF animation via Tencent Cloud IoT", "params": {"gif_data": "GIF frame data", "frame_delay": "Frame delay (ms)", "loop_count": "Loop count"}}
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
            self.logger.error(f"Failed to issue STS credentials: {str(e)}")
            raise
    
    def _get_base_credentials(self):
        """Get base credentials for initial STS call
        
        This is used only for the initial STS AssumeRole call.
        Priority: Sub-account keys > Main account keys
        """
        try:
            # Use explicit AK/SK from environment variables
            secret_id = os.getenv("TC_SECRET_ID")
            secret_key = os.getenv("TC_SECRET_KEY")
            
            if secret_id and secret_key:
                # Check if it's sub-account or main account
                account_type = self._detect_account_type(secret_id)
                self.logger.info(f"Using {account_type} credentials from environment variables - only for initial STS call")
                return credential.Credential(secret_id, secret_key)
            else:
                raise ValueError("No base credentials available for STS call. Please set TC_SECRET_ID and TC_SECRET_KEY environment variables.")
                
        except Exception as e:
            self.logger.error(f"Failed to get base credentials for STS: {str(e)}")
            raise ValueError("Unable to get base credentials for ALAYA network STS call")
    
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
    
    def _get_tencent_credentials(self, sts_credentials: Dict[str, Any] = None):
        """Get Tencent Cloud credentials for ALAYA network operations
        
        In ALAYA network, we should use STS temporary credentials for all operations
        """
        try:
            if sts_credentials:
                # Use STS temporary credentials (preferred for ALAYA network)
                self.logger.info("Using STS temporary credentials for ALAYA network operations")
                return credential.Credential(
                    sts_credentials["tmpSecretId"],
                    sts_credentials["tmpSecretKey"],
                    sts_credentials["token"]
                )
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
    

    def _create_iot_client_with_sts(self, sts_credentials: Dict[str, Any]):
        """Create Tencent Cloud IoT Explorer client with STS temporary credentials"""
        try:
            # Check if IoT Explorer SDK is available
            if not IOT_EXPLORER_AVAILABLE:
                raise ImportError("Tencent Cloud IoT Explorer SDK not installed, please install tencentcloud-sdk-python-iotexplorer")
            
            # Create credentials with STS temporary credentials
            cred = credential.Credential(
                sts_credentials["tmpSecretId"],
                sts_credentials["tmpSecretKey"],
                sts_credentials["token"]
            )
            
            # Get region from STS credentials
            region = sts_credentials["region"]
            
            # Configure HTTP and Client Profile
            httpProfile = HttpProfile()
            httpProfile.endpoint = "iotexplorer.tencentcloudapi.com"
            
            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            
            # Create IoT Explorer client with STS credentials
            client = iotexplorer_client.IotexplorerClient(cred, region, clientProfile)
            
            self.logger.info(f"Successfully created IoT Explorer client with STS credentials for region {region}")
            return client
            
        except Exception as e:
            self.logger.error(f"Failed to create IoT Explorer client with STS: {str(e)}")
            raise

    def _push_asset_to_cos(self, product_id: str, device_name: str, asset_data: bytes, 
                          asset_kind: str, asset_id: str, metadata: Dict[str, Any], 
                          ttl_sec: int = 300) -> Dict[str, Any]:
        """Push asset to COS and get signed URL with proper key pattern and metadata"""
        try:
            if not COS_AVAILABLE:
                raise ImportError("Tencent Cloud COS SDK not installed, please install tencentcloud-sdk-python-cos")
            
            # 1. Get STS credentials
            sts_info = self.issue_sts(product_id, device_name)
            
            # 2. Generate COS client
            cos_config = CosConfig(
                Region=sts_info["region"],
                SecretId=sts_info["tmpSecretId"],
                SecretKey=sts_info["tmpSecretKey"],
                Token=sts_info["token"],
                Scheme="https"
            )
            cos_client = CosS3Client(cos_config)
            
            # 3. Generate SHA256 hash and key with new pattern
            sha256 = hashlib.sha256(asset_data).hexdigest()
            sha8 = sha256[:8]  # First 8 characters of SHA256
            current_date = datetime.datetime.utcnow().strftime("%Y%m")
            
            # Key pattern: pmug/{deviceName}/{YYYYMM}/{assetId}-{sha8}.{ext}
            if asset_kind == "pixel-json":
                ext = "json"
            elif asset_kind == "gif":
                ext = "gif"
            else:
                ext = "json"
            
            key = f"pmug/{device_name}/{current_date}/{asset_id}-{sha8}.{ext}"
            
            # 4. Set Content-Type based on asset kind
            content_type = "application/vnd.pmug.pixel+json" if asset_kind == "pixel-json" else "image/gif"
            
            # 5. Prepare metadata
            cos_metadata = {
                "x-cos-meta-sha256": sha256,
                "x-cos-meta-width": str(metadata.get("width", 0)),
                "x-cos-meta-height": str(metadata.get("height", 0)),
                "x-cos-meta-frames": str(metadata.get("frame_count", 1)),
                "x-cos-meta-asset-id": asset_id,
                "x-cos-meta-device-name": device_name,
                "x-cos-meta-product-id": product_id
            }
            
            # 6. Upload to COS with metadata and cache headers
            bucket_name = os.getenv("COS_BUCKET", "pixelmug-assets")
            cos_client.put_object(
                Bucket=bucket_name,
                Body=asset_data,
                Key=key,
                ContentType=content_type,
                Metadata=cos_metadata,
                CacheControl="public, max-age=31536000, immutable",
                StorageClass="STANDARD"
            )
            
            # 7. Generate signed URL
            get_url = cos_client.get_presigned_url(
                Method="GET",
                Bucket=bucket_name,
                Key=key,
                Expired=ttl_sec
            )
            
            # 8. Calculate expiration timestamp
            expires_at = int((datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl_sec)).timestamp())
            
            return {
                "key": key,
                "sha256": sha256,
                "sha8": sha8,
                "assetId": asset_id,
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
                        use_cos: bool = True, ttl_sec: int = 900) -> Dict[str, Any]:
        """Send pixel image to device via Tencent Cloud IoT Explorer with optional COS upload"""
        try:
            # Get STS credentials for device access
            sts_credentials = self.issue_sts(product_id, device_name)
            
            # Create IoT client with STS credentials
            client = self._create_iot_client_with_sts(sts_credentials)
            
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
            
            # Prepare asset data for COS upload if enabled
            asset_info = None
            if use_cos:
                try:
                    # Generate asset ID
                    asset_id = f"asset_{int(datetime.datetime.utcnow().timestamp())}"
                    
                    # Convert pixel matrix to JSON bytes
                    asset_data = json.dumps({
                        "kind": "pixel-json",
                        "width": width,
                        "height": height,
                        "pixel_data": pixel_matrix,
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                    }).encode('utf-8')
                    
                    # Prepare metadata
                    metadata = {
                        "width": width,
                        "height": height,
                        "frame_count": 1
                    }
                    
                    # Upload to COS
                    asset_info = self._push_asset_to_cos(product_id, device_name, asset_data, "pixel-json", asset_id, metadata, ttl_sec)
                    self.logger.info(f"Successfully uploaded pixel image to COS: {asset_info['key']}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload to COS, falling back to direct transmission: {str(e)}")
                    use_cos = False
            
            # Prepare input parameters for IoT device action
            input_params = {
                "action": "display_pixel_image",
                "width": width,
                "height": height,
                "pixel_data": pixel_matrix,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            # Add COS asset info if available - use new payload format
            if use_cos and asset_info:
                # Generate nonce for security
                nonce = hashlib.md5(f"{asset_info['assetId']}{datetime.datetime.utcnow().timestamp()}".encode()).hexdigest()[:8]
                current_ts = int(datetime.datetime.utcnow().timestamp())
                
                input_params.update({
                    "method": "control.push_asset",
                    "clientToken": f"cmd_{current_ts}",
                    "params": {
                        "assetId": asset_info["assetId"],
                        "type": asset_info["contentType"],
                        "url": asset_info["url"],
                        "bytes": asset_info["bytes"],
                        "hash": f"sha256:{asset_info['sha256']}",
                        "width": asset_info["width"],
                        "height": asset_info["height"],
                        "loop": False,
                        "expiresAt": asset_info["expiresAt"],
                        "nonce": nonce,
                        "ts": current_ts
                    },
                    "delivery_method": "cos"
                })
            else:
                input_params["delivery_method"] = "direct"
            
            # Create CallDeviceActionAsync request with complete common parameters
            req = iot_models.CallDeviceActionAsyncRequest()
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                "ActionId": "display_pixel_image",
                "InputParams": json.dumps(input_params),
                # Add common parameters as per Tencent Cloud API documentation
                "Region": sts_credentials["region"],
                "Version": "2019-04-23",  # IoT Explorer API version
                "Token": sts_credentials["token"]  # STS temporary token
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
                "action_id": "display_pixel_image",
                "image_info": {
                    "width": width,
                    "height": height,
                    "total_pixels": width * height
                },
                "delivery_method": "cos" if use_cos else "direct",
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

    def send_gif_animation(self, product_id: str, device_name: str, gif_data: Union[str, List, Dict], 
                          frame_delay: int = 100, loop_count: int = 0, 
                          target_width: int = 16, target_height: int = 16,
                          use_cos: bool = True, ttl_sec: int = 900) -> Dict[str, Any]:
        """Send GIF pixel animation to device via Tencent Cloud IoT Explorer with optional COS upload"""
        try:
            # Get STS credentials for device access
            sts_credentials = self.issue_sts(product_id, device_name)
            
            # Create IoT client with STS credentials
            client = self._create_iot_client_with_sts(sts_credentials)
            
            # Process GIF data
            if isinstance(gif_data, str):
                # If it's base64 encoded GIF, process to frames
                frames = self._process_gif_to_frames(gif_data, target_width, target_height)
            elif isinstance(gif_data, dict) and "frames" in gif_data:
                # If it's palette-based GIF format
                frames = self._process_palette_gif_animation(gif_data, target_width, target_height)
            else:
                # If it's already frame array
                frames = gif_data
                
            # Validate frames
            if not frames:
                raise ValueError("No frames found in GIF data")
            
            # Prepare asset data for COS upload if enabled
            asset_info = None
            if use_cos:
                try:
                    # Generate asset ID
                    asset_id = f"asset_{int(datetime.datetime.utcnow().timestamp())}"
                    
                    # Convert frames to JSON bytes
                    asset_data = json.dumps({
                        "kind": "gif",
                        "frame_count": len(frames),
                        "frames": frames,
                        "frame_delay": frame_delay,
                        "loop_count": loop_count,
                        "width": target_width,
                        "height": target_height,
                        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
                    }).encode('utf-8')
                    
                    # Prepare metadata
                    metadata = {
                        "width": target_width,
                        "height": target_height,
                        "frame_count": len(frames)
                    }
                    
                    # Upload to COS
                    asset_info = self._push_asset_to_cos(product_id, device_name, asset_data, "gif", asset_id, metadata, ttl_sec)
                    self.logger.info(f"Successfully uploaded GIF animation to COS: {asset_info['key']}")
                except Exception as e:
                    self.logger.warning(f"Failed to upload to COS, falling back to direct transmission: {str(e)}")
                    use_cos = False
                
            # Prepare input parameters for IoT device action
            input_params = {
                "action": "display_gif_animation",
                "frame_count": len(frames),
                "frames": frames,
                "frame_delay": frame_delay,
                "loop_count": loop_count,
                "width": target_width,
                "height": target_height,
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            # Add COS asset info if available - use new payload format
            if use_cos and asset_info:
                # Generate nonce for security
                nonce = hashlib.md5(f"{asset_info['assetId']}{datetime.datetime.utcnow().timestamp()}".encode()).hexdigest()[:8]
                current_ts = int(datetime.datetime.utcnow().timestamp())
                
                input_params.update({
                    "method": "control.push_asset",
                    "clientToken": f"cmd_{current_ts}",
                    "params": {
                        "assetId": asset_info["assetId"],
                        "type": asset_info["contentType"],
                        "url": asset_info["url"],
                        "bytes": asset_info["bytes"],
                        "hash": f"sha256:{asset_info['sha256']}",
                        "width": asset_info["width"],
                        "height": asset_info["height"],
                        "loop": loop_count != 0,
                        "expiresAt": asset_info["expiresAt"],
                        "nonce": nonce,
                        "ts": current_ts
                    },
                    "delivery_method": "cos"
                })
            else:
                input_params["delivery_method"] = "direct"
            
            # Create CallDeviceActionAsync request with complete common parameters
            req = iot_models.CallDeviceActionAsyncRequest()
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                "ActionId": "display_gif_animation",
                "InputParams": json.dumps(input_params),
                # Add common parameters as per Tencent Cloud API documentation
                "Region": sts_credentials["region"],
                "Version": "2019-04-23",  # IoT Explorer API version
                "Token": sts_credentials["token"]  # STS temporary token
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
                "action_id": "display_gif_animation",
                "animation_info": {
                    "frame_count": len(frames),
                    "frame_delay": frame_delay,
                    "loop_count": loop_count,
                    "width": target_width,
                    "height": target_height,
                    "total_pixels": target_width * target_height
                },
                "delivery_method": "cos" if use_cos else "direct",
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

    def get_device_status(self, product_id: str, device_name: str) -> Dict[str, Any]:
        """Query device online status and basic information"""
        try:
            # Get STS credentials for device access
            sts_credentials = self.issue_sts(product_id, device_name)
            
            # Create IoT client with STS credentials
            client = self._create_iot_client_with_sts(sts_credentials)
            
            # Create GetDeviceStatus request with complete common parameters
            req = iot_models.GetDeviceStatusRequest()
            params = {
                "ProductId": product_id,
                "DeviceName": device_name,
                # Add common parameters as per Tencent Cloud API documentation
                "Region": sts_credentials["region"],
                "Version": "2019-04-23",  # IoT Explorer API version
                "Token": sts_credentials["token"]  # STS temporary token
            }
            req.from_json_string(json.dumps(params))
            
            # Send request to get device status
            resp = client.GetDeviceStatus(req)
            
            result = {
                "status": "success",
                "product_id": product_id,
                "device_name": device_name,
                "device_status": {
                    "online": resp.Online,
                    "last_online_time": resp.LastOnlineTime,
                    "last_offline_time": resp.LastOfflineTime,
                    "client_ip": resp.ClientIP,
                    "device_cert": resp.DeviceCert,
                    "device_secret": resp.DeviceSecret
                },
                "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
            }
            
            self.logger.info(f"Successfully queried device status for {product_id}/{device_name}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get device status: {str(e)}")
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
        gif_data: str = Query(..., description="Base64 encoded GIF or frame array JSON"),
        frame_delay: int = Query(100, description="Frame delay in milliseconds"),
        loop_count: int = Query(0, description="Loop count (0 for infinite)"),
        width: int = Query(16, description="Target width"),
        height: int = Query(16, description="Target height"),
        use_cos: bool = Query(True, description="Enable COS upload"),
        ttl_sec: int = Query(900, description="COS signed URL TTL in seconds"),
        user_id: str = Query("default_user", description="User ID (for authorization)")
    ):
        """
        Send GIF pixel animation to device via Tencent Cloud IoT
        
        Args:
            pid: Product ID
            dn: Device name
            gif_data: Base64 encoded GIF or JSON encoded frame array
            frame_delay: Frame delay in milliseconds (default: 100)
            loop_count: Loop count, 0 for infinite (default: 0)
            width: Target width (default: 16)
            height: Target height (default: 16)
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
            result = mug_service.send_gif_animation(pid, dn, gif_input, frame_delay, loop_count, width, height, use_cos, ttl_sec)
            
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
                "health": "/health",
                "api_docs": "/docs"
            },
            "requirements": {
                "env_vars": {
                    "IOT_ROLE_ARN": "CAM Role ARN (required)",
                    "COS_BUCKET": "COS bucket name (optional, default: pixelmug-assets)",
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
                "display_gif_animation": "Display animated GIF on device screen"
            }
        }
else:
    print("Warning: FastAPI not installed, unable to start HTTP service")
