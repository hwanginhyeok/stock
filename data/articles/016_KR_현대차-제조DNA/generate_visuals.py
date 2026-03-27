"""KR-03 현대차① — 바꾸지 않아도 되는 것: 시각화 생성."""

import os
from pathlib import Path

import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

matplotlib.use("Agg")

HERE = Path(__file__).parent
OUT  = HERE / "visuals"
OUT.mkdir(exist_ok=True)

# 한글 폰트
_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_FONT_PATH):
    fm.fontManager.addfont(_FONT_PATH)
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False

# 색상 팔레트
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
CYAN   = "#39d2c0"

FIG_SIZE = (8, 8)
DPI      = 135


def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(
        path, dpi=DPI, bbox_inches="tight",
        facecolor=fig.get_facecolor(), pad_inches=0.1,
    )
    plt.close(fig)
    return path


# ── 이미지 1: 공장 건설 속도 비교 ──────────────────────────────

def make_factory_speed() -> Path:
    """현대차 vs Ford 공장 건설 속도 비교 — 수평 바 차트."""
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.50, 0.93, "공장 건설 속도 비교", fontsize=22, fontweight="bold",
            color=WHITE, ha="center", va="center", transform=ax.transAxes)
    ax.text(0.50, 0.885, "착공에서 양산까지 (개월)",
            fontsize=13, color=DIM, ha="center", va="center", transform=ax.transAxes)

    # 데이터
    factories = [
        ("Ford BlueOval City",  72, RED,    "2021발표 → 2027~2028 전망 (6년+)"),
        ("",                     0, BG,     ""),   # spacer
        ("HMGMA (조지아)",       24, GREEN,  "2022.10 → 2024.10"),
        ("베이징현대 5공장",      24, GREEN,  "충칭, 2015 → 2017"),
        ("베이징현대 4공장",      18, GREEN,  "창저우, 2015.04 → 2016.10"),
        ("베이징현대 3공장",      20, GREEN,  "2010.11 → 2012"),
        ("베이징현대 2공장",      24, GREEN,  "2006.04 → 2008.04"),
        ("베이징현대 1공장",       7, CYAN,   "2002.05 → 2002.12"),
    ]

    n = len(factories)
    bar_area_top = 0.82
    bar_area_bot = 0.10
    bar_h = (bar_area_top - bar_area_bot) / n
    max_months = 80
    bar_left = 0.30
    bar_right = 0.92
    bar_width = bar_right - bar_left

    for i, (label, months, color, note) in enumerate(factories):
        y_center = bar_area_top - (i + 0.5) * bar_h

        if not label:
            # 구분선
            ax.plot([0.05, 0.95], [y_center, y_center],
                    color=GRAY, linewidth=0.5, alpha=0.4, transform=ax.transAxes)
            continue

        # 라벨
        ax.text(bar_left - 0.02, y_center, label, fontsize=11,
                color=WHITE, ha="right", va="center", transform=ax.transAxes)

        # 바
        w = (months / max_months) * bar_width
        rect = mpatches.FancyBboxPatch(
            (bar_left, y_center - bar_h * 0.3), w, bar_h * 0.6,
            boxstyle="round,pad=0.005", facecolor=color, alpha=0.85,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # 개월 수 표시
        label_x = bar_left + w + 0.015
        if months >= 72:
            month_text = "72+ 개월 (6년+)"
        else:
            month_text = f"{months}개월"
        ax.text(label_x, y_center, month_text, fontsize=11,
                color=color, fontweight="bold", ha="left", va="center",
                transform=ax.transAxes)

    # 하단 범례
    ax.text(0.50, 0.04,
            "출처: Hyundai Newsroom, Ford Newsroom, China Daily, IEEE Spectrum",
            fontsize=9, color=GRAY, ha="center", va="center", transform=ax.transAxes)

    # 구간 라벨 — Ford 위, 현대차 위 (구분선 기준)
    # spacer는 index=1 → y = bar_area_top - 1.5*bar_h
    spacer_y = bar_area_top - 1.5 * bar_h
    ax.text(0.05, spacer_y - 0.015, "현대차그룹",
            fontsize=10, color=GREEN, fontweight="bold",
            ha="left", va="top", transform=ax.transAxes)

    return _save(fig, "01_factory_speed.png")


# ── 이미지 2: 제조 DNA 카드 ────────────────────────────────────

def make_dna_card() -> Path:
    """현대차 제조 DNA — 핵심 수치 3열 카드."""
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.50, 0.93, "현대차 제조 DNA", fontsize=24, fontweight="bold",
            color=WHITE, ha="center", va="center", transform=ax.transAxes)
    ax.text(0.50, 0.885, "빠르게, 정확하게, 대규모로",
            fontsize=14, color=DIM, ha="center", va="center", transform=ax.transAxes)

    # 3열 카드
    cards = [
        {
            "x": 0.18, "num": "1억 대", "label": "글로벌 누적 생산",
            "color": GREEN,
            "details": [
                "창립 57년 만 (2024.09)",
                "처음 5천만: 46년",
                "다음 5천만: 11년",
            ],
        },
        {
            "x": 0.50, "num": "850+", "label": "HMGMA 로봇 (대)",
            "color": BLUE,
            "details": [
                "AGV 300대",
                "차체 자동화율 91%",
                "북미 최고 자동화 공장",
            ],
        },
        {
            "x": 0.82, "num": "1위", "label": "J.D. Power IQS",
            "color": CYAN,
            "details": [
                "2년 연속 (2024-2025)",
                "울산5/광주1: 아태 공동 2위",
                "기아 멕시코: 미주 3위",
            ],
        },
    ]

    card_w = 0.28
    card_h = 0.42
    card_top = 0.78

    for card in cards:
        cx = card["x"]
        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (cx - card_w / 2, card_top - card_h), card_w, card_h,
            boxstyle="round,pad=0.015", facecolor=BG2,
            edgecolor=card["color"], linewidth=1.5, alpha=0.9,
            transform=ax.transAxes,
        )
        ax.add_patch(rect)

        # 큰 숫자
        ax.text(cx, card_top - 0.07, card["num"],
                fontsize=30, fontweight="bold", color=card["color"],
                ha="center", va="center", transform=ax.transAxes)

        # 라벨
        ax.text(cx, card_top - 0.15, card["label"],
                fontsize=11, color=WHITE, ha="center", va="center",
                transform=ax.transAxes)

        # 구분선
        ax.plot([cx - card_w * 0.35, cx + card_w * 0.35],
                [card_top - 0.19, card_top - 0.19],
                color=GRAY, linewidth=0.5, alpha=0.5, transform=ax.transAxes)

        # 디테일
        for j, detail in enumerate(card["details"]):
            ax.text(cx, card_top - 0.24 - j * 0.06, detail,
                    fontsize=10, color=DIM, ha="center", va="center",
                    transform=ax.transAxes)

    # 하단 — 건설 속도 요약 박스
    summary_top = 0.26
    summary_h = 0.16
    summary_rect = mpatches.FancyBboxPatch(
        (0.06, summary_top - summary_h), 0.88, summary_h,
        boxstyle="round,pad=0.015", facecolor=BG2,
        edgecolor=GRAY, linewidth=0.8, alpha=0.7,
        transform=ax.transAxes,
    )
    ax.add_patch(summary_rect)

    ax.text(0.50, summary_top - 0.03, "건설 속도 — 어디서든 18~24개월",
            fontsize=13, fontweight="bold", color=WHITE,
            ha="center", va="center", transform=ax.transAxes)

    speed_items = [
        ("베이징 1공장", "7개월", CYAN),
        ("중국 2~5공장", "18~24개월", GREEN),
        ("HMGMA (미국)", "24개월", GREEN),
    ]
    for k, (place, speed, clr) in enumerate(speed_items):
        sx = 0.18 + k * 0.27
        ax.text(sx, summary_top - 0.08, place, fontsize=10,
                color=DIM, ha="center", va="center", transform=ax.transAxes)
        ax.text(sx, summary_top - 0.13, speed, fontsize=12, fontweight="bold",
                color=clr, ha="center", va="center", transform=ax.transAxes)

    # 출처
    ax.text(0.50, 0.04,
            "출처: Hyundai Newsroom, J.D. Power, IEEE Spectrum, Boston Dynamics",
            fontsize=9, color=GRAY, ha="center", va="center", transform=ax.transAxes)

    return _save(fig, "02_manufacturing_dna.png")


# ── QA ──────────────────────────────────────────────────────────

def qa_check() -> None:
    from PIL import Image
    print("\n=== QA Check ===")
    for name in ["01_factory_speed.png", "02_manufacturing_dna.png"]:
        fp = OUT / name
        if not fp.exists():
            print(f"  x {name} - 파일 없음")
            continue
        size_kb = fp.stat().st_size / 1024
        issues = []
        if size_kb < 10:
            issues.append(f"파일 크기 너무 작음 ({size_kb:.1f} KB)")
        with Image.open(fp) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"해상도 부족 ({w}x{h}px, 최소 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"비율 이탈 ({ratio:.2f})")
        if issues:
            print(f"  !! {name}")
            for i in issues:
                print(f"       -> {i}")
        else:
            print(f"  OK {name} ({size_kb:.0f} KB, {w}x{h}px)")


if __name__ == "__main__":
    print("Generating visuals...")
    p1 = make_factory_speed()
    print(f"  -> {p1}")
    p2 = make_dna_card()
    print(f"  -> {p2}")
    qa_check()
    print("Done.")
