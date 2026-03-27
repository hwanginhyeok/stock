#!/usr/bin/env python3
"""KR-04 현대차 철학비교 — 시각화 생성

📎 1: Tesla 5단계 제조 철학 (대부분의 기업 vs Tesla 시작점)
📎 2: 자율주행 센서 비교 (Tesla vs Waymo vs 42dot)
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

# ── 경로 ──────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(SCRIPT_DIR, "visuals")
os.makedirs(OUT_DIR, exist_ok=True)

# ── 한글 폰트 ────────────────────────────────────
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# ── 색상 팔레트 ──────────────────────────────────
BG = "#0d1117"
CARD_BG = "#161b22"
BLUE = "#58a6ff"
GREEN = "#3fb950"
YELLOW = "#d29922"
ORANGE = "#db6d28"
RED = "#f85149"
GRAY = "#6e7681"
WHITE = "#e6edf3"
DIM = "#8b949e"


# ═══════════════════════════════════════════════════
# 📎 1: Tesla 5단계 제조 철학
# ═══════════════════════════════════════════════════
def generate_01_tesla_5steps():
    fig, ax = plt.subplots(figsize=(10, 8))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # 제목
    ax.text(5, 9.4, "Tesla 5단계 제조 철학", fontsize=22, fontweight="bold",
            color=WHITE, ha="center", va="center")
    ax.text(5, 8.85, "순서가 핵심이다 — 대부분의 기업은 4단계에서 시작한다",
            fontsize=12, color=DIM, ha="center", va="center")

    steps = [
        ("1", "요구조건을 의심하라", '"누가 이 요구조건을 넣었는가?"'),
        ("2", "삭제하라", '"없는 부품이 최고의 부품이다"'),
        ("3", "단순화 / 최적화", "존재하지 않아야 할 것을 최적화하지 마라"),
        ("4", "사이클 시간을 가속하라", "라인 속도 ↑  택트 타임 ↓"),
        ("5", "자동화하라", "자동화는 마지막이다"),
    ]

    # 색상: 1-3 = Tesla zone (blue), 4-5 = Industry zone (gray)
    step_colors = [BLUE, BLUE, BLUE, GRAY, GRAY]
    step_accent = [GREEN, GREEN, GREEN, ORANGE, ORANGE]

    y_start = 8.0
    bar_h = 1.15
    gap = 0.18

    for i, (num, title, desc) in enumerate(steps):
        y = y_start - i * (bar_h + gap)
        color = step_colors[i]
        accent = step_accent[i]

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (0.8, y - bar_h / 2), 8.4, bar_h,
            boxstyle="round,pad=0.15", facecolor=CARD_BG,
            edgecolor=color, linewidth=1.5, alpha=0.9
        )
        ax.add_patch(rect)

        # 번호 원
        circle = plt.Circle((1.7, y), 0.35, color=accent, alpha=0.9)
        ax.add_patch(circle)
        ax.text(1.7, y, num, fontsize=16, fontweight="bold",
                color=BG, ha="center", va="center")

        # 제목 + 설명
        ax.text(2.5, y + 0.18, title, fontsize=14, fontweight="bold",
                color=WHITE, va="center")
        ax.text(2.5, y - 0.25, desc, fontsize=10, color=DIM, va="center")

    # 좌측 레이블: Tesla 시작점
    ax.annotate(
        "Tesla →\n여기서 시작",
        xy=(0.6, y_start - 0 * (bar_h + gap)),
        fontsize=10, fontweight="bold", color=GREEN,
        ha="right", va="center",
    )

    # 좌측 레이블: 대부분의 기업
    ax.annotate(
        "대부분의 기업 →\n여기서 시작",
        xy=(0.6, y_start - 3 * (bar_h + gap)),
        fontsize=10, fontweight="bold", color=ORANGE,
        ha="right", va="center",
    )

    # 하단 주석
    ax.text(5, 0.3, "출처: Elon Musk, Everyday Astronaut Starbase Tour (2021)",
            fontsize=8, color=GRAY, ha="center", va="center")

    out = os.path.join(OUT_DIR, "01_tesla_5steps.png")
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.3)
    plt.close(fig)
    print(f"  ✅ {out}")
    return out


# ═══════════════════════════════════════════════════
# 📎 2: 자율주행 센서 비교
# ═══════════════════════════════════════════════════
def generate_02_sensor_comparison():
    fig, ax = plt.subplots(figsize=(10, 8.5))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # ── 제목 ──
    ax.text(5, 9.45, "자율주행 센서 — 같은 목표, 다른 질문",
            fontsize=20, fontweight="bold", color=WHITE, ha="center")
    ax.text(5, 8.95, "Giga Press가 부품을 삭제했다면, 순수 비전은 감각을 삭제했다",
            fontsize=11, color=DIM, ha="center")

    # ── 3사 데이터 ──
    companies = [
        {
            "name": "Tesla",
            "approach": "순수 비전 (Vision Only)",
            "sensors": [
                ("카메라", "8대", GREEN),
            ],
            "total": "8개",
            "cost": "~$1,000",
            "color": GREEN,
            "question": '"카메라 외에 다른 센서가\n 필요한가?"',
        },
        {
            "name": "42dot (현대차)",
            "approach": "센서 퓨전 (Lite)",
            "sensors": [
                ("카메라", "8대", BLUE),
                ("레이더", "1대", YELLOW),
            ],
            "total": "9개",
            "cost": "$35B 투자",
            "color": YELLOW,
            "question": '"센서를 어떻게 더\n 추가할까?"',
        },
        {
            "name": "Waymo",
            "approach": "풀 센서 퓨전",
            "sensors": [
                ("카메라", "13대", BLUE),
                ("LiDAR", "4대", RED),
                ("레이더", "6대", YELLOW),
            ],
            "total": "23개",
            "cost": "~$200,000+",
            "color": RED,
            "question": '"어떻게 더 정밀하게\n 감지할까?"',
        },
    ]

    # ── 레이아웃: 3개 카드 가로 배치 ──
    card_w = 2.7
    card_h = 5.8
    gap = 0.3
    total_w = 3 * card_w + 2 * gap
    x_start = (10 - total_w) / 2
    y_top = 8.2

    for ci, comp in enumerate(companies):
        cx = x_start + ci * (card_w + gap)
        cy = y_top

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (cx, cy - card_h), card_w, card_h,
            boxstyle="round,pad=0.15", facecolor=CARD_BG,
            edgecolor=comp["color"], linewidth=2.0, alpha=0.95
        )
        ax.add_patch(rect)

        # 회사명
        ax.text(cx + card_w / 2, cy - 0.4, comp["name"],
                fontsize=14, fontweight="bold", color=comp["color"],
                ha="center", va="center")

        # 접근법
        ax.text(cx + card_w / 2, cy - 0.85, comp["approach"],
                fontsize=9, color=DIM, ha="center", va="center")

        # 구분선
        ax.plot([cx + 0.3, cx + card_w - 0.3], [cy - 1.15, cy - 1.15],
                color=GRAY, linewidth=0.5, alpha=0.5)

        # 센서 목록
        sensor_y = cy - 1.6
        for si, (stype, scount, scolor) in enumerate(comp["sensors"]):
            y = sensor_y - si * 0.65

            # 센서 타입 아이콘 (작은 원)
            circle = plt.Circle((cx + 0.45, y), 0.12, color=scolor, alpha=0.8)
            ax.add_patch(circle)

            ax.text(cx + 0.75, y, stype,
                    fontsize=10, color=WHITE, va="center")
            ax.text(cx + card_w - 0.3, y, scount,
                    fontsize=11, fontweight="bold", color=scolor,
                    ha="right", va="center")

        # 빈 센서 슬롯 표시 (Tesla만 — 삭제된 것들)
        if comp["name"] == "Tesla":
            deleted_y = sensor_y - 1 * 0.65
            for di, deleted in enumerate(["LiDAR", "레이더"]):
                y = deleted_y - di * 0.55
                ax.text(cx + 0.75, y, deleted,
                        fontsize=9, color=GRAY, va="center", alpha=0.4)
                ax.text(cx + card_w - 0.3, y, "삭제",
                        fontsize=9, fontweight="bold", color=RED,
                        ha="right", va="center", alpha=0.6)
                # 취소선 효과
                ax.plot([cx + 0.65, cx + card_w - 0.2], [y, y],
                        color=RED, linewidth=0.8, alpha=0.3)

        # 하단: 총 센서 수 + 비용
        bottom_y = cy - card_h + 1.5

        # 구분선
        ax.plot([cx + 0.3, cx + card_w - 0.3], [bottom_y + 0.45, bottom_y + 0.45],
                color=GRAY, linewidth=0.5, alpha=0.5)

        ax.text(cx + card_w / 2, bottom_y + 0.05, f"센서 합계: {comp['total']}",
                fontsize=11, fontweight="bold", color=WHITE, ha="center", va="center")
        ax.text(cx + card_w / 2, bottom_y - 0.4, f"비용: {comp['cost']}",
                fontsize=10, color=comp["color"], ha="center", va="center")

        # 질문
        ax.text(cx + card_w / 2, bottom_y - 1.1, comp["question"],
                fontsize=8.5, color=DIM, ha="center", va="center",
                fontstyle="italic", linespacing=1.4)

    # ── 하단 핵심 메시지 ──
    ax.text(5, 0.7, "인간은 눈 두 개로 운전한다. 360° 카메라 8대는 이미 인간보다 많이 본다.",
            fontsize=10.5, color=WHITE, ha="center", va="center", fontweight="bold")

    # 출처
    ax.text(5, 0.2, "출처: Tesla 공식, Waymo 6세대 사양, 42dot Atria AI (CES 2026)",
            fontsize=7.5, color=GRAY, ha="center", va="center")

    out = os.path.join(OUT_DIR, "02_sensor_comparison.png")
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=BG, pad_inches=0.3)
    plt.close(fig)
    print(f"  ✅ {out}")
    return out


# ═══════════════════════════════════════════════════
# QA 체크
# ═══════════════════════════════════════════════════
def qa_check(paths: list[str]):
    print("\n📎 QA 검증")
    print("─" * 40)
    ok = True
    for p in paths:
        if not os.path.exists(p):
            print(f"  ❌ 파일 없음: {p}")
            ok = False
            continue
        size = os.path.getsize(p)
        if size < 10_000:
            print(f"  ⚠️ 파일 작음 ({size:,} bytes): {p}")
            ok = False
        else:
            print(f"  ✅ {os.path.basename(p)} — {size:,} bytes")

    # 마커 수 검증
    v2_path = os.path.join(SCRIPT_DIR, "drafts", "kr-04_hyundai_philosophy_v2.md")
    xp_path = os.path.join(SCRIPT_DIR, "drafts", "kr-04_hyundai_philosophy_x_publish.md")

    for label, fpath in [("v2", v2_path), ("x_publish", xp_path)]:
        if os.path.exists(fpath):
            with open(fpath, encoding="utf-8") as f:
                count = f.read().count("📎")
            expected = len(paths)
            status = "✅" if count == expected else "❌"
            print(f"  {status} {label} 📎 마커: {count}개 (기대: {expected})")

    if ok:
        print("\n✅ QA 통과")
    else:
        print("\n⚠️ QA 이슈 있음 — 위 항목 확인")
    return ok


# ═══════════════════════════════════════════════════
# 메인
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    print("🎨 KR-04 현대차 철학비교 — 시각화 생성")
    print("=" * 40)

    paths = [
        generate_01_tesla_5steps(),
        generate_02_sensor_comparison(),
    ]

    qa_check(paths)
