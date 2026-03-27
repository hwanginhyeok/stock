"""
generate_visuals.py — 팔란티어 3편: 국제정세 시각화

생성 이미지:
  01_old_vs_new_paradigm.png     — 구 방산 vs 팔란티어 패러다임 비교
  02_defense_contracts.png       — 2024~2026 국방 계약 타임라인 + 금액

Usage:
    python data/articles/008_PLTR_팔란티어-3편/generate_visuals.py
"""

import os
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm
from pathlib import Path

# ── 경로 ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# ── 한글 폰트 ─────────────────────────────────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 팔레트 ───────────────────────────────────────────────────────────────
BG     = "#0d1117"
BG2    = "#161b22"
GREEN  = "#3fb950"
YELLOW = "#d29922"
RED    = "#f85149"
BLUE   = "#58a6ff"
ORANGE = "#db6d28"
GRAY   = "#6e7681"
WHITE  = "#e6edf3"
DIM    = "#8b949e"
BORDER = "#30363d"
PURPLE = "#bc8cff"

FIG_SIZE = (8, 8)
DPI      = 135


def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════════════
# 01. 구 방산 vs 팔란티어 패러다임 비교
# ══════════════════════════════════════════════════════════════════════════════
def make_paradigm_comparison() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "두 패러다임의 충돌",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "구 방산 (하드웨어)  vs  팔란티어 (소프트웨어)",
            ha="center", va="center", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # 비교 항목
    rows = [
        ("억지력 단위",     "무기의 양",              "의사결정의 질"),
        ("전력 구조",       "대규모 병력 투입",        "소수 운용자\n+ 자율 에이전트"),
        ("조달 주기",       "수년~10년",              "30일 내 배포"),
        ("비즈니스 모델",    "무기 판매량 = 수익",      "효율화 = 가치"),
        ("공급망",          "소수 대형사 독점",        "스타트업 진입\n플랫폼 (Warp Speed)"),
        ("전쟁과의 관계",    "전쟁 지속 = 이익",        "전쟁 억지 = 목적"),
    ]

    LEFT_X = 0.04
    RIGHT_X = 0.52
    CARD_W = 0.44
    CARD_H = 0.095
    GAP_Y = 0.015
    START_Y = 0.86
    LABEL_W = 0.14

    for i, (label, old_val, new_val) in enumerate(rows):
        y_top = START_Y - i * (CARD_H + GAP_Y)

        # 가운데 라벨
        ax.text(0.5, y_top - CARD_H / 2,
                label, ha="center", va="center",
                color=WHITE, fontsize=8.5, fontweight="bold",
                transform=ax.transAxes)

        # 좌측: 구 방산 (RED)
        rect_l = mpatches.FancyBboxPatch(
            (LEFT_X, y_top - CARD_H), CARD_W - LABEL_W, CARD_H,
            boxstyle="round,pad=0.008",
            facecolor=BG2,
            edgecolor=RED, linewidth=1.0, alpha=0.8,
            transform=ax.transAxes
        )
        ax.add_patch(rect_l)
        ax.text(LEFT_X + (CARD_W - LABEL_W) / 2, y_top - CARD_H / 2,
                old_val, ha="center", va="center",
                color=RED, fontsize=8.5,
                multialignment="center",
                transform=ax.transAxes)

        # 우측: 팔란티어 (GREEN)
        rect_r = mpatches.FancyBboxPatch(
            (RIGHT_X + LABEL_W, y_top - CARD_H), CARD_W - LABEL_W, CARD_H,
            boxstyle="round,pad=0.008",
            facecolor=BG2,
            edgecolor=GREEN, linewidth=1.0, alpha=0.8,
            transform=ax.transAxes
        )
        ax.add_patch(rect_r)
        ax.text(RIGHT_X + LABEL_W + (CARD_W - LABEL_W) / 2,
                y_top - CARD_H / 2,
                new_val, ha="center", va="center",
                color=GREEN, fontsize=8.5,
                multialignment="center",
                transform=ax.transAxes)

    # 컬럼 헤더
    ax.text(LEFT_X + (CARD_W - LABEL_W) / 2, 0.89,
            "구 방산", ha="center", va="center",
            color=RED, fontsize=11, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.89,
            "VS", ha="center", va="center",
            color=GRAY, fontsize=10, fontweight="bold",
            transform=ax.transAxes)
    ax.text(RIGHT_X + LABEL_W + (CARD_W - LABEL_W) / 2, 0.89,
            "팔란티어", ha="center", va="center",
            color=GREEN, fontsize=11, fontweight="bold",
            transform=ax.transAxes)

    # 하단 핵심 메시지
    BOT_Y = 0.04
    BOT_H = 0.09
    rect = mpatches.FancyBboxPatch(
        (0.06, BOT_Y), 0.88, BOT_H,
        boxstyle="round,pad=0.010",
        facecolor=GREEN, alpha=0.06,
        edgecolor=GREEN, linewidth=1.0,
        transform=ax.transAxes
    )
    ax.add_patch(rect)
    ax.text(0.5, BOT_Y + BOT_H / 2 + 0.012,
            "\\$3,600억 무기 판매 vs \\$10B 소프트웨어 계약",
            ha="center", va="center",
            color=GREEN, fontsize=10.5, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, BOT_Y + BOT_H / 2 - 0.02,
            "어느 쪽이 억지력인가",
            ha="center", va="center",
            color=DIM, fontsize=9,
            transform=ax.transAxes)

    return _save(fig, "01_old_vs_new_paradigm.png")


