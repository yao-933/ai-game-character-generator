"""
AI 游戏角色生成器 — 主应用
将用户口语描述通过 DeepSeek 优化后，由 Stable Diffusion 生成角色立绘

面试亮点：
  1. 多AI协作架构（DeepSeek + SD）
  2. ComfyUI 本地管线 + Replicate 云端备降
  3. Prompt工程可视化

运行方式：
  cd ai-game-character-generator
  python app.py
"""

import os
import gradio as gr

from config import OUTPUT_DIR
from prompt_optimizer import optimize_prompt
from image_generator import generate_image
from style_presets import STYLE_PRESETS


def create_character(
    user_description: str,
    style_name: str,
    num_images: int = 1,
    steps: int = 25,
    width: int = 1024,
    height: int = 1024,
):
    """
    核心流程：
      用户口语 → DeepSeek优化 → SD生成 → 返回结果
    """
    if not user_description.strip():
        return [], "⚠️ 请输入角色描述", "", ""

    results_gallery = []
    markdown_log = ""

    for i in range(num_images):
        # ========== 步骤1：DeepSeek 优化 Prompt ==========
        markdown_log += f"### 🎯 第 {i+1} 轮生成\n\n"
        markdown_log += "**📝 步骤1：DeepSeek Prompt 优化**\n"

        prompt_data = optimize_prompt(user_description, style_name)
        positive = prompt_data.get("positive", "")
        negative = prompt_data.get("negative", "")
        explanation = prompt_data.get("explanation_cn", "")
        tags = prompt_data.get("tags", [])

        markdown_log += f"> 用户原文：*{user_description}*\n\n"
        markdown_log += f"> 优化后的Prompt：\n```\n{positive}\n```\n\n"
        markdown_log += f"> 优化说明：{explanation}\n\n"

        # ========== 步骤2：Stable Diffusion 生成图像 ==========
        markdown_log += "**🎨 步骤2：Stable Diffusion 生成图像**\n"

        result = generate_image(
            positive_prompt=positive,
            negative_prompt=negative,
            steps=steps,
            width=width,
            height=height,
        )

        if result["success"]:
            results_gallery.append(result["image_path"])
            markdown_log += (
                f"> ✅ 生成成功 | 后端：{result['backend']} "
                f"| 种子：{result.get('seed', 'N/A')}\n\n"
            )
        else:
            markdown_log += f"> ❌ 生成失败：{result.get('error', '未知错误')}\n\n"

    # ========== 对比展示 ==========
    prompt_comparison = f"""## 🔍 Prompt 优化对比

### 用户原文
{user_description}

### 风格
{style_name} — {STYLE_PRESETS.get(style_name, {}).get('description', '')}

### DeepSeek 优化后的 Positive Prompt
```
{positive}
```

### Negative Prompt
```
{negative}
```

### 标签
{', '.join(tags) if tags else '无'}
"""

    return results_gallery, markdown_log, prompt_comparison, prompt_data.get("explanation_cn", "")


# ============================================================
# Gradio 界面
# ============================================================

with gr.Blocks(title="AI 游戏角色生成器") as demo:
    gr.Markdown("""
    # 🎮 AI 游戏角色生成器

    **多AI协作工作流**：你用口语描述角色 → **DeepSeek** 优化为专业Prompt → **Stable Diffusion** 生成角色立绘

    面试时打开这个页面，现场演示：输入 → 优化 → 出图，全程 30 秒
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 1️⃣ 描述你的角色")
            user_input = gr.Textbox(
                label="角色描述（支持中文口语）",
                placeholder="例如：一个白发的仙侠女剑客，穿着飘逸的红袍，眼神坚定，站在山巅",
                lines=3,
            )

            style_dropdown = gr.Dropdown(
                label="游戏风格",
                choices=list(STYLE_PRESETS.keys()),
                value="仙侠国风",
            )

            with gr.Row():
                num_images = gr.Slider(1, 4, value=1, step=1, label="生成数量")
                steps = gr.Slider(15, 50, value=25, step=5, label="推理步数（越多越精细）")

            with gr.Row():
                width = gr.Slider(512, 2048, value=1024, step=64, label="宽度")
                height = gr.Slider(512, 2048, value=1024, step=64, label="高度")

            generate_btn = gr.Button("🎨 生成角色", variant="primary", size="lg")

        with gr.Column(scale=2):
            gr.Markdown("### 2️⃣ 生成结果")
            gallery = gr.Gallery(
                label="角色立绘",
                columns=2,
                height=400,
            )
            gr.Markdown("### 3️⃣ 优化说明")
            explanation_box = gr.Textbox(
                label="DeepSeek 的优化解释",
                lines=2,
                interactive=False,
            )

    gr.Markdown("---")

    with gr.Row():
        log_output = gr.Markdown(
            label="生成日志",
            value="👆 输入角色描述后点击生成按钮",
        )

    with gr.Accordion("📊 Prompt 优化对比（面试展示用）", open=False):
        comparison_output = gr.Markdown("等待生成...")

    # 绑定事件
    generate_btn.click(
        fn=create_character,
        inputs=[user_input, style_dropdown, num_images, steps, width, height],
        outputs=[gallery, log_output, comparison_output, explanation_box],
    )

    # 预设示例
    gr.Examples(
        examples=[
            ["一个仙风道骨的白发老道士，手持拂尘，站在云海之上", "仙侠国风"],
            ["未来女特种兵，穿着高科技战斗服，霓虹城市背景", "科幻赛博"],
            ["日本高中生少女，校服，樱花飘落，动漫风格", "二次元动漫"],
            ["黑暗骑士，全身重甲，血色月光下站在城堡废墟前", "暗黑魔幻"],
            ["一只可爱的Q版小猫法师，戴着巫师帽，周围有魔法星星", "Q版可爱"],
        ],
        inputs=[user_input, style_dropdown],
    )


if __name__ == "__main__":
    print("=" * 60)
    print("AI Game Character Generator Starting...")
    print("=" * 60)
    print(f"Output Dir: {OUTPUT_DIR}")
    print(f"Styles: {', '.join(STYLE_PRESETS.keys())}")
    print("=" * 60)
    print("Tip: Describe your character -> Generate -> Wait for DeepSeek + SD")
    print("=" * 60)

    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        theme=gr.themes.Soft(),
        css="""
        .prompt-box textarea { font-family: 'Courier New', monospace !important; }
        """,
    )
