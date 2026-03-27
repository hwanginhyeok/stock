"""
generate_visuals_kr01.py — KR-01 HBM 병목 아티클 시각화 생성

생성 이미지:
  01_gpu_bom.png           — B200 GPU 원가 구조 (14% 패러독스)
  02_opm_swing.png         — SK하이닉스 영업이익률 스윙 (-67% → +58%)
  03_supply_demand.png     — DRAM 수요 +35% vs 공급 +16%
  04_dram_everywhere.png   — 모든 디바이스가 메모리를 원한다

Usage:
    source .venv-wsl/bin/activate && python data/research/korea/articles/generate_visuals_kr01.py
"""

import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.font_manager as fm

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
BG      = "#0d1117"
BG2     = "#161b22"
GREEN   = "#3fb950"
YELLOW  = "#d29922"
RED     = "#f85149"
BLUE    = "#58a6ff"
ORANGE  = "#db6d28"
PURPLE  = "#bc8cff"
GRAY    = "#6e7681"
WHITE   = "#e6edf3"
DIM     = "#8b949e"
BORDER  = "#30363d"

FIG_SIZE = (8, 8)
DPI      = 135


def _save(fig: plt.Figure, name: str) -> dict:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    size = path.stat().st_size
    return {"name": name, "path": str(path), "size": size, "ok": size > 10_000}


# ══════════════════════════════════════════════════════════════════════════════
# 01. GPU BOM — B200 원가 구조 (14% 패러독스)
# ══════════════════════════════════════════════════════════════════════════════
def make_gpu_bom() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.95, "NVIDIA B200 GPU 제조원가 구조",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.90, "총 원가 ~$6,400  /  판매가 $30,000~$40,000  /  마진 82%",
            ha="center", va="top", color=DIM,
            fontsize=10, transform=ax.transAxes)

    # 데이터
    components = [
        ("HBM3e 메모리 (192GB)",  45, "$2,900",  BLUE,   True),
        ("어드밴스드 패키징",       17, "$1,100",  PURPLE, False),
        ("패키징 수율 손실",        16, "$1,000",  YELLOW, False),
        ("로직 다이 (NVIDIA 설계)", 14, "$900",    GREEN,  True),
        ("보조 부품",                8, "$500",    GRAY,   False),
    ]

    # 수평 누적 바
    bar_y = 0.72
    bar_h = 0.06
    bar_left = 0.08
    bar_width = 0.84

    x_cursor = bar_left
    bar_rects = []
    for name, pct, cost, color, highlight in components:
        w = bar_width * pct / 100
        rect = mpatches.FancyBboxPatch(
            (x_cursor, bar_y), w, bar_h,
            boxstyle="square,pad=0",
            facecolor=color, alpha=0.85 if highlight else 0.55,
            edgecolor=BG, linewidth=1,
            transform=ax.transAxes
        )
        ax.add_patch(rect)
        bar_rects.append((x_cursor, w, name, pct, cost, color, highlight))
        x_cursor += w

    # 바 위 퍼센트 라벨
    for bx, bw, name, pct, cost, color, highlight in bar_rects:
        cx = bx + bw / 2
        if bw > 0.06:
            ax.text(cx, bar_y + bar_h / 2, f"{pct}%",
                    ha="center", va="center", color=WHITE,
                    fontsize=10, fontweight="bold", transform=ax.transAxes)

    # 상세 카드 — 각 구성요소
    card_top = 0.62
    card_h = 0.085
    card_gap = 0.015

    for i, (name, pct, cost, color, highlight) in enumerate(components):
        y = card_top - i * (card_h + card_gap)

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (0.06, y - card_h), 0.88, card_h,
            boxstyle="round,pad=0.008",
            facecolor=BG2 if not highlight else color,
            alpha=1.0 if not highlight else 0.12,
            edgecolor=color if highlight else BORDER,
            linewidth=1.5 if highlight else 0.7,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 퍼센트 바지표 (작은 원형)
        ax.add_patch(mpatches.Circle(
            (0.12, y - card_h / 2), 0.022,
            facecolor=color, alpha=0.8,
            transform=ax.transAxes
        ))
        ax.text(0.12, y - card_h / 2, f"{pct}%",
                ha="center", va="center", color=WHITE,
                fontsize=7.5, fontweight="bold", transform=ax.transAxes)

        # 이름
        ax.text(0.17, y - card_h / 2, name,
                ha="left", va="center",
                color=color if highlight else WHITE,
                fontsize=11, fontweight="bold" if highlight else "normal",
                transform=ax.transAxes)

        # 비용
        ax.text(0.90, y - card_h / 2, cost,
                ha="right", va="center", color=DIM,
                fontsize=10, transform=ax.transAxes)

    # 핵심 메시지 박스
    msg_y = 0.14
    msg_h = 0.12
    rect = mpatches.FancyBboxPatch(
        (0.06, msg_y - msg_h), 0.88, msg_h,
        boxstyle="round,pad=0.015",
        facecolor=GREEN, alpha=0.08,
        edgecolor=GREEN, linewidth=1.5,
        transform=ax.transAxes
    )
    ax.add_patch(rect)

    ax.text(0.5, msg_y - 0.02,
            "14% 패러독스",
            ha="center", va="top", color=GREEN,
            fontsize=14, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, msg_y - 0.06,
            "NVIDIA의 경쟁 우위는 설계와 CUDA 생태계에 있다.",
            ha="center", va="top", color=WHITE,
            fontsize=10, transform=ax.transAxes)
    ax.text(0.5, msg_y - 0.09,
            "그런데 원가의 86%는 TSMC의 패키징과 SK하이닉스의 메모리가 가져간다.",
            ha="center", va="top", color=DIM,
            fontsize=9, transform=ax.transAxes)

    return _save(fig, "01_gpu_bom.png")


