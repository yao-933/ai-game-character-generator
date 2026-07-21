# 🎮 AI 游戏角色生成器

> **多AI协作工作流**：口语描述 → DeepSeek Prompt优化 → Stable Diffusion 生成 → 游戏角色立绘

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange)](https://www.gradio.app/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-SDXL-green)](https://github.com/comfyanonymous/ComfyUI)

## 💡 项目动机

游戏公司每天需要大量角色原画，传统流程是：策划写需求 → 美术画草图 → 反复修改 → 定稿，一个角色可能需要数天。

我想探索的是：**能否让AI承担"初级原画师"的工作？** 策划用口语描述 → AI自动优化Prompt → 立刻出图，30秒拿到可讨论的视觉方案。

> 这个项目的灵感来自三七互娱的"小七"AI系统——我听说他们80%的2D图像由AI生成，于是自己动手实现了一个简化版管线。

## 🏗️ 技术架构

```
┌──────────────────────────────────────────────────────┐
│                  多AI协作工作流                        │
│                                                        │
│  用户口语输入("白发仙侠女剑客")                         │
│         │                                              │
│         ▼                                              │
│  ┌─────────────┐                                       │
│  │  DeepSeek   │ ← Prompt优化（文案能力）               │
│  │  优化Prompt  │   口语→专业英文提示词                   │
│  └──────┬──────┘                                       │
│         │                                              │
│         ▼                                              │
│  ┌─────────────┐                                       │
│  │ Stable      │ ← 角色生成（绘画能力）                 │
│  │ Diffusion   │   ComfyUI本地管线 / Replicate云端备降   │
│  │   SDXL      │                                       │
│  └──────┬──────┘                                       │
│         │                                              │
│         ▼                                              │
│  ┌─────────────┐                                       │
│  │  输出结果    │   角色立绘 + Prompt对比 + 优化说明      │
│  └─────────────┘                                       │
│                                                        │
│  我是架构师：搭管线、做调度、写界面                      │
└──────────────────────────────────────────────────────┘
```

## 🎨 支持的游戏风格

| 风格 | 说明 | 适用场景 |
|------|------|----------|
| 🏔️ 仙侠国风 | 水墨飘逸、古典建筑 | MMORPG、卡牌 |
| 🤖 科幻赛博 | 霓虹、机甲、未来都市 | 射击、MOBA |
| 🎌 二次元动漫 | 赛璐珞、日系美学 | 二次元卡牌 |
| 🖤 暗黑魔幻 | 哥特、魂系、重甲 | ARPG、魂Like |
| 🧸 Q版可爱 | 大头小身、明亮色彩 | 休闲放置 |
| 🎬 写实电影级 | UE5级画质、8K | 次世代3A |

## 🚀 快速开始

### 环境要求
- Python 3.10+
- NVIDIA GPU + 8GB+ VRAM（本地模式）
- 或 Replicate API Token（云端模式，无需GPU）

### 1. 克隆项目
```bash
git clone https://github.com/YOUR_USERNAME/ai-game-character-generator.git
cd ai-game-character-generator
pip install -r requirements.txt
```

### 2. 配置 API 密钥
```bash
# 注册 DeepSeek API：https://platform.deepseek.com
set DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx

# （可选）注册 Replicate：https://replicate.com
set REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxx
```

### 3. 启动本地 ComfyUI（推荐）
```bash
cd D:\ComfyUI
python main.py
# 浏览器打开 http://127.0.0.1:8188 确认启动
```

### 4. 启动角色生成器
```bash
python app.py
# 浏览器打开 http://127.0.0.1:7860
```

## 📸 效果展示

*（运行 `python app.py` 并生成后，截图放在 examples/ 目录）*

## 🛠️ 技术栈

- **Prompt优化**：DeepSeek API（`deepseek-chat`）
- **图像生成**：ComfyUI + SDXL 1.0（本地）/ Replicate API（云端）
- **Web界面**：Gradio
- **降级策略**：ComfyUI不可用时自动切换Replicate；DeepSeek不可用时使用本地模板

## 📂 项目结构

```
ai-game-character-generator/
├── app.py                 # Gradio 主界面
├── config.py              # API密钥和配置
├── prompt_optimizer.py    # DeepSeek Prompt优化模块
├── image_generator.py     # SD图像生成模块（双后端）
├── style_presets.py       # 6种游戏美术风格预设
├── requirements.txt       # 依赖
├── README.md              # 本文件
├── outputs/               # 生成的图像
└── examples/              # 展示截图
```

## 🔮 后续计划

- [ ] 接入 ControlNet 实现姿态控制
- [ ] 支持角色三视图（正面/侧面/背面）
- [ ] 批量生成 + 风格一致性检测
- [ ] 接入 ComfyUI 视频工作流 → AI视频分镜工具

## 👤 关于我

无锡太湖学院 物联网工程 大三学生

对 AI + 游戏 + 美术的交叉领域充满热情。这个项目是我"多AI协作"思路的实践——我认为未来的游戏开发不是AI取代人，而是人指挥多个AI协作。

目前正在寻找 **AI方向的游戏公司实习机会**，特别对三七互娱的"小七"AI系统感兴趣。

---

*Built with ❤️ and AI collaboration (DeepSeek + Claude Code + Stable Diffusion)*
