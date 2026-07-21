# 🎮 AI Game Character Generator

> **Multi-AI Collaboration Pipeline**: Natural language → DeepSeek Prompt Optimization → Stable Diffusion → Game Character Art

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://www.python.org/)
[![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange?logo=gradio)](https://www.gradio.app/)
[![ComfyUI](https://img.shields.io/badge/ComfyUI-SDXL-green)](https://github.com/comfyanonymous/ComfyUI)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-API-purple)](https://platform.deepseek.com)
[![License](https://img.shields.io/badge/License-MIT-lightgrey)](LICENSE)

---

## 💡 Why This Project

Game studios produce hundreds of character concepts daily. The traditional pipeline — designer writes brief → artist sketches → rounds of revision → final concept — can take **days per character**.

**What if AI could serve as a "junior concept artist"?**

This project explores exactly that: a designer types "white-haired female warrior in red robes" in plain language → DeepSeek optimizes it into a professional-grade prompt → Stable Diffusion generates the artwork → **30 seconds from idea to visual prototype**.

> Inspired by 37 Interactive's (三七互娱) "Xiao Qi" AI system, which reportedly handles **80% of their 2D asset production**. This is a micro-scale implementation of the same idea.

---

## 🏗️ Implementation Steps

We built this project in 5 steps over 2 days, from empty folder to working tool. Each step adds one layer of the pipeline.

---

### Step 1: ComfyUI Local Deployment — "Set Up the Artist's Studio"

**Purpose**: Before writing any code, we need a working Stable Diffusion backend. **ComfyUI** is a node-based SD workflow editor — think of it as the "Photoshop engine" that will draw our characters. Deploying it locally means zero API cost and full control over the generation pipeline.

**What we did**:
- Cloned ComfyUI from GitHub and installed dependencies including **PyTorch** with **CUDA** (Compute Unified Device Architecture / 统一计算设备架构) support for GPU acceleration
- Downloaded only the **SDXL 1.0** model (6.5 GB) — one model, enough for high-quality character art at 1024×1024. Skipped the typical "all-in-one" package that bloats to 500+ GB
- Fixed the PyTorch version mismatch — the default `pip install` pulls the CPU-only build, which can't use the GPU. Replaced with `torch-2.11.0+cu128` for CUDA 12.8 compatibility
- Verified the pipeline: submitted a test image generation via ComfyUI's API → confirmation that the RTX 4060 (8GB VRAM) can generate one 1024×1024 image in ~15 seconds

**Key terms**:
- **ComfyUI**: A node-based interface for Stable Diffusion. Each node is one step in the pipeline (load model / encode text / sample / decode). Nodes connect like circuit components
- **SDXL** (Stable Diffusion XL): The "XL" variant of Stable Diffusion. Native resolution 1024×1024 (vs SD 1.5's 512×512). Better at details, composition, and text rendering
- **CUDA** (Compute Unified Device Architecture): Nvidia's parallel computing platform. AI models run on CUDA cores — without CUDA, PyTorch falls back to CPU which is 10-50× slower
- **VRAM** (Video Random Access Memory / 显存): GPU's dedicated memory. SDXL needs ~6-7 GB to generate one 1024×1024 image. RTX 4060 has 8 GB

---

### Step 2: Prompt Optimizer — "Teach AI to Speak Artist"

**Purpose**: Stable Diffusion speaks "prompt language" — dense English descriptions with specific art keywords. A designer typing "白发女剑客" in Chinese won't get good results. This module bridges that gap: it takes casual natural language and translates it into professional SD prompts using **DeepSeek's LLM** (Large Language Model / 大语言模型).

**What we did**:
- Designed a system prompt that role-plays as a game concept artist fluent in SD prompt engineering
- Built the optimization function: user's casual Chinese → DeepSeek API → structured JSON with `positive` (what to draw), `negative` (what to avoid), `explanation_cn` (human-readable rationale in Chinese), and `tags` (categorization)
- Added a fallback module: if the API is unreachable, a local template stitches the user's description with style-specific prompt suffixes — graceful degradation instead of crashing
- Used DeepSeek's JSON mode (`response_format: json_object`) to guarantee structured output — no regex parsing of free-text responses

**Key file**: [`prompt_optimizer.py`](prompt_optimizer.py)

**Key terms**:
- **Prompt** (提示词): The text instruction given to Stable Diffusion. A good prompt contains: subject description + style keywords + quality keywords + composition hints
- **Negative Prompt** (负面提示词): What the model should *avoid*. Standard negatives: "bad quality, blurry, distorted, watermark, text"
- **LLM** (Large Language Model / 大语言模型): A neural network trained on massive text data. DeepSeek is one; GPT-4, Claude, and Gemini are others

---

### Step 3: Style Presets — "Encode Game Industry Knowledge"

**Purpose**: A character generator that only produces one "generic" style isn't useful for a game studio. Games span genres — a souls-like needs dark fantasy; a gacha game needs anime. This module encodes 6 distinct visual styles as reusable prompt templates, mapping each to its target game genre.

**What we did**:
- Defined 6 style presets, each with: `positive_suffix` (appended to every prompt to define the style direction) and `negative_prefix` (prepended to negatives to suppress conflicting styles)
- Mapped each style to its target game type — showing understanding of the industry (e.g., 暗黑魔幻 = ARPG/魂Like, Q版可爱 = 休闲放置)
- Stored presets as a Python dict in a standalone file — adding a 7th style is one dictionary entry, no code changes needed

**Key file**: [`style_presets.py`](style_presets.py)

**Preset list**:
| Style | Game Types | Visual Direction |
|-------|-----------|------------------|
| 仙侠国风 | MMORPG, Card | Ink wash, flowing silk, ancient architecture |
| 科幻赛博 | FPS, MOBA | Neon, holographic UI, high-tech armor |
| 二次元动漫 | Gacha, VN | Cel shading, clean lineart, vibrant colors |
| 暗黑魔幻 | ARPG, Souls-like | Gothic, heavy armor, dramatic shadows |
| Q版可爱 | Casual, Idle | Chibi proportions, bright pastels |
| 写实电影级 | AAA, Next-gen | Photorealistic, UE5-quality, 8K |

---

### Step 4: ComfyUI API Integration — "Wire the Pipeline"

**Purpose**: Connect the prompt optimizer to the image generator. This module sends prompts to the local ComfyUI server and retrieves the generated images — translating our abstract workflow (text → prompt → image) into concrete API calls.

**What we did**:
- Reconstructed the ComfyUI **SDXL workflow as a Python dictionary** — each key is a node ID, each value is the node's class type and inputs. This lets us programmatically inject prompts and parameters without touching the ComfyUI UI
- Implemented polling logic: submit workflow → get `prompt_id` → poll `/history/{prompt_id}` every second until generation completes → download the image
- Designed a **dual-backend fallback architecture**: primary = local ComfyUI (fast, free, private); fallback = cloud Replicate API (works even when ComfyUI is down). The switch is automatic — the caller doesn't need to know which backend is active
- Added configurable parameters: seed (reproducibility), steps (quality vs speed trade-off), resolution

**Key file**: [`image_generator.py`](image_generator.py)

**Key terms**:
- **ComfyUI Workflow**: A JSON object describing the entire generation pipeline — which nodes, how they connect, what parameters. Equivalent to a Photoshop action
- **KSampler** (采样器): The core denoising step in SD. Takes random noise + text guidance → iteratively removes noise to reveal the image. "Steps" = how many denoising iterations. More steps = better quality but slower
- **Seed** (随机种子): A number that initializes the random noise. Same seed + same prompt + same parameters = same image every time. Essential for reproducible results
- **VAE** (Variational Autoencoder / 变分自编码器): Decodes the model's internal "latent" representation into a human-viewable image. Think of it as the translator between AI's mathematical world and our visual world

---

### Step 5: Gradio Web Interface — "Make It a Tool, Not a Script"

**Purpose**: A Python script that generates images is a prototype. A web interface with input fields, style selectors, and image previews is a **tool that non-technical team members can use**. This is the difference between "I wrote some AI code" and "I built an AI tool for my team."

**What we did**:
- Built a single-page Gradio app: text input (character description) + dropdown (style) + sliders (count, steps, resolution) → gallery output + prompt comparison + optimization explanation
- Designed the layout to tell the story: left column = user input area, right column = results. The prompt comparison section shows "before vs after" — making the DeepSeek optimization transparent and educational
- Added example presets so new users can click one button to see what the tool does, without needing to write their own descriptions first
- Made the tool self-documenting: every generation logs the full process (original text → optimized prompt → generation params → result) in the UI

**Key file**: [`app.py`](app.py)

**Key terms**:
- **Gradio**: A Python library for building ML demo interfaces. Each UI element (text box, dropdown, button, gallery) maps to one line of Python code. Ideal for rapid prototyping — build a working web UI in ~100 lines
- **127.0.0.1** (localhost / 本地回环地址): The IP address that means "this computer." Tools running on `127.0.0.1:7860` are only accessible from your own machine — not deployed to the public internet

---

## 🏗️ Architecture Overview

```
User Input: "白发仙侠女剑客，穿红袍"
        │
        ▼
┌──────────────────────────┐
│ Step 1: DeepSeek API      │  Prompt Optimization
│ Casual Chinese → Pro Eng  │  LLM does language work
│ + JSON structured output  │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Step 2: ComfyUI Pipeline  │  Image Generation
│ Checkpoint → CLIP Encode  │  SD does visual work
│ → KSampler → VAE Decode   │  Local RTX 4060 8GB
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ Step 3: Output            │  Result Delivery
│ Image + Prompt comparison │  Transparent & educational
│ + Optimization rationale  │
└──────────────────────────┘
```

---

## 🎨 Style Presets

| Style | Description | Game Types |
|-------|-------------|------------|
| 仙侠国风 | Ink wash influence, flowing silk, ancient architecture | MMORPG, Card Games |
| 科幻赛博 | Neon lights, holographic UI, high-tech armor | FPS, MOBA |
| 二次元动漫 | Cel shading, clean lineart, vibrant colors | Gacha, Visual Novel |
| 暗黑魔幻 | Gothic atmosphere, heavy armor, dramatic shadows | ARPG, Souls-like |
| Q版可爱 | Big head, small body, bright pastels | Casual, Idle Games |
| 写实电影级 | Photorealistic, UE5-quality, 8K detail | AAA, Next-gen |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.13 |
| GPU VRAM | 6 GB | 8 GB+ |
| Disk Space | ~15 GB | 30 GB+ |

### 1. Clone & Install

```bash
git clone https://github.com/yao-933/ai-game-character-generator.git
cd ai-game-character-generator
pip install -r requirements.txt
```

### 2. Configure DeepSeek API Key

```bash
# Option A: Environment variable
set DEEPSEEK_API_KEY=sk-your-key-here

# Option B: .env file
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env
```

Get your key at [platform.deepseek.com](https://platform.deepseek.com)

### 3. Start ComfyUI (Local Image Generation Backend)

```bash
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
# Download SDXL model to models/checkpoints/
python main.py
# → http://127.0.0.1:8188
```

### 4. Launch the Generator

```bash
python app.py
# → http://127.0.0.1:7860
```

---

## 📂 Project Structure

```
ai-game-character-generator/
├── app.py                  # Gradio web interface (main entry)
├── config.py               # API keys, ComfyUI URL, output paths
├── prompt_optimizer.py     # DeepSeek: casual text → professional prompt
├── image_generator.py      # SD image gen (ComfyUI local + Replicate cloud)
├── style_presets.py        # 6 game art styles with prompt templates
├── requirements.txt        # Python dependencies
├── .env                    # Local API keys (gitignored)
├── .gitignore
└── outputs/                # Generated images
```

---

## 🔧 Key Design Decisions

1. **ComfyUI over Diffusers/Python SDK**: Node-based workflows are transparent and debuggable — you see exactly which nodes ran and what they output. The Python SDK abstracts this away, making debugging harder
2. **Multi-AI over single-model**: DeepSeek does language, SD does vision. Each model excels in its domain; a single "do everything" model would perform worse at both
3. **Gradio over custom React frontend**: ~100 lines of Python for a complete web UI vs hundreds of lines of JSX+CSS. For prototype tools, Gradio's speed-to-demo is unmatched
4. **Dual-backend fallback**: Local ComfyUI is free and fast but can crash. Replicate API costs ~$0.002/image but is always available. Automatic failover means the tool never "just doesn't work"

---

*Built with Python · Gradio · ComfyUI · SDXL · DeepSeek*
