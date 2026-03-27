"""
generate_visuals.py — KR-04 인사로 보는 현대차의 방향

생성 이미지:
  01_layer_chain.png      — 5-Layer 체인: 빈 고리가 전체를 무너뜨린다
  02_google_asymmetry.png — 구글의 비대칭: 로봇의 안드로이드
  03_two_paths.png        — 두 갈래: 제조업체 vs Physical AI 기업

Usage:
    source .venv-wsl/bin/activate && python data/articles/018_KR_현대차-인사/generate_visuals.py
"""

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# ── 경로 ──────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# ── 한글 폰트 ─────────────────────────────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 팔레트 ───────────────────────────────────────────────────────────
BG      = "#0d1117"
BG2     = "#161b22"
GREEN   = "#3fb950"
YELLOW  = "#d29922"
RED     = "#f85149"
BLUE    = "#58a6ff"
ORANGE  = "#db6d28"
PURPLE  = "#bc8cff"
GRAY    = "#6e7681"
WHITE   = "#e6edf3"
DIM     = "#8b949e"
BORDER  = "#30363d"

FIG_SIZE = (8, 8)
DPI      = 135


def _save(fig: plt.Figure, name: str) -> dict:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    size = path.stat().st_size
    return {"name": name, "path": str(path), "size": size, "ok": size > 10_000}


