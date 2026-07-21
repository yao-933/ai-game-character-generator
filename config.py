"""
配置文件 — 管理 API 密钥和服务地址
面试亮点：展示对配置管理的理解，敏感信息用环境变量
"""

import os

# 自动加载 .env 文件（如果存在）
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key not in os.environ:
                    os.environ[key] = val

# ============================================
# DeepSeek API — 用于 Prompt 优化（"多AI协作"核心）
# 注册地址：https://platform.deepseek.com
# ============================================
# 复制你的 DeepSeek API Key 替换下面这行（注册地址：https://platform.deepseek.com）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "your-deepseek-api-key-here")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# ============================================
# ComfyUI — 本地 Stable Diffusion 服务
# 启动方式：cd D:\ComfyUI && python main.py
# ============================================
COMFYUI_BASE_URL = "http://127.0.0.1:8188"

# ============================================
# Replicate API — 云端 SD 备选方案
# 注册地址：https://replicate.com
# ============================================
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "your-replicate-token-here")

# 图像生成模式："comfyui" 或 "replicate"
IMAGE_GEN_MODE = "comfyui"

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
