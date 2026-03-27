"""KR-08 반도체 팹 — $650억의 해부와 테라팹 — 시각화 생성 스크립트."""

import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
from PIL import Image

# ── 경로 설정 ──────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "visuals")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 폰트 설정 ──────────────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 팔레트 ────────────────────────────────────────────
BG = "#0d1117"
CARD_BG = "#161b22"
GREEN = "#3fb950"
YELLOW = "#d29922"
BLUE = "#58a6ff"
RED = "#f85149"
ORANGE = "#db6d28"
GRAY = "#6e7681"
WHITE = "#e6edf3"
LIGHT_GRAY = "#8b949e"
BORDER = "#30363d"

DPI = 180
SIZE_PX = 1080
SIZE_IN = SIZE_PX / DPI


def fig_base(height_ratio=1.0):
    """Create a dark-themed figure."""
    fig = plt.figure(
        figsize=(SIZE_IN, SIZE_IN * height_ratio),
        dpi=DPI,
        facecolor=BG,
    )
    return fig


# ═══════════════════════════════════════════════════════════
# Visual 1: 팹 비용 해부도 — $650억의 분해
# ═══════════════════════════════════════════════════════════
def gen_fab_cost_anatomy():
    """팹 비용 해부도 — 4층 구조 + 비용 분해 + 전력 분배."""
    fig = fig_base(height_ratio=1.2)

    # ── Title ──
    fig.text(0.5, 0.96, "팹 비용 해부도", color=WHITE,
             fontsize=18, fontweight="bold", ha="center")
    fig.text(0.5, 0.93, "$200억 규모 첨단 팹의 비용 구조 — 칩 제조 직접 비용은 얼마인가",
             color=LIGHT_GRAY, fontsize=8.5, ha="center")

    # ════════════════════════════════════════════════
    # Section A: 팹 4층 구조 (left half)
    # ════════════════════════════════════════════════
    fig.text(0.05, 0.88, "건물 구조", color=WHITE,
             fontsize=12, fontweight="bold")

    floors = [
        ("4층 — 팬 덱", "공기순환 · HEPA 필터", "~25%", BLUE, "인간 관리"),
        ("3층 — 클린룸", "생산 + 가운룸 · 복도", "~25%", GREEN, "칩 제조"),
        ("2층 — 서브팹", "펌프 · 가스 · 화학배관", "~30%", YELLOW, "공정 지원"),
        ("1층 — 유틸리티", "전기 · 냉각 · HVAC", "~20%", ORANGE, "인프라"),
    ]

    floor_w = 0.42
    floor_h = 0.12
    floor_x = 0.04
    floor_start_y = 0.82

    for i, (name, desc, pct, color, role) in enumerate(floors):
        y = floor_start_y - i * (floor_h + 0.02)

        # Floor block
        rect = mpatches.FancyBboxPatch(
            (floor_x, y - floor_h), floor_w, floor_h,
            boxstyle="round,pad=0.008", facecolor=CARD_BG,
            edgecolor=color, linewidth=1.5,
            transform=fig.transFigure, zorder=1,
        )
        fig.patches.append(rect)

        # Chip manufacturing highlight (only floor 3)
        if i == 1:
            # Green accent background
            accent = mpatches.FancyBboxPatch(
                (floor_x, y - floor_h), floor_w, floor_h,
                boxstyle="round,pad=0.008",
                facecolor=GREEN, alpha=0.08,
                edgecolor="none",
                transform=fig.transFigure, zorder=0,
            )
            fig.patches.append(accent)

        # Floor text
        fig.text(floor_x + 0.02, y - 0.03, name, color=color,
                 fontsize=9.5, fontweight="bold", zorder=2)
        fig.text(floor_x + 0.02, y - 0.065, desc, color=LIGHT_GRAY,
                 fontsize=7.5, zorder=2)
        fig.text(floor_x + floor_w - 0.02, y - 0.03, pct, color=color,
                 fontsize=11, fontweight="bold", ha="right", zorder=2)
        fig.text(floor_x + floor_w - 0.02, y - 0.065, role, color=LIGHT_GRAY,
                 fontsize=7, ha="right", zorder=2)

    # Fab 18 stat box
    stat_y = floor_start_y - 4 * (floor_h + 0.02) - 0.03
    fig.text(0.04, stat_y, "TSMC Fab 18", color=WHITE,
             fontsize=9, fontweight="bold")
    fig.text(0.04, stat_y - 0.03, "총 95만 m²  |  클린룸 16만 m²  |  ", color=LIGHT_GRAY,
             fontsize=7.5)
    fig.text(0.34, stat_y - 0.03, "17%만 칩 제조", color=GREEN,
             fontsize=7.5, fontweight="bold")

    # ════════════════════════════════════════════════
    # Section B: 비용 분해 (right half — horizontal bars)
    # ════════════════════════════════════════════════
    fig.text(0.54, 0.88, "비용 분해 ($200억 기준)", color=WHITE,
             fontsize=12, fontweight="bold")

    ax_cost = fig.add_axes([0.60, 0.58, 0.37, 0.28])
    ax_cost.set_facecolor(CARD_BG)

    cost_items = ["공정 장비", "건물/건설", "클린룸 인프라", "설치/기타"]
    cost_pcts = [62.5, 22.5, 12.5, 5.0]
    cost_colors = [GREEN, BLUE, YELLOW, GRAY]
    cost_amounts = ["$125억", "$45억", "$25억", "$10억"]

    bars = ax_cost.barh(range(len(cost_items)), cost_pcts,
                        color=cost_colors, edgecolor=BG, linewidth=0.5,
                        height=0.6, zorder=3)

    for i, (bar, pct, amt) in enumerate(zip(bars, cost_pcts, cost_amounts)):
        ax_cost.text(bar.get_width() + 1.5, i, f"{pct:.0f}%  ({amt})",
                     color=WHITE, fontsize=8, fontweight="bold",
                     va="center")

    ax_cost.set_yticks(range(len(cost_items)))
    ax_cost.set_yticklabels(cost_items, color=WHITE, fontsize=8.5)
    ax_cost.set_xlim(0, 85)
    ax_cost.invert_yaxis()
    ax_cost.set_xticks([])
    ax_cost.spines["top"].set_visible(False)
    ax_cost.spines["right"].set_visible(False)
    ax_cost.spines["bottom"].set_visible(False)
    ax_cost.spines["left"].set_color(BORDER)
    ax_cost.tick_params(colors=LIGHT_GRAY, length=0)

    # ════════════════════════════════════════════════
    # Section C: 전력 분배 (right bottom — pie-like donut)
    # ════════════════════════════════════════════════
    fig.text(0.54, 0.52, "전력 분배 (100MW 기준)", color=WHITE,
             fontsize=12, fontweight="bold")

    ax_power = fig.add_axes([0.60, 0.22, 0.37, 0.28])
    ax_power.set_facecolor(CARD_BG)

    power_items = ["HVAC/공기순환", "공정 장비", "냉각 (칠러)", "기타 (조명 등)"]
    power_pcts = [40, 45, 12, 3]
    power_colors = [BLUE, GREEN, YELLOW, GRAY]

    bars_p = ax_power.barh(range(len(power_items)), power_pcts,
                           color=power_colors, edgecolor=BG, linewidth=0.5,
                           height=0.6, zorder=3)

    for i, (bar, pct) in enumerate(zip(bars_p, power_pcts)):
        mw = pct  # 100MW 기준이니 pct = MW
        ax_power.text(bar.get_width() + 1.5, i, f"{pct}%  (~{mw}MW)",
                      color=WHITE, fontsize=8, fontweight="bold",
                      va="center")

    ax_power.set_yticks(range(len(power_items)))
    ax_power.set_yticklabels(power_items, color=WHITE, fontsize=8.5)
    ax_power.set_xlim(0, 65)
    ax_power.invert_yaxis()
    ax_power.set_xticks([])
    ax_power.spines["top"].set_visible(False)
    ax_power.spines["right"].set_visible(False)
    ax_power.spines["bottom"].set_visible(False)
    ax_power.spines["left"].set_color(BORDER)
    ax_power.tick_params(colors=LIGHT_GRAY, length=0)

    # ════════════════════════════════════════════════
    # Section D: 오염원 (bottom left)
    # ════════════════════════════════════════════════
    fig.text(0.04, 0.22, "오염원 — 왜 이렇게 많은 비용이 드는가", color=WHITE,
             fontsize=10, fontweight="bold")

    contam_items = [
        ("인간 (피부·호흡·움직임)", "75~80%", RED),
        ("장비·공정", "15~20%", YELLOW),
        ("클린룸 인프라", "2~5%", GRAY),
        ("소모재", "~5%", GRAY),
    ]

    for i, (label, pct, color) in enumerate(contam_items):
        y = 0.18 - i * 0.04
        fig.text(0.06, y, "●", color=color, fontsize=10, va="center")
        fig.text(0.09, y, label, color=WHITE, fontsize=8, va="center")
        fig.text(0.40, y, pct, color=color, fontsize=8.5,
                 fontweight="bold", va="center", ha="right")

    # Callout
    fig.text(0.04, 0.03, "팹의 대부분은 칩이 아니라 인간을 관리하는 데 쓰인다",
             color=YELLOW, fontsize=9, fontweight="bold")

    # Source
    fig.text(0.96, 0.01, "출처: Construction Physics, McKinsey, Cleanroom Connect",
             color=GRAY, fontsize=6, ha="right")

    path = os.path.join(OUT_DIR, "01_fab_cost_anatomy.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 2: 메모리·파운드리 6강 팹 투자 비교
# ═══════════════════════════════════════════════════════════
def gen_fab_investment_6way():
    """메모리 3강 + 파운드리 3강 — CapEx 비교 + 주요 팹 프로젝트."""
    fig = fig_base(height_ratio=1.15)

    # ── Title ──
    fig.text(0.5, 0.96, "반도체 6강 — 팹 투자 비교", color=WHITE,
             fontsize=18, fontweight="bold", ha="center")
    fig.text(0.5, 0.93, "2025년 CapEx + 주요 팹 프로젝트 — 누가 얼마를 어디에 쓰는가",
             color=LIGHT_GRAY, fontsize=8.5, ha="center")

    # ════════════════════════════════════════════════
    # Section A: 파운드리 3강 (top)
    # ════════════════════════════════════════════════
    fig.text(0.05, 0.88, "파운드리 3강 — 2025 CapEx ($B)", color=WHITE,
             fontsize=11, fontweight="bold")

    ax_foundry = fig.add_axes([0.15, 0.62, 0.80, 0.24])
    ax_foundry.set_facecolor(CARD_BG)

    # Foundry data
    foundry_names = ["TSMC", "Intel (전체)", "Samsung\n(파운드리)"]
    foundry_capex = [41, 19, 3.5]  # $B
    foundry_colors = [GREEN, BLUE, RED]

    bars_f = ax_foundry.barh(range(len(foundry_names)), foundry_capex,
                             color=foundry_colors, edgecolor=BG, linewidth=0.5,
                             height=0.55, zorder=3)

    for i, (bar, val) in enumerate(zip(bars_f, foundry_capex)):
        ax_foundry.text(bar.get_width() + 0.5, i, f"${val}B",
                        color=WHITE, fontsize=10, fontweight="bold",
                        va="center")

    # Fab project labels
    fab_projects = [
        "Arizona $1,650억 (3기)",
        "Ohio $200억 (2030 지연)",
        "Taylor $440억 (고객 부재)",
    ]
    for i, proj in enumerate(fab_projects):
        color = foundry_colors[i]
        ax_foundry.text(max(foundry_capex[i] / 2, 2), i + 0.25, proj,
                        color=LIGHT_GRAY, fontsize=7, va="center",
                        ha="center" if foundry_capex[i] > 10 else "left")

    ax_foundry.set_yticks(range(len(foundry_names)))
    ax_foundry.set_yticklabels(foundry_names, color=WHITE, fontsize=9)
    ax_foundry.set_xlim(0, 52)
    ax_foundry.invert_yaxis()
    ax_foundry.set_xticks([])
    ax_foundry.spines["top"].set_visible(False)
    ax_foundry.spines["right"].set_visible(False)
    ax_foundry.spines["bottom"].set_visible(False)
    ax_foundry.spines["left"].set_color(BORDER)
    ax_foundry.tick_params(colors=LIGHT_GRAY, length=0)

    # TSMC is 12x Samsung label
    fig.text(0.92, 0.86, "12배 격차", color=YELLOW,
             fontsize=9, fontweight="bold", ha="right")

    # Separator
    sep = mlines.Line2D([0.05, 0.95], [0.58, 0.58],
                        color=BORDER, linewidth=0.8,
                        transform=fig.transFigure)
    fig.add_artist(sep)

    # ════════════════════════════════════════════════
    # Section B: 메모리 3강 (middle)
    # ════════════════════════════════════════════════
    fig.text(0.05, 0.55, "메모리 3강 — 2025 CapEx ($B)", color=WHITE,
             fontsize=11, fontweight="bold")

    ax_memory = fig.add_axes([0.15, 0.32, 0.80, 0.21])
    ax_memory.set_facecolor(CARD_BG)

    # Memory data (Samsung DS total includes foundry)
    mem_names = ["Samsung\n(DS 전체)", "SK하이닉스", "Micron"]
    mem_capex = [34, 20, 14]  # $B
    mem_colors = [RED, GREEN, YELLOW]

    bars_m = ax_memory.barh(range(len(mem_names)), mem_capex,
                            color=mem_colors, edgecolor=BG, linewidth=0.5,
                            height=0.55, zorder=3)

    for i, (bar, val) in enumerate(zip(bars_m, mem_capex)):
        ax_memory.text(bar.get_width() + 0.5, i, f"${val}B",
                       color=WHITE, fontsize=10, fontweight="bold",
                       va="center")

    # HBM yield annotations
    mem_notes = [
        "메모리+파운드리 분산 | HBM 수율 ~50%",
        "메모리 올인 (85~90% DRAM) | HBM 수율 ~80%",
        "CHIPS Act $62억 | MR-MUF 채택",
    ]
    for i, note in enumerate(mem_notes):
        ax_memory.text(max(mem_capex[i] / 2, 5), i + 0.25, note,
                       color=LIGHT_GRAY, fontsize=6.5, va="center",
                       ha="center" if mem_capex[i] > 15 else "left")

    ax_memory.set_yticks(range(len(mem_names)))
    ax_memory.set_yticklabels(mem_names, color=WHITE, fontsize=9)
    ax_memory.set_xlim(0, 45)
    ax_memory.invert_yaxis()
    ax_memory.set_xticks([])
    ax_memory.spines["top"].set_visible(False)
    ax_memory.spines["right"].set_visible(False)
    ax_memory.spines["bottom"].set_visible(False)
    ax_memory.spines["left"].set_color(BORDER)
    ax_memory.tick_params(colors=LIGHT_GRAY, length=0)

    # Key insight
    fig.text(0.92, 0.53, "투자 규모 ≠ 수율", color=YELLOW,
             fontsize=9, fontweight="bold", ha="right")

    # Separator
    sep2 = mlines.Line2D([0.05, 0.95], [0.28, 0.28],
                         color=BORDER, linewidth=0.8,
                         transform=fig.transFigure)
    fig.add_artist(sep2)

    # ════════════════════════════════════════════════
    # Section C: CHIPS Act 보조금 (bottom)
    # ════════════════════════════════════════════════
    fig.text(0.05, 0.24, "CHIPS Act 보조금 ($B)", color=WHITE,
             fontsize=11, fontweight="bold")

    ax_chips = fig.add_axes([0.15, 0.05, 0.80, 0.18])
    ax_chips.set_facecolor(CARD_BG)

    chips_names = ["Intel", "TSMC", "Micron", "Samsung", "SK하이닉스"]
    chips_amounts = [7.86, 6.6, 6.2, 4.75, 0.46]
    chips_colors = [BLUE, GREEN, YELLOW, RED, GREEN]

    bars_c = ax_chips.barh(range(len(chips_names)), chips_amounts,
                           color=chips_colors, edgecolor=BG, linewidth=0.5,
                           height=0.55, zorder=3)

    for i, (bar, val) in enumerate(zip(bars_c, chips_amounts)):
        ax_chips.text(bar.get_width() + 0.15, i, f"${val}B",
                      color=WHITE, fontsize=8, fontweight="bold",
                      va="center")

    ax_chips.set_yticks(range(len(chips_names)))
    ax_chips.set_yticklabels(chips_names, color=WHITE, fontsize=8)
    ax_chips.set_xlim(0, 10)
    ax_chips.invert_yaxis()
    ax_chips.set_xticks([])
    ax_chips.spines["top"].set_visible(False)
    ax_chips.spines["right"].set_visible(False)
    ax_chips.spines["bottom"].set_visible(False)
    ax_chips.spines["left"].set_color(BORDER)
    ax_chips.tick_params(colors=LIGHT_GRAY, length=0)

    # Source
    fig.text(0.96, 0.01, "출처: TrendForce, CHIPS Act Tracker, 각사 IR | 2025 기준",
             color=GRAY, fontsize=6, ha="right")

    path = os.path.join(OUT_DIR, "02_fab_investment_6way.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# QA Check
# ═══════════════════════════════════════════════════════════
def qa_check():
    """이미지 QA — 파일 크기, 해상도 확인."""
    print("\n── QA Check ──")
    files = sorted(
        f for f in os.listdir(OUT_DIR)
        if f.endswith(".png")
    )
    if not files:
        print("  ⚠ 생성된 이미지 없음")
        return False

    all_ok = True
    for fname in files:
        fpath = os.path.join(OUT_DIR, fname)
        size_kb = os.path.getsize(fpath) / 1024
        try:
            img = Image.open(fpath)
            w, h = img.size
            img.close()
        except Exception as e:
            print(f"  ✗ {fname} — 열기 실패: {e}")
            all_ok = False
            continue

        issues = []
        if size_kb < 10:
            issues.append(f"파일 크기 {size_kb:.0f}KB < 10KB")
        if w < 800 or h < 800:
            issues.append(f"해상도 {w}×{h} < 800×800")

        if issues:
            print(f"  ✗ {fname} ({w}×{h}, {size_kb:.0f}KB) — {', '.join(issues)}")
            all_ok = False
        else:
            print(f"  ✓ {fname} ({w}×{h}, {size_kb:.0f}KB)")

    if all_ok:
        print("  ── 모든 이미지 QA 통과 ──")
    else:
        print("  ── QA 실패 항목 있음 ──")
    return all_ok


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("KR-08 시각화 생성 시작\n")
    gen_fab_cost_anatomy()
    gen_fab_investment_6way()
    qa_check()
    print("\n완료")
