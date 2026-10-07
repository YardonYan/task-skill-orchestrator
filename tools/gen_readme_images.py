# -*- coding: utf-8 -*-
"""为 task-skill-orchestrator 生成 README 配图。

字体：中文一律走 msyh / msyhbd，Consolas 只用于纯英文与代码片段，
否则中文字形会渲染成方块。
"""
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

REG = "C:/Windows/Fonts/msyh.ttc"
BOLD = "C:/Windows/Fonts/msyhbd.ttc"
MONO = "C:/Windows/Fonts/consola.ttf"

BG_TOP = (13, 20, 34)
BG_BOT = (24, 38, 63)
CARD = (28, 44, 74)
CARD2 = (35, 54, 88)
LINE = (62, 88, 130)
TXT = (255, 255, 255)
SUB = (150, 166, 188)
DIM = (104, 120, 145)

WAVE0 = (79, 195, 247)
WAVE1 = (167, 139, 250)
DONE = (110, 231, 183)
AMBER = (245, 176, 66)
RED = (248, 113, 113)


def f(path, size):
    return ImageFont.truetype(path, size)


def vgrad(size, c1, c2):
    w, h = size
    strip = Image.new("RGB", (1, h))
    d = ImageDraw.Draw(strip)
    for y in range(h):
        t = y / max(h - 1, 1)
        d.point((0, y), fill=tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
    return strip.resize((w, h))


def card(draw, box, radius=16, fill=CARD, outline=LINE, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw, x1, y, x2, color=LINE, head=10):
    draw.line([x1, y, x2 - head, y], fill=color, width=3)
    draw.polygon([(x2, y), (x2 - head, y - 6), (x2 - head, y + 6)], fill=color)


def dag_waves():
    W, H = 1500, 660
    img = vgrad((W, H), BG_TOP, BG_BOT)
    d = ImageDraw.Draw(img)

    d.text((70, 46), "分波并行是怎么跑的 / How wave-based execution works",
           font=f(BOLD, 38), fill=TXT)
    d.text((70, 100), "同一个波次内的任务互相独立，由多个 Sub Agent 同时执行；下一波必须等上一波全部完成",
           font=f(REG, 24), fill=SUB)

    # 用户需求
    card(d, [70, 296, 300, 388], fill=CARD2, outline=LINE, width=1)
    d.text((98, 320), "用户需求", font=f(BOLD, 26), fill=TXT)
    d.text((98, 356), "User request", font=f(REG, 20), fill=SUB)
    arrow(d, 302, 342, 332)

    # Wave 0 容器
    d.rounded_rectangle([336, 168, 786, 520], radius=20, outline=WAVE0, width=2)
    d.text((364, 186), "Wave 0", font=f(BOLD, 28), fill=WAVE0)
    d.text((500, 192), "并行 parallel", font=f(REG, 21), fill=SUB)

    tasks0 = [("①  调研特斯拉 2025 份额与技术", "Tesla research", "search-agent"),
              ("②  调研比亚迪 2025 份额与技术", "BYD research", "search-agent"),
              ("③  调研蔚来 2025 份额与技术", "NIO research", "search-agent")]
    y = 238
    for cn, en, agent in tasks0:
        card(d, [364, y, 758, y + 82])
        d.rectangle([364, y, 369, y + 82], fill=WAVE0)
        fo = f(MONO, 17)
        d.text((390, y + 12), cn, font=f(REG, 21), fill=TXT)
        d.text((390, y + 48), en, font=f(REG, 18), fill=DIM)
        d.text((745 - d.textlength(agent, font=fo), y + 49), agent, font=fo, fill=WAVE0)
        y += 94

    for ty in (279, 373, 467):
        arrow(d, 788, ty, 812, color=WAVE0)
    d.line([800, 279, 800, 467], fill=WAVE0, width=2)

    # Wave 1 容器
    d.rounded_rectangle([816, 252, 1166, 432], radius=20, outline=WAVE1, width=2)
    d.text((844, 274), "Wave 1", font=f(BOLD, 28), fill=WAVE1)
    d.text((968, 280), "汇总 aggregation", font=f(REG, 21), fill=SUB)
    card(d, [844, 322, 1138, 404])
    d.rectangle([844, 322, 849, 404], fill=WAVE1)
    d.text((870, 336), "④  合并三份调研产出报告", font=f(REG, 21), fill=TXT)
    d.text((870, 368), "file-agent", font=f(MONO, 18), fill=WAVE1)

    arrow(d, 1168, 342, 1198, color=WAVE1)

    # 交付
    card(d, [1204, 292, 1430, 392], fill=(23, 52, 48), outline=DONE, width=2)
    d.text([1232, 316], "最终交付", font=f(BOLD, 26), fill=DONE)
    d.text([1232, 352], "comparison", font=f(MONO, 19), fill=DONE)
    d.text([1330, 352], ".md", font=f(MONO, 19), fill=(134, 239, 210))

    # 底部对比
    d.text((70, 556), "串行需要依次跑完 4 个任务；并行下 T1/T2/T3 同时开始，总耗时明显更短",
           font=f(REG, 22), fill=SUB)

    bars = [("串行 sequential", 4, 560, RED), ("并行 parallel", 2, 280, DONE)]
    y = 592
    for label, units, width, color in bars:
        d.text((70, y - 4), label, font=f(REG, 21), fill=TXT)
        d.rounded_rectangle([260, y - 4, 260 + width, y + 20], radius=6, fill=color)
        d.text((260 + width + 16, y - 4), "%d 个时间单位" % units, font=f(REG, 20), fill=SUB)
        y += 34

    img.save(os.path.join(OUT, "dag-waves.png"))
    print("dag-waves.png")


def pipeline():
    W, H = 1500, 430
    img = vgrad((W, H), BG_TOP, BG_BOT)
    d = ImageDraw.Draw(img)

    d.text((70, 46), "四阶段流水线 / Four-phase pipeline", font=f(BOLD, 38), fill=TXT)
    d.text((70, 100), "先拆解、再建依赖图、然后分波，最后同波并行执行并汇总",
           font=f(REG, 24), fill=SUB)

    steps = [
        ("1", "分析拆解", "Decompose", "把需求切成原子子任务", "Split into atomic subtasks", WAVE0),
        ("2", "构建依赖图", "Build DAG", "识别依赖并验证无环", "Detect deps, validate acyclic", (96, 165, 250)),
        ("3", "波次规划", "Wave Planning", "拓扑分层，输出执行计划", "Topological layering", WAVE1),
        ("4", "执行与汇总", "Execute & Merge", "同波并行派发，结果统一合并", "Parallel per wave, then merge", DONE),
    ]

    x = 70
    for num, cn, en, b1, b2, color in steps:
        card(d, [x, 180, x + 310, 370], fill=CARD, outline=LINE)
        d.rounded_rectangle([x + 22, 202, x + 54, 234], radius=8, fill=color)
        fn = f(BOLD, 22)
        d.text((x + 38 - d.textlength(num, font=fn) / 2, 206), num, font=fn, fill=(13, 20, 34))
        d.text((x + 66, 203), cn, font=f(BOLD, 25), fill=TXT)
        d.text((x + 22, 250), en, font=f(REG, 19), fill=color)
        d.line([x + 22, 282, x + 288, 282], fill=LINE, width=1)
        d.text((x + 22, 296), b1, font=f(REG, 18), fill=SUB)
        d.text((x + 22, 326), b2, font=f(REG, 17), fill=DIM)
        if x + 310 < 1400:
            arrow(d, x + 316, 275, x + 348, color=LINE)
        x += 350

    img.save(os.path.join(OUT, "pipeline.png"))
    print("pipeline.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    dag_waves()
    pipeline()