# ══════════════════════════════════════════════════════════════════════════
# 01. 5-Layer 체인 — 빈 고리가 전체를 무너뜨린다
# ══════════════════════════════════════════════════════════════════════════
def make_layer_chain() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── 제목 ──
    ax.text(0.5, 0.96, "5-Layer 체인",
            ha="center", va="top", color=WHITE,
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.915, "현대차의 수직통합 — 누가 채우고, 어디가 비어 있는가",
            ha="center", va="top", color=DIM, fontsize=9.5)

    # ── 레이어 데이터 ──
    layers = [
        {
            "name": "Layer 1", "label": "AI 두뇌",
            "owner": "박민우, Kovac",
            "detail": "자동차: 자체  /  로봇: 구글",
            "color": YELLOW, "status_color": YELLOW,
            "status": "부분",
        },
        {
            "name": "Layer 2", "label": "훈련 데이터",
            "owner": "?",
            "detail": "구글이 복합 데이터 독점",
            "color": RED, "status_color": RED,
            "status": "외부 의존",
        },
        {
            "name": "Layer 3", "label": "컴퓨팅 인프라",
            "owner": "?",
            "detail": "NVIDIA  (2027~2029 완공 예정)",
            "color": RED, "status_color": RED,
            "status": "미완공",
        },
        {
            "name": "Layer 4", "label": "시뮬레이션",
            "owner": "Kovac",
            "detail": "NVIDIA Cosmos / Omniverse",
            "color": ORANGE, "status_color": ORANGE,
            "status": "부분",
        },
        {
            "name": "Layer 5", "label": "제조",
            "owner": "현대차",
            "detail": "730만 대. 이건 원래 잘한다.",
            "color": GREEN, "status_color": GREEN,
            "status": "자체 소유",
        },
    ]

    n = len(layers)
    chain_top = 0.85
    chain_bot = 0.24
    total_h = chain_top - chain_bot
    layer_h = total_h / n
    block_h = layer_h * 0.68
    block_w = 0.72
    cx = 0.46  # slightly left to make room for status

    for i, layer in enumerate(layers):
        cy = chain_top - (i + 0.5) * layer_h
        color = layer["color"]
        is_broken = color == RED

        # ── 연결선 (이전 레이어와의 연결) ──
        if i > 0:
            prev_bot = chain_top - (i) * layer_h + block_h * 0.5 - layer_h
            cur_top = cy + block_h * 0.5
            line_y_top = chain_top - i * layer_h + block_h * 0.18
            line_y_bot = cy + block_h * 0.42

            prev_color = layers[i - 1]["color"]
            # if current or previous is RED, draw broken line
            if is_broken or prev_color == RED:
                ax.plot([cx, cx], [line_y_bot, line_y_top],
                        color=RED, linewidth=2, linestyle=":",
                        alpha=0.5, zorder=1)
                # X mark at break point
                mid_y = (line_y_bot + line_y_top) / 2
                ax.text(cx, mid_y, "x", ha="center", va="center",
                        color=RED, fontsize=14, fontweight="bold",
                        alpha=0.7, zorder=2)
            else:
                ax.plot([cx, cx], [line_y_bot, line_y_top],
                        color=GREEN, linewidth=2.5, alpha=0.4, zorder=1)

        # ── 블록 ──
        alpha_fill = 0.08 if is_broken else 0.18
        lw = 2.5 if is_broken else 1.8
        box = mpatches.FancyBboxPatch(
            (cx - block_w / 2, cy - block_h / 2), block_w, block_h,
            boxstyle="round,pad=0.012",
            facecolor=color, alpha=alpha_fill,
            edgecolor=color, linewidth=lw, zorder=3)
        ax.add_patch(box)

        # ── 텍스트: 레이어명 + 라벨 ──
        ax.text(cx - block_w / 2 + 0.025, cy + block_h * 0.22,
                f"{layer['name']}  {layer['label']}",
                ha="left", va="center", color=WHITE,
                fontsize=10.5, fontweight="bold", zorder=4)

        # ── 텍스트: 담당자 ──
        owner_color = WHITE if not is_broken else RED
        ax.text(cx - block_w / 2 + 0.025, cy - block_h * 0.08,
                layer["owner"],
                ha="left", va="center", color=owner_color,
                fontsize=10, fontweight="bold", zorder=4)

        # ── 텍스트: 상세 ──
        ax.text(cx - block_w / 2 + 0.025, cy - block_h * 0.33,
                layer["detail"],
                ha="left", va="center", color=DIM,
                fontsize=8.5, zorder=4)

        # ── 우측 상태 배지 ──
        badge_x = cx + block_w / 2 - 0.02
        badge_y = cy + block_h * 0.22
        sc = layer["status_color"]
        ax.text(badge_x, badge_y, layer["status"],
                ha="right", va="center", color=sc,
                fontsize=8.5, fontweight="bold", zorder=4,
                bbox=dict(boxstyle="round,pad=0.2",
                          facecolor=sc, alpha=0.12,
                          edgecolor=sc, linewidth=0.8))

    # ── 좌측 소유 비율 바 ──
    bar_x = cx - block_w / 2 - 0.04
    bar_w = 0.012
    # Layer 1: YELLOW
    y1_top = chain_top - 0 * layer_h
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, y1_top - layer_h), bar_w, layer_h,
        boxstyle="round,pad=0.001",
        facecolor=YELLOW, alpha=0.35))
    # Layer 2-3: RED
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, y1_top - 3 * layer_h), bar_w, layer_h * 2,
        boxstyle="round,pad=0.001",
        facecolor=RED, alpha=0.35))
    # Layer 4: ORANGE
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, y1_top - 4 * layer_h), bar_w, layer_h,
        boxstyle="round,pad=0.001",
        facecolor=ORANGE, alpha=0.35))
    # Layer 5: GREEN
    ax.add_patch(mpatches.FancyBboxPatch(
        (bar_x, y1_top - 5 * layer_h), bar_w, layer_h,
        boxstyle="round,pad=0.001",
        facecolor=GREEN, alpha=0.4))

    ax.text(bar_x + bar_w / 2, chain_top + 0.015, "1/5",
            ha="center", va="bottom", color=RED,
            fontsize=9, fontweight="bold")
    ax.text(bar_x + bar_w / 2, chain_top + 0.035, "자체 소유",
            ha="center", va="bottom", color=DIM, fontsize=7)

    # ── 하단 인사이트 박스 ──
    box = mpatches.FancyBboxPatch(
        (0.06, 0.04), 0.88, 0.155,
        boxstyle="round,pad=0.015",
        facecolor=BG2, edgecolor=RED, linewidth=1.2)
    ax.add_patch(box)

    ax.text(0.5, 0.163,
            "체인의 강도는 가장 약한 고리가 결정한다.",
            ha="center", va="center", color=RED,
            fontsize=12, fontweight="bold")
    ax.text(0.5, 0.12,
            "Layer 1과 5가 아무리 강해도,",
            ha="center", va="center", color=WHITE, fontsize=10)
    ax.text(0.5, 0.09,
            "Layer 2와 3이 비어 있으면 전체가 멈춘다.",
            ha="center", va="center", color=WHITE, fontsize=10)
    ax.text(0.5, 0.055,
            "빈 층의 소유자가 전체 가치 사슬의 조건을 결정한다.",
            ha="center", va="center", color=YELLOW,
            fontsize=9.5, fontweight="bold")

    return _save(fig, "01_layer_chain.png")