# ══════════════════════════════════════════════════════════════════════════════
# 02. SK하이닉스 영업이익률 스윙
# ══════════════════════════════════════════════════════════════════════════════
def make_opm_swing() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.97, "SK하이닉스 영업이익률 추이",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.93, "2년 반 만에 125%p 스윙 — 메모리 사상 최대",
            ha="center", va="top", color=DIM,
            fontsize=10, transform=ax.transAxes)

    # 데이터
    quarters = [
        ("2023\nQ1", -67, "적자 바닥"),
        ("2023\nQ2", -48, ""),
        ("2023\nQ3", -19, ""),
        ("2023\nQ4",  +3, "흑자 전환"),
        ("2024\nQ1", +14, ""),
        ("2024\nQ2", +35, ""),
        ("2024\nQ3", +38, ""),
        ("2024\nQ4", +41, ""),
        ("2025\nQ1", +44, ""),
        ("2025\nQ2", +49, ""),
        ("2025\nQ3", +54, ""),
        ("2025\nQ4", +58, "사상 최고"),
    ]

    n = len(quarters)
    chart_left = 0.10
    chart_right = 0.92
    chart_bottom = 0.20
    chart_top = 0.82
    chart_w = chart_right - chart_left
    chart_h = chart_top - chart_bottom

    # 0% 기준선
    val_min, val_max = -75, 65
    val_range = val_max - val_min
    zero_y = chart_bottom + (0 - val_min) / val_range * chart_h

    # 0% 라인
    ax.plot([chart_left, chart_right], [zero_y, zero_y],
            color=BORDER, linewidth=1, linestyle="--",
            alpha=0.6, transform=ax.transAxes)
    ax.text(chart_left - 0.02, zero_y, "0%",
            ha="right", va="center", color=DIM,
            fontsize=8, transform=ax.transAxes)

    # 바 차트
    bar_total_w = chart_w / n
    bar_w = bar_total_w * 0.65
    bar_gap = bar_total_w * 0.35

    for i, (label, opm, note) in enumerate(quarters):
        cx = chart_left + (i + 0.5) * bar_total_w
        bx = cx - bar_w / 2
        val_y = chart_bottom + (opm - val_min) / val_range * chart_h

        color = RED if opm < 0 else GREEN
        alpha = 0.9 if note else 0.65

        if opm < 0:
            rect = mpatches.FancyBboxPatch(
                (bx, val_y), bar_w, zero_y - val_y,
                boxstyle="square,pad=0",
                facecolor=color, alpha=alpha,
                transform=ax.transAxes
            )
        else:
            rect = mpatches.FancyBboxPatch(
                (bx, zero_y), bar_w, val_y - zero_y,
                boxstyle="square,pad=0",
                facecolor=color, alpha=alpha,
                transform=ax.transAxes
            )
        ax.add_patch(rect)

        # 값 라벨
        label_y = val_y - 0.02 if opm < 0 else val_y + 0.01
        va = "top" if opm < 0 else "bottom"
        ax.text(cx, label_y, f"{opm:+d}%",
                ha="center", va=va, color=WHITE,
                fontsize=7.5, fontweight="bold" if note else "normal",
                transform=ax.transAxes)

        # 분기 라벨
        ax.text(cx, chart_bottom - 0.02, label,
                ha="center", va="top", color=DIM,
                fontsize=6.5, linespacing=1.1,
                transform=ax.transAxes)

        # 주석
        if note:
            note_y = val_y + 0.04 if opm >= 0 else val_y - 0.04
            va_n = "bottom" if opm >= 0 else "top"
            ax.text(cx, note_y, note,
                    ha="center", va=va_n, color=YELLOW,
                    fontsize=7.5, fontweight="bold",
                    transform=ax.transAxes)

    # 화살표: -67% → +58%
    arrow_y = 0.88
    ax.annotate(
        "", xy=(chart_right - 0.03, arrow_y),
        xytext=(chart_left + 0.03, arrow_y),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=2.0,
                        mutation_scale=18)
    )

    # 하단 핵심 수치 카드
    cards = [
        ("-7.73조", "2023 영업이익", RED),
        ("+47.21조", "2025 영업이익", GREEN),
        ("55조원", "스윙 폭", YELLOW),
    ]
    card_w = 0.25
    card_h_b = 0.07
    card_y = 0.04

    for j, (val, label, color) in enumerate(cards):
        cx = 0.18 + j * 0.32
        rect = mpatches.FancyBboxPatch(
            (cx - card_w / 2, card_y), card_w, card_h_b,
            boxstyle="round,pad=0.008",
            facecolor=color, alpha=0.1,
            edgecolor=color, linewidth=1,
            transform=ax.transAxes
        )
        ax.add_patch(rect)
        ax.text(cx, card_y + card_h_b * 0.65, val,
                ha="center", va="center", color=color,
                fontsize=12, fontweight="bold", transform=ax.transAxes)
        ax.text(cx, card_y + card_h_b * 0.25, label,
                ha="center", va="center", color=DIM,
                fontsize=8, transform=ax.transAxes)

    return _save(fig, "02_opm_swing.png")


