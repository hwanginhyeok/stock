"""HIMS 아티클 시각화 — 히어로 + GLP-1 가격 비교 + 글로벌 확장 카드"""
import os
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

matplotlib.use("Agg")

HERE = Path(__file__).parent
OUT = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# 한글 폰트
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# 색상 팔레트
BG = "#0d1117"
BG2 = "#161b22"
GREEN = "#3fb950"
YELLOW = "#d29922"
RED = "#f85149"
BLUE = "#58a6ff"
ORANGE = "#db6d28"
GRAY = "#6e7681"
WHITE = "#e6edf3"
DIM = "#8b949e"
PURPLE = "#a371f7"

FIG_SIZE = (8, 8)
DPI = 135


def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(
        path, dpi=DPI, bbox_inches="tight",
        facecolor=fig.get_facecolor(), pad_inches=0.1,
    )
    plt.close(fig)
    return path


# ── Visual 0: 히어로 — HIMS 핵심 지표 대시보드 ───────────────────


def make_hero() -> Path:
    """HIMS 히어로 이미지 — 핵심 밸류에이션 + 성장 지표 대시보드"""
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── Title ──
    ax.text(
        0.5, 0.94, "HIMS",
        fontsize=42, fontweight="bold", color=WHITE,
        ha="center", va="top",
    )
    ax.text(
        0.5, 0.86, "약은 누구나 팔 수 있다",
        fontsize=20, color=DIM, ha="center", va="top",
    )

    # ── Subtitle line ──
    ax.plot([0.2, 0.8], [0.82, 0.82], color=BLUE, linewidth=1.5, alpha=0.5)

    ax.text(
        0.5, 0.785, "Hims & Hers Health  |  의료 민주화 플랫폼",
        fontsize=12, color=GRAY, ha="center", va="top",
    )

    # ── 4 metric cards (2x2) ──
    metrics = [
        ("P/S", "1.4x", r"시총 $33억 / 매출 $23.5억", RED),
        ("Rule of 40", "72.5", "성장률 59% + 마진 13.5%", GREEN),
        ("구독자", "251만", "월간 리텐션 82%", BLUE),
        ("글로벌", "3개 대륙", "12개월 내 유럽·캐나다·호주", PURPLE),
    ]

    card_w = 0.38
    card_h = 0.20
    gap_x = 0.06
    gap_y = 0.05
    grid_top = 0.72
    grid_left = 0.5 - (2 * card_w + gap_x) / 2

    for idx, (label, value, sub, color) in enumerate(metrics):
        row = idx // 2
        col = idx % 2
        cx = grid_left + col * (card_w + gap_x)
        cy = grid_top - row * (card_h + gap_y)

        # Card bg
        rect = FancyBboxPatch(
            (cx, cy - card_h), card_w, card_h,
            boxstyle="round,pad=0.012",
            facecolor=BG2, edgecolor=color, linewidth=1.2, alpha=0.9,
        )
        ax.add_patch(rect)

        # Label
        ax.text(
            cx + 0.025, cy - 0.03, label,
            fontsize=11, color=GRAY, ha="left", va="top",
        )
        # Value
        ax.text(
            cx + 0.025, cy - 0.065, value,
            fontsize=26, fontweight="bold", color=color,
            ha="left", va="top",
        )
        # Sub
        ax.text(
            cx + 0.025, cy - card_h + 0.035, sub,
            fontsize=9, color=DIM, ha="left", va="bottom",
        )

    # ── Bottom context ──
    bottom_y = 0.18
    ax.text(
        0.5, bottom_y, r"FY2025  |  매출 $23.5억  |  +59% YoY  |  흑자 전환",
        fontsize=13, fontweight="bold", color=WHITE,
        ha="center", va="center",
    )

    # ── Tagline ──
    ax.text(
        0.5, 0.10, "시장은 \"컴파운딩 약국\"에 가격을 매겼다",
        fontsize=12, color=YELLOW, ha="center", va="center",
    )
    ax.text(
        0.5, 0.055, "하지만 만들어 놓은 것은 글로벌 텔레헬스 플랫폼이다",
        fontsize=12, color=BLUE, ha="center", va="center",
    )

    return _save(fig, "00_hero_hims.png")


# ── Visual 1: GLP-1 가격 비교 ──────────────────────────────────────


