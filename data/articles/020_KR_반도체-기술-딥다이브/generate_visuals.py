"""KR-02 반도체 기술 딥다이브 — 시각화 생성 스크립트."""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.gridspec import GridSpec
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


def fig_base(rows=1, cols=1, height_ratio=1.0):
    """Create a dark-themed figure."""
    fig = plt.figure(
        figsize=(SIZE_IN, SIZE_IN * height_ratio),
        dpi=DPI,
        facecolor=BG,
    )
    return fig


# ═══════════════════════════════════════════════════════════
# Visual 1: 수율의 지수 법칙
# ═══════════════════════════════════════════════════════════
def gen_yield_curve():
    """수율의 지수 법칙 — 단일 다이 수율별 최종 스택 수율 곡선."""
    fig = fig_base()
    ax = fig.add_axes([0.12, 0.12, 0.82, 0.72])
    ax.set_facecolor(CARD_BG)

    layers = np.arange(1, 21)
    die_yields = [0.99, 0.97, 0.95, 0.90]
    colors = [GREEN, BLUE, YELLOW, RED]
    labels = ["99%", "97%", "95%", "90%"]

    for dy, color, label in zip(die_yields, colors, labels):
        stack_yield = (dy ** layers) * 100
        ax.plot(layers, stack_yield, color=color, linewidth=2.2,
                label=f"다이 수율 {label}", zorder=3)
        # Endpoint label
        ax.text(20.3, stack_yield[-1], f"{stack_yield[-1]:.0f}%",
                color=color, fontsize=8, va="center", fontweight="bold")

    # Reference lines for SK Hynix (~80%) and Samsung (~50%)
    ax.axhline(y=80, color=GREEN, linestyle="--", alpha=0.3, linewidth=1)
    ax.text(1.2, 82, "SK하이닉스 실측 ~80% (12단)", color=GREEN,
            fontsize=7.5, alpha=0.7)
    ax.axhline(y=50, color=RED, linestyle="--", alpha=0.3, linewidth=1)
    ax.text(1.2, 52, "삼성 실측 ~50% (12단)", color=RED,
            fontsize=7.5, alpha=0.7)

    # Vertical reference lines for common stacking
    for n, lbl in [(8, "8-Hi"), (12, "12-Hi"), (16, "16-Hi")]:
        ax.axvline(x=n, color=GRAY, linestyle=":", alpha=0.4, linewidth=0.8)
        ax.text(n, 2, lbl, color=LIGHT_GRAY, fontsize=7, ha="center")

    ax.set_xlim(1, 22)
    ax.set_ylim(0, 105)
    ax.set_xlabel("적층 수 (레이어)", color=WHITE, fontsize=10)
    ax.set_ylabel("최종 스택 수율 (%)", color=WHITE, fontsize=10)
    ax.set_xticks([1, 4, 8, 12, 16, 20])
    ax.tick_params(colors=LIGHT_GRAY, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["left"].set_color(BORDER)
    ax.grid(axis="y", color=BORDER, alpha=0.3, linewidth=0.5)
    ax.legend(loc="upper right", fontsize=8, facecolor=CARD_BG,
              edgecolor=BORDER, labelcolor=WHITE, framealpha=0.9)

    # Title
    fig.text(0.5, 0.92, "수율의 지수 법칙", color=WHITE,
             fontsize=16, fontweight="bold", ha="center")
    fig.text(0.5, 0.875, "단일 다이 수율 4%p 차이가 16단 스택에서 41%p 격차로 벌어진다",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    path = os.path.join(OUT_DIR, "01_yield_exponential.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 2: MR-MUF vs TC-NCF 비교
# ═══════════════════════════════════════════════════════════
def gen_bonding_comparison():
    """MR-MUF vs TC-NCF — 핵심 지표 비교 카드."""
    fig = fig_base()

    # Title
    fig.text(0.5, 0.93, "MR-MUF vs TC-NCF", color=WHITE,
             fontsize=16, fontweight="bold", ha="center")
    fig.text(0.5, 0.885, "같은 DRAM, 같은 설계 — 본딩 방식 하나가 만든 격차",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    # Two card columns — gap widened for metric labels
    left_x, right_x = 0.04, 0.58
    card_w = 0.38
    card_h = 0.72
    card_y = 0.10

    # Left card — SK Hynix MR-MUF
    left_card = mpatches.FancyBboxPatch(
        (left_x, card_y), card_w, card_h,
        boxstyle="round,pad=0.015", facecolor=CARD_BG,
        edgecolor=GREEN, linewidth=1.5,
        transform=fig.transFigure, zorder=1,
    )
    fig.patches.append(left_card)

    # Right card — Samsung TC-NCF
    right_card = mpatches.FancyBboxPatch(
        (right_x, card_y), card_w, card_h,
        boxstyle="round,pad=0.015", facecolor=CARD_BG,
        edgecolor=RED, linewidth=1.5,
        transform=fig.transFigure, zorder=1,
    )
    fig.patches.append(right_card)

    # Card headers
    fig.text(left_x + card_w / 2, card_y + card_h - 0.04,
             "SK하이닉스", color=GREEN, fontsize=14,
             fontweight="bold", ha="center", zorder=2)
    fig.text(left_x + card_w / 2, card_y + card_h - 0.09,
             "MR-MUF", color=WHITE, fontsize=11, ha="center", zorder=2)

    fig.text(right_x + card_w / 2, card_y + card_h - 0.04,
             "삼성", color=RED, fontsize=14,
             fontweight="bold", ha="center", zorder=2)
    fig.text(right_x + card_w / 2, card_y + card_h - 0.09,
             "TC-NCF", color=WHITE, fontsize=11, ha="center", zorder=2)

    # Comparison rows
    rows = [
        ("본딩 방식", "일괄 리플로우", "순차 열압착"),
        ("온도", "~260°C", "~300°C"),
        ("열전도 소재", "EMC (高)", "NCF (低)"),
        ("수율", "~80%", "~50-60%"),
        ("NVIDIA 인증", "선발 납품", "18개월 지연"),
        ("핵심 공급사", "Namics (日)", "—"),
    ]

    row_start_y = card_y + card_h - 0.16
    row_gap = 0.11

    for i, (metric, left_val, right_val) in enumerate(rows):
        y = row_start_y - i * row_gap

        # Metric label (centered between cards)
        fig.text(0.5, y + 0.025, metric, color=LIGHT_GRAY, fontsize=8,
                 ha="center", zorder=2)

        # Left value
        left_color = GREEN if i in (3, 4) else WHITE  # highlight yield & nvidia
        fig.text(left_x + card_w / 2, y - 0.01, left_val,
                 color=left_color, fontsize=10.5, fontweight="bold",
                 ha="center", zorder=2)

        # Right value
        right_color = RED if i in (3, 4) else WHITE
        fig.text(right_x + card_w / 2, y - 0.01, right_val,
                 color=right_color, fontsize=10.5, fontweight="bold",
                 ha="center", zorder=2)

        # Separator line
        if i < len(rows) - 1:
            sep_y = y - 0.035
            line_l = mlines.Line2D(
                [left_x + 0.03, left_x + card_w - 0.03],
                [sep_y, sep_y], color=BORDER, linewidth=0.5,
                transform=fig.transFigure, zorder=2)
            fig.add_artist(line_l)
            line_r = mlines.Line2D(
                [right_x + 0.03, right_x + card_w - 0.03],
                [sep_y, sep_y], color=BORDER, linewidth=0.5,
                transform=fig.transFigure, zorder=2)
            fig.add_artist(line_r)

    # Bottom note
    fig.text(0.5, 0.03, "30%p 수율 격차 = 18개월 납품 지연",
             color=YELLOW, fontsize=9, fontweight="bold", ha="center")

    path = os.path.join(OUT_DIR, "02_bonding_comparison.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 3: HBM 시장 점유율 변동
# ═══════════════════════════════════════════════════════════
def gen_market_share():
    """HBM 시장 점유율 변동 — 삼성의 붕괴와 SK하이닉스의 부상."""
    fig = fig_base()
    ax = fig.add_axes([0.12, 0.12, 0.82, 0.70])
    ax.set_facecolor(CARD_BG)

    periods = ["2024 초", "2025 Q2", "2025 Q3", "2026 전망"]
    x = np.arange(len(periods))
    bar_w = 0.22

    # Data
    sk = [50, 62, 57, 50]
    samsung = [60, 17, 22, 30]
    micron = [5, 21, 21, 20]  # 2024초 소량 → ~5% 추정

    colors_sk = [BLUE, GREEN, GREEN, BLUE]
    colors_ss = [GREEN, RED, ORANGE, YELLOW]
    colors_mc = [GRAY, BLUE, BLUE, BLUE]

    # Bars
    bars_sk = ax.bar(x - bar_w, sk, bar_w, color=BLUE, label="SK하이닉스",
                     edgecolor=BG, linewidth=0.5, zorder=3)
    bars_ss = ax.bar(x, samsung, bar_w, color=RED, label="삼성",
                     edgecolor=BG, linewidth=0.5, zorder=3)
    bars_mc = ax.bar(x + bar_w, micron, bar_w, color=YELLOW, label="Micron",
                     edgecolor=BG, linewidth=0.5, zorder=3)

    # Value labels
    for bars, vals in [(bars_sk, sk), (bars_ss, samsung), (bars_mc, micron)]:
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5,
                    f"{v}%", ha="center", va="bottom", color=WHITE,
                    fontsize=8, fontweight="bold")

    # Samsung collapse annotation
    ax.annotate("", xy=(1, 17), xytext=(0, 60),
                arrowprops=dict(arrowstyle="->", color=RED,
                                lw=1.5, connectionstyle="arc3,rad=-0.2"))
    ax.text(0.65, 42, "−43%p", color=RED, fontsize=10,
            fontweight="bold", rotation=-50)

    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(0, 75)
    ax.set_xticks(x)
    ax.set_xticklabels(periods, color=WHITE, fontsize=9)
    ax.set_ylabel("시장 점유율 (%)", color=WHITE, fontsize=10)
    ax.tick_params(colors=LIGHT_GRAY, labelsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color(BORDER)
    ax.spines["left"].set_color(BORDER)
    ax.grid(axis="y", color=BORDER, alpha=0.3, linewidth=0.5)
    ax.legend(loc="upper right", fontsize=8.5, facecolor=CARD_BG,
              edgecolor=BORDER, labelcolor=WHITE, framealpha=0.9)

    # Title
    fig.text(0.5, 0.92, "HBM 시장 점유율 변동", color=WHITE,
             fontsize=16, fontweight="bold", ha="center")
    fig.text(0.5, 0.875, "1년 반 만에 삼성 60% → 17% — 부회장이 공개 사과했다",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    path = os.path.join(OUT_DIR, "03_market_share.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 4: 대표 이미지 — HBM4 3사 대결
# ═══════════════════════════════════════════════════════════
def gen_hero_image():
    """대표 이미지 — SK하이닉스 vs 삼성 vs Micron HBM4 3사 대결."""
    IMG_DIR = os.path.join(SCRIPT_DIR, "images")

    fig = fig_base(height_ratio=1.0)

    # ── Title area ──
    fig.text(0.5, 0.94, "HBM4 — 3사의 승부", color=WHITE,
             fontsize=20, fontweight="bold", ha="center")
    fig.text(0.5, 0.895, "같은 규격, 다른 전략 — 누가 AI의 기억을 지배하는가",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    # ── Three columns: product images + company info ──
    companies = [
        {
            "name": "SK하이닉스", "color": GREEN,
            "img": os.path.join(IMG_DIR, "03_skhynix_hbm4_press.png"),
            "share": "57%", "tag": "선두 주자",
            "strategy": "TSMC 협업\n수율 최적화",
        },
        {
            "name": "삼성", "color": RED,
            "img": os.path.join(IMG_DIR, "07_samsung_hbm4_02.png"),
            "share": "22%", "tag": "턴키 반격",
            "strategy": "자체 파운드리\n풀스택 수직통합",
        },
        {
            "name": "Micron", "color": YELLOW,
            "img": os.path.join(IMG_DIR, "04_micron_hbm4.jpg"),
            "share": "21%", "tag": "효율 추격",
            "strategy": "저전력 특화\nBrownfield 전략",
        },
    ]

    col_w = 0.28
    gap = 0.04
    total_w = 3 * col_w + 2 * gap
    start_x = (1.0 - total_w) / 2

    img_top = 0.82
    img_h = 0.32

    for i, co in enumerate(companies):
        cx = start_x + i * (col_w + gap)
        mid_x = cx + col_w / 2

        # Card background
        card = mpatches.FancyBboxPatch(
            (cx, 0.06), col_w, 0.78,
            boxstyle="round,pad=0.012", facecolor=CARD_BG,
            edgecolor=co["color"], linewidth=1.8,
            transform=fig.transFigure, zorder=1,
        )
        fig.patches.append(card)

        # Product image
        try:
            img = Image.open(co["img"])
            # Calculate position in figure coords → axes coords
            ax_img = fig.add_axes(
                [cx + 0.02, img_top - img_h, col_w - 0.04, img_h],
                zorder=2,
            )
            ax_img.imshow(img, aspect="equal")
            ax_img.set_facecolor(CARD_BG)
            ax_img.axis("off")
            img.close()
        except Exception as e:
            print(f"  ⚠ 이미지 로드 실패: {co['img']} — {e}")

        # Company name
        fig.text(mid_x, 0.46, co["name"], color=co["color"],
                 fontsize=15, fontweight="bold", ha="center", zorder=3)

        # Tag
        fig.text(mid_x, 0.42, co["tag"], color=WHITE,
                 fontsize=9, ha="center", zorder=3)

        # Market share circle
        fig.text(mid_x, 0.33, co["share"], color=co["color"],
                 fontsize=22, fontweight="bold", ha="center", zorder=3)
        fig.text(mid_x, 0.29, "HBM 점유율", color=LIGHT_GRAY,
                 fontsize=7, ha="center", zorder=3)

        # Separator
        sep = mlines.Line2D(
            [cx + 0.04, cx + col_w - 0.04], [0.25, 0.25],
            color=BORDER, linewidth=0.5,
            transform=fig.transFigure, zorder=3)
        fig.add_artist(sep)

        # Strategy
        fig.text(mid_x, 0.18, co["strategy"], color=LIGHT_GRAY,
                 fontsize=8, ha="center", va="center",
                 linespacing=1.6, zorder=3)

    # VS markers between cards
    for i in range(2):
        vx = start_x + (i + 1) * col_w + (i + 0.5) * gap
        fig.text(vx, 0.65, "VS", color=GRAY, fontsize=11,
                 fontweight="bold", ha="center", va="center",
                 zorder=4, alpha=0.6)

    # Bottom: data source
    fig.text(0.5, 0.02, "점유율: 2025 Q3 기준 | TrendForce, Counterpoint",
             color=GRAY, fontsize=7, ha="center")

    path = os.path.join(OUT_DIR, "00_hero_hbm4_3way.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 5: HBM3E vs HBM4 스펙 비교
# ═══════════════════════════════════════════════════════════
def gen_hbm4_spec():
    """HBM3E vs HBM4 — 핵심 스펙 비교 카드."""
    fig = fig_base()

    # Title
    fig.text(0.5, 0.93, "HBM3E → HBM4", color=WHITE,
             fontsize=18, fontweight="bold", ha="center")
    fig.text(0.5, 0.885, "인터페이스 2배, 대역폭 2배, 용량 2배 — 진짜 변화는 베이스 다이",
             color=LIGHT_GRAY, fontsize=8.5, ha="center")

    # Two columns — wide center gap for metric labels
    left_x, right_x = 0.04, 0.61
    card_w = 0.35
    card_h = 0.74
    card_y = 0.08

    # Left card — HBM3E
    left_card = mpatches.FancyBboxPatch(
        (left_x, card_y), card_w, card_h,
        boxstyle="round,pad=0.015", facecolor=CARD_BG,
        edgecolor=GRAY, linewidth=1.5,
        transform=fig.transFigure, zorder=1,
    )
    fig.patches.append(left_card)

    # Right card — HBM4
    right_card = mpatches.FancyBboxPatch(
        (right_x, card_y), card_w, card_h,
        boxstyle="round,pad=0.015", facecolor=CARD_BG,
        edgecolor=BLUE, linewidth=1.5,
        transform=fig.transFigure, zorder=1,
    )
    fig.patches.append(right_card)

    # Card headers
    fig.text(left_x + card_w / 2, card_y + card_h - 0.04,
             "HBM3E", color=GRAY, fontsize=15,
             fontweight="bold", ha="center", zorder=2)
    fig.text(left_x + card_w / 2, card_y + card_h - 0.08,
             "현재 세대", color=LIGHT_GRAY, fontsize=9, ha="center", zorder=2)

    fig.text(right_x + card_w / 2, card_y + card_h - 0.04,
             "HBM4", color=BLUE, fontsize=15,
             fontweight="bold", ha="center", zorder=2)
    fig.text(right_x + card_w / 2, card_y + card_h - 0.08,
             "차세대", color=LIGHT_GRAY, fontsize=9, ha="center", zorder=2)

    rows = [
        ("인터페이스", "1024-bit\n(16채널)", "2048-bit\n(32채널)", True),
        ("스택당 대역폭", "~1.2 TB/s", "최대 2 TB/s", True),
        ("최대 스택", "12-Hi", "16-Hi", True),
        ("최대 용량", "36GB", "64GB", True),
        ("베이스 다이", "DRAM 공정", "파운드리 공정\n(3~12nm)", True),
    ]

    row_start_y = card_y + card_h - 0.15
    row_gap = 0.125

    for i, (metric, left_val, right_val, highlight) in enumerate(rows):
        y = row_start_y - i * row_gap

        # Metric label (centered)
        fig.text(0.5, y + 0.03, metric, color=LIGHT_GRAY, fontsize=7.5,
                 ha="center", zorder=2)

        # Left value
        fig.text(left_x + card_w / 2, y - 0.005, left_val,
                 color=WHITE, fontsize=10, fontweight="bold",
                 ha="center", va="center", linespacing=1.3, zorder=2)

        # Right value — highlight new
        right_color = BLUE if highlight else WHITE
        fig.text(right_x + card_w / 2, y - 0.005, right_val,
                 color=right_color, fontsize=10, fontweight="bold",
                 ha="center", va="center", linespacing=1.3, zorder=2)

        # Arrow between columns
        fig.text(0.5, y - 0.005, "→", color=YELLOW, fontsize=12,
                 ha="center", va="center", fontweight="bold", zorder=2)

        # Separator
        if i < len(rows) - 1:
            sep_y = y - 0.04
            for cx in [left_x, right_x]:
                line = mlines.Line2D(
                    [cx + 0.03, cx + card_w - 0.03],
                    [sep_y, sep_y], color=BORDER, linewidth=0.5,
                    transform=fig.transFigure, zorder=2)
                fig.add_artist(line)

    # Bottom highlight
    fig.text(0.5, 0.025, "메모리 안에 로직이 들어온다 — DRAM만 잘 만드는 시대는 끝났다",
             color=YELLOW, fontsize=8.5, fontweight="bold", ha="center")

    path = os.path.join(OUT_DIR, "04_hbm4_spec.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 6: 3사 HBM4 전략 비교 (상세)
# ═══════════════════════════════════════════════════════════
def gen_three_strategies():
    """3사 HBM4 전략 — 기술 의사결정 비교 카드."""
    fig = fig_base(height_ratio=1.15)

    # Title
    fig.text(0.5, 0.96, "3사 3색 — HBM4 기술 의사결정", color=WHITE,
             fontsize=16, fontweight="bold", ha="center")
    fig.text(0.5, 0.925, "같은 규격, 완전히 다른 전략",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    companies = [
        {
            "name": "SK하이닉스", "color": GREEN, "tag": "최고와 손잡는다",
            "items": [
                ("HBM 본딩", "MR-MUF (수율 ~80%)"),
                ("로직 다이", "TSMC 3nm"),
                ("전압", "0.8V (최저)"),
                ("패키징", "TSMC CoWoS"),
                ("EUV", "6레이어 (업계 최다)"),
                ("리스크", "TSMC 의존"),
            ],
        },
        {
            "name": "삼성", "color": RED, "tag": "전부 직접 한다",
            "items": [
                ("HBM 본딩", "TC-NCF → 하이브리드"),
                ("로직 다이", "자체 파운드리 4nm"),
                ("전압", "—"),
                ("패키징", "자체 I-Cube/SoP"),
                ("EUV", "5대 High-NA 구매"),
                ("리스크", "모든 부문 2등"),
            ],
        },
        {
            "name": "Micron", "color": YELLOW, "tag": "안전하게 간다",
            "items": [
                ("HBM 본딩", "MR-MUF 채택"),
                ("로직 다이", "DRAM 공정 유지"),
                ("전압", "—"),
                ("패키징", "TSMC + OSAT"),
                ("EUV", "평가 중"),
                ("리스크", "HBM4 성능 열세"),
            ],
        },
    ]

    col_w = 0.29
    gap = 0.03
    total_w = 3 * col_w + 2 * gap
    start_x = (1.0 - total_w) / 2

    for ci, co in enumerate(companies):
        cx = start_x + ci * (col_w + gap)
        mid_x = cx + col_w / 2
        card_top = 0.89
        card_h = 0.80

        # Card
        card = mpatches.FancyBboxPatch(
            (cx, card_top - card_h), col_w, card_h,
            boxstyle="round,pad=0.012", facecolor=CARD_BG,
            edgecolor=co["color"], linewidth=1.5,
            transform=fig.transFigure, zorder=1,
        )
        fig.patches.append(card)

        # Header
        fig.text(mid_x, card_top - 0.04, co["name"], color=co["color"],
                 fontsize=14, fontweight="bold", ha="center", zorder=2)
        fig.text(mid_x, card_top - 0.075, co["tag"], color=WHITE,
                 fontsize=8.5, ha="center", zorder=2)

        # Separator under header
        sep = mlines.Line2D(
            [cx + 0.02, cx + col_w - 0.02],
            [card_top - 0.095, card_top - 0.095],
            color=BORDER, linewidth=0.8,
            transform=fig.transFigure, zorder=2)
        fig.add_artist(sep)

        # Items
        item_start_y = card_top - 0.125
        item_gap = 0.105

        for ii, (label, value) in enumerate(co["items"]):
            y = item_start_y - ii * item_gap

            fig.text(mid_x, y + 0.02, label, color=LIGHT_GRAY,
                     fontsize=7, ha="center", zorder=2)

            # Color risk items differently
            val_color = ORANGE if label == "리스크" else WHITE
            fig.text(mid_x, y - 0.01, value, color=val_color,
                     fontsize=8.5, fontweight="bold", ha="center", zorder=2)

            # Separator between items
            if ii < len(co["items"]) - 1:
                sep_y = y - 0.035
                item_sep = mlines.Line2D(
                    [cx + 0.03, cx + col_w - 0.03],
                    [sep_y, sep_y], color=BORDER, linewidth=0.3,
                    transform=fig.transFigure, zorder=2)
                fig.add_artist(item_sep)

    # Bottom
    fig.text(0.5, 0.02, "출처: TrendForce, Bloomberg, KED Global, Tom's Hardware | 2025 Q3 기준",
             color=GRAY, fontsize=6.5, ha="center")

    path = os.path.join(OUT_DIR, "05_three_strategies.png")
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print(f"  ✓ {path}")
    return path


# ═══════════════════════════════════════════════════════════
# Visual 7: HBM 너머 — 3계층 타임라인
# ═══════════════════════════════════════════════════════════
def gen_beyond_hbm():
    """HBM 너머 — CXL / PIM / 광학 3계층 타임라인."""
    fig = fig_base()

    # Title
    fig.text(0.5, 0.93, "HBM 너머 — 세 가지 돌파구", color=WHITE,
             fontsize=16, fontweight="bold", ha="center")
    fig.text(0.5, 0.885, "경쟁이 아니라 계층이다 — 각각 다른 병목을 해결한다",
             color=LIGHT_GRAY, fontsize=9, ha="center")

    techs = [
        {
            "name": "CXL", "color": GREEN,
            "problem": "용량 부족",
            "relation": "HBM 보완",
            "timeline": "2025~2027",
            "status": "양산 중",
            "key_stat": "SSD 대비 21.9× 처리량",
        },
        {
            "name": "PIM", "color": BLUE,
            "problem": "데이터 이동 병목",
            "relation": "HBM 내장",
            "timeline": "2026~2028",
            "status": "상용 초기",
            "key_stat": "에너지 50% 절감",
        },
        {
            "name": "광학 인터커넥트", "color": ORANGE,
            "problem": "구리 배선 한계",
            "relation": "HBM 재정의",
            "timeline": "2028~2030+",
            "status": "R&D → 초기 배치",
            "key_stat": "CPO 대비 25× 대역폭",
        },
    ]

    card_h = 0.22
    card_w = 0.88
    start_x = (1.0 - card_w) / 2
    start_y = 0.80

    for i, tech in enumerate(techs):
        y = start_y - i * (card_h + 0.03)

        # Card
        card = mpatches.FancyBboxPatch(
            (start_x, y - card_h), card_w, card_h,
            boxstyle="round,pad=0.012", facecolor=CARD_BG,
            edgecolor=tech["color"], linewidth=1.5,
            transform=fig.transFigure, zorder=1,
        )
        fig.patches.append(card)

        # Left: name + status badge
        name_x = start_x + 0.04
        fig.text(name_x, y - 0.04, tech["name"], color=tech["color"],
                 fontsize=14, fontweight="bold", va="center", zorder=2)
        fig.text(name_x, y - 0.08, tech["status"], color=LIGHT_GRAY,
                 fontsize=8, va="center", zorder=2)

        # Center: problem → relation
        center_x = 0.42
        fig.text(center_x, y - 0.04, f'풀려는 문제: {tech["problem"]}',
                 color=WHITE, fontsize=9, fontweight="bold",
                 va="center", zorder=2)
        fig.text(center_x, y - 0.08, f'HBM과의 관계: {tech["relation"]}',
                 color=LIGHT_GRAY, fontsize=8, va="center", zorder=2)

        # Right: timeline + key stat
        right_x = 0.78
        fig.text(right_x, y - 0.04, tech["timeline"], color=tech["color"],
                 fontsize=11, fontweight="bold", ha="center",
                 va="center", zorder=2)
        fig.text(right_x, y - 0.08, tech["key_stat"], color=LIGHT_GRAY,
                 fontsize=7.5, ha="center", va="center", zorder=2)

        # Vertical connector between cards
        if i < len(techs) - 1:
            conn_y = y - card_h - 0.015
            fig.text(0.5, conn_y, "▼", color=GRAY, fontsize=10,
                     ha="center", va="center", alpha=0.5)


    # Timeline arrow at bottom
    ax_timeline = fig.add_axes([0.1, 0.03, 0.8, 0.04])
    ax_timeline.set_facecolor(BG)
    ax_timeline.set_xlim(2024, 2032)
    ax_timeline.set_ylim(0, 1)
    ax_timeline.axhline(y=0.5, color=BORDER, linewidth=1)

    markers = [
        (2025, "CXL\n양산", GREEN),
        (2026, "PIM\n상용", BLUE),
        (2028, "광학\n배치", ORANGE),
        (2030, "광학\n주류", ORANGE),
    ]
    for mx, mlabel, mcolor in markers:
        ax_timeline.plot(mx, 0.5, "o", color=mcolor, markersize=6, zorder=3)
        ax_timeline.text(mx, 0.95, mlabel, color=mcolor, fontsize=6.5,
                         ha="center", va="top", fontweight="bold")

    ax_timeline.set_xticks(range(2024, 2033))
    ax_timeline.tick_params(colors=LIGHT_GRAY, labelsize=6, length=0)
    ax_timeline.spines["top"].set_visible(False)
    ax_timeline.spines["right"].set_visible(False)
    ax_timeline.spines["left"].set_visible(False)
    ax_timeline.spines["bottom"].set_color(BORDER)
    ax_timeline.set_yticks([])

    path = os.path.join(OUT_DIR, "06_beyond_hbm.png")
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
    print("KR-02 시각화 생성 시작\n")
    gen_hero_image()
    gen_yield_curve()
    gen_bonding_comparison()
    gen_market_share()
    gen_hbm4_spec()
    gen_three_strategies()
    gen_beyond_hbm()
    qa_check()
    print("\n완료")
