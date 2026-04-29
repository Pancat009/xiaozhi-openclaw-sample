from mcp.server.fastmcp import FastMCP
import requests
import logging
import os
import time
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

mcp = FastMCP("OpenClaw")

@mcp.tool()
def ask_openclaw(instruction: str) -> str:
    """
    【最重要触发规则】
    用户只要提到以下任意关键词，就必须立即、无条件调用 ask_openclaw 这个工具：

    龙虾、小龙虾、OpenClaw、openclaw、给龙虾、问龙虾、让龙虾、叫龙虾、找龙虾、龙虾帮我

    注意：
    - 飞书、QQ、微信、企业微信等只是龙虾的发送渠道之一
    - 用户说“通过飞书”“发到QQ”“用微信发”等时，也要调用本工具，由龙虾自己决定如何处理
    - instruction 必须是用户说的**完整原话**，一个字都不允许修改或省略

    作用：把用户指令完整转发给本地 OpenClaw 智能体执行。
    """
    logging.info(f"收到小智云端任务 → 龙虾: {instruction}")
    
    token = os.getenv("OPENCLAW_GATEWAY_TOKEN", 
                     "<你的Token>")  # 请在环境变量中设置 OPENCLAW_GATEWAY_TOKEN，或者直接替换成你的 Token
    
    try:
        # 立即返回提示，防止小智判定超时
        prompt_reply = "好的，已转给龙虾处理 🦞\n它正在思考，请稍等几秒，我会把它的回复告诉你。"
        logging.info("已立即返回提示给小智，避免超时")
        
        # 后台异步调用 OpenClaw（真正执行任务）
        threading.Thread(
            target=call_openclaw_async,
            args=(instruction, token),
            daemon=True
        ).start()
        
        return prompt_reply
        
    except Exception as e:
        logging.error(f"ask_openclaw 工具异常: {str(e)}")
        return "转给龙虾时发生错误，请稍后再试。"


def call_openclaw_async(instruction: str, token: str):
    """后台真正调用 OpenClaw，让龙虾处理（包括飞书、QQ、微信等渠道）"""
    try:
        response = requests.post(
            "http://127.0.0.1:18789/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            json={
                "model": "openclaw",
                "messages": [{"role": "user", "content": instruction}],
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 1500
            },
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            
            if content:
                logging.info(f"龙虾实际回复成功（长度 {len(content)}）: {content[:120]}...")
                # TODO: 未来可以在这里把龙虾的回复再推送回小智（需要额外机制）
            else:
                logging.warning("龙虾返回了空回复")
        else:
            logging.error(f"OpenClaw 返回 HTTP 错误: {response.status_code} - {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        logging.error("调用 OpenClaw 超时")
    except Exception as e:
        logging.error(f"后台调用 OpenClaw 失败: {str(e)}", exc_info=True)


if __name__ == "__main__":
    mcp.run(transport="stdio")