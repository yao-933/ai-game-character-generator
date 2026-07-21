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

> Inspired by 37 Interactive Entertainment's (三七互娱) "Xiao Qi" AI system, which reportedly handles **80% of their 2D asset production**. This is my micro-scale implementation of the same idea: an AI pipeline wrapped into a tool that non-technical team members can actually use.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   MULTI-AI COLLABORATION PIPELINE            │
│                                                              │
│  Step 1: User Input                                          │
│  "A white-haired xianxia swordswoman in flowing red robes"   │
│                          │                                   │
│                          ▼                                   │
│  Step 2: DeepSeek API — Prompt Optimization                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Input: casual Chinese description                   │     │
│  │ Output: professional English SD prompt              │     │
│  │ + negative prompt + optimization rationale          │     │
│  │                                                     │     │
│  │ "1girl, white long hair, flowing red hanfu,         │     │
│  │  ancient chinese fantasy, ink wash influence,       │     │
│  │  dramatic lighting, 8k, artstation trending"        │     │
│  └────────────────────┬───────────────────────────────┘     │
│                       │                                      │
│                       ▼                                      │
│  Step 3: ComfyUI Pipeline — Image Generation                 │
│  ┌────────────────────────────────────────────────────┐     │
│  │ Checkpoint Load ──► CLIP Text Encode (+/-)          │     │
│  │       │                    │                        │     │
│  │       └────────┬───────────┘                        │     │
│  │                ▼                                    │     │
│  │           KSampler (25 steps, Euler Ancestral)       │     │
│  │                │                                    │     │
│  │                ▼                                    │     │
│  │          VAE Decode ──► Save Image                   │     │
│  │                                                     │     │
│  │  Hardware: RTX 4060 Laptop GPU (8GB VRAM)            │     │
│  │  Model: SDXL 1.0 Base (6.5GB)                       │     │
│  │  Resolution: 1024×1024                              │     │
│  │  Generation time: ~15 seconds per image              │     │
│  └────────────────────┬───────────────────────────────┘     │
│                       │                                      │
│                       ▼                                      │
│  Step 4: Output                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │ • Generated character art                           │     │
│  │ • Original vs optimized prompt comparison           │     │
│  │ • DeepSeek's optimization explanation               │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
│  My Role: Pipeline Architect — I design the workflow,        │
│  connect the models, and build the interface.                │
└─────────────────────────────────────────────────────────────┘
```

### Why Multi-AI?

Each model has a specialty:
- **DeepSeek** → Language understanding, prompt engineering (text domain)
- **Stable Diffusion** → Visual generation, artistic rendering (image domain)
- **Me** → Architecture design, pipeline orchestration, UI/UX

This is the same division of labor as a game studio: designer + artist + technical director.

---

## 🎨 Style Presets

| Style | Description | Game Types |
|-------|-------------|------------|
| **仙侠国风** (Chinese Fantasy) | Ink wash influence, flowing silk, ancient architecture | MMORPG, Card Games |
| **科幻赛博** (Cyberpunk) | Neon lights, holographic UI, high-tech armor | FPS, MOBA |
| **二次元动漫** (Anime) | Cel shading, clean lineart, vibrant colors | Gacha, Visual Novel |
| **暗黑魔幻** (Dark Fantasy) | Gothic atmosphere, heavy armor, dramatic shadows | ARPG, Souls-like |
| **Q版可爱** (Chibi) | Big head, small body, bright pastels | Casual, Idle Games |
| **写实电影级** (Cinematic) | Photorealistic, UE5-quality, 8K detail | AAA, Next-gen |

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| Python | 3.10+ | 3.13 |
| GPU VRAM | 6 GB | 8 GB+ |
| Disk Space | ~15 GB | 30 GB+ |
| OS | Windows / Linux / macOS | Windows 11 |

### 1. Clone & Install

```bash
git clone https://github.com/yao-933/ai-game-character-generator.git
cd ai-game-character-generator
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
# Option A: Environment variable (recommended)
# Windows
set DEEPSEEK_API_KEY=sk-your-key-here
# Linux/macOS
export DEEPSEEK_API_KEY=sk-your-key-here

# Option B: Create .env file in project root
echo "DEEPSEEK_API_KEY=sk-your-key-here" > .env
```

Get your key at [platform.deepseek.com](https://platform.deepseek.com)

### 3. Start ComfyUI (Local Backend)

```bash
# Clone and set up ComfyUI (one-time setup)
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt

# Download SDXL model to models/checkpoints/
# huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
# → sd_xl_base_1.0.safetensors (6.94 GB)

# Start the server
python main.py
# → http://127.0.0.1:8188
```

### 4. Launch the Generator

```bash
cd ai-game-character-generator
python app.py
# → http://127.0.0.1:7860
```

### Cloud-Only Mode (No GPU Required)

Set `IMAGE_GEN_MODE = "replicate"` in `config.py` and add your [Replicate](https://replicate.com) API token. Falls back automatically when ComfyUI is unavailable.

---

## 📂 Project Structure

```
ai-game-character-generator/
│
├── app.py                  # Gradio web interface (main entry)
├── config.py               # API keys, ComfyUI URL, output settings
├── prompt_optimizer.py     # DeepSeek: casual text → professional prompt
├── image_generator.py      # SD image gen (ComfyUI local + Replicate cloud)
├── style_presets.py        # 6 game art styles with prompt templates
├── requirements.txt        # Python dependencies
│
├── .env                    # Local API keys (gitignored)
├── .gitignore              # Excludes .env, outputs, __pycache__
├── README.md               # This file
├── LICENSE                 # MIT
│
├── outputs/                # Generated images (gitignored)
└── examples/               # Screenshots for documentation
```

---

## 🔧 Technical Details

### ComfyUI Pipeline

```
CheckpointLoaderSimple (SDXL 1.0)
        │
        ├──► CLIP Text Encode (+) ──┐
        │                            │
        ├──► CLIP Text Encode (-) ──┤
        │                            ▼
        └──► EmptyLatentImage ──► KSampler ──► VAE Decode ──► SaveImage
                                 (25 steps,    (decode latent
                                  Euler A)      to pixels)
```

### Fallback Strategy

| Component | Primary | Fallback | Trigger |
|-----------|---------|----------|---------|
| Prompt Optimization | DeepSeek API | Local template | API timeout |
| Image Generation | ComfyUI (local) | Replicate (cloud) | ComfyUI unreachable |
| Configuration | `.env` file | Environment variables | `.env` absent |

### Key Design Decisions

1. **ComfyUI over Diffusers**: Node-based workflows are more transparent and debuggable
2. **Gradio over FastAPI+React**: Faster prototyping, less boilerplate for demo tools
3. **Style presets with prompt suffixes**: Ensures brand consistency across generations
4. **JSON response format from DeepSeek**: Structured output avoids regex parsing

---

## 🔮 Roadmap

- [ ] ControlNet integration for pose/sketch control
- [ ] Character turnaround views (front / side / back)
- [ ] Batch generation with style consistency checks
- [ ] LoRA support for custom character styles

---

---

*Built with DeepSeek + Claude Code + ComfyUI + Stable Diffusion*
