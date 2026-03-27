"""
generate_visuals.py — 궤도 데이터센터 시각화 생성

생성 이미지:
  01_earth_vs_orbit.png — 지구 DC vs 궤도 DC 비교 카드
  03_challenges.png     — 도전과 돌파 요약 카드
  04_timeline.png       — 궤도 DC 타임라인 (수직 레이아웃)

Usage:
    python data/articles/013_TSLA_궤도-데이터센터/generate_visuals.py
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# ── korean font ───────────────────────────────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
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
# 01. 지구 DC vs 궤도 DC 비교 카드
# ══════════════════════════════════════════════════════════════════════════════
def make_comparison_card() -> dict:
    rows = [
        # (category, earth_number, earth_details, orbit_number, orbit_details)
        ("전력",   "포화",          ["수요 945 TWh (2030, +128%)", "아일랜드: 국가 전력 22%"],
                   "무제한",        ["태양광 1,366 W/m², 24/7", "인허가·용량 제약 없음"]),
        ("냉각",   "30~40%",       ["전력의 1/3이 냉각에 소비", "칠러 + 냉각탑 + 물"],
                   "0%",           ["T\u2074 복사 냉각", "추가 전력·물 불필요"]),
        ("수자원", "수영장 2개/일", ["MS 단일 데이터센터", "전체 물 소비 +34% YoY"],
                   "0",            ["진공 환경", "물 자체가 불필요"]),
        ("부지",   "11배 폭등",    ["버지니아 전력 용량 가격", "$30 → $330/MW-day"],
                   "무제한",       ["궤도 슬롯 무한", "NIMBY·인허가 없음"]),
    ]

    fig, ax = plt.subplots(figsize=(8, 8), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.96, "왜 데이터센터가 우주로 가는가",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.925, "지구에 남은 용량이 없다",
            ha="center", va="top", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # ── column headers ──
    hdr_y = 0.885
    ax.text(0.31, hdr_y, "지구 DC", ha="center", va="center",
            color=RED, fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.text(0.755, hdr_y, "궤도 DC", ha="center", va="center",
            color=GREEN, fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.plot([0.04, 0.96], [hdr_y - 0.02, hdr_y - 0.02],
            color=BORDER, lw=1, transform=ax.transAxes)

    # ── rows ──
    n = len(rows)
    row_h = 0.17
    gap = 0.015
    y_start = 0.845

    for i, (cat, e_num, e_lines, o_num, o_lines) in enumerate(rows):
        y_top = y_start - i * (row_h + gap)
        y_mid = y_top - row_h / 2

        # row background
        row_rect = mpatches.FancyBboxPatch(
            (0.03, y_top - row_h), 0.94, row_h,
            boxstyle="round,pad=0.008",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.5,
            transform=ax.transAxes)
        ax.add_patch(row_rect)

        # category label with accent bar
        accent = mpatches.FancyBboxPatch(
            (0.035, y_top - row_h + 0.01), 0.005, row_h - 0.02,
            boxstyle="round,pad=0.001", facecolor=BLUE,
            transform=ax.transAxes)
        ax.add_patch(accent)
        ax.text(0.08, y_mid, cat, ha="center", va="center",
                color=WHITE, fontsize=11, fontweight="bold",
                transform=ax.transAxes)

        # earth card background
        e_bg = mpatches.FancyBboxPatch(
            (0.13, y_top - row_h + 0.012), 0.36, row_h - 0.024,
            boxstyle="round,pad=0.008",
            facecolor="#1a1215", edgecolor="#3d2020", linewidth=0.6,
            transform=ax.transAxes)
        ax.add_patch(e_bg)

        # earth number
        ax.text(0.31, y_mid + 0.038, e_num, ha="center", va="center",
                color=RED, fontsize=14, fontweight="bold",
                transform=ax.transAxes)
        # earth details
        for j, line in enumerate(e_lines):
            ax.text(0.31, y_mid - 0.012 - j * 0.032, line,
                    ha="center", va="center", color=DIM, fontsize=8.5,
                    transform=ax.transAxes)

        # arrow
        ax.text(0.52, y_mid, "\u2192", ha="center", va="center",
                color=GRAY, fontsize=18, fontweight="bold",
                transform=ax.transAxes)

        # orbit card background
        o_bg = mpatches.FancyBboxPatch(
            (0.55, y_top - row_h + 0.012), 0.41, row_h - 0.024,
            boxstyle="round,pad=0.008",
            facecolor="#0d1a12", edgecolor="#1a3d20", linewidth=0.6,
            transform=ax.transAxes)
        ax.add_patch(o_bg)

        # orbit number
        ax.text(0.755, y_mid + 0.038, o_num, ha="center", va="center",
                color=GREEN, fontsize=14, fontweight="bold",
                transform=ax.transAxes)
        # orbit details
        for j, line in enumerate(o_lines):
            ax.text(0.755, y_mid - 0.012 - j * 0.032, line,
                    ha="center", va="center", color=WHITE, fontsize=8.5,
                    transform=ax.transAxes)

    # ── bottom note ──
    bot_y = y_start - n * (row_h + gap) - 0.02
    ax.text(0.50, bot_y, "냉각이 공짜가 아니다 — 비용 구조가 바뀌는 것이다",
            ha="center", va="top", color=YELLOW,
            fontsize=10, fontweight="bold", transform=ax.transAxes)

    return _save(fig, OUT / "01_earth_vs_orbit.png", "01_earth_vs_orbit.png")


# ══════════════════════════════════════════════════════════════════════════════
# 03. 도전과 돌파 요약 카드
# ══════════════════════════════════════════════════════════════════════════════
def make_challenges_card() -> dict:
    # (challenge, problem, solution, status_text, status_color)
    rows = [
        ("열 관리",    "대류 불가\n복사만 가능",
         "고온 설계로 돌파\nT\u2074 → 온도↑ 효율 3.2배\nISS 25년 실증",
         "TRL 7~9",  GREEN),
        ("방사선",    "위성 고장의\n70% 원인",
         "굳히지 않고 교체\n상용칩 + SW 보정\n발사비↓ = 교체가 더 싸다",
         "검증 중",   YELLOW),
        ("유지보수",  "기술자\n접근 불가",
         "수리 대신 통째로 교체\nStarlink 9,400기 모델\n5년마다 최신 GPU로",
         "운용 중",   GREEN),
        ("우주 파편",  "100만 기\n충돌 위험",
         "자정 궤도 480km\n2~6개월 자연 디오빗\n전략적 선점",
         "적용 중",   GREEN),
        ("데이터 주권", "법적 공백\n관할권 불명확",
         "기국주의 논의\nDigital Flag State\n규제 프레임 부재",
         "미확립",    RED),
    ]

    fig, ax = plt.subplots(figsize=(8, 9), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.96, "궤도 데이터센터 : 도전과 돌파",
            ha="center", va="top", color=WHITE,
            fontsize=15, fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.925, "물리학이 불가능하다고 말하는 항목은 하나도 없다",
            ha="center", va="top", color=DIM,
            fontsize=9.5, transform=ax.transAxes)

    # ── column layout ──
    col_x = [0.04, 0.20, 0.55, 0.86]   # challenge, problem, solution, status
    col_w = [0.14, 0.33, 0.29, 0.12]
    headers = ["도전", "핵심 문제", "돌파 전략", "현황"]
    hdr_colors = [WHITE, RED, GREEN, BLUE]

    hdr_y = 0.885
    hdr_h = 0.04

    for cx, cw, hdr, hc in zip(col_x, col_w, headers, hdr_colors):
        ax.text(cx + cw / 2, hdr_y, hdr,
                ha="center", va="center", color=hc,
                fontsize=10.5, fontweight="bold", transform=ax.transAxes)

    ax.plot([0.04, 0.96], [hdr_y - 0.025, hdr_y - 0.025],
            color=BORDER, lw=1, transform=ax.transAxes)

    # ── rows ──
    n = len(rows)
    row_h = 0.135
    row_gap = 0.015
    y_start = hdr_y - 0.045

    for i, (challenge, problem, solution, status, s_color) in enumerate(rows):
        y_top = y_start - i * (row_h + row_gap)

        # row background
        row_rect = mpatches.FancyBboxPatch(
            (0.03, y_top - row_h), 0.94, row_h,
            boxstyle="round,pad=0.008",
            facecolor=CARD_BG, edgecolor=BORDER, linewidth=0.6,
            transform=ax.transAxes)
        ax.add_patch(row_rect)

        y_mid = y_top - row_h / 2

        # challenge name (with colored left accent)
        accent = mpatches.FancyBboxPatch(
            (0.035, y_top - row_h + 0.01), 0.005, row_h - 0.02,
            boxstyle="round,pad=0.001",
            facecolor=s_color,
            transform=ax.transAxes)
        ax.add_patch(accent)
        ax.text(col_x[0] + col_w[0] / 2 + 0.01, y_mid, challenge,
                ha="center", va="center", color=WHITE,
                fontsize=11, fontweight="bold",
                transform=ax.transAxes)

        # problem
        ax.text(col_x[1] + col_w[1] / 2, y_mid, problem,
                ha="center", va="center", color=DIM,
                fontsize=9, multialignment="center",
                transform=ax.transAxes)

        # solution
        ax.text(col_x[2] + col_w[2] / 2, y_mid, solution,
                ha="center", va="center", color=WHITE,
                fontsize=9, multialignment="center",
                transform=ax.transAxes)

        # status indicator (colored dot + text)
        sx = col_x[3] + col_w[3] / 2
        ax.scatter(sx, y_mid + 0.02, s=100, color=s_color, zorder=5,
                   transform=ax.transAxes)
        ax.text(sx, y_mid - 0.025, status,
                ha="center", va="center", color=s_color,
                fontsize=8.5, fontweight="bold",
                transform=ax.transAxes)

    # ── bottom note ──
    bot_y = y_start - n * (row_h + row_gap) - 0.01
    ax.text(0.50, bot_y, "전부 공학과 제도의 문제다 — 물리학의 벽이 아니다",
            ha="center", va="top", color=YELLOW,
            fontsize=10, fontweight="bold", transform=ax.transAxes)

    return _save(fig, OUT / "03_challenges.png", "03_challenges.png")


# ══════════════════════════════════════════════════════════════════════════════
# 04. 궤도 DC 타임라인 (수직 레이아웃)
# ══════════════════════════════════════════════════════════════════════════════
def make_timeline() -> dict:
    cat_color = {"done": GREEN, "planned": BLUE, "bull": YELLOW, "bear": GRAY}
    cat_label = {"done": "실증 완료", "planned": "계획/진행",
                 "bull": "옹호론", "bear": "회의론"}

    # Section 1: 실증 & 계획 — year label shown only for first event per year
    sec1 = [
        ("2025", "Starcloud-1 발사",     "최초 H100 궤도 투입",     "done"),
        ("",     "궤도 LLM 학습",        "세계 최초 우주 AI 학습",  "done"),
        ("2026", "FCC 100만 위성",       "SpaceX 궤도 DC 신청",     "planned"),
        ("",     "K2 GRAVITAS",          "Mega Class 위성 시연",    "planned"),
        ("",     "Starcloud-2",          "H100 + B200 클러스터",    "planned"),
        ("2027", "Suncatcher / Axiom",   "Google TPU + ISS ODC",    "planned"),
    ]

    # Section 2: 전망 — 옹호론 vs 회의론
    sec2 = [
        ("2028~29", "머스크",        "\u201c우주가 가장 경제적인 AI 장소\u201d",  "bull"),
        ("2029~31", "Portal Space",  "\u201c제대로 작동하는 것\u201d",            "bear"),
        ("2035",    "Deutsche Bank", "\u201c경쟁력 있는 궤도 DC\u201d",          "bear"),
        ("2035",    "Starcloud CEO", "\u201c신규 DC 대부분 우주에\u201d",        "bull"),
        ("2045+",   "ESPI",          "\u201c경쟁력 있는 전력등가\u201d",          "bear"),
    ]

    fig, ax = plt.subplots(figsize=(8, 10), facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── title ──
    ax.text(0.50, 0.97, "궤도 데이터센터 타임라인",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.50, 0.945, "방향은 같다 — 차이는 시기의 문제",
            ha="center", va="top", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # ── vertical timeline line ──
    LINE_X = 0.16
    line_top = 0.905
    line_bot = 0.14

    ax.plot([LINE_X, LINE_X], [line_top, line_bot],
            color=BORDER, linewidth=2.5, transform=ax.transAxes, zorder=1)

    # ── Section 1 header ──
    sec1_y = 0.915
    ax.text(LINE_X + 0.04, sec1_y, "실증 & 계획",
            ha="left", va="center", color=BLUE,
            fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.plot([LINE_X + 0.04, 0.38], [sec1_y - 0.012, sec1_y - 0.012],
            color=BLUE, lw=0.8, alpha=0.4, transform=ax.transAxes)

    # ── Section 1 events ──
    ev_spacing = 0.065
    y = 0.875

    for yr_label, name, detail, cat in sec1:
        color = cat_color[cat]

        # year label (left of line)
        if yr_label:
            ax.text(LINE_X - 0.025, y, yr_label,
                    ha="right", va="center", color=DIM,
                    fontsize=11, fontweight="bold", transform=ax.transAxes)

        # dot on line
        ax.scatter(LINE_X, y, s=90, color=color, zorder=4,
                   transform=ax.transAxes)
        ax.scatter(LINE_X, y, s=25, color=BG, zorder=5,
                   transform=ax.transAxes)

        # horizontal connector
        ax.plot([LINE_X + 0.012, LINE_X + 0.04], [y, y],
                color=color, lw=1.2, alpha=0.5,
                transform=ax.transAxes, zorder=2)

        # event name
        ax.text(LINE_X + 0.05, y + 0.01, name,
                ha="left", va="center", color=color,
                fontsize=10.5, fontweight="bold", transform=ax.transAxes)

        # event detail
        ax.text(LINE_X + 0.05, y - 0.018, detail,
                ha="left", va="center", color=DIM,
                fontsize=9, transform=ax.transAxes)

        y -= ev_spacing

    # ── section divider ──
    div_y = y + 0.01
    ax.plot([0.05, 0.95], [div_y, div_y],
            color=BORDER, lw=1, transform=ax.transAxes)

    # ── Section 2 header ──
    sec2_hdr_y = div_y - 0.025
    ax.text(LINE_X + 0.04, sec2_hdr_y, "전망 — 옹호론 vs 회의론",
            ha="left", va="center", color=YELLOW,
            fontsize=12, fontweight="bold", transform=ax.transAxes)
    ax.plot([LINE_X + 0.04, 0.55], [sec2_hdr_y - 0.012, sec2_hdr_y - 0.012],
            color=YELLOW, lw=0.8, alpha=0.4, transform=ax.transAxes)

    # ── Section 2 events ──
    y = sec2_hdr_y - 0.055

    for yr_label, source, quote, cat in sec2:
        color = cat_color[cat]

        # year/period label
        ax.text(LINE_X - 0.025, y, yr_label,
                ha="right", va="center", color=DIM,
                fontsize=10, fontweight="bold", transform=ax.transAxes)

        # dot on line
        ax.scatter(LINE_X, y, s=90, color=color, zorder=4,
                   transform=ax.transAxes)
        ax.scatter(LINE_X, y, s=25, color=BG, zorder=5,
                   transform=ax.transAxes)

        # horizontal connector
        ax.plot([LINE_X + 0.012, LINE_X + 0.04], [y, y],
                color=color, lw=1.2, alpha=0.5,
                transform=ax.transAxes, zorder=2)

        # source name
        ax.text(LINE_X + 0.05, y + 0.01, source,
                ha="left", va="center", color=color,
                fontsize=10.5, fontweight="bold", transform=ax.transAxes)

        # quote
        ax.text(LINE_X + 0.05, y - 0.018, quote,
                ha="left", va="center", color=DIM,
                fontsize=9, transform=ax.transAxes)

        y -= ev_spacing

    # ── legend ──
    legend_y = 0.045
    cats_display = ["done", "planned", "bull", "bear"]
    total_w = len(cats_display) * 0.22
    legend_x_start = 0.5 - total_w / 2

    for j, cat in enumerate(cats_display):
        lx = legend_x_start + j * 0.22
        ax.scatter(lx, legend_y, s=60, color=cat_color[cat],
                   transform=ax.transAxes, zorder=4)
        ax.text(lx + 0.025, legend_y, cat_label[cat],
                ha="left", va="center", color=cat_color[cat],
                fontsize=9, transform=ax.transAxes)

    return _save(fig, OUT / "04_timeline.png", "04_timeline.png")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("궤도 데이터센터 시각화 생성 시작...\n")
    results = []

    results.append(make_comparison_card())
    print("  [1/3] 01_earth_vs_orbit.png")

    results.append(make_challenges_card())
    print("  [2/3] 03_challenges.png")

    results.append(make_timeline())
    print("  [3/3] 04_timeline.png")

    qa_check(results)
    print(f"\n저장 위치: {OUT}\n")