# ══════════════════════════════════════════════════════════════════════════════
# 02. 2024~2026 국방 계약 타임라인 + 금액
# ══════════════════════════════════════════════════════════════════════════════
def make_defense_contracts() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "국방 계약 타임라인",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "2024~2026 주요 계약 + 금액",
            ha="center", va="center", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # 타임라인 기준선
    LINE_Y = 0.50
    X_START, X_END = 0.08, 0.92
    ax.plot([X_START, X_END], [LINE_Y, LINE_Y],
            color=BORDER, linewidth=2.5,
            transform=ax.transAxes, zorder=1)

    # 연도 범위
    YEAR_MIN = 2024.0
    YEAR_MAX = 2026.5

    def year_to_x(y: float) -> float:
        return X_START + (y - YEAR_MIN) / (YEAR_MAX - YEAR_MIN) * (X_END - X_START)

    # 연도 마커
    for yr in [2024, 2025, 2026]:
        x = year_to_x(yr)
        ax.text(x, LINE_Y - 0.04, str(yr),
                ha="center", va="top",
                color=GRAY, fontsize=9, fontweight="bold",
                transform=ax.transAxes)
        ax.plot([x, x], [LINE_Y - 0.015, LINE_Y + 0.015],
                color=GRAY, linewidth=1.5,
                transform=ax.transAxes)

    # 계약 이벤트
    events = [
        (2024.25, "TITAN", "\\$178M", "AI 심층 감지 시스템\n1차 납품 완료", BLUE, +1),
        (2024.90, "Anduril\n컨소시엄", "", "경쟁 → 협력 전환\n역할 분담 합의", ORANGE, -1),
        (2025.30, "NATO MSS", "", "30일 내 운용 개시\n35개 전투사령부", YELLOW, +1),
        (2025.42, "Maven", "\\$1.3B", "20,000+ 사용자\n2029년까지 상한", PURPLE, -1),
        (2025.58, "Army EA", "\\$10B", "75개 계약 통합\n역대 최대 SW 계약", GREEN, +1),
        (2026.17, "Warp Speed\n코호트 2", "", "6개 방산 스타트업\n제조/배포 인프라", BLUE, -1),
    ]

    for yr, name, amount, desc, color, direction in events:
        x = year_to_x(yr)

        # 마커
        ax.scatter(x, LINE_Y, s=120, color=color, zorder=4,
                   transform=ax.transAxes)
        ax.scatter(x, LINE_Y, s=40, color=BG, zorder=5,
                   transform=ax.transAxes)

        # 수직 연결선
        stem_len = 0.22
        y_end = LINE_Y + direction * stem_len
        ax.plot([x, x], [LINE_Y, y_end],
                color=color, linewidth=1.0, alpha=0.5,
                transform=ax.transAxes, zorder=2)

        # 카드
        card_w = 0.14
        card_h = 0.13
        card_y = y_end + (0.01 if direction > 0 else -card_h - 0.01)

        rect = mpatches.FancyBboxPatch(
            (x - card_w / 2, card_y), card_w, card_h,
            boxstyle="round,pad=0.008",
            facecolor=BG2,
            edgecolor=color, linewidth=1.0,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 이름
        name_y = card_y + card_h - 0.025
        ax.text(x, name_y, name,
                ha="center", va="center",
                color=color, fontsize=8, fontweight="bold",
                multialignment="center",
                transform=ax.transAxes)

        # 금액 (있으면)
        if amount:
            ax.text(x, name_y - 0.035, amount,
                    ha="center", va="center",
                    color=WHITE, fontsize=11, fontweight="bold",
                    transform=ax.transAxes)
            desc_y = name_y - 0.07
        else:
            desc_y = name_y - 0.04

        # 설명
        ax.text(x, desc_y, desc,
                ha="center", va="center",
                color=DIM, fontsize=6.5,
                multialignment="center", linespacing=1.3,
                transform=ax.transAxes)

    # 하단 인사이트
    ax.text(0.5, 0.06,
            "20년간 편을 지킨 회사에게 시장이 보낸 답",
            ha="center", va="center",
            color=GREEN, fontsize=11, fontweight="bold",
            transform=ax.transAxes)

    return _save(fig, "02_defense_contracts.png")


# ══════════════════════════════════════════════════════════════════════════════
# QA
# ══════════════════════════════════════════════════════════════════════════════
def qa_check() -> None:
    from PIL import Image
    files = [
        OUT / "01_old_vs_new_paradigm.png",
        OUT / "02_defense_contracts.png",
    ]
    print("\n-- QA -------------------------------------------")
    for fp in files:
        issues = []
        if not fp.exists():
            print(f"  x {fp.name} -- no file"); continue
        size_kb = fp.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"size too small ({size_kb:.1f} KB)")
        with Image.open(fp) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"resolution low ({w}x{h}px, min 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"ratio off ({ratio:.2f})")
        if issues:
            print(f"  !! {fp.name}")
            for i in issues:
                print(f"       -> {i}")
        else:
            print(f"  OK {fp.name} ({size_kb:.0f} KB, {w}x{h}px)")
    print("-" * 49)


if __name__ == "__main__":
    print("3 Geopolitics visuals ...\n")
    make_paradigm_comparison()
    print("  + 01 old vs new paradigm")
    make_defense_contracts()
    print("  + 02 defense contracts")
    qa_check()
    print(f"\nSaved to: {OUT}\n")
