"""
generate_visuals.py — SpaceX 비용혁명과 달 시각화 생성

생성 이미지:
  01_cost_revolution.png  — 발사 비용 혁명 ($/kg LEO)
  02_starship_flights.png — Starship 비행 시험 마일스톤
  03_moon_pivot.png       — 달 vs 화성 비교 카드
  04_cost_unlocks.png     — 비용 임계점별 우주 산업

Usage:
    python data/articles/012_TSLA_SpaceX-비용혁명과-달/generate_visuals.py
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np

# ── paths ─────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# ── korean font ───────────────────────────────────────────────────────────────
_FONT_PATH = os.path.expanduser("~/.fonts/NotoSansCJK-Regular.ttc")
_FONT_PATH_FALLBACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if not os.path.exists(_FONT_PATH):
    _FONT_PATH = _FONT_PATH_FALLBACK
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── palette ───────────────────────────────────────────────────────────────────
BG      = "#0d1117"
CARD_BG = "#161b22"
GREEN   = "#3fb950"
YELLOW  = "#d29922"
BLUE    = "#58a6ff"
RED     = "#f85149"
ORANGE  = "#db6d28"
GRAY    = "#6e7681"
WHITE   = "#e6edf3"
DIM     = "#8b949e"
BORDER  = "#30363d"
CYAN    = "#56d4dd"
PURPLE  = "#bc8cff"


def _save(fig: plt.Figure, path: Path, name: str) -> dict:
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.15)
    plt.close(fig)
    size = path.stat().st_size
    return {"name": name, "path": str(path), "size": size, "ok": size > 10_000}


def qa_check(results: list[dict]) -> None:
    from PIL import Image
    print("\n── QA 결과 " + "─" * 50)
    all_ok = True
    for r in results:
        issues = []
        p = Path(r["path"])
        if r["size"] < 10_000:
            issues.append(f"파일 크기 부족 ({r['size']:,} B)")
        with Image.open(p) as img:
            w, h = img.size
            if w < 900 or h < 900:
                issues.append(f"해상도 부족 ({w}x{h})")
        if issues:
            print(f"  ❌  {r['name']:<40}  {r['size']:>8,} B")
            for i in issues:
                print(f"       -> {i}")
            all_ok = False
        else:
            print(f"  ✅  {r['name']:<40}  {r['size']:>8,} B  ({w}x{h})")
    print("─" * 62)
    if all_ok:
        print("  모든 이미지 정상 생성")
    else:
        print("  ⚠️  일부 이미지 QA 실패")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# 01. 발사 비용 혁명 — $/kg LEO 비교
# ══════════════════════════════════════════════════════════════════════════════
def make_cost_revolution() -> dict:
    data = [
        ("Space Shuttle",       54500, RED,    "1981~2011"),
        ("Falcon 9 (고객가)",    2720, ORANGE, "2010~"),
        ("Falcon 9 (내부 비용)",  630, YELLOW, "2025~"),
        ("Starship (목표)",       100, GREEN,  "완전 재사용"),
    ]

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.96, "97% — 비용 혁명",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold")
    ax.text(0.50, 0.925, "LEO까지 1kg 보내는 비용 ($/kg)",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── bars (log-proportional width) ──
    n = len(data)
    row_h = 0.115
    row_gap = 0.025
    y_start = 0.86
    max_log = np.log10(data[0][1])
    bar_left = 0.33
    bar_max_w = 0.53

    for i, (name, cost, color, era) in enumerate(data):
        y_top = y_start - i * (row_h + row_gap)
        y_mid = y_top - row_h / 2

        # row background
        row_bg = mpatches.FancyBboxPatch(
            (0.03, y_top - row_h), 0.94, row_h,
            boxstyle="round,pad=0.008",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.5,
            transform=ax.transAxes)
        ax.add_patch(row_bg)

        # accent bar (left edge)
        accent = mpatches.FancyBboxPatch(
            (0.035, y_top - row_h + 0.01), 0.005, row_h - 0.02,
            boxstyle="round,pad=0.001", facecolor=color,
            transform=ax.transAxes)
        ax.add_patch(accent)

        # name + era (left column)
        ax.text(0.06, y_mid + 0.018, name,
                ha="left", va="center", color=WHITE,
                fontsize=10.5, fontweight="bold")
        ax.text(0.06, y_mid - 0.018, era,
                ha="left", va="center", color=DIM, fontsize=8.5)

        # cost bar (log-proportional)
        log_val = np.log10(cost)
        w = (log_val / max_log) * bar_max_w
        bar = mpatches.FancyBboxPatch(
            (bar_left, y_top - row_h + 0.025), w, row_h - 0.05,
            boxstyle="round,pad=0.004",
            facecolor=color, alpha=0.8,
            transform=ax.transAxes)
        ax.add_patch(bar)

        # value label
        val_x = bar_left + w + 0.02
        ax.text(val_x, y_mid, f"${cost:,}",
                ha="left", va="center", color=color,
                fontsize=14, fontweight="bold")

    # ── bottom: reduction summary ──
    bot_y = y_start - n * (row_h + row_gap) - 0.015
    ax.plot([0.10, 0.90], [bot_y, bot_y],
            color=BORDER, lw=1, transform=ax.transAxes)

    ax.text(0.50, bot_y - 0.03, "Space Shuttle → Starship : 545배 절감",
            ha="center", va="top", color=GREEN,
            fontsize=13, fontweight="bold")
    ax.text(0.50, bot_y - 0.07,
            "\"원자재 비용은 완성 로켓의 3%에 불과했다.\n97%는 비효율이었다.\"",
            ha="center", va="top", color=DIM,
            fontsize=9.5, fontstyle="italic", multialignment="center")

    # ── SpaceX market share mini section ──
    share_y = bot_y - 0.14
    ax.text(0.50, share_y, "글로벌 발사 점유율",
            ha="center", va="top", color=WHITE,
            fontsize=12, fontweight="bold")

    share_data = [
        ("2015",   7,  87),
        ("2020",  25, 114),
        ("2024", 134, 260),
        ("2025", 167, 320),
    ]

    bar_h = 0.03
    bar_gap = 0.012
    bar_area_left = 0.18
    bar_area_w = 0.55
    sy = share_y - 0.04

    for j, (year, spx, total) in enumerate(share_data):
        y_s = sy - j * (bar_h + bar_gap)
        pct = spx / total

        # year
        ax.text(bar_area_left - 0.03, y_s - bar_h / 2, year,
                ha="right", va="center", color=DIM,
                fontsize=9, fontweight="bold")

        # bg bar
        bg_bar = mpatches.FancyBboxPatch(
            (bar_area_left, y_s - bar_h), bar_area_w, bar_h,
            boxstyle="round,pad=0.003",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.3,
            transform=ax.transAxes)
        ax.add_patch(bg_bar)

        # SpaceX bar
        spx_w = pct * bar_area_w
        spx_bar = mpatches.FancyBboxPatch(
            (bar_area_left, y_s - bar_h), spx_w, bar_h,
            boxstyle="round,pad=0.003",
            facecolor=BLUE, alpha=0.8,
            transform=ax.transAxes)
        ax.add_patch(spx_bar)

        # pct label
        ax.text(bar_area_left + bar_area_w + 0.02, y_s - bar_h / 2,
                f"{pct:.0%}  ({spx}회)",
                ha="left", va="center", color=BLUE,
                fontsize=8.5, fontweight="bold")

    return _save(fig, OUT / "01_cost_revolution.png", "01_cost_revolution")


# ══════════════════════════════════════════════════════════════════════════════
# 02. Starship 비행 시험 마일스톤
# ══════════════════════════════════════════════════════════════════════════════
def make_starship_flights() -> dict:
    # (flight, date, result, category)
    # category: fail=RED, partial=YELLOW, success=GREEN, milestone=BLUE, special=ORANGE
    flights = [
        ("IFT-1",  "2023.4",  "T+4:00 폭발",                     RED),
        ("IFT-2",  "2023.11", "분리 성공, 양쪽 상실",             YELLOW),
        ("IFT-3",  "2024.3",  "우주 도달, 재진입 실패",           YELLOW),
        ("IFT-4",  "2024.6",  "양쪽 해상 착수 성공",              GREEN),
        ("IFT-5",  "2024.10", "★ 최초 부스터 타워 캐치",         BLUE),
        ("IFT-6",  "2024.11", "캐치 미시도, 해상 착수",           YELLOW),
        ("IFT-7",  "2025.1",  "2차 캐치 성공, 우주선 상실",       BLUE),
        ("IFT-8",  "2025.3",  "3차 캐치, 우주선 상실",            BLUE),
        ("IFT-9",  "2025.5",  "최초 부스터 재사용 (B14)",         ORANGE),
        ("IFT-10", "2025.8",  "★ 최초 우주선 해상 착륙",         BLUE),
        ("IFT-11", "2025.10", "2차 착륙 + 뱅킹 기동",            BLUE),
    ]

    fig, ax = plt.subplots(figsize=(8, 10), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.97, "Starship — 2.5년, 11번",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold")
    ax.text(0.50, 0.945, "SLS는 같은 기간 1번 날았다",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── vertical timeline ──
    LINE_X = 0.18
    n = len(flights)
    ev_spacing = 0.068
    y_start = 0.895
    line_bot = y_start - (n - 1) * ev_spacing - 0.04

    ax.plot([LINE_X, LINE_X], [y_start + 0.015, line_bot],
            color=BORDER, linewidth=2.5, transform=ax.transAxes, zorder=1)

    for i, (flight, date, result, color) in enumerate(flights):
        y = y_start - i * ev_spacing

        # date (left of line)
        ax.text(LINE_X - 0.025, y, date,
                ha="right", va="center", color=DIM,
                fontsize=9, fontweight="bold")

        # dot on line (outer + inner)
        ax.scatter(LINE_X, y, s=100, color=color, zorder=4,
                   transform=ax.transAxes)
        ax.scatter(LINE_X, y, s=25, color=BG, zorder=5,
                   transform=ax.transAxes)

        # connector line
        ax.plot([LINE_X + 0.015, LINE_X + 0.045], [y, y],
                color=color, lw=1.2, alpha=0.5,
                transform=ax.transAxes, zorder=2)

        # flight name
        ax.text(LINE_X + 0.055, y + 0.012, flight,
                ha="left", va="center", color=color,
                fontsize=11, fontweight="bold")

        # result
        ax.text(LINE_X + 0.055, y - 0.016, result,
                ha="left", va="center", color=WHITE if "★" in result else DIM,
                fontsize=9)

    # ── legend ──
    legend_y = line_bot - 0.04
    ax.plot([0.05, 0.95], [legend_y + 0.02, legend_y + 0.02],
            color=BORDER, lw=1, transform=ax.transAxes)

    cats = [
        (RED, "실패"), (YELLOW, "부분 성공"), (GREEN, "성공"),
        (BLUE, "마일스톤"), (ORANGE, "특별"),
    ]
    total_w = len(cats) * 0.18
    lx_start = 0.5 - total_w / 2

    for j, (c, label) in enumerate(cats):
        lx = lx_start + j * 0.18
        ax.scatter(lx, legend_y, s=50, color=c, transform=ax.transAxes)
        ax.text(lx + 0.02, legend_y, label,
                ha="left", va="center", color=c,
                fontsize=8.5)

    # ── bottom stats ──
    stat_y = legend_y - 0.05
    stats = [
        ("부스터 캐치", "3회", GREEN),
        ("부스터 재사용", "1회", ORANGE),
        ("우주선 착륙", "2회", BLUE),
    ]

    for k, (label, val, color) in enumerate(stats):
        sx = 0.18 + k * 0.27
        ax.text(sx, stat_y, val, ha="center", va="center",
                color=color, fontsize=16, fontweight="bold")
        ax.text(sx, stat_y - 0.03, label, ha="center", va="center",
                color=DIM, fontsize=9)

    return _save(fig, OUT / "02_starship_flights.png", "02_starship_flights")


# ══════════════════════════════════════════════════════════════════════════════
# 03. 달 vs 화성 — 왜 달 먼저인가
# ══════════════════════════════════════════════════════════════════════════════
def make_moon_pivot() -> dict:
    rows = [
        ("편도 시간",    "3일",       "6~9개월"),
        ("발사 창",      "상시",      "26개월마다"),
        ("통신 지연",    "1.3초",     "4~24분"),
        ("왕복 주기",    "~10일",     "~26개월"),
        ("10년 반복",    "365회",     "4회"),
    ]

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.96, "왜 화성이 아니라 달 먼저인가",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold")
    ax.text(0.50, 0.925, "2026년 2월 — 머스크의 피봇",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── column headers ──
    hdr_y = 0.885
    ax.text(0.38, hdr_y, "달", ha="center", va="center",
            color=CYAN, fontsize=13, fontweight="bold")
    ax.text(0.72, hdr_y, "화성", ha="center", va="center",
            color=RED, fontsize=13, fontweight="bold")
    ax.plot([0.04, 0.96], [hdr_y - 0.02, hdr_y - 0.02],
            color=BORDER, lw=1, transform=ax.transAxes)

    # ── rows ──
    n = len(rows)
    row_h = 0.115
    row_gap = 0.018
    y_start = 0.84

    for i, (cat, moon_val, mars_val) in enumerate(rows):
        y_top = y_start - i * (row_h + row_gap)
        y_mid = y_top - row_h / 2

        # row bg
        row_bg = mpatches.FancyBboxPatch(
            (0.03, y_top - row_h), 0.94, row_h,
            boxstyle="round,pad=0.008",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.5,
            transform=ax.transAxes)
        ax.add_patch(row_bg)

        # accent bar
        accent = mpatches.FancyBboxPatch(
            (0.035, y_top - row_h + 0.01), 0.005, row_h - 0.02,
            boxstyle="round,pad=0.001", facecolor=BLUE,
            transform=ax.transAxes)
        ax.add_patch(accent)

        # category label
        ax.text(0.12, y_mid, cat, ha="center", va="center",
                color=WHITE, fontsize=10.5, fontweight="bold")

        # moon card
        m_bg = mpatches.FancyBboxPatch(
            (0.22, y_top - row_h + 0.015), 0.32, row_h - 0.03,
            boxstyle="round,pad=0.008",
            facecolor="#0d1a1a", edgecolor="#1a3d3d", linewidth=0.6,
            transform=ax.transAxes)
        ax.add_patch(m_bg)
        ax.text(0.38, y_mid, moon_val, ha="center", va="center",
                color=CYAN, fontsize=14, fontweight="bold")

        # mars card
        r_bg = mpatches.FancyBboxPatch(
            (0.56, y_top - row_h + 0.015), 0.40, row_h - 0.03,
            boxstyle="round,pad=0.008",
            facecolor="#1a1215", edgecolor="#3d2020", linewidth=0.6,
            transform=ax.transAxes)
        ax.add_patch(r_bg)
        ax.text(0.72, y_mid, mars_val, ha="center", va="center",
                color=RED, fontsize=14, fontweight="bold")

    # ── bottom emphasis ──
    bot_y = y_start - n * (row_h + row_gap) - 0.025
    ax.plot([0.10, 0.90], [bot_y, bot_y],
            color=BORDER, lw=1, transform=ax.transAxes)

    # key quote
    ax.text(0.50, bot_y - 0.03, "\"달에서 실패하면 3일 만에 돌아온다.\"",
            ha="center", va="top", color=CYAN,
            fontsize=11, fontweight="bold")
    ax.text(0.50, bot_y - 0.065, "\"화성에서 실패하면 죽는다.\"",
            ha="center", va="top", color=RED,
            fontsize=11, fontweight="bold")

    # Shackleton note
    ax.text(0.50, bot_y - 0.12, "Shackleton Crater — 전력·냉각·물이 한 곳에",
            ha="center", va="top", color=YELLOW,
            fontsize=10, fontweight="bold")
    ax.text(0.50, bot_y - 0.155,
            "림 92~95% 일조  ·  내부 -253°C  ·  수분 얼음 확인",
            ha="center", va="top", color=DIM, fontsize=9)

    return _save(fig, OUT / "03_moon_pivot.png", "03_moon_pivot")


# ══════════════════════════════════════════════════════════════════════════════
# 04. 비용 임계점 — $/kg별 열리는 산업
# ══════════════════════════════════════════════════════════════════════════════
def make_cost_unlocks() -> dict:
    tiers = [
        ("$2,700",  "현재 (Falcon 9)", [
            "Starlink 위성 배치", "ISS 보급",
        ], GRAY),
        ("$100",    "Starship 초기", [
            "테라팹 D3 위성 대량 투입", "Optimus 궤도 투입",
        ], YELLOW),
        ("$50",     "Starship 성숙", [
            "궤도 데이터센터 — xAI 연산 이전", "",
        ], BLUE),
        ("$20",     "대량 운용", [
            "달 정기 화물", "Tesla Energy + Optimus 달 기지",
        ], CYAN),
        ("$10",     "장기 목표", [
            "달 산업 기지", "화성 전초기지",
        ], GREEN),
    ]

    fig, ax = plt.subplots(figsize=(8, 9), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.97, "모든 길은 Starship으로",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold")
    ax.text(0.50, 0.94, "$/kg이 내려갈수록 열리는 산업이 달라진다",
            ha="center", va="top", color=DIM, fontsize=10)

    # ── step chart ──
    n = len(tiers)
    row_h = 0.13
    row_gap = 0.02
    y_start = 0.88

    # vertical step line
    step_x = 0.15
    line_top = y_start
    line_bot = y_start - (n - 1) * (row_h + row_gap) - row_h
    ax.plot([step_x, step_x], [line_top, line_bot],
            color=BORDER, linewidth=2, transform=ax.transAxes, zorder=1)

    for i, (price, era, items, color) in enumerate(tiers):
        y_top = y_start - i * (row_h + row_gap)
        y_mid = y_top - row_h / 2

        # dot on step line
        ax.scatter(step_x, y_mid, s=120, color=color, zorder=4,
                   transform=ax.transAxes)
        ax.scatter(step_x, y_mid, s=30, color=BG, zorder=5,
                   transform=ax.transAxes)

        # price label (left)
        ax.text(step_x - 0.03, y_mid + 0.015, price,
                ha="right", va="center", color=color,
                fontsize=14, fontweight="bold")
        ax.text(step_x - 0.03, y_mid - 0.02, era,
                ha="right", va="center", color=DIM,
                fontsize=8)

        # connector
        ax.plot([step_x + 0.015, step_x + 0.04], [y_mid, y_mid],
                color=color, lw=1.5, alpha=0.5,
                transform=ax.transAxes, zorder=2)

        # content card
        card_left = step_x + 0.05
        card_w = 0.78
        card = mpatches.FancyBboxPatch(
            (card_left, y_top - row_h + 0.005), card_w, row_h - 0.01,
            boxstyle="round,pad=0.008",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.5,
            transform=ax.transAxes)
        ax.add_patch(card)

        # accent bar
        accent = mpatches.FancyBboxPatch(
            (card_left + 0.005, y_top - row_h + 0.015), 0.004, row_h - 0.03,
            boxstyle="round,pad=0.001", facecolor=color,
            transform=ax.transAxes)
        ax.add_patch(accent)

        # items as pills/tags
        tag_x = card_left + 0.03
        tag_y = y_mid + 0.01 if len(items) > 2 else y_mid
        for j, item in enumerate(items):
            if len(items) <= 2:
                # single row
                ax.text(tag_x, y_mid, "  ·  ".join(items),
                        ha="left", va="center", color=WHITE,
                        fontsize=10)
                break
            else:
                # multi row
                row_offset = (j - (len(items) - 1) / 2) * 0.03
                ax.text(tag_x, y_mid - row_offset, f"·  {item}",
                        ha="left", va="center", color=WHITE,
                        fontsize=9.5)

    # ── bottom: apollo comparison ──
    bot_y = line_bot - 0.04
    ax.plot([0.05, 0.95], [bot_y + 0.015, bot_y + 0.015],
            color=BORDER, lw=1, transform=ax.transAxes)

    ax.text(0.50, bot_y - 0.01,
            "달 1kg 배송비:  Apollo \$1,700만  →  Starship \$1,100",
            ha="center", va="top", color=GREEN,
            fontsize=11, fontweight="bold")
    ax.text(0.50, bot_y - 0.05, "2,200배 절감 — 불가능이 가능으로 바뀌는 임계점",
            ha="center", va="top", color=DIM, fontsize=9.5)

    return _save(fig, OUT / "04_cost_unlocks.png", "04_cost_unlocks")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("SpaceX 비용혁명과 달 — 시각화 생성 시작...\n")
    results = []

    results.append(make_cost_revolution())
    print("  [1/4] 01_cost_revolution.png")

    results.append(make_starship_flights())
    print("  [2/4] 02_starship_flights.png")

    results.append(make_moon_pivot())
    print("  [3/4] 03_moon_pivot.png")

    results.append(make_cost_unlocks())
    print("  [4/4] 04_cost_unlocks.png")

    qa_check(results)
    print(f"\n저장 위치: {OUT}\n")