def make_price_comparison() -> Path:
    """GLP-1 가격 비교 수평 바 차트 — HIMS vs 빅파마 vs TrumpRx vs 제네릭"""
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── Title ──
    ax.text(
        0.5, 0.96, "GLP-1 가격 지도",
        fontsize=24, fontweight="bold", color=WHITE,
        ha="center", va="top",
    )
    ax.text(
        0.5, 0.91, "같은 약, 다른 가격 \u2014 월 기준 (USD)",
        fontsize=12, color=DIM, ha="center", va="top",
    )

    # ── Data: (label, price, color, group, ref_price_for_savings) ──
    items = [
        ("Wegovy 주사 (Novo)", 1349, RED, "list", None),
        ("Zepbound 주사 (Lilly)", 1086, RED, "list", None),
        ("TrumpRx Wegovy", 350, ORANGE, "gov", 1349),
        ("TrumpRx Zepbound", 346, ORANGE, "gov", 1086),
        ("Medicare GLP-1", 245, ORANGE, "gov", 1349),
        ("HIMS 컴파운딩", 199, BLUE, "hims", 1349),
        ("Wegovy 알약 (Novo)", 149, PURPLE, "next", 1349),
        ("캐나다 제네릭 (추정)", 70, GREEN, "gen", 1349),
        ("인도 제네릭 (추정)", 50, GREEN, "gen", 1349),
    ]

    n = len(items)
    max_price = 1349
    bar_left = 0.35
    bar_max_w = 0.52

    top_y = 0.84
    bottom_y = 0.12
    total_h = top_y - bottom_y
    row_h = total_h / n
    bar_h = row_h * 0.50

    sep_after = {1, 4, 5, 6}

    for i, (label, price, color, group, ref) in enumerate(items):
        y_center = top_y - i * row_h - row_h / 2

        ax.text(
            bar_left - 0.02, y_center, label,
            fontsize=11, color=WHITE, ha="right", va="center",
        )

        w = (price / max_price) * bar_max_w
        rect = FancyBboxPatch(
            (bar_left, y_center - bar_h / 2), w, bar_h,
            boxstyle="round,pad=0.003",
            facecolor=color, edgecolor="none", alpha=0.85,
        )
        ax.add_patch(rect)

        price_str = f"${price:,}" if price >= 100 else f"~${price}"
        txt_x = bar_left + w + 0.015
        ax.text(
            txt_x, y_center, price_str,
            fontsize=11, fontweight="bold", color=color,
            ha="left", va="center",
        )

        if ref is not None:
            pct = (1 - price / ref) * 100
            badge_str = f"-{pct:.0f}%"
            badge_x = txt_x + 0.065
            ax.text(
                badge_x, y_center, badge_str,
                fontsize=9, color=DIM, ha="left", va="center",
            )

        if i in sep_after:
            sep_y = top_y - (i + 1) * row_h
            ax.plot(
                [0.06, 0.94], [sep_y, sep_y],
                color=GRAY, linewidth=0.5, alpha=0.3,
            )

    legend_items = [
        ("\u25cf  빅파마 정가", RED),
        ("\u25cf  TrumpRx/Medicare", ORANGE),
        ("\u25cf  HIMS", BLUE),
        ("\u25cf  제네릭/차세대", GREEN),
    ]
    leg_y = 0.05
    total_leg_w = 0.88
    leg_spacing = total_leg_w / len(legend_items)
    for j, (leg_label, leg_color) in enumerate(legend_items):
        lx = 0.06 + j * leg_spacing
        ax.text(
            lx, leg_y, leg_label,
            fontsize=10, color=leg_color, ha="left", va="center",
        )

    return _save(fig, "01_glp1_price_comparison.png")


# ── Visual 2: 글로벌 확장 인수 카드 ────────────────────────────────