# ══════════════════════════════════════════════════════════════════════════════
# 03. DRAM 수요 vs 공급 갭
# ══════════════════════════════════════════════════════════════════════════════
def make_supply_demand() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.95, "2026 DRAM: 수요 vs 공급",
            ha="center", va="top", color=WHITE,
            fontsize=16, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.90, "구조적 갭 — 12~19%p",
            ha="center", va="top", color=DIM,
            fontsize=10, transform=ax.transAxes)

    # 메인 비교 — 두 개의 큰 막대
    bar_left = 0.15
    bar_right = 0.85
    max_val = 40

    bars = [
        ("수요 성장", 35, GREEN, 0.72),
        ("공급 성장", 16, RED, 0.55),
        ("웨이퍼 캐파 증가", 8.7, GRAY, 0.38),
    ]

    for label, val, color, y in bars:
        w = (bar_right - bar_left) * val / max_val
        rect = mpatches.FancyBboxPatch(
            (bar_left, y - 0.03), w, 0.06,
            boxstyle="round,pad=0.005",
            facecolor=color, alpha=0.7,
            edgecolor=color, linewidth=1,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 라벨
        ax.text(bar_left - 0.02, y, label,
                ha="right", va="center", color=WHITE,
                fontsize=10, transform=ax.transAxes)

        # 값
        ax.text(bar_left + w + 0.02, y, f"+{val}%",
                ha="left", va="center", color=color,
                fontsize=14, fontweight="bold", transform=ax.transAxes)

    # 갭 표시 — 수요와 공급 사이 화살표
    gap_x = bar_left + (bar_right - bar_left) * 16 / max_val + 0.06
    ax.annotate(
        "", xy=(gap_x, 0.72),
        xytext=(gap_x, 0.55),
        xycoords="axes fraction",
        arrowprops=dict(arrowstyle="<->", color=YELLOW, lw=2.5,
                        mutation_scale=18)
    )
    ax.text(gap_x + 0.03, 0.635, "GAP\n12~19%p",
            ha="left", va="center", color=YELLOW,
            fontsize=11, fontweight="bold", linespacing=1.3,
            transform=ax.transAxes)

    # 구분선
    ax.plot([0.08, 0.92], [0.30, 0.30],
            color=BORDER, linewidth=1, transform=ax.transAxes)

    # 하단 — 새 팹 타임라인
    ax.text(0.5, 0.26, "새 팹은 전부 2027년 이후",
            ha="center", va="top", color=YELLOW,
            fontsize=13, fontweight="bold", transform=ax.transAxes)

    fabs = [
        ("SK하이닉스 용인 1공장", "2027년 5월", BLUE),
        ("Micron 보이시 ID1", "2027년 중반", PURPLE),
        ("삼성 평택 P5", "2028년", ORANGE),
    ]

    for i, (name, date, color) in enumerate(fabs):
        y = 0.19 - i * 0.055
        ax.text(0.15, y, "---", ha="center", va="center",
                color=color, fontsize=10, transform=ax.transAxes)
        ax.text(0.20, y, name, ha="left", va="center",
                color=WHITE, fontsize=9.5, transform=ax.transAxes)
        ax.text(0.85, y, date, ha="right", va="center",
                color=color, fontsize=9.5, fontweight="bold",
                transform=ax.transAxes)

    # IDC 인용
    ax.text(0.5, 0.04,
            '"잠재적으로 영구적인 전략적 재배분" — IDC',
            ha="center", va="bottom", color=DIM,
            fontsize=8.5, style="italic", transform=ax.transAxes)

    return _save(fig, "03_supply_demand.png")


# ══════════════════════════════════════════════════════════════════════════════
# 04. 모든 디바이스가 메모리를 원한다
# ══════════════════════════════════════════════════════════════════════════════
def make_dram_everywhere() -> dict:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "모든 디바이스가 메모리를 원한다",
            ha="center", va="top", color=WHITE,
            fontsize=15, fontweight="bold", transform=ax.transAxes)
    ax.text(0.5, 0.91, "데이터센터만이 아니다 — 같은 웨이퍼에서 나온다",
            ha="center", va="top", color=DIM,
            fontsize=9.5, transform=ax.transAxes)

    # 2x2 카드 레이아웃
    cards = [
        {
            "title": "AI PC",
            "icon": "[PC]",
            "color": BLUE,
            "stats": [
                ("기존 표준", "8GB", DIM),
                ("AI PC 요구", "16~32GB", BLUE),
                ("2026년 출하", "1.43억대 (55%)", WHITE),
                ("BOM 비중", "18% (2배)", YELLOW),
            ],
        },
        {
            "title": "스마트폰",
            "icon": "[PHONE]",
            "color": GREEN,
            "stats": [
                ("Galaxy S25", "12GB 표준화", WHITE),
                ("AI 추가 수요", "+48%", GREEN),
                ("Apple 가격 수용", "+100%", YELLOW),
                ("저가폰 역행", "8GB -> 4GB", RED),
            ],
        },
        {
            "title": "로봇 / 자율주행",
            "icon": "[ROBOT]",
            "color": ORANGE,
            "stats": [
                ("Jetson Thor", "128GB", WHITE),
                ("Tesla AI5", "144GB (9배)", ORANGE),
                ("차량 반도체", "200개 -> 1000+", WHITE),
                ("자동차 DRAM CAGR", "+21%", GREEN),
            ],
        },
        {
            "title": "게이밍",
            "icon": "[GAME]",
            "color": PURPLE,
            "stats": [
                ("RTX 50 감산", "-40%", RED),
                ("GDDR7 웨이퍼", "1.7배 소비", YELLOW),
                ("PS6 / Xbox", "30~48GB GDDR7", WHITE),
                ("차세대 콘솔", "2028~29 연기?", RED),
            ],
        },
    ]

    # 카드 위치: 2x2 grid
    positions = [
        (0.06, 0.50),   # top-left
        (0.52, 0.50),   # top-right
        (0.06, 0.07),   # bottom-left
        (0.52, 0.07),   # bottom-right
    ]
    card_w = 0.42
    card_h = 0.36

    for card, (cx, cy) in zip(cards, positions):
        color = card["color"]

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (cx, cy), card_w, card_h,
            boxstyle="round,pad=0.012",
            facecolor=BG2,
            edgecolor=color, linewidth=1.5, alpha=0.9,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 헤더 배경
        hdr_h = 0.065
        hdr_rect = mpatches.FancyBboxPatch(
            (cx, cy + card_h - hdr_h), card_w, hdr_h,
            boxstyle="square,pad=0",
            facecolor=color, alpha=0.15,
            transform=ax.transAxes
        )
        ax.add_patch(hdr_rect)

        # 카드 제목
        ax.text(cx + card_w / 2, cy + card_h - hdr_h / 2,
                card["title"],
                ha="center", va="center", color=color,
                fontsize=13, fontweight="bold", transform=ax.transAxes)

        # 통계 행
        n_stats = len(card["stats"])
        stat_area_top = cy + card_h - hdr_h - 0.02
        stat_h = (stat_area_top - cy - 0.01) / n_stats

        for i, (label, value, val_color) in enumerate(card["stats"]):
            sy = stat_area_top - (i + 0.5) * stat_h

            # 라벨
            ax.text(cx + 0.03, sy, label,
                    ha="left", va="center", color=DIM,
                    fontsize=8, transform=ax.transAxes)
            # 값
            ax.text(cx + card_w - 0.03, sy, value,
                    ha="right", va="center", color=val_color,
                    fontsize=9, fontweight="bold", transform=ax.transAxes)

    return _save(fig, "04_dram_everywhere.png")


