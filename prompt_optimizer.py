"""
Prompt 优化器 — 用 DeepSeek 将用户口语描述转化为专业 SD 提示词
面试亮点：展示"多AI协作"思路 — DeepSeek做文案，SD做画师，你是架构师
"""

import json
import requests
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL
from style_presets import STYLE_PRESETS

SYSTEM_PROMPT = """你是一位资深游戏原画概念设计师，精通 Stable Diffusion 提示词工程。

你的任务：将用户的口语化角色描述，转化为专业的 Stable Diffusion 英文提示词。

要求：
1. 用英文输出（SD对英文理解更好）
2. 提示词结构：主体描述 + 服装细节 + 姿态动作 + 背景环境 + 画风 + 画质关键词
3. 同时输出中文翻译，让用户看懂你做了什么优化
4. 输出 JSON 格式（只输出JSON，不要其他内容）

输出格式：
{
  "positive": "专业的英文positive prompt",
  "negative": "专业的英文negative prompt",
  "explanation_cn": "用中文解释你做了哪些优化，为什么这样修改",
  "tags": ["标签1", "标签2"]
}
"""


def optimize_prompt(user_input: str, style_name: str = "仙侠国风") -> dict:
    """
    用 DeepSeek 将用户的口语描述优化为专业 SD Prompt

    Args:
        user_input: 用户的原始描述（可以是中文口语）
        style_name: 风格名称，对应 STYLE_PRESETS 中的 key

    Returns:
        dict: {"positive": str, "negative": str, "explanation_cn": str, "tags": list}
    """
    # 获取风格预设
    style = STYLE_PRESETS.get(style_name, STYLE_PRESETS["仙侠国风"])

    user_message = f"""风格：{style_name}（{style['description']}）
风格参考词（附加到positive）：{style['positive_suffix']}
风格参考词（附加到negative）：{style['negative_prefix']}

用户描述：{user_input}

请将以上描述转化为专业SD提示词。"""

    try:
        response = requests.post(
            f"{DEEPSEEK_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "response_format": {"type": "json_object"},
            },
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content)

    except requests.exceptions.RequestException as e:
        print(f"[WARN] DeepSeek API 调用失败: {e}")
        # 降级方案：用模板生成基础 prompt
        return _fallback_prompt(user_input, style_name)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"[WARN] DeepSeek 返回解析失败: {e}")
        return _fallback_prompt(user_input, style_name)


def _fallback_prompt(user_input: str, style_name: str) -> dict:
    """API不可用时的本地降级方案"""
    style = STYLE_PRESETS.get(style_name, STYLE_PRESETS["仙侠国风"])
    return {
        "positive": (
            f"game character design, {user_input}, "
            f"professional concept art, 8k, highly detailed, "
            f"{style['positive_suffix']}, artstation trending"
        ),
        "negative": (
            f"bad quality, blurry, distorted, ugly, "
            f"{style['negative_prefix']}, watermark, text, signature"
        ),
        "explanation_cn": (
            "（降级模式）DeepSeek API 暂不可用，使用本地模板生成。"
            "已自动附加风格关键词和通用质量词。"
        ),
        "tags": ["降级模式", style_name],
    }
