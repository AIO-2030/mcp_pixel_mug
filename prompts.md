
### 🎯 项目名称

`mcp_pixel_mug`

### 📦 项目结构建议

```
mcp_pixel_mug
├── LICENSE
├── README.md
├── build.py
├── mcp_server.py
├── stdio_server.py
├── mug_service.py
├── requirements.txt
├── test_prepare.sh
├── test_publish.sh
└── test_help.sh
```

---

### 🚀 MCP 功能目标

本服务为 PixelMug 智能马克杯提供 MQTT 控制接口，核心能力包括：

* **prepare\_mqtt\_connection**：根据传入设备 ID，查询 IoT 云平台注册信息，返回连接参数、topic、payload 模板与认证凭据等。
* **publish\_action**：向指定 topic 主动推送操作指令（如加热/显示信息/变色），通过 AWS IoT 平台驱动 PixelMug 实体响应。

---

### 📡 支持的 method 列表（AIO JSON-RPC 标准）

#### 1. `help`

返回本服务支持的操作及接口格式

#### 2. `prepare_mqtt_connection`

```json
{
  "jsonrpc": "2.0",
  "method": "prepare_mqtt_connection",
  "params": {
    "device_id": "mug_001"
  },
  "id": 1
}
```

返回结果：

```json
{
  "result": {
    "host": "xxxx.iot.ap-northeast-1.amazonaws.com",
    "topic": "pixelmug/mug_001/cmd",
    "protocol": "mqtts",
    "port": 8883,
    "client_id": "mug_001",
    "cert": "...",  // PEM 编码证书
    "key": "...",   // PEM 编码私钥
    "payload_schema": {
      "action": "string",
      "params": {
        "temperature": "int",
        "color": "string"
      }
    }
  }
}
```

#### 3. `publish_action`

```json
{
  "jsonrpc": "2.0",
  "method": "publish_action",
  "params": {
    "device_id": "mug_001",
    "action": "heat",
    "params": {
      "temperature": 60
    }
  },
  "id": 2
}
```

返回结果：

```json
{
  "result": {
    "status": "published",
    "timestamp": "2025-08-21T20:10:00Z"
  }
}
```
生成完整的 `mug_service.py` 实现代码与 build 脚本,topic命名规范： univoice_mug_{action},设备注册由厂商按批次直接内置生产，目前按mock数据生产， MQTT连接信息也按mock生成

、、、
生成调用范例程序，从设备信息获取（用来实现蓝牙与设备通讯）到向设备下发消息

---

### 📖 用法说明（README建议摘要）


## Building Executables

1. Make the build script executable:
bash chmod +x build_exec.sh
2. Build stdio mode executable:
bash ./build_exec.sh
3. Build MCP mode executable:
bash ./build_exec.sh mcp
The executables will be created at:
- stdio mode: `dist/mcp_mug`
- MCP mode: `dist/mcp_mug`

## Testing

Run the test scripts:
bash chmod +x test_*.sh ./test_help.sh 


