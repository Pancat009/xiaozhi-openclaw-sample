# xiaozhi-openclaw-bridge

把 [小智 AI 音箱](https://xiaozhi.me/) 通过 MCP 协议接入本地 [OpenClaw（龙虾）](https://github.com/openclaw/openclaw) 智能体的桥接工具。

对小智说一句"让龙虾帮我发个飞书消息"，指令就会被转发到本地 OpenClaw 去自动处理飞书 / QQ / 微信等渠道任务。

📺 **演示视频**：[B 站观看](https://www.bilibili.com/video/BV1KudSBdEir)

## 工作原理

```
小智音箱 (云端)
    ↓  WebSocket
xiaozhi_tunnel.py  (MCP 隧道)
    ↓  stdio
openclaw_agent.py  (MCP Server, 暴露 ask_openclaw 工具)
    ↓  HTTP
本地 OpenClaw 网关 (127.0.0.1:18789)
    ↓
飞书 / QQ / 微信 / ...
```

- `xiaozhi_tunnel.py` — 维持与小智云端的 WebSocket 长连接，把消息桥接到本地 MCP Server 的 stdio。带断线指数退避重连。
- `openclaw_agent.py` — FastMCP Server，暴露 `ask_openclaw` 工具。命中触发词后异步调用本地 OpenClaw HTTP 接口，并立刻返回占位回复给小智，避免超时。

## 触发关键词

只要你对小智说出以下任一关键词，就会触发转发：

> 龙虾、小龙虾、OpenClaw、给龙虾、问龙虾、让龙虾、叫龙虾、找龙虾、龙虾帮我

例：
- "让龙虾通过飞书提醒我下午三点开会"
- "叫龙虾发个微信给老王说我晚到十分钟"

## 快速开始

### 1. 安装依赖

```bash
pip install mcp websockets requests python-dotenv
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的小智 MCP 接入地址：

```
MCP_ENDPOINT=wss://your-xiaozhi-mcp-endpoint
```

如果本地 OpenClaw 网关启用了 token 鉴权，再设置：

```bash
# Linux / macOS
export OPENCLAW_GATEWAY_TOKEN=your_token

# Windows PowerShell
$env:OPENCLAW_GATEWAY_TOKEN = "your_token"
```

### 3. 启动本地 OpenClaw

确保 OpenClaw 网关已在 `http://127.0.0.1:18789` 运行。

### 4. 启动桥接

```bash
python xiaozhi_tunnel.py openclaw_agent.py
```

看到 `Successfully connected to WebSocket server` 即接入成功，可以对小智说话了。

## 配置文件（可选）

`xiaozhi_tunnel.py` 支持通过 `mcp_config.json` 同时挂载多个 MCP Server：

```json
{
  "mcpServers": {
    "openclaw": {
      "type": "stdio",
      "command": "python",
      "args": ["openclaw_agent.py"]
    }
  }
}
```

支持的类型：`stdio` / `sse` / `http` / `streamablehttp`。配置文件路径优先读取 `$MCP_CONFIG`，否则取当前目录下的 `mcp_config.json`。

## 已知限制

- 龙虾的真实回复目前仅在终端日志可见，尚未推送回小智（受小智 MCP 工具同步返回模型所限）。

## License

MIT