def make_global_expansion() -> Path:
    """HIMS 글로벌 확장 — 3개 대륙 인수 기업 카드 (재무 데이터 포함)"""
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # ── Title ──
    ax.text(
        0.5, 0.96, "HIMS 글로벌 확장",
        fontsize=24, fontweight="bold", color=WHITE,
        ha="center", va="top",
    )
    ax.text(
        0.5, 0.91, "3개 대륙, 12개월 \u2014 컴파운딩 없는 텔레헬스 인프라",
        fontsize=12, color=DIM, ha="center", va="top",
    )

    # ── Card data (updated with financial figures) ──
    cards = [
        {
            "name": "ZAVA",
            "region": "영국 / 독일\n프랑스 / 아일랜드",
            "accent": "#4488ff",  # EU blue (brighter)
            "date": "2025.07",
            "stats": [
                ("인수가", "$2.58억"),
                ("고객", "130만 명"),
                ("매출 기여", "국제 400%↑"),
            ],
            "tag": "유럽 4개국 — 국제 매출 견인",
        },
        {
            "name": "Livewell",
            "region": "캐나다",
            "accent": "#FF4444",  # Canada red (brighter)
            "date": "2025.12",
            "stats": [
                ("제네릭 가격", "$60-70 CAD/월"),
                ("모델", "컴파운딩 없이 운영"),
                ("의미", "HIMS 모델 첫 증명"),
            ],
            "tag": "제네릭 GLP-1 시험대",
        },
        {
            "name": "Eucalyptus",
            "region": "호주 / 영국 / 일본",
            "accent": "#FFCD00",  # Australia gold
            "date": "2026.02",
            "stats": [
                ("인수가", "$11.5억"),
                ("ARR", "$4.5억+"),
                ("성장", "매 분기 3자리수 YoY"),
            ],
            "tag": "P/S 2.5x · 3자리수 성장 인수",
        },
    ]

    card_w = 0.275
    gap = 0.037
    start_x = 0.5 - (3 * card_w + 2 * gap) / 2
    card_top = 0.84
    card_bot = 0.18
    card_h = card_top - card_bot

    for i, card in enumerate(cards):
        cx = start_x + i * (card_w + gap)

        bg_rect = FancyBboxPatch(
            (cx, card_bot), card_w, card_h,
            boxstyle="round,pad=0.015",
            facecolor=BG2, edgecolor=GRAY, linewidth=0.8,
        )
        ax.add_patch(bg_rect)

        accent_rect = FancyBboxPatch(
            (cx + 0.012, card_top - 0.012), card_w - 0.024, 0.006,
            boxstyle="round,pad=0.001",
            facecolor=card["accent"], edgecolor="none", alpha=0.8,
        )
        ax.add_patch(accent_rect)

        ax.text(
            cx + card_w / 2, card_top - 0.06, card["name"],
            fontsize=18, fontweight="bold", color=WHITE,
            ha="center", va="top",
        )

        ax.text(
            cx + card_w / 2, card_top - 0.12, card["region"],
            fontsize=9, color=DIM, ha="center", va="top",
            linespacing=1.5,
        )

        badge_y = card_top - 0.22
        badge_w = 0.085
        badge_rect = FancyBboxPatch(
            (cx + card_w / 2 - badge_w / 2, badge_y - 0.013),
            badge_w, 0.026,
            boxstyle="round,pad=0.005",
            facecolor=card["accent"], edgecolor="none", alpha=0.15,
        )
        ax.add_patch(badge_rect)
        ax.text(
            cx + card_w / 2, badge_y, card["date"],
            fontsize=10, fontweight="bold", color=card["accent"],
            ha="center", va="center",
        )

        stats_top = card_top - 0.30
        for j, (key, val) in enumerate(card["stats"]):
            sy = stats_top - j * 0.09

            ax.text(
                cx + 0.025, sy, key,
                fontsize=9, color=GRAY, ha="left", va="top",
            )
            ax.text(
                cx + 0.025, sy - 0.028, val,
                fontsize=12, fontweight="bold", color=WHITE,
                ha="left", va="top",
            )

        tag_y = card_bot + 0.035
        ax.text(
            cx + card_w / 2, tag_y, card["tag"],
            fontsize=9, fontweight="bold", color=card["accent"],
            ha="center", va="center", alpha=0.85,
        )

    # ── Bottom insight ──
    ax.text(
        0.5, 0.10,
        "국제 매출: FY2024 $0.27억 → FY2025 $1.34억 → 장기 $10억+ 목표",
        fontsize=12, fontweight="bold", color=GREEN,
        ha="center", va="center",
    )
    ax.text(
        0.5, 0.05, "약이 아니라 플랫폼을 수출한다",
        fontsize=11, color=DIM, ha="center", va="center",
    )

    return _save(fig, "02_global_expansion.png")


# ── QA ──────────────────────────────────────────────────────────────


def qa_check() -> None:
    from PIL import Image

    files = [
        OUT / "00_hero_hims.png",
        OUT / "01_glp1_price_comparison.png",
        OUT / "02_global_expansion.png",
    ]
    print("\n=== QA Check ===")
    for fp in files:
        issues: list[str] = []
        if not fp.exists():
            print(f"  [X] {fp.name} -- file missing")
            continue
        size_kb = fp.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"file too small ({size_kb:.1f} KB)")
        with Image.open(fp) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"resolution too low ({w}x{h}px, min 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"ratio out of range ({ratio:.2f})")
        if issues:
            print(f"  [!] {fp.name}")
            for issue in issues:
                print(f"       -> {issue}")
        else:
            print(f"  [OK] {fp.name} ({size_kb:.0f} KB, {w}x{h}px)")


if __name__ == "__main__":
    print("Generating HIMS visuals...")
    p0 = make_hero()
    print(f"  -> {p0}")
    p1 = make_price_comparison()
    print(f"  -> {p1}")
    p2 = make_global_expansion()
    print(f"  -> {p2}")
    qa_check()
    print("\nDone.")
