"""
Tesla Master Plan Article — Visual Generator (Mobile-Optimized)

포맷: 1080×1080 정사각형 (X 모바일 최적)
산출물:
  visuals/01_timeline.png       — 마스터 플랜 타임라인
  visuals/02_achievement.png    — 달성 현황 테이블
  visuals/03_mission_cards.png  — 미션 진화 2×2 카드
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

matplotlib.use("Agg")

# ── 경로 ──────────────────────────────────────────────────
HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# ── 한글 폰트 ─────────────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 ──────────────────────────────────────────────────
BG     = "#0d1117"
BG2    = "#161b22"
BG3    = "#1c2128"
GREEN  = "#3fb950"
YELLOW = "#d29922"
RED    = "#f85149"
BLUE   = "#58a6ff"
ORANGE = "#db6d28"
GRAY   = "#6e7681"
WHITE  = "#e6edf3"
DIM    = "#8b949e"

STATUS_COLOR = {
    "완료":    GREEN,
    "부분완료": YELLOW,
    "지연완료": YELLOW,
    "진행중":  BLUE,
    "전략변경": ORANGE,
    "미완료":  RED,
    "미착수":  GRAY,
    "급성장":  GREEN,
}
STATUS_LABEL = {
    "완료":    "✓ 완료",
    "부분완료": "◑ 부분",
    "지연완료": "◑ 지연",
    "진행중":  "● 진행중",
    "전략변경": "~ 변경",
    "미완료":  "× 미완료",
    "미착수":  "○ 미착수",
    "급성장":  "↑ 급성장",
}

# 1080×1080 @ dpi=135
FIG_SIZE = (8, 8)
DPI = 135

def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    print(f"  저장: {path}")
    return path


# ══════════════════════════════════════════════════════════
# 01. 타임라인 (수평 → 정사각 최적화)
# ══════════════════════════════════════════════════════════

def make_timeline() -> Path:
    # 핵심 6개 이벤트로 압축
    events = [
        (2006, "Part 1 공개\n비밀 플랜",        "up",   "#58a6ff"),
        (2012, "Model S\n출시",                 "down", GREEN),
        (2016, "Part Deux\n자율주행 선언",       "up",   "#bc8cff"),
        (2020, "Model Y\n전 세계 판매 1위",      "down", GREEN),
        (2023, "Part 3 발표\nCybertruck",        "up",   "#3fb950"),
        (2025, "Part 4\nAbundance",              "down", "#f0883e"),
    ]

    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")

    # 제목
    ax.text(0.5, 0.95, "Tesla Master Plan",
            transform=ax.transAxes, fontsize=26, fontweight="bold",
            color=WHITE, ha="center", va="top")
    ax.text(0.5, 0.88, "20년의 타임라인",
            transform=ax.transAxes, fontsize=16,
            color=DIM, ha="center", va="top")

    # Fix #1: 좌우 여백 확대 (0.07→0.11) — 2006·2025 라벨 박스 잘림 방지
    y_min, y_max = 2004, 2027
    def xp(yr: int) -> float:
        return 0.11 + (yr - y_min) / (y_max - y_min) * 0.78

    cy = 0.50  # 중앙선 y

    # 중앙 수평선
    ax.plot([0.05, 0.95], [cy, cy],
            transform=ax.transAxes,
            color=GRAY, linewidth=2, zorder=1)

    for year, label, pos, color in events:
        x = xp(year)

        stem_len = 0.16
        y1 = cy + stem_len if pos == "up" else cy - stem_len
        y_text = y1 + 0.04 if pos == "up" else y1 - 0.04
        va = "bottom" if pos == "up" else "top"

        # 수직선
        ax.plot([x, x], [cy, y1],
                transform=ax.transAxes,
                color=color, linewidth=1.8, alpha=0.8, zorder=2)

        # 도트
        ax.scatter([x], [cy], s=120, color=color,
                   transform=ax.transAxes,
                   zorder=4, edgecolors=BG, linewidths=2)

        # 연도
        yr_y = cy + 0.04 if pos == "up" else cy - 0.04
        ax.text(x, yr_y, str(year),
                transform=ax.transAxes, fontsize=11,
                color=color, ha="center",
                va="bottom" if pos == "up" else "top",
                fontweight="bold")

        # 라벨 박스
        ax.text(x, y_text, label,
                transform=ax.transAxes, fontsize=12,
                color=WHITE, ha="center", va=va,
                linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.45",
                          facecolor=BG2, edgecolor=color,
                          linewidth=1.2, alpha=0.95))

    # 현재 마커
    nx = xp(2026)
    ax.plot([nx, nx], [cy - 0.07, cy + 0.07],
            transform=ax.transAxes,
            color=WHITE, linewidth=1, linestyle="--", alpha=0.35)
    ax.text(nx, cy - 0.09, "현재",
            transform=ax.transAxes, fontsize=10,
            color=DIM, ha="center", va="top")

    # 하단 워터마크
    ax.text(0.5, 0.02, "Tesla Master Plan Part 1–4  |  2006–2025",
            transform=ax.transAxes, fontsize=9,
            color=GRAY, ha="center", va="bottom")

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return _save(fig, "01_timeline.png")


# ══════════════════════════════════════════════════════════
# 02. 달성 현황 테이블 (Plan | Goal | Status 3열)
# ══════════════════════════════════════════════════════════

def make_achievement_table() -> Path:
    sections = [
        {
            "plan": "Part 1  ·  2006",
            "color": "#58a6ff",
            "rows": [
                ("Roadster (스포츠카)",     "완료"),
                ("Model S (중가 세단)",     "완료"),
                ("Model 3 (대중 보급형)",   "완료"),
                ("무배출 발전 옵션",        "부분완료"),
            ],
        },
        {
            "plan": "Part Deux  ·  2016",
            "color": "#bc8cff",
            "rows": [
                ("Model Y (소형 SUV)",            "완료"),
                ("Cybertruck (픽업트럭)",         "완료"),
                ("Tesla Semi (대형 트럭)",        "지연완료"),
                ("Tesla Bus",                     "미완료"),
                ("FSD — 인간 대비 10배 안전",     "진행중"),
                ("Robotaxi / 공유 플릿",          "진행중"),
            ],
        },
        {
            "plan": "Part 3  ·  2023",
            "color": "#3fb950",
            "rows": [
                ("$25,000 보급형 차량",   "전략변경"),
                ("Cybercab",              "진행중"),
                ("Megapack (에너지 저장)","급성장"),
                ("전기 밴 / 버스",        "미착수"),
            ],
        },
        {
            "plan": "Part 4  ·  2025",
            "color": "#f0883e",
            "rows": [
                ("에너지 — Megapack + Solar", "진행중"),
                ("모빌리티 — FSD + Cybercab", "진행중"),
                ("노동 — Optimus",            "진행중"),
            ],
        },
    ]

    total_rows = sum(len(s["rows"]) for s in sections)
    n_sections = len(sections)

    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")

    # 제목
    ax.text(0.5, 0.97, "달성 현황",
            transform=ax.transAxes, fontsize=26, fontweight="bold",
            color=WHITE, ha="center", va="top")
    ax.text(0.5, 0.91, "Tesla Master Plan Part 1 – 4",
            transform=ax.transAxes, fontsize=14, color=DIM,
            ha="center", va="top")

    # Fix #2: 하단 여백 확대 (0.04→0.08) — 마지막 행과 범례 겹침 방지
    body_top  = 0.87
    body_bot  = 0.08
    body_h    = body_top - body_bot
    row_count = total_rows + n_sections  # 섹션 헤더 포함
    rh        = body_h / row_count

    col_plan   = 0.02
    col_goal   = 0.32
    col_status = 0.80

    cur_y = body_top

    for sec in sections:
        color = sec["color"]

        # ── 섹션 헤더 ──
        header_y = cur_y - rh * 0.5

        # 왼쪽 컬러 바
        ax.plot([col_plan, col_plan + 0.006], [cur_y - rh * 0.1, cur_y - rh * 0.9],
                transform=ax.transAxes,
                color=color, linewidth=4, solid_capstyle="round")

        ax.text(col_plan + 0.025, header_y, sec["plan"],
                transform=ax.transAxes, fontsize=13,
                color=color, fontweight="bold", va="center")

        # 구분선
        ax.plot([0.01, 0.99], [cur_y - rh, cur_y - rh],
                transform=ax.transAxes,
                color=color, linewidth=0.6, alpha=0.4)

        cur_y -= rh

        # ── 데이터 행 ──
        for i, (goal, status) in enumerate(sec["rows"]):
            row_y = cur_y - rh * 0.5
            bg_color = BG2 if i % 2 == 0 else BG

            # 배경
            rect = mpatches.FancyBboxPatch(
                (0.01, cur_y - rh * 0.92), 0.98, rh * 0.85,
                transform=ax.transAxes,
                boxstyle="square,pad=0",
                facecolor=bg_color, edgecolor="none", zorder=0,
            )
            ax.add_patch(rect)

            # 목표
            ax.text(col_goal, row_y, goal,
                    transform=ax.transAxes, fontsize=12,
                    color=WHITE, va="center")

            # 상태 배지
            sc = STATUS_COLOR.get(status, GRAY)
            sl = STATUS_LABEL.get(status, status)
            ax.text(col_status, row_y, sl,
                    transform=ax.transAxes, fontsize=11,
                    color=sc, fontweight="bold", va="center",
                    ha="left")

            cur_y -= rh

    # 범례
    items = [
        (GREEN,  "완료/급성장"),
        (YELLOW, "부분/지연"),
        (BLUE,   "진행중"),
        (ORANGE, "전략변경"),
        (RED,    "미완료"),
        (GRAY,   "미착수"),
    ]
    lx = 0.02
    for c, lbl in items:
        ax.text(lx, 0.015, f"● {lbl}",
                transform=ax.transAxes, fontsize=8.5,
                color=c, va="center")
        lx += 0.16

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    return _save(fig, "02_achievement.png")


# ══════════════════════════════════════════════════════════
# 03. 미션 진화 2×2 카드
# ══════════════════════════════════════════════════════════

def make_mission_cards() -> Path:
    plans = [
        {
            "label":     "Part 1  ·  2006",
            "color":     "#58a6ff",
            "mission":   "Roadster → Model S\n→ Model 3",
            "sub":       "단계적 대중화",
            "principle": "배터리 원자재 $80/kWh\nvs 완제품 $600/kWh\n→ 7.5배 gap",
            "keyword":   "크로스 서브시디",
            "rate":      90,
        },
        {
            "label":     "Part Deux  ·  2016",
            "color":     "#bc8cff",
            "mission":   "에너지 생태계 +\n자율주행 + Robotaxi",
            "sub":       "차가 돈을 버는 구조",
            "principle": "차는 95% 주차 중\n→ 놀고 있는 시간을\n수익화하면?",
            "keyword":   "Tesla Network",
            "rate":      55,
        },
        {
            "label":     "Part 3  ·  2023",
            "color":     "#3fb950",
            "mission":   "지구 전체\n에너지 전환",
            "sub":       "Sustainable Energy",
            "principle": "전환 비용 $10.4조\nvs 유지 비용 $14조\n→ 전환이 더 싸다",
            "keyword":   "지구 에너지 백서",
            "rate":      40,
        },
        {
            "label":     "Part 4  ·  2025",
            "color":     "#f0883e",
            "mission":   "에너지 + 모빌리티\n+ 노동 = 풍요",
            "sub":       "Sustainable Abundance",
            "principle": "노동·이동의 물리적\n제약은 AI+로봇으로\n제거 가능",
            "keyword":   "지구 문명 인프라",
            "rate":      15,
        },
    ]

    fig, axes = plt.subplots(2, 2, figsize=FIG_SIZE, facecolor=BG)
    fig.suptitle("미션의 진화  —  Tesla Master Plan",
                 fontsize=20, fontweight="bold", color=WHITE, y=0.98)
    fig.subplots_adjust(hspace=0.08, wspace=0.08,
                        left=0.03, right=0.97,
                        top=0.93, bottom=0.02)

    for ax, plan in zip(axes.flat, plans):
        ax.set_facecolor(BG2)
        ax.axis("off")
        color = plan["color"]

        # 상단 컬러 바
        ax.plot([0.0, 1.0], [0.97, 0.97],
                transform=ax.transAxes,
                color=color, linewidth=5,
                solid_capstyle="butt")

        # 플랜 라벨
        ax.text(0.5, 0.91, plan["label"],
                transform=ax.transAxes, fontsize=11,
                fontweight="bold", color=color,
                ha="center", va="top")

        # 미션
        ax.text(0.5, 0.82, plan["mission"],
                transform=ax.transAxes, fontsize=13,
                color=WHITE, ha="center", va="top",
                linespacing=1.45, fontweight="bold")

        # 서브 — y=0.63으로 올려 구분선(0.58) 위로 배치
        ax.text(0.5, 0.63, plan["sub"],
                transform=ax.transAxes, fontsize=10,
                color=color, ha="center", va="top")

        # 구분선 — sub 텍스트 하단(~0.590) 아래인 0.57에 배치
        ax.plot([0.08, 0.92], [0.57, 0.57],
                transform=ax.transAxes,
                color=GRAY, linewidth=0.5, alpha=0.5)

        # 제1원칙
        ax.text(0.5, 0.52, plan["principle"],
                transform=ax.transAxes, fontsize=9.5,
                color=DIM, ha="center", va="top",
                linespacing=1.45)

        # 구분선
        ax.plot([0.08, 0.92], [0.26, 0.26],
                transform=ax.transAxes,
                color=GRAY, linewidth=0.5, alpha=0.5)

        # 키워드 배지
        ax.text(0.5, 0.21, plan["keyword"],
                transform=ax.transAxes, fontsize=10,
                color=color, ha="center", va="top",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35",
                          facecolor=BG,
                          edgecolor=color,
                          linewidth=0.8, alpha=0.95))

        # 달성률 바 — bar_y=0.06으로 낮춰 키워드 배지와 간격 확보
        rate = plan["rate"] / 100
        bar_y = 0.06
        ax.text(0.5, bar_y + 0.055,
                f"달성률  {plan['rate']}%",
                transform=ax.transAxes, fontsize=9,
                color=DIM, ha="center", va="bottom")

        # 배경
        rect_bg = mpatches.FancyBboxPatch(
            (0.08, bar_y - 0.016), 0.84, 0.032,
            transform=ax.transAxes,
            boxstyle="round,pad=0",
            facecolor=GRAY, alpha=0.25, edgecolor="none",
        )
        ax.add_patch(rect_bg)

        # 진행
        bar_color = (GREEN if rate >= 0.7
                     else YELLOW if rate >= 0.4
                     else BLUE)
        rect_fg = mpatches.FancyBboxPatch(
            (0.08, bar_y - 0.016), 0.84 * rate, 0.032,
            transform=ax.transAxes,
            boxstyle="round,pad=0",
            facecolor=bar_color, alpha=0.9, edgecolor="none",
        )
        ax.add_patch(rect_fg)

    return _save(fig, "03_mission_cards.png")


# ══════════════════════════════════════════════════════════
# QA 체크
# ══════════════════════════════════════════════════════════

def qa_check() -> None:
    """생성된 PNG 파일의 품질을 자동으로 검토한다.

    체크 항목:
    - 파일 존재 및 최소 크기 (> 10 KB)
    - 이미지 해상도 (가로·세로 모두 900px 이상)
    - 가로/세로 비율이 정사각형에 근접하는지 (0.9 ~ 1.1)
    """
    from PIL import Image

    files = [
        OUT / "01_timeline.png",
        OUT / "02_achievement.png",
        OUT / "03_mission_cards.png",
    ]

    print("\n── QA 검토 결과 ──────────────────────────")
    all_pass = True

    for fp in files:
        issues = []

        # 1. 파일 존재
        if not fp.exists():
            print(f"  ❌ {fp.name} — 파일 없음")
            all_pass = False
            continue

        # 2. 파일 크기
        size_kb = fp.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"파일 크기 너무 작음 ({size_kb:.1f} KB)")

        # 3. 해상도 + 비율
        try:
            with Image.open(fp) as img:
                w, h = img.size
                ratio = w / h
                if w < 900 or h < 900:
                    issues.append(f"해상도 부족 ({w}×{h}px, 최소 900px)")
                if not (0.85 <= ratio <= 1.15):
                    issues.append(f"비율 이탈 ({ratio:.2f}, 정사각형 기준 0.85~1.15)")
                res_str = f"{w}×{h}px"
        except Exception as e:
            issues.append(f"이미지 열기 실패: {e}")
            res_str = "unknown"

        if issues:
            all_pass = False
            print(f"  ⚠️  {fp.name} ({size_kb:.0f} KB, {res_str})")
            for iss in issues:
                print(f"       → {iss}")
        else:
            print(f"  ✅ {fp.name} ({size_kb:.0f} KB, {res_str})")

    print("──────────────────────────────────────────")
    if all_pass:
        print("  모든 항목 통과\n")
    else:
        print("  ⚠️  일부 항목 수정 필요\n")


# ══════════════════════════════════════════════════════════
# 실행
# ══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Tesla Master Plan 시각화 생성 중...\n")
    make_timeline()
    make_achievement_table()
    make_mission_cards()
    qa_check()