# ══════════════════════════════════════════════════════════════════════════
# 02. 구글의 비대칭 — 로봇의 안드로이드
# ══════════════════════════════════════════════════════════════════════════
def make_google_asymmetry() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── 제목 ──
    ax.text(0.5, 0.96, "구글의 비대칭",
            ha="center", va="top", color=WHITE,
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.915, "로봇의 안드로이드 — 모든 파트너의 데이터가 하나의 모델로",
            ha="center", va="top", color=DIM, fontsize=9.5)

    # ── 중앙 허브: Google DeepMind ──
    hub_x, hub_y = 0.5, 0.56
    hub_r = 0.1

    hub_circle = mpatches.Circle(
        (hub_x, hub_y), hub_r,
        facecolor=GREEN, alpha=0.12,
        edgecolor=GREEN, linewidth=2.5, zorder=5)
    ax.add_patch(hub_circle)

    ax.text(hub_x, hub_y + 0.025, "Google",
            ha="center", va="center", color=GREEN,
            fontsize=13, fontweight="bold", zorder=6)
    ax.text(hub_x, hub_y - 0.015, "DeepMind",
            ha="center", va="center", color=GREEN,
            fontsize=13, fontweight="bold", zorder=6)
    ax.text(hub_x, hub_y - 0.055, "Gemini Robotics",
            ha="center", va="center", color=DIM,
            fontsize=8.5, zorder=6)

    # ── 파트너 노드들 (spoke) ──
    partners = [
        {"name": "Atlas",      "company": "BD / 현대차", "x": 0.13, "y": 0.78, "color": BLUE},
        {"name": "Apollo",     "company": "Apptronik",   "x": 0.87, "y": 0.78, "color": PURPLE},
        {"name": "Digit",      "company": "Agility",     "x": 0.13, "y": 0.34, "color": ORANGE},
        {"name": "기타 로봇",   "company": "Agile, Enchanted...", "x": 0.87, "y": 0.34, "color": GRAY},
    ]

    node_w = 0.19
    node_h = 0.09

    for p in partners:
        px, py = p["x"], p["y"]
        pc = p["color"]

        # 노드 박스
        node = mpatches.FancyBboxPatch(
            (px - node_w / 2, py - node_h / 2), node_w, node_h,
            boxstyle="round,pad=0.012",
            facecolor=pc, alpha=0.12,
            edgecolor=pc, linewidth=1.5, zorder=5)
        ax.add_patch(node)

        ax.text(px, py + 0.012, p["name"],
                ha="center", va="center", color=WHITE,
                fontsize=10, fontweight="bold", zorder=6)
        ax.text(px, py - 0.022, p["company"],
                ha="center", va="center", color=DIM,
                fontsize=7.5, zorder=6)

        # ── 화살표: 파트너 → 구글 (데이터) ──
        # 파트너에서 허브 방향으로
        dx = hub_x - px
        dy = hub_y - py
        dist = (dx**2 + dy**2) ** 0.5
        # 시작점: 노드 경계에서
        start_offset = 0.08
        end_offset = hub_r + 0.015
        sx = px + dx / dist * start_offset
        sy = py + dy / dist * start_offset
        ex = hub_x - dx / dist * end_offset
        ey = hub_y - dy / dist * end_offset

        # 데이터 화살표 (파트너 → 구글)
        ax.annotate("",
                    xy=(ex, ey), xytext=(sx, sy),
                    arrowprops=dict(
                        arrowstyle="->,head_width=0.25,head_length=0.12",
                        color=pc, lw=1.8, alpha=0.6,
                        connectionstyle="arc3,rad=0.1"),
                    zorder=4)

        # 데이터 라벨
        mid_x = (sx + ex) / 2
        mid_y = (sy + ey) / 2
        # offset label slightly
        label_offset_x = -0.04 if px < 0.5 else 0.04
        label_offset_y = 0.02 if py > hub_y else -0.02
        ax.text(mid_x + label_offset_x, mid_y + label_offset_y,
                "데이터",
                ha="center", va="center", color=pc,
                fontsize=7.5, fontweight="bold", alpha=0.7, zorder=4)

    # ── 중앙에서 바깥으로: 개선된 모델 (얇은 점선) ──
    ax.text(hub_x, hub_y - hub_r - 0.035,
            "개선된 모델이 모든 파트너에게 돌아간다",
            ha="center", va="center", color=GREEN,
            fontsize=8.5, fontweight="bold", alpha=0.7,
            bbox=dict(boxstyle="round,pad=0.3",
                      facecolor=GREEN, alpha=0.08,
                      edgecolor=GREEN, linewidth=0.5))

    # ── 비교 박스: 스마트폰 시대 유추 ──
    cmp_top = 0.195
    cmp_h = 0.06
    cmp_w = 0.38

    # 좌측: 스마트폰
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.06, cmp_top - cmp_h / 2), cmp_w, cmp_h,
        boxstyle="round,pad=0.01",
        facecolor=BG2, edgecolor=BORDER, linewidth=0.8))

    ax.text(0.06 + cmp_w / 2, cmp_top + 0.008,
            "스마트폰 시대",
            ha="center", va="center", color=DIM, fontsize=8)
    ax.text(0.06 + cmp_w / 2, cmp_top - 0.018,
            "삼성은 Galaxy 데이터만. 구글은 전체를.",
            ha="center", va="center", color=WHITE, fontsize=8)

    # 우측: 로봇
    ax.add_patch(mpatches.FancyBboxPatch(
        (0.56, cmp_top - cmp_h / 2), cmp_w, cmp_h,
        boxstyle="round,pad=0.01",
        facecolor=BG2, edgecolor=BORDER, linewidth=0.8))

    ax.text(0.56 + cmp_w / 2, cmp_top + 0.008,
            "Physical AI 시대",
            ha="center", va="center", color=DIM, fontsize=8)
    ax.text(0.56 + cmp_w / 2, cmp_top - 0.018,
            "현대차는 Atlas 데이터만. 구글은 전체를.",
            ha="center", va="center", color=WHITE, fontsize=8)

    # 등호
    ax.text(0.50, cmp_top, "=",
            ha="center", va="center", color=YELLOW,
            fontsize=16, fontweight="bold")

    # ── 하단 인사이트 박스 ──
    box = mpatches.FancyBboxPatch(
        (0.06, 0.04), 0.88, 0.10,
        boxstyle="round,pad=0.015",
        facecolor=BG2, edgecolor=GREEN, linewidth=1.2)
    ax.add_patch(box)

    ax.text(0.5, 0.105,
            "구글만 전체를 본다.",
            ha="center", va="center", color=GREEN,
            fontsize=12, fontweight="bold")
    ax.text(0.5, 0.065,
            "데이터의 복합 이점은 플랫폼 사업자에게만 돌아간다.",
            ha="center", va="center", color=WHITE, fontsize=9.5)

    return _save(fig, "02_google_asymmetry.png")