# ══════════════════════════════════════════════════════════════════════════════
# QA
# ══════════════════════════════════════════════════════════════════════════════
def qa_check(results: list[dict]) -> None:
    from PIL import Image

    print("\n── QA 결과 " + "─" * 45)
    all_ok = True
    for r in results:
        issues = []
        path = Path(r["path"])
        if not path.exists():
            print(f"  x  {r['name']} -- 파일 없음")
            all_ok = False
            continue

        size_kb = path.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"파일 크기 너무 작음 ({size_kb:.1f} KB)")

        with Image.open(path) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"해상도 부족 ({w}x{h}px, 최소 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"비율 이탈 ({ratio:.2f})")

        if issues:
            print(f"  !!  {r['name']}")
            for issue in issues:
                print(f"       -> {issue}")
            all_ok = False
        else:
            print(f"  ok  {r['name']} ({size_kb:.0f} KB, {w}x{h}px)")

    print("─" * 57)
    if all_ok:
        print("  모든 이미지 정상 생성")
    else:
        print("  일부 이미지 QA 미통과")
        sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("KR-01 HBM 병목 아티클 시각화 생성 시작...\n")
    results = []

    results.append(make_gpu_bom())
    print("  + 01 GPU BOM (14% 패러독스)")

    results.append(make_opm_swing())
    print("  + 02 SK하이닉스 OPM 스윙")

    results.append(make_supply_demand())
    print("  + 03 수요 vs 공급 갭")

    results.append(make_dram_everywhere())
    print("  + 04 디바이스별 DRAM 수요")

    qa_check(results)
    print(f"\n저장 위치: {OUT}\n")
