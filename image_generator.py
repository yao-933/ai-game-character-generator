"""
图像生成器 — 调用 Stable Diffusion 生成游戏角色
支持两种后端：本地 ComfyUI API / 云端 Replicate API
面试亮点：展示多后端切换的工程思维
"""

import json
import time
import uuid
import os
import requests
from config import COMFYUI_BASE_URL, REPLICATE_API_TOKEN, IMAGE_GEN_MODE, OUTPUT_DIR


# ============================================================
# ComfyUI 后端（本地 RTX 4060）
# ============================================================

# ComfyUI SDXL 基础工作流 — 这是面试时能讲的核心
COMFYUI_SDXL_WORKFLOW = {
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 7,
            "denoise": 1,
            "model": ["4", 0],
            "positive": ["6", 0],
            "negative": ["7", 0],
            "latent_image": ["5", 0],
            "seed": 42,
            "steps": 25,
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {"width": 1024, "height": 1024, "batch_size": 1}
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "beautiful scenery",
            "clip": ["4", 1]
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "text": "bad quality, blurry",
            "clip": ["4", 1]
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": ["3", 0],
            "vae": ["4", 2]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "character",
            "images": ["8", 0]
        }
    },
}


def generate_via_comfyui(positive_prompt: str, negative_prompt: str,
                         seed: int = None, steps: int = 25,
                         width: int = 1024, height: int = 1024) -> dict:
    """
    通过 ComfyUI API 生成图像

    面试要点：理解 ComfyUI 的节点流管道 —
    Load Checkpoint → CLIP Encode(+/-) → KSampler → VAE Decode → Save Image
    """
    import random
    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    # 1. 加载工作流模板
    workflow = json.loads(json.dumps(COMFYUI_SDXL_WORKFLOW))

    # 2. 注入 Prompt 参数
    workflow["6"]["inputs"]["text"] = positive_prompt
    workflow["7"]["inputs"]["text"] = negative_prompt
    workflow["3"]["inputs"]["seed"] = seed
    workflow["3"]["inputs"]["steps"] = steps
    workflow["5"]["inputs"]["width"] = width
    workflow["5"]["inputs"]["height"] = height

    prompt_id = str(uuid.uuid4())
    workflow["9"]["inputs"]["filename_prefix"] = prompt_id

    try:
        # 3. 提交工作流到 ComfyUI
        resp = requests.post(
            f"{COMFYUI_BASE_URL}/prompt",
            json={"prompt": workflow, "client_id": prompt_id},
            timeout=10,
        )
        resp.raise_for_status()
        prompt_result = resp.json()

        if "prompt_id" not in prompt_result:
            raise RuntimeError(f"ComfyUI 返回异常: {prompt_result}")

        prompt_id = prompt_result["prompt_id"]

        # 4. 轮询等待生成完成
        image_data = _wait_for_comfyui_result(prompt_id)

        # 5. 保存图像
        output_path = os.path.join(OUTPUT_DIR, f"{prompt_id}.png")
        with open(output_path, "wb") as f:
            f.write(image_data)

        return {
            "success": True,
            "backend": "comfyui",
            "image_path": output_path,
            "seed": seed,
            "prompt_id": prompt_id,
        }

    except requests.exceptions.RequestException as e:
        print(f"[WARN] ComfyUI 连接失败: {e}")
        return {
            "success": False,
            "backend": "comfyui",
            "error": f"ComfyUI 不可用，请确认已启动: {str(e)}",
        }


def _wait_for_comfyui_result(prompt_id: str, timeout: int = 120) -> bytes:
    """轮询 ComfyUI 的执行结果"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            # 检查执行状态
            history_resp = requests.get(
                f"{COMFYUI_BASE_URL}/history/{prompt_id}", timeout=5
            )
            history_resp.raise_for_status()
            history = history_resp.json()

            if prompt_id in history:
                outputs = history[prompt_id]["outputs"]
                # 找到 SaveImage 节点的输出
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        image_info = node_output["images"][0]
                        filename = image_info["filename"]
                        subfolder = image_info.get("subfolder", "")

                        # 获取图像数据
                        img_url = f"{COMFYUI_BASE_URL}/view"
                        params = {"filename": filename, "subfolder": subfolder, "type": "output"}
                        img_resp = requests.get(img_url, params=params, timeout=10)
                        img_resp.raise_for_status()
                        return img_resp.content

        except requests.exceptions.RequestException:
            pass

        time.sleep(1)

    raise TimeoutError(f"ComfyUI 生成超时 ({timeout}s)")


# ============================================================
# Replicate 后端（云端备选）
# ============================================================

def generate_via_replicate(positive_prompt: str, negative_prompt: str,
                           seed: int = None, steps: int = 25,
                           width: int = 1024, height: int = 1024) -> dict:
    """通过 Replicate API 生成图像（云端SDXL）"""
    import random
    import replicate

    if seed is None:
        seed = random.randint(0, 2**32 - 1)

    try:
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": positive_prompt,
                "negative_prompt": negative_prompt,
                "width": width,
                "height": height,
                "num_outputs": 1,
                "num_inference_steps": steps,
                "seed": seed,
            },
        )

        # Replicate 返回的是图片 URL 列表
        if output and len(output) > 0:
            image_url = output[0]
            # 下载到本地
            img_data = requests.get(image_url, timeout=30).content
            output_path = os.path.join(OUTPUT_DIR, f"replicate_{seed}.png")
            with open(output_path, "wb") as f:
                f.write(img_data)

            return {
                "success": True,
                "backend": "replicate",
                "image_path": output_path,
                "seed": seed,
                "image_url": image_url,
            }

    except Exception as e:
        print(f"[WARN] Replicate API 调用失败: {e}")
        return {
            "success": False,
            "backend": "replicate",
            "error": str(e),
        }


# ============================================================
# 统一接口
# ============================================================

def generate_image(positive_prompt: str, negative_prompt: str,
                   seed: int = None, steps: int = 25,
                   width: int = 1024, height: int = 1024,
                   mode: str = None) -> dict:
    """
    统一的图像生成接口，自动选择后端

    Returns:
        dict: {"success": bool, "image_path": str, ...}
    """
    if mode is None:
        mode = IMAGE_GEN_MODE

    if mode == "comfyui":
        result = generate_via_comfyui(
            positive_prompt, negative_prompt, seed, steps, width, height
        )
        if result["success"]:
            return result
        # ComfyUI 失败，降级到 Replicate
        print("[INFO] ComfyUI 不可用，降级到 Replicate API")
        mode = "replicate"

    if mode == "replicate":
        return generate_via_replicate(
            positive_prompt, negative_prompt, seed, steps, width, height
        )

    return {"success": False, "error": "无可用后端"}
