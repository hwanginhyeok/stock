"""
generate_visuals.py — 팔란티어 2편: 고객사/경쟁사 시각화

생성 이미지:
  01_customer_cases.png       — 주요 고객 사례 인포그래픽 (분야별 핵심 성과)
  02_competition_matrix.png   — 경쟁 포지셔닝 매트릭스 (읽기/쓰기 x 분석/운영)

Usage:
    python data/articles/007_PLTR_팔란티어-2편/generate_visuals.py
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
# 01. 주요 고객 사례 인포그래픽
# ══════════════════════════════════════════════════════════════════════════════
def make_customer_cases() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "Ontology가 증명하는 현장",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "규모와 산업이 다른 고객이 같은 결론에 도달한다",
            ha="center", va="center", color=DIM, fontsize=9.5,
            transform=ax.transAxes)

    # 4개 고객 카드 (2x2 그리드)
    customers = [
        {
            "sector": "FINANCE",
            "name": "Fannie Mae",
            "metric": "10초",
            "desc": "모기지 사기 탐지\n(인간: ~2개월)",
            "color": BLUE,
        },
        {
            "sector": "DEFENSE",
            "name": "US Army",
            "metric": "$10B",
            "desc": "역대 최대 소프트웨어\n단일 계약 (75개 통합)",
            "color": GREEN,
        },
        {
            "sector": "HEALTHCARE",
            "name": "NHS (UK)",
            "metric": "5x ROI",
            "desc": "170+ 조직 가입\n퇴원 시간 37% 단축",
            "color": YELLOW,
        },
        {
            "sector": "CONSTRUCTION",
            "name": "Cavanagh",
            "metric": "어닝콜 증언",
            "desc": "\"Ontology가 비밀 병기\"\n1년 내 서드파티 능가",
            "color": ORANGE,
        },
    ]

    CARD_W = 0.43
    CARD_H = 0.28
    GAP_X = 0.04
    GAP_Y = 0.04
    START_X = 0.05
    START_Y = 0.86

    for idx, cust in enumerate(customers):
        row = idx // 2
        col = idx % 2
        x = START_X + col * (CARD_W + GAP_X)
        y_top = START_Y - row * (CARD_H + GAP_Y)
        color = cust["color"]

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (x, y_top - CARD_H), CARD_W, CARD_H,
            boxstyle="round,pad=0.012",
            facecolor=BG2,
            edgecolor=color, linewidth=1.5,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 섹터 태그
        tag_w = 0.12
        tag_h = 0.028
        tag = mpatches.FancyBboxPatch(
            (x + 0.015, y_top - 0.04), tag_w, tag_h,
            boxstyle="round,pad=0.004",
            facecolor=color, alpha=0.18,
            edgecolor=color, linewidth=0.8,
            transform=ax.transAxes
        )
        ax.add_patch(tag)
        ax.text(x + 0.015 + tag_w / 2, y_top - 0.04 + tag_h / 2,
                cust["sector"], ha="center", va="center",
                color=color, fontsize=7, fontweight="bold",
                transform=ax.transAxes)

        # 회사명
        ax.text(x + 0.015, y_top - 0.08,
                cust["name"], ha="left", va="center",
                color=WHITE, fontsize=11, fontweight="bold",
                transform=ax.transAxes)

        # 핵심 수치 (크게)
        ax.text(x + CARD_W / 2, y_top - 0.16,
                cust["metric"], ha="center", va="center",
                color=color, fontsize=22, fontweight="bold",
                transform=ax.transAxes)

        # 설명
        ax.text(x + CARD_W / 2, y_top - CARD_H + 0.04,
                cust["desc"], ha="center", va="center",
                color=DIM, fontsize=8,
                multialignment="center", linespacing=1.4,
                transform=ax.transAxes)

    # 하단 공통 패턴 인사이트
    BOT_Y = 0.04
    BOT_H = 0.10
    rect = mpatches.FancyBboxPatch(
        (0.05, BOT_Y), 0.90, BOT_H,
        boxstyle="round,pad=0.010",
        facecolor=GREEN, alpha=0.06,
        edgecolor=GREEN, linewidth=1.0,
        transform=ax.transAxes
    )
    ax.add_patch(rect)

    ax.text(0.5, BOT_Y + BOT_H / 2 + 0.015,
            "공통 패턴",
            ha="center", va="center",
            color=GREEN, fontsize=11, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, BOT_Y + BOT_H / 2 - 0.02,
            "이질적 데이터 연결  /  의사결정 속도 단축  /  인력 의존 감소",
            ha="center", va="center",
            color=DIM, fontsize=9,
            transform=ax.transAxes)

    return _save(fig, "01_customer_cases.png")


# ══════════════════════════════════════════════════════════════════════════════
# 02. 경쟁 포지셔닝 매트릭스 (읽기/쓰기 x 분석/운영)
# ══════════════════════════════════════════════════════════════════════════════
def make_competition_matrix() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "경쟁 포지셔닝 매트릭스",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "같은 시장에 있는가?",
            ha="center", va="center", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # 2x2 매트릭스
    # X축: 분석(Analysis) ←→ 운영(Operations)
    # Y축: 읽기(Read) ←→ 쓰기(Write/Execute)

    MATRIX_X = 0.15
    MATRIX_Y = 0.20
    MATRIX_W = 0.72
    MATRIX_H = 0.62

    # 매트릭스 배경
    rect = mpatches.FancyBboxPatch(
        (MATRIX_X, MATRIX_Y), MATRIX_W, MATRIX_H,
        boxstyle="round,pad=0.008",
        facecolor=BG2,
        edgecolor=BORDER, linewidth=1.0,
        transform=ax.transAxes
    )
    ax.add_patch(rect)

    # 중심선 (십자)
    mid_x = MATRIX_X + MATRIX_W / 2
    mid_y = MATRIX_Y + MATRIX_H / 2
    ax.plot([mid_x, mid_x], [MATRIX_Y + 0.02, MATRIX_Y + MATRIX_H - 0.02],
            color=BORDER, linewidth=1.0, alpha=0.5,
            transform=ax.transAxes)
    ax.plot([MATRIX_X + 0.02, MATRIX_X + MATRIX_W - 0.02], [mid_y, mid_y],
            color=BORDER, linewidth=1.0, alpha=0.5,
            transform=ax.transAxes)

    # 축 라벨
    ax.text(MATRIX_X + MATRIX_W / 4, MATRIX_Y + MATRIX_H + 0.02,
            "분석 (Analysis)", ha="center", va="center",
            color=DIM, fontsize=9, fontweight="bold",
            transform=ax.transAxes)
    ax.text(MATRIX_X + 3 * MATRIX_W / 4, MATRIX_Y + MATRIX_H + 0.02,
            "운영 (Operations)", ha="center", va="center",
            color=DIM, fontsize=9, fontweight="bold",
            transform=ax.transAxes)
    ax.text(MATRIX_X - 0.05, mid_y + MATRIX_H / 4,
            "쓰기\n(Write)", ha="center", va="center",
            color=DIM, fontsize=9, fontweight="bold",
            multialignment="center",
            transform=ax.transAxes)
    ax.text(MATRIX_X - 0.05, mid_y - MATRIX_H / 4,
            "읽기\n(Read)", ha="center", va="center",
            color=DIM, fontsize=9, fontweight="bold",
            multialignment="center",
            transform=ax.transAxes)

    # 포지셔닝 아이템
    items = [
        # (x_frac, y_frac, name, desc, color, size)
        # 좌하: 읽기+분석
        (0.25, 0.35, "Semantic Layer", "dbt / Cube.dev\n분석 지표 표준화", BLUE, 9),
        (0.20, 0.22, "Knowledge Graph", "Neo4j / Neptune\n관계 탐색", BLUE, 9),
        # 우하: 읽기+운영
        (0.75, 0.30, "Digital Twin", "Siemens / Azure\n물리자산 시뮬레이션", YELLOW, 9),
        # 좌상: 쓰기+분석
        (0.30, 0.70, "Databricks", "레이크하우스\n+ Unity Catalog", PURPLE, 9),
        (0.20, 0.62, "Snowflake", "Cortex\n+ Unistore", PURPLE, 9),
        # 우상: 쓰기+운영 (팔란티어 영역)
        (0.72, 0.72, "Palantir", "Ontology\n= Read + Write\n+ 실행 + 감사", GREEN, 12),
    ]

    for x_frac, y_frac, name, desc, color, size in items:
        px = MATRIX_X + x_frac * MATRIX_W
        py = MATRIX_Y + y_frac * MATRIX_H

        is_pltr = (name == "Palantir")

        # 마커
        marker_size = 200 if is_pltr else 100
        ax.scatter(px, py, s=marker_size, color=color, zorder=4,
                   alpha=0.3, transform=ax.transAxes)
        ax.scatter(px, py, s=marker_size * 0.4, color=color, zorder=5,
                   transform=ax.transAxes)

        # 이름
        ax.text(px, py + 0.05, name,
                ha="center", va="center",
                color=color, fontsize=size, fontweight="bold",
                transform=ax.transAxes)
        # 설명
        ax.text(px, py - 0.04, desc,
                ha="center", va="center",
                color=DIM if not is_pltr else WHITE,
                fontsize=7 if not is_pltr else 8,
                multialignment="center", linespacing=1.3,
                transform=ax.transAxes)

    # Palantir 강조 영역 (우상 사분면)
    highlight = mpatches.FancyBboxPatch(
        (mid_x + 0.02, mid_y + 0.02),
        MATRIX_W / 2 - 0.04, MATRIX_H / 2 - 0.04,
        boxstyle="round,pad=0.008",
        facecolor=GREEN, alpha=0.04,
        edgecolor=GREEN, linewidth=0.8, linestyle="--",
        transform=ax.transAxes
    )
    ax.add_patch(highlight)

    # 파트너십 화살표 (Databricks/Snowflake → Palantir)
    pltr_x = MATRIX_X + 0.72 * MATRIX_W
    pltr_y = MATRIX_Y + 0.72 * MATRIX_H
    for fx, fy in [(0.30, 0.70), (0.20, 0.62)]:
        from_x = MATRIX_X + fx * MATRIX_W
        from_y = MATRIX_Y + fy * MATRIX_H
        ax.annotate(
            "", xy=(pltr_x - 0.03, pltr_y - 0.02),
            xytext=(from_x + 0.03, from_y),
            xycoords="axes fraction",
            arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.0,
                            mutation_scale=10, alpha=0.4,
                            connectionstyle="arc3,rad=0.1")
        )

    ax.text(0.42, 0.78, "partnership",
            ha="center", va="center",
            color=GRAY, fontsize=7, fontstyle="italic",
            rotation=15,
            transform=ax.transAxes)

    # 하단 인사이트
    ax.text(0.5, 0.10,
            "경쟁사들이 Ontology를 직접 만들지 않고 파트너십을 택했다",
            ha="center", va="center",
            color=GREEN, fontsize=10, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.05,
            "데이터 레이크 = 사실의 저장  /  Ontology = 의미의 소유  ―  층위가 다르다",
            ha="center", va="center",
            color=DIM, fontsize=8.5,
            transform=ax.transAxes)

    return _save(fig, "02_competition_matrix.png")


# ══════════════════════════════════════════════════════════════════════════════
# QA
# ══════════════════════════════════════════════════════════════════════════════
def qa_check() -> None:
    from PIL import Image
    files = [
        OUT / "01_customer_cases.png",
        OUT / "02_competition_matrix.png",
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
    print("2 Customer/Competition visuals ...\n")
    make_customer_cases()
    print("  + 01 customer cases")
    make_competition_matrix()
    print("  + 02 competition matrix")
    qa_check()
    print(f"\nSaved to: {OUT}\n")
