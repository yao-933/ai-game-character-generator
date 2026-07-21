"""
风格预设 — 游戏原画常用风格模板
面试亮点：体现你对游戏美术风格的了解
"""

STYLE_PRESETS = {
    "仙侠国风": {
        "positive_suffix": (
            "chinese fantasy style, ink wash painting influence, "
            "flowing silk fabric, ancient chinese architecture background, "
            "elegant and ethereal atmosphere, soft golden lighting"
        ),
        "negative_prefix": (
            "western style, modern clothing, realistic photograph, "
            "oil painting, thick lines, heavy makeup"
        ),
        "description": "适合仙侠/古风游戏角色，飘逸水墨感"
    },

    "科幻赛博": {
        "positive_suffix": (
            "cyberpunk style, neon lights, holographic interfaces, "
            "high-tech armor, mechanical details, futuristic city background, "
            "blue and purple color scheme, glowing elements"
        ),
        "negative_prefix": (
            "medieval, ancient, organic, natural landscape, "
            "rustic, vintage, low-tech, fantasy magic"
        ),
        "description": "适合科幻/机甲/赛博朋克风格游戏"
    },

    "二次元动漫": {
        "positive_suffix": (
            "anime style, cel shading, clean lineart, "
            "vibrant colors, manga aesthetics, japanese animation style, "
            "expressive eyes, simple background"
        ),
        "negative_prefix": (
            "realistic, photorealistic, 3d render, "
            "oil painting, sketch, rough, blurry"
        ),
        "description": "适合二次元/卡牌类游戏角色"
    },

    "暗黑魔幻": {
        "positive_suffix": (
            "dark fantasy style, gothic atmosphere, dramatic lighting, "
            "detailed armor with dark metal, moody and mysterious, "
            "fog and shadows, blood red accents, souls-like aesthetics"
        ),
        "negative_prefix": (
            "cute, colorful, bright, cartoon, anime, "
            "sunny, cheerful, pastel colors, simple"
        ),
        "description": "适合暗黑/魂系/西方魔幻风格游戏"
    },

    "Q版可爱": {
        "positive_suffix": (
            "chibi style, cute and adorable, big head small body, "
            "bright and cheerful colors, soft shading, "
            "kawaii aesthetics, rounded shapes, simple cute background"
        ),
        "negative_prefix": (
            "realistic, horror, dark, serious, "
            "detailed muscles, mature, scary, gothic"
        ),
        "description": "适合休闲/放置/养成类手游"
    },

    "写实电影级": {
        "positive_suffix": (
            "photorealistic, cinematic lighting, unreal engine 5, "
            "hyper-detailed, 8k resolution, artstation trending, "
            "professional concept art, dramatic composition, subsurface scattering"
        ),
        "negative_prefix": (
            "cartoon, anime, painting, sketch, "
            "low quality, blurry, distorted, ugly"
        ),
        "description": "适合3A大作/次世代游戏角色"
    },
}
