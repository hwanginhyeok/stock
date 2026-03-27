#!/usr/bin/env python3
"""오늘의 통계 #001 — 대한민국 총부채 시각화"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from pathlib import Path

# ── 폰트 설정 ──
_FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    os.path.expanduser("~/.fonts/NotoSansCJK-Regular.ttc"),
]
for _fp in _FONT_CANDIDATES:
    if os.path.exists(_fp):
        fm.fontManager.addfont(_fp)
        plt.rcParams["font.family"] = "Noto Sans CJK JP"
        break
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 팔레트 (다크 테마) ──
BG = "#0d1117"
CARD_BG = "#161b22"
TEXT = "#e6edf3"
TEXT_DIM = "#8b949e"
GREEN = "#3fb950"
BLUE = "#58a6ff"
RED = "#f85149"
YELLOW = "#d29922"
ORANGE = "#db6d28"
PURPLE = "#bc8cff"
GRID = "#21262d"

# ── 데이터 ──
YEARS = list(range(2005, 2026))
GDP = [995, 1046, 1135, 1203, 1255, 1379, 1449, 1505, 1571, 1638,
       1741, 1833, 1934, 2007, 2041, 2058, 2222, 2324, 2409, 2557, 2663]

HOUSEHOLD = [608, 680, 755, 819, 880, 968, 1062, 1114, 1177, 1252,
             1379, 1520, 1640, 1742, 1828, 1999, 2193, 2261, 2240, 2291, 2343]
CORPORATE = [701, 805, 925, 1100, 1183, 1233, 1305, 1374, 1467, 1557,
             1621, 1642, 1698, 1814, 1949, 2133, 2375, 2596, 2719, 2828, 2907]
GOVERNMENT = [248, 282, 298, 312, 362, 390, 459, 504, 566, 621,
              675, 717, 735, 761, 810, 945, 1067, 1157, 1221, 1273, 1251]
TOTAL = [h + c + g for h, c, g in zip(HOUSEHOLD, CORPORATE, GOVERNMENT)]

# GDP 대비 비율
HH_RATIO = [61.1, 65.0, 66.5, 68.1, 70.1, 70.2, 73.3, 74.0, 74.9, 76.4,
            79.2, 82.9, 84.8, 86.8, 89.6, 97.1, 98.7, 97.3, 93.0, 89.6, 88.0]
CORP_RATIO = [70.5, 77.0, 81.5, 91.4, 94.2, 89.4, 90.1, 91.3, 93.4, 95.0,
              93.1, 89.6, 87.8, 90.4, 95.5, 103.6, 106.9, 111.7, 112.9, 110.6, 109.2]
GOVT_RATIO = [24.9, 27.0, 26.3, 25.9, 28.8, 28.3, 31.7, 33.5, 36.0, 37.9,
              38.8, 39.1, 38.0, 37.9, 39.7, 45.9, 48.0, 49.8, 50.7, 49.8, 47.0]

OUT_DIR = Path(__file__).parent / "visuals"
OUT_DIR.mkdir(exist_ok=True)


def _set_dark_style(ax, fig):
    """다크 테마 공통 스타일"""
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT_DIM, labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.yaxis.grid(True, color=GRID, linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)


def chart_01_stacked_area():
    """01: 총부채 연도별 추이 — 스택 영역 차트"""
    fig, ax = plt.subplots(figsize=(12, 6.5))
    _set_dark_style(ax, fig)

    ax.stackplot(YEARS, GOVERNMENT, HOUSEHOLD, CORPORATE,
                 colors=[YELLOW, BLUE, GREEN],
                 labels=["정부", "가계", "기업"], alpha=0.85)

    # 총부채 라인
    ax.plot(YEARS, TOTAL, color=TEXT, linewidth=1.5, linestyle="--", alpha=0.6)

    # 주요 포인트 어노테이션
    annotations = [
        (2005, TOTAL[0], f"{TOTAL[0]:,}조", -30, 15),
        (2008, TOTAL[3], "금융위기", -40, 20),
        (2020, TOTAL[15], "코로나", -45, 20),
        (2025, TOTAL[-1], f"{TOTAL[-1]:,}조", -35, 15),
    ]
    for x, y, label, dx, dy in annotations:
        ax.annotate(label, (x, y), textcoords="offset points",
                    xytext=(dx, dy), fontsize=9, color=TEXT, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=TEXT_DIM, lw=0.8))

    ax.set_xlim(2005, 2025)
    ax.set_ylim(0, 7500)
    ax.set_ylabel("조원", color=TEXT_DIM, fontsize=10)
    ax.set_title("대한민국 총부채 추이 (2005~2025)", color=TEXT,
                 fontsize=14, fontweight="bold", pad=15)

    legend = ax.legend(loc="upper left", fontsize=9, frameon=True,
                       facecolor=CARD_BG, edgecolor=GRID, labelcolor=TEXT)
    legend.get_frame().set_alpha(0.9)

    # 우측 상단 GDP 배수 표기
    ax.text(0.98, 0.95, "GDP의 2.5배", transform=ax.transAxes,
            fontsize=11, color=RED, fontweight="bold",
            ha="right", va="top")

    fig.tight_layout(pad=1.5)
    out = OUT_DIR / "01_총부채_추이.png"
    fig.savefig(out, dpi=180, facecolor=BG)
    plt.close(fig)
    print(f"  ✅ {out.name} ({out.stat().st_size // 1024}KB)")
    return out


def chart_02_gdp_ratio_lines():
    """02: GDP 대비 부문별 비율 추이 — 라인 차트"""
    fig, ax = plt.subplots(figsize=(12, 6))
    _set_dark_style(ax, fig)

    ax.plot(YEARS, CORP_RATIO, color=GREEN, linewidth=2.5, marker="o",
            markersize=3, label="기업", zorder=3)
    ax.plot(YEARS, HH_RATIO, color=BLUE, linewidth=2.5, marker="o",
            markersize=3, label="가계", zorder=3)
    ax.plot(YEARS, GOVT_RATIO, color=YELLOW, linewidth=2.5, marker="o",
            markersize=3, label="정부", zorder=3)

    # 100% 기준선
    ax.axhline(y=100, color=RED, linestyle=":", linewidth=1, alpha=0.5)
    ax.text(2025.3, 100, "GDP 100%", fontsize=8, color=RED, alpha=0.7, va="center")

    # 피크 표시
    peak_hh_idx = HH_RATIO.index(max(HH_RATIO))
    ax.annotate(f"가계 피크\n{HH_RATIO[peak_hh_idx]}%\n({YEARS[peak_hh_idx]})",
                (YEARS[peak_hh_idx], HH_RATIO[peak_hh_idx]),
                textcoords="offset points", xytext=(15, 10), fontsize=8,
                color=BLUE, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=BLUE, lw=0.8))

    peak_corp_idx = CORP_RATIO.index(max(CORP_RATIO))
    ax.annotate(f"기업 피크\n{CORP_RATIO[peak_corp_idx]}%\n({YEARS[peak_corp_idx]})",
                (YEARS[peak_corp_idx], CORP_RATIO[peak_corp_idx]),
                textcoords="offset points", xytext=(15, 5), fontsize=8,
                color=GREEN, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GREEN, lw=0.8))

    # y축 범위 — min-10% ~ max+10% 패딩
    all_vals = HH_RATIO + CORP_RATIO + GOVT_RATIO
    lo, hi = min(all_vals), max(all_vals)
    rng = hi - lo
    ax.set_ylim(lo - 0.1 * rng, hi + 0.1 * rng)
    ax.set_xlim(2004.5, 2026)

    ax.set_ylabel("GDP 대비 %", color=TEXT_DIM, fontsize=10)
    ax.set_title("GDP 대비 부문별 부채 비율 (2005~2025)", color=TEXT,
                 fontsize=14, fontweight="bold", pad=15)

    legend = ax.legend(loc="upper left", fontsize=10, frameon=True,
                       facecolor=CARD_BG, edgecolor=GRID, labelcolor=TEXT)
    legend.get_frame().set_alpha(0.9)

    fig.tight_layout(pad=1.5)
    out = OUT_DIR / "02_GDP대비_비율_추이.png"
    fig.savefig(out, dpi=180, facecolor=BG)
    plt.close(fig)
    print(f"  ✅ {out.name} ({out.stat().st_size // 1024}KB)")
    return out


def chart_03_composition():
    """03: 구성비 변화 — 그룹 바 차트 (2005·2010·2015·2020·2025)"""
    fig, ax = plt.subplots(figsize=(10, 6))
    _set_dark_style(ax, fig)

    labels = ["2005", "2010", "2015", "2020", "2025"]
    idx_map = [0, 5, 10, 15, 20]  # YEARS index

    hh_pct = [HOUSEHOLD[i] / TOTAL[i] * 100 for i in idx_map]
    cp_pct = [CORPORATE[i] / TOTAL[i] * 100 for i in idx_map]
    gv_pct = [GOVERNMENT[i] / TOTAL[i] * 100 for i in idx_map]

    x = np.arange(len(labels))
    w = 0.25

    bars_gv = ax.bar(x - w, gv_pct, w, color=YELLOW, label="정부", alpha=0.9, zorder=3)
    bars_hh = ax.bar(x, hh_pct, w, color=BLUE, label="가계", alpha=0.9, zorder=3)
    bars_cp = ax.bar(x + w, cp_pct, w, color=GREEN, label="기업", alpha=0.9, zorder=3)

    # 비율 텍스트
    for bars in [bars_gv, bars_hh, bars_cp]:
        for bar in bars:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                    f"{h:.1f}%", ha="center", va="bottom",
                    fontsize=8, color=TEXT, fontweight="bold")

    # 총부채 금액 표시 (하단)
    for i, idx in enumerate(idx_map):
        ax.text(x[i], -3, f"총 {TOTAL[idx]:,}조",
                ha="center", fontsize=8, color=TEXT_DIM)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11, color=TEXT)
    ax.set_ylim(0, 55)
    ax.set_ylabel("구성비 (%)", color=TEXT_DIM, fontsize=10)
    ax.set_title("총부채 구성비 변화 (2005→2025)", color=TEXT,
                 fontsize=14, fontweight="bold", pad=15)

    legend = ax.legend(loc="upper right", fontsize=10, frameon=True,
                       facecolor=CARD_BG, edgecolor=GRID, labelcolor=TEXT)
    legend.get_frame().set_alpha(0.9)

    fig.tight_layout(pad=1.5)
    out = OUT_DIR / "03_구성비_변화.png"
    fig.savefig(out, dpi=180, facecolor=BG)
    plt.close(fig)
    print(f"  ✅ {out.name} ({out.stat().st_size // 1024}KB)")
    return out


def qa_check():
    """QA 체크 — 파일 크기 확인"""
    ok = True
    for f in sorted(OUT_DIR.glob("*.png")):
        size_kb = f.stat().st_size // 1024
        if size_kb < 10:
            print(f"  ❌ {f.name}: {size_kb}KB (< 10KB)")
            ok = False
        else:
            print(f"  ✅ {f.name}: {size_kb}KB")
    return ok


if __name__ == "__main__":
    print("시각화 생성 중...")
    chart_01_stacked_area()
    chart_02_gdp_ratio_lines()
    chart_03_composition()
    print("\nQA 체크...")
    if qa_check():
        print("\n✅ 모든 시각화 정상 생성")
    else:
        print("\n❌ QA 실패 — 위 항목 확인 필요")
        sys.exit(1)
