"""
generate_visuals.py — KR-02 Physical AI 가치 분배 시각화

생성 이미지:
  01_value_distribution.png   — 플랫폼 시대별 가치 분배 구조도
  02_vertical_integration.png — 수직통합 스펙트럼 (Tesla vs Hyundai)

Usage:
    source .venv-wsl/bin/activate && python data/articles/016_KR_데이터-Physical-AI/generate_visuals.py
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
# 01. 플랫폼 시대별 가치 분배 구조도
# ══════════════════════════════════════════════════════════════════════════
def make_value_distribution() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── 제목 ──
    ax.text(0.5, 0.96, "플랫폼 시대별 가치 분배",
            ha="center", va="top", color=WHITE,
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.91, "하드웨어를 만드는 자 vs 생태계를 설계하는 자",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── 3개 컬럼 ──
    cols_x = [0.17, 0.50, 0.83]
    col_w = 0.27
    eras = ["인터넷 시대", "스마트폰 시대", "Physical AI 시대"]

    for x, era in zip(cols_x, eras):
        ax.text(x, 0.84, era, ha="center", va="center",
                color=BLUE, fontsize=11, fontweight="bold")

    # 구분선
    ax.plot([0.335, 0.335], [0.20, 0.82], color=BORDER, linewidth=0.8)
    ax.plot([0.665, 0.665], [0.20, 0.82], color=BORDER, linewidth=0.8)

    # ── 데이터 ──
    winners = [
        ("서비스 / 검색", "Google", "$2T", GREEN),
        ("OS / 앱스토어", "Apple", "이익 85%", GREEN),
        ("AI 두뇌 / 인프라", "NVIDIA / Google", "?", BLUE),
    ]
    losers = [
        ("인프라 / 통신", "AT&T", "$130B", GRAY),
        ("하드웨어 제조", "Samsung", "이익 12%", GRAY),
        ("본체 제조", "현대차", "?", GRAY),
    ]
    gaps = ["x15배", "x7배", "?"]

    winner_y = 0.70
    loser_y = 0.44
    block_h = 0.16

    # 좌측 레이블
    ax.text(0.03, winner_y, "가치\n집중", ha="center", va="center",
            color=GREEN, fontsize=8.5, fontweight="bold", linespacing=1.6)
    ax.text(0.03, loser_y, "가치\n이탈", ha="center", va="center",
            color=RED, fontsize=8.5, fontweight="bold", linespacing=1.6)

    for i in range(3):
        cx = cols_x[i]
        w_label, w_company, w_value, w_color = winners[i]
        l_label, l_company, l_value, l_color = losers[i]
        gap = gaps[i]

        # 상단 블록 (가치 집중)
        _draw_block(ax, cx, winner_y, col_w, block_h,
                    w_color, w_label, w_company, w_value)

        # 갭 표시
        gap_y = (winner_y + loser_y) / 2
        gap_color = YELLOW if gap != "?" else DIM
        ax.text(cx, gap_y, gap, ha="center", va="center",
                color=gap_color, fontsize=15, fontweight="bold")

        # 하단 블록 (가치 이탈)
        _draw_block(ax, cx, loser_y, col_w, block_h,
                    l_color, l_label, l_company, l_value)

    # ── 하단 인사이트 박스 ──
    box = mpatches.FancyBboxPatch(
        (0.06, 0.05), 0.88, 0.15,
        boxstyle="round,pad=0.015",
        facecolor=BG2, edgecolor=YELLOW, linewidth=1.2)
    ax.add_patch(box)

    ax.text(0.5, 0.165, "반복되는 패턴",
            ha="center", va="center", color=YELLOW,
            fontsize=13, fontweight="bold")
    ax.text(0.5, 0.12,
            "하드웨어를 만드는 자와,",
            ha="center", va="center", color=WHITE, fontsize=10.5)
    ax.text(0.5, 0.092,
            "생태계를 설계하는 자 사이의 가치 분배는",
            ha="center", va="center", color=WHITE, fontsize=10.5)
    ax.text(0.5, 0.064,
            "언제나 후자에게 기울었다.",
            ha="center", va="center", color=GREEN,
            fontsize=11.5, fontweight="bold")

    return _save(fig, "01_value_distribution.png")


def _draw_block(ax, cx, cy, w, h, border_color,
                label, company, value):
    """Draw a rounded block with label, company name, and value."""
    box = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.012",
        facecolor=BG2, edgecolor=border_color,
        linewidth=2, alpha=0.9)
    ax.add_patch(box)

    ax.text(cx, cy + h * 0.30, label,
            ha="center", va="center", color=DIM, fontsize=8)
    ax.text(cx, cy + h * 0.02, company,
            ha="center", va="center", color=WHITE,
            fontsize=12, fontweight="bold")
    ax.text(cx, cy - h * 0.28, value,
            ha="center", va="center", color=border_color,
            fontsize=13, fontweight="bold")


# ══════════════════════════════════════════════════════════════════════════
# 02. 수직통합 스펙트럼 — Tesla vs Hyundai
# ══════════════════════════════════════════════════════════════════════════
def make_vertical_integration() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── 제목 ──
    ax.text(0.5, 0.96, "수직통합 스펙트럼",
            ha="center", va="top", color=WHITE,
            fontsize=18, fontweight="bold")
    ax.text(0.5, 0.91, "로봇 사업에서 각 기업이 소유하는 레이어",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── 컬럼 헤더 ──
    ax.text(0.24, 0.855, "Tesla",
            ha="center", va="center", color=GREEN,
            fontsize=16, fontweight="bold")
    ax.text(0.76, 0.855, "Hyundai",
            ha="center", va="center", color=BLUE,
            fontsize=16, fontweight="bold")

    # ── 레이어 정의 ──
    layers = [
        "AI 두뇌 / 모델",
        "훈련 데이터",
        "컴퓨팅 인프라",
        "시뮬레이션",
        "본체 제조",
    ]

    tesla_data = [
        ("자체 FSD / Optimus AI", GREEN),
        ("수십억 마일 주행 데이터", GREEN),
        ("NVIDIA GPU + Dojo (자체 전환 중)", YELLOW),
        ("자체 시뮬레이션 환경", GREEN),
        ("Fremont / Austin 공장", GREEN),
    ]

    hyundai_data = [
        ("Google DeepMind", RED),
        ("Google 축적", RED),
        ("NVIDIA Blackwell 5만장", ORANGE),
        ("NVIDIA Cosmos / Omniverse", ORANGE),
        ("새만금 로봇 공장", GREEN),
    ]

    n = len(layers)
    layer_top = 0.80
    layer_bottom = 0.25
    layer_h = (layer_top - layer_bottom) / n
    block_h = layer_h * 0.72
    block_w_side = 0.30

    left_cx = 0.24
    right_cx = 0.76

    for i in range(n):
        cy = layer_top - (i + 0.5) * layer_h
        t_desc, t_color = tesla_data[i]
        h_desc, h_color = hyundai_data[i]

        # 중앙 레이어 라벨
        ax.text(0.50, cy, layers[i],
                ha="center", va="center", color=WHITE,
                fontsize=9.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25",
                          facecolor=BG, edgecolor=BORDER, linewidth=0.8))

        # Tesla 블록 (좌)
        _draw_ownership(ax, left_cx, cy, block_w_side, block_h,
                        t_color, t_desc)

        # Hyundai 블록 (우)
        _draw_ownership(ax, right_cx, cy, block_w_side, block_h,
                        h_color, h_desc)

    # ── 수직 소유 비율 바 ──
    bar_w = 0.012
    bar_top = layer_top
    bar_bot = layer_bottom

    # Tesla: 대부분 GREEN, 컴퓨팅만 YELLOW (3번째 = index 2)
    t_bar_x = left_cx - block_w_side / 2 - 0.025
    # 상위 2레이어 (AI 두뇌, 훈련 데이터) = GREEN
    ax.add_patch(mpatches.FancyBboxPatch(
        (t_bar_x, bar_bot + layer_h * 3), bar_w, layer_h * 2,
        boxstyle="round,pad=0.002",
        facecolor=GREEN, alpha=0.4))
    # 중간 1레이어 (컴퓨팅 인프라) = YELLOW
    ax.add_patch(mpatches.FancyBboxPatch(
        (t_bar_x, bar_bot + layer_h * 2), bar_w, layer_h,
        boxstyle="round,pad=0.002",
        facecolor=YELLOW, alpha=0.4))
    # 하위 2레이어 (시뮬레이션, 본체 제조) = GREEN
    ax.add_patch(mpatches.FancyBboxPatch(
        (t_bar_x, bar_bot), bar_w, layer_h * 2,
        boxstyle="round,pad=0.002",
        facecolor=GREEN, alpha=0.4))
    ax.text(t_bar_x + bar_w / 2, bar_top + 0.015, "4/5",
            ha="center", va="bottom", color=GREEN,
            fontsize=9, fontweight="bold")

    # Hyundai: 상위 4 RED/ORANGE, 하위 1 GREEN
    h_bar_x = right_cx + block_w_side / 2 + 0.013
    ext_h = layer_h * 4
    own_h = layer_h * 1
    ax.add_patch(mpatches.FancyBboxPatch(
        (h_bar_x, bar_bot + own_h), bar_w, ext_h,
        boxstyle="round,pad=0.002",
        facecolor=RED, alpha=0.3))
    ax.add_patch(mpatches.FancyBboxPatch(
        (h_bar_x, bar_bot), bar_w, own_h,
        boxstyle="round,pad=0.002",
        facecolor=GREEN, alpha=0.4))
    ax.text(h_bar_x + bar_w / 2, bar_top + 0.015, "1/5",
            ha="center", va="bottom", color=RED,
            fontsize=9, fontweight="bold")

    # ── 수직 구분선 ──
    ax.plot([0.50, 0.50], [bar_bot - 0.01, bar_top + 0.01],
            color=BORDER, linewidth=0.5, linestyle=":", alpha=0.4)

    # ── 하단 인사이트 박스 ──
    box = mpatches.FancyBboxPatch(
        (0.06, 0.04), 0.88, 0.16,
        boxstyle="round,pad=0.015",
        facecolor=BG2, edgecolor=BORDER, linewidth=1)
    ax.add_patch(box)

    ax.text(0.5, 0.165,
            "통합이란 결국 이것이다.",
            ha="center", va="center", color=WHITE,
            fontsize=12, fontweight="bold")
    ax.text(0.5, 0.125,
            '"교체 불가능한 것"을 최대한 많이 소유하는 것.',
            ha="center", va="center", color=YELLOW,
            fontsize=10.5)
    ax.text(0.5, 0.085,
            "애플은 그렇게 했다. 테슬라는 그렇게 하고 있다.",
            ha="center", va="center", color=DIM, fontsize=9.5)
    ax.text(0.5, 0.055,
            "삼성은 그러지 못했다. 현대차는?",
            ha="center", va="center", color=RED,
            fontsize=10, fontweight="bold")

    return _save(fig, "02_vertical_integration.png")


def _draw_ownership(ax, cx, cy, w, h, color, desc):
    """Draw an ownership indicator block."""
    alpha_fill = 0.15 if color != GREEN else 0.20
    box = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.008",
        facecolor=color, alpha=alpha_fill,
        edgecolor=color, linewidth=1.3)
    ax.add_patch(box)

    ax.text(cx, cy, desc,
            ha="center", va="center", color=WHITE,
            fontsize=8.5)


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
    print("KR-02 Physical AI 가치 분배 시각화 생성...\n")
    results = []

    results.append(make_value_distribution())
    print("  + 01 플랫폼 시대별 가치 분배")

    results.append(make_vertical_integration())
    print("  + 02 수직통합 스펙트럼")

    qa_check(results)
    print(f"\n저장 위치: {OUT}\n")