# ══════════════════════════════════════════════════════════════════════════
# 03. 두 갈래 — 제조업체 vs Physical AI 기업
# ══════════════════════════════════════════════════════════════════════════
def make_two_paths() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── 제목 ──
    ax.text(0.5, 0.96, "두 갈래",
            ha="center", va="top", color=WHITE,
            fontsize=20, fontweight="bold")
    ax.text(0.5, 0.915, "현대차 앞에 놓인 선택",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── 상단: 현대차 출발점 ──
    start_x, start_y = 0.5, 0.82
    start_box = mpatches.FancyBboxPatch(
        (start_x - 0.12, start_y - 0.03), 0.24, 0.06,
        boxstyle="round,pad=0.012",
        facecolor=BLUE, alpha=0.2,
        edgecolor=BLUE, linewidth=2, zorder=5)
    ax.add_patch(start_box)
    ax.text(start_x, start_y, "현대차 2026",
            ha="center", va="center", color=WHITE,
            fontsize=13, fontweight="bold", zorder=6)

    # ── 분기 화살표 ──
    # 좌측 (제조업체)
    left_x = 0.24
    right_x = 0.76
    fork_y = 0.72
    dest_y = 0.58

    # 분기선 — 좌측
    ax.annotate("",
                xy=(left_x, dest_y + 0.06), xytext=(start_x - 0.04, fork_y),
                arrowprops=dict(
                    arrowstyle="->,head_width=0.3,head_length=0.12",
                    color=GRAY, lw=2.5, alpha=0.5,
                    connectionstyle="arc3,rad=0.15"),
                zorder=3)

    # 분기선 — 우측
    ax.annotate("",
                xy=(right_x, dest_y + 0.06), xytext=(start_x + 0.04, fork_y),
                arrowprops=dict(
                    arrowstyle="->,head_width=0.3,head_length=0.12",
                    color=GREEN, lw=2.5, alpha=0.6,
                    connectionstyle="arc3,rad=-0.15"),
                zorder=3)

    # ── 좌측 카드: 제조업체 ──
    card_w = 0.40
    card_h = 0.42
    lc_x = left_x - card_w / 2
    lc_y = dest_y - card_h + 0.04

    ax.add_patch(mpatches.FancyBboxPatch(
        (lc_x, lc_y), card_w, card_h,
        boxstyle="round,pad=0.015",
        facecolor=GRAY, alpha=0.08,
        edgecolor=GRAY, linewidth=1.5, zorder=4))

    # 좌측 헤더
    ax.text(left_x, dest_y - 0.01, "제조업체",
            ha="center", va="center", color=GRAY,
            fontsize=15, fontweight="bold", zorder=5)
    ax.text(left_x, dest_y - 0.055, "익숙한 길",
            ha="center", va="center", color=DIM,
            fontsize=9, zorder=5)

    # 좌측 항목
    left_items = [
        ("730만 대 생산 규모 유지", GRAY),
        ("중국과 가격 경쟁", GRAY),
        ("AI 두뇌는 파트너 의존", GRAY),
        ('"몸을 만드는 자"의 몫', RED),
    ]
    for i, (text, color) in enumerate(left_items):
        y = dest_y - 0.12 - i * 0.055
        ax.text(left_x - card_w / 2 + 0.03, y, "·",
                ha="left", va="center", color=color,
                fontsize=12, zorder=5)
        ax.text(left_x - card_w / 2 + 0.055, y, text,
                ha="left", va="center", color=color if color == RED else DIM,
                fontsize=9.5, zorder=5)

    # 좌측 하단 결론
    ax.add_patch(mpatches.FancyBboxPatch(
        (lc_x + 0.02, lc_y + 0.025), card_w - 0.04, 0.055,
        boxstyle="round,pad=0.008",
        facecolor=RED, alpha=0.08,
        edgecolor=RED, linewidth=0.8, zorder=5))
    ax.text(left_x, lc_y + 0.052,
            "스마트폰의 삼성이 걸어간 길",
            ha="center", va="center", color=RED,
            fontsize=9.5, fontweight="bold", zorder=6)

    # ── 우측 카드: Physical AI 기업 ──
    rc_x = right_x - card_w / 2
    rc_y = dest_y - card_h + 0.04

    ax.add_patch(mpatches.FancyBboxPatch(
        (rc_x, rc_y), card_w, card_h,
        boxstyle="round,pad=0.015",
        facecolor=GREEN, alpha=0.08,
        edgecolor=GREEN, linewidth=1.5, zorder=4))

    # 우측 헤더
    ax.text(right_x, dest_y - 0.01, "Physical AI 기업",
            ha="center", va="center", color=GREEN,
            fontsize=15, fontweight="bold", zorder=5)
    ax.text(right_x, dest_y - 0.055, "훨씬 힘든 길",
            ha="center", va="center", color=DIM,
            fontsize=9, zorder=5)

    # 우측 항목
    right_items = [
        ("5개 층 수직통합 소유", GREEN),
        ("자체 데이터 플라이휠 구축", GREEN),
        ("AI 두뇌부터 제조까지", GREEN),
        ('"뇌를 설계하는 자"의 몫', GREEN),
    ]
    for i, (text, color) in enumerate(right_items):
        y = dest_y - 0.12 - i * 0.055
        ax.text(right_x - card_w / 2 + 0.03, y, "·",
                ha="left", va="center", color=color,
                fontsize=12, zorder=5)
        ax.text(right_x - card_w / 2 + 0.055, y, text,
                ha="left", va="center", color=WHITE,
                fontsize=9.5, zorder=5)

    # 우측 하단 결론
    ax.add_patch(mpatches.FancyBboxPatch(
        (rc_x + 0.02, rc_y + 0.025), card_w - 0.04, 0.055,
        boxstyle="round,pad=0.008",
        facecolor=GREEN, alpha=0.08,
        edgecolor=GREEN, linewidth=0.8, zorder=5))
    ax.text(right_x, rc_y + 0.052,
            "테슬라가 가고 있는 길",
            ha="center", va="center", color=GREEN,
            fontsize=9.5, fontweight="bold", zorder=6)

    # ── 중앙 VS ──
    vs_y = dest_y - card_h / 2 + 0.04
    ax.text(0.5, vs_y, "vs",
            ha="center", va="center", color=DIM,
            fontsize=18, fontweight="bold", alpha=0.4)

    # ── 하단 인사이트 박스 ──
    box = mpatches.FancyBboxPatch(
        (0.06, 0.04), 0.88, 0.12,
        boxstyle="round,pad=0.015",
        facecolor=BG2, edgecolor=YELLOW, linewidth=1.2)
    ax.add_patch(box)

    ax.text(0.5, 0.12,
            "기술의 문제가 아니다. 구성원들의 의지의 문제다.",
            ha="center", va="center", color=YELLOW,
            fontsize=12, fontweight="bold")
    ax.text(0.5, 0.07,
            "무운을 빈다, 현대차.",
            ha="center", va="center", color=WHITE,
            fontsize=11)

    return _save(fig, "03_two_paths.png")


# ══════════════════════════════════════════════════════════════════════════
# QA
# ══════════════════════════════════════════════════════════════════════════
def qa_check(results: list[dict]) -> None:
    from PIL import Image

    print("\n── QA 결과 " + "─" * 45)
    all_ok = True
    for r in results:
        issues = []
        path = Path(r["path"])
        if not path.exists():
            print(f"  x  {r['name']} -- 파일 없음")
            all_ok = False
            continue

        size_kb = path.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"파일 크기 너무 작음 ({size_kb:.1f} KB)")

        with Image.open(path) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"해상도 부족 ({w}x{h}px, 최소 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"비율 이탈 ({ratio:.2f})")

        if issues:
            print(f"  !!  {r['name']}")
            for issue in issues:
                print(f"       -> {issue}")
            all_ok = False
        else:
            print(f"  ok  {r['name']} ({size_kb:.0f} KB, {w}x{h}px)")

    print("─" * 57)
    if all_ok:
        print("  모든 이미지 정상 생성")
    else:
        print("  일부 이미지 QA 미통과")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("KR-04 인사로 보는 현대차의 방향 시각화 생성...\n")
    results = []

    results.append(make_layer_chain())
    print("  + 01 5-Layer 체인")

    results.append(make_google_asymmetry())
    print("  + 02 구글의 비대칭")

    results.append(make_two_paths())
    print("  + 03 두 갈래")

    qa_check(results)
    print(f"\n저장 위치: {OUT}\n")
