"""
generate_schedule_visual.py — 아티클 게시 스케줄 시각화 (달력 그리드)

Output: docs/프로젝트/schedule_visual.png
Usage: python docs/프로젝트/generate_schedule_visual.py
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from pathlib import Path

OUT_PATH = Path(__file__).parent / "schedule_visual.png"

_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT):
    fm.fontManager.addfont(_FONT)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 ─────────────────────────────────────────────────────────────────────
BG      = "#0d1117"
CARD_BG = "#161b22"
BORDER  = "#30363d"
WHITE   = "#e6edf3"
GRAY    = "#6e7681"
SUB     = "#8b949e"

S_READY    = "#3fb950"  # 초록 — 게시 가능
S_DRAFT    = "#d29922"  # 노랑 — 퇴고 필요
S_RESEARCH = "#58a6ff"  # 파랑 — 초안 필요
S_PLAN     = "#484f58"  # 회색 — 기획 예정

EMPTY_BG     = "#0d1117"
EMPTY_BORDER = "#21262d"
EMPTY_TEXT   = "#30363d"

# 카테고리 (요일 → 색상, 이름)
CAT = {
    "월": ("#f85149", "테슬라"),
    "화": ("#58a6ff", "기업 딥다이브"),
    "수": ("#3fb950", "한국 시장"),
    "금": ("#d29922", "미국 시장"),
}
DAYS = ["월", "화", "수", "금"]

# ── 주차별 날짜 (월, 화, 수, 금) ────────────────────────────────────────────────
WEEKS = [
    ("W1", ["3/10", "3/11", "3/12", "3/14"]),
    ("W2", ["3/17", "3/18", "3/19", "3/21"]),
    ("W3", ["3/24", "3/25", "3/26", "3/28"]),
    ("W4", ["3/31", "4/1",  "4/2",  "4/4"]),
    ("W5", ["4/7",  "4/8",  "4/9",  "4/11"]),
    ("W6", ["4/14", "4/15", "4/16", "4/18"]),
    ("W7", ["4/21", "4/22", "4/23", "4/25"]),
    ("W8", ["4/28", "4/29", "4/30", "5/2"]),
]

N_WEEKS = len(WEEKS)
N_DAYS = len(DAYS)

# ── 아티클 데이터 (달력 그리드) ─────────────────────────────────────────────────
# key: (week_idx, day_idx)  →  day_idx: 0=월, 1=화, 2=수, 3=금
# val: (series, title, series_color, status_color, status_label)
# 없으면 빈 슬롯
GRID = {
    # W1 (3/10~3/14)
    (0, 0): ("TSLA #012",  "의식을 우주로 확장한다는 것", "#f85149", S_READY, "게시 가능"),
    (0, 1): ("PLTR 도입편", "팔란티어의 영혼",     "#58a6ff", S_READY,    "게시 가능"),
    # W2 (3/17~3/21)
    (1, 1): ("PLTR 0편",  "기업 전체 조망",        "#58a6ff", S_DRAFT,    "퇴고 필요"),
    # W3 (3/24~3/28)
    (2, 1): ("PLTR 1편",  "오해받는 기업",         "#58a6ff", S_DRAFT,    "퇴고 필요"),
    (2, 2): ("현대차 ①",  "가치는 어디에 쌓이는가", "#3fb950", S_READY,    "게시 가능"),
    # W4 (3/31~4/4)
    (3, 1): ("PLTR 2편",  "전쟁터의 소프트웨어",    "#58a6ff", S_DRAFT,    "퇴고 필요"),
    (3, 2): ("현대차 ②",  "110조의 행방",          "#3fb950", S_READY,    "게시 가능"),
    # W5 (4/7~4/11)
    (4, 1): ("PLTR 3편",  "온톨로지 해자",         "#58a6ff", S_DRAFT,    "퇴고 필요"),
    (4, 2): ("현대차 ③",  "DNA는 사람이 아니다",    "#3fb950", S_DRAFT,    "퇴고 필요"),
    # W6 (4/14~4/18)
    (5, 1): ("PLTR 4편",  "20년을 사는 기업",      "#58a6ff", S_DRAFT,    "퇴고 필요"),
    (5, 2): ("현대차 ④",  "바꾸지 않아도 되는 DNA", "#3fb950", S_DRAFT,    "퇴고 필요"),
    # W7 (4/21~4/25)
    (6, 1): ("BTC #1",    "블록체인 — 비트코인",    "#d29922", S_RESEARCH, "초안 필요"),
    # W8 (4/28~5/2)
    (7, 1): ("ETH #2",    "블록체인 — 이더리움",    "#a371f7", S_RESEARCH, "초안 필요"),
}

# ── 레이아웃 ──────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 13))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.axis("off")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)

LEFT   = 0.07
RIGHT  = 0.02
TOP    = 0.12
BOTTOM = 0.05

COL_GAP = 0.012
ROW_GAP = 0.010

avail_w = 1.0 - LEFT - RIGHT
avail_h = 1.0 - TOP - BOTTOM
col_w = (avail_w - (N_DAYS - 1) * COL_GAP) / N_DAYS
row_h = (avail_h - (N_WEEKS - 1) * ROW_GAP) / N_WEEKS


def cell_rect(wi: int, di: int):
    """(x, y_bottom, width, height) of grid cell."""
    x = LEFT + di * (col_w + COL_GAP)
    y = (1.0 - TOP) - (wi + 1) * row_h - wi * ROW_GAP
    return x, y, col_w, row_h


# ── 제목 ─────────────────────────────────────────────────────────────────────
ax.text(0.5, 0.98, "아티클 게시 스케줄 — 2026",
        ha="center", va="top", color=WHITE,
        fontsize=16, fontweight="bold")
ax.text(0.5, 0.955, "X Notes + 네이버 블로그  ·  게시 완료 3편  ·  게시 가능 3편 (TSLA·PLTR·현대차)  ·  목 토 일 OFF",
        ha="center", va="top", color=SUB, fontsize=10)

# ── 컬럼 헤더 ────────────────────────────────────────────────────────────────
header_y = 1.0 - TOP + 0.030
for di, day in enumerate(DAYS):
    cx = LEFT + di * (col_w + COL_GAP) + col_w / 2
    cat_color, cat_name = CAT[day]
    # 요일 배지
    badge_w, badge_h = 0.022, 0.016
    ax.add_patch(mpatches.FancyBboxPatch(
        (cx - badge_w / 2, header_y - badge_h / 2 + 0.006),
        badge_w, badge_h,
        boxstyle="round,pad=0.003",
        facecolor=cat_color, alpha=0.18,
        edgecolor=cat_color, linewidth=0.8,
    ))
    ax.text(cx, header_y + 0.006, day,
            ha="center", va="center", color=cat_color,
            fontsize=11, fontweight="bold")
    ax.text(cx, header_y - 0.014, cat_name,
            ha="center", va="center", color=SUB, fontsize=8.5)

# 헤더 아래 구분선
div_y = 1.0 - TOP + 0.004
ax.plot([LEFT - 0.01, 1.0 - RIGHT],
        [div_y, div_y], color=BORDER, linewidth=0.7)

# ── 카드 렌더링 ──────────────────────────────────────────────────────────────
for wi in range(N_WEEKS):
    wk_label, dates = WEEKS[wi]

    # 주차 라벨 (왼쪽)
    x0, y0, _, rh = cell_rect(wi, 0)
    ax.text(x0 - 0.012, y0 + rh / 2, wk_label,
            ha="right", va="center", color=GRAY,
            fontsize=8.5, fontweight="bold", alpha=0.7)

    for di in range(N_DAYS):
        x, y, cw, ch = cell_rect(wi, di)
        date_str = dates[di]
        art = GRID.get((wi, di))

        if art:
            series, title, s_color, st_color, st_label = art

            # ── 채워진 카드 ──
            # 카드 배경
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, y), cw, ch,
                boxstyle="round,pad=0.005",
                facecolor=s_color, alpha=0.07,
                edgecolor=s_color, linewidth=1.3,
            ))
            # 상단 악센트 라인 (카테고리 색상)
            cat_color = CAT[DAYS[di]][0]
            ax.plot([x + 0.006, x + cw - 0.006],
                    [y + ch - 0.003, y + ch - 0.003],
                    color=cat_color, linewidth=2.5, solid_capstyle="round")

            # 날짜 (우상단)
            ax.text(x + cw - 0.008, y + ch - 0.012, date_str,
                    ha="right", va="top", color=SUB, fontsize=7.5)

            # 시리즈 레이블 (좌상단)
            ax.text(x + 0.008, y + ch - 0.014, series,
                    ha="left", va="top", color=s_color,
                    fontsize=9.5, fontweight="bold")

            # 제목 (중앙)
            ax.text(x + cw / 2, y + ch / 2 - 0.005, title,
                    ha="center", va="center", color=WHITE, fontsize=9)

            # 상태 (하단)
            ax.scatter(x + 0.014, y + 0.013, s=35, color=st_color, zorder=3)
            ax.text(x + 0.026, y + 0.013, st_label,
                    ha="left", va="center", color=st_color,
                    fontsize=7.5, zorder=3)
        else:
            # ── 빈 슬롯 ──
            ax.add_patch(mpatches.FancyBboxPatch(
                (x, y), cw, ch,
                boxstyle="round,pad=0.005",
                facecolor=EMPTY_BG, alpha=0.5,
                edgecolor=EMPTY_BORDER, linewidth=0.8,
                linestyle=(0, (4, 3)),   # dashed
            ))
            # 날짜
            ax.text(x + cw - 0.008, y + ch - 0.012, date_str,
                    ha="right", va="top", color=GRAY, fontsize=7.5, alpha=0.4)
            # "빈 슬롯" — 눈에 띄게
            ax.text(x + cw / 2, y + ch / 2 + 0.004, "—",
                    ha="center", va="center", color=EMPTY_TEXT,
                    fontsize=16, alpha=0.5)
            ax.text(x + cw / 2, y + ch / 2 - 0.012, "기획 필요",
                    ha="center", va="center", color=EMPTY_TEXT,
                    fontsize=8, alpha=0.5)

# ── 범례 ─────────────────────────────────────────────────────────────────────
legend_y = BOTTOM / 2 + 0.005
# 구분선
ax.plot([LEFT, 1.0 - RIGHT],
        [legend_y + 0.018, legend_y + 0.018],
        color=BORDER, linewidth=0.5, alpha=0.5)

legend_items = [
    ("게시 가능",  S_READY),
    ("퇴고 필요",  S_DRAFT),
    ("초안 필요",  S_RESEARCH),
    ("기획 필요",  EMPTY_TEXT),
]
start_x = 0.22
for j, (label, color) in enumerate(legend_items):
    lx = start_x + j * 0.16
    ax.scatter(lx, legend_y, s=50, color=color)
    ax.text(lx + 0.014, legend_y, label,
            ha="left", va="center", color=SUB, fontsize=8.5)

# ── 빈 슬롯 카운트 요약 ──────────────────────────────────────────────────────
total_slots = N_WEEKS * N_DAYS
filled = len(GRID)
empty = total_slots - filled
ax.text(1.0 - RIGHT, legend_y, f"채움 {filled}/{total_slots}  ·  빈 슬롯 {empty}개",
        ha="right", va="center", color=GRAY, fontsize=8.5)

# ── 저장 ─────────────────────────────────────────────────────────────────────
fig.savefig(OUT_PATH, dpi=180, bbox_inches="tight", facecolor=BG)
plt.close(fig)
size_kb = OUT_PATH.stat().st_size / 1024
print(f"✅ 생성 완료: {OUT_PATH}  ({size_kb:.1f} KB)")
