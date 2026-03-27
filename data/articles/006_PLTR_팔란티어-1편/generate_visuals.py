"""
generate_visuals.py — 팔란티어 1편: Ontology 시각화

생성 이미지:
  01_ontology_structure.png  — Ontology 3계층 + 6대 구성 요소 구조도
  02_llm_synergy.png         — LLM + Ontology 시너지 흐름도

Usage:
    python data/articles/006_PLTR_팔란티어-1편/generate_visuals.py
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
# 01. Ontology 3계층 + 6대 구성 요소 구조도
# ══════════════════════════════════════════════════════════════════════════════
def make_ontology_structure() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "Ontology 아키텍처",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "3개 계층 + 6개 구성 요소",
            ha="center", va="center", color=DIM, fontsize=10,
            transform=ax.transAxes)

    # ── 3계층 (좌측 영역, 위에서 아래로) ──
    layers = [
        {
            "name": "Semantic (의미)",
            "desc": "\"무엇인가\"를 정의한다",
            "example": "납기 지연 = 계약 유형별\n복합 정의로 통합",
            "color": BLUE,
        },
        {
            "name": "Kinetic (행동)",
            "desc": "\"무엇을 할 수 있는가\"를 정의한다",
            "example": "자동 통지 / 보상 처리 /\nCEO 에스컬레이션 로직",
            "color": YELLOW,
        },
        {
            "name": "Dynamic (강제)",
            "desc": "\"어떻게 실행되는가\"를 강제한다",
            "example": "모든 액션 기록 + 권한 체계\n(인간/AI 동일 규칙)",
            "color": GREEN,
        },
    ]

    LAYER_X = 0.04
    LAYER_W = 0.50
    LAYER_H = 0.20
    LAYER_GAP = 0.03
    START_Y = 0.85

    for i, layer in enumerate(layers):
        y_top = START_Y - i * (LAYER_H + LAYER_GAP)
        color = layer["color"]

        # 카드 배경
        rect = mpatches.FancyBboxPatch(
            (LAYER_X, y_top - LAYER_H), LAYER_W, LAYER_H,
            boxstyle="round,pad=0.010",
            facecolor=BG2,
            edgecolor=color, linewidth=1.8,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 좌측 색상 바
        bar = mpatches.FancyBboxPatch(
            (LAYER_X, y_top - LAYER_H), 0.012, LAYER_H,
            boxstyle="square,pad=0",
            facecolor=color, alpha=0.6,
            transform=ax.transAxes
        )
        ax.add_patch(bar)

        # 레이어 이름
        ax.text(LAYER_X + 0.035, y_top - 0.035,
                layer["name"], ha="left", va="center",
                color=color, fontsize=11, fontweight="bold",
                transform=ax.transAxes)
        # 부제
        ax.text(LAYER_X + 0.035, y_top - 0.07,
                layer["desc"], ha="left", va="center",
                color=WHITE, fontsize=8.5,
                transform=ax.transAxes)
        # 구분선
        ax.plot(
            [LAYER_X + 0.035, LAYER_X + LAYER_W - 0.02],
            [y_top - 0.09, y_top - 0.09],
            color=BORDER, linewidth=0.5, alpha=0.4,
            transform=ax.transAxes
        )
        # 예시
        ax.text(LAYER_X + 0.035, y_top - 0.14,
                layer["example"], ha="left", va="center",
                color=DIM, fontsize=7.8,
                multialignment="left", linespacing=1.4,
                transform=ax.transAxes)

        # 화살표 (계층 사이)
        if i < 2:
            arr_y = y_top - LAYER_H - LAYER_GAP / 2
            ax.annotate(
                "", xy=(LAYER_X + LAYER_W / 2, arr_y - 0.005),
                xytext=(LAYER_X + LAYER_W / 2, arr_y + 0.005),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.5,
                                mutation_scale=14)
            )

    # ── 6대 구성 요소 (우측 영역, 2x3 그리드) ──
    components = [
        ("Object Type", "현실 세계 대응물\n(Airport, Patient...)", BLUE),
        ("Link Type", "Object 간 관계\n(1:1, 1:N, M:N)", BLUE),
        ("Action Type", "원자적 트랜잭션\n(비즈니스 규칙+권한)", YELLOW),
        ("Function", "서버 사이드 로직\n(TypeScript/Python)", YELLOW),
        ("Interface", "다형성 제공\n(공통 프레임)", GREEN),
        ("OSDK", "타입 안전 API\n(외부 앱 접근)", GREEN),
    ]

    COMP_START_X = 0.58
    COMP_W = 0.19
    COMP_H = 0.13
    COMP_GAP_X = 0.02
    COMP_GAP_Y = 0.025
    COMP_START_Y = 0.85

    ax.text(0.68, 0.90, "6대 구성 요소",
            ha="center", va="center",
            color=WHITE, fontsize=11, fontweight="bold",
            transform=ax.transAxes)

    for idx, (name, desc, color) in enumerate(components):
        row = idx // 2
        col = idx % 2
        x = COMP_START_X + col * (COMP_W + COMP_GAP_X)
        y_top = COMP_START_Y - row * (COMP_H + COMP_GAP_Y)

        rect = mpatches.FancyBboxPatch(
            (x, y_top - COMP_H), COMP_W, COMP_H,
            boxstyle="round,pad=0.008",
            facecolor=BG2,
            edgecolor=color, linewidth=1.0, alpha=0.9,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        ax.text(x + COMP_W / 2, y_top - 0.03,
                name, ha="center", va="center",
                color=color, fontsize=8.5, fontweight="bold",
                transform=ax.transAxes)
        ax.text(x + COMP_W / 2, y_top - COMP_H / 2 - 0.015,
                desc, ha="center", va="center",
                color=DIM, fontsize=6.8,
                multialignment="center", linespacing=1.3,
                transform=ax.transAxes)

    # ── 하단 결론 ──
    rect = mpatches.FancyBboxPatch(
        (0.08, 0.03), 0.84, 0.09,
        boxstyle="round,pad=0.010",
        facecolor=GREEN, alpha=0.07,
        edgecolor=GREEN, linewidth=1.0,
        transform=ax.transAxes
    )
    ax.add_patch(rect)
    ax.text(0.5, 0.09,
            "운영 두뇌 (Operating Brain)",
            ha="center", va="center",
            color=GREEN, fontsize=12, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.05,
            "LLM을 교체해도 사라지지 않는다  /  쌓일수록 깊어진다",
            ha="center", va="center",
            color=DIM, fontsize=8.5,
            transform=ax.transAxes)

    return _save(fig, "01_ontology_structure.png")


# ══════════════════════════════════════════════════════════════════════════════
# 02. LLM + Ontology 시너지 흐름도
# ══════════════════════════════════════════════════════════════════════════════
def make_llm_synergy() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # 제목
    ax.text(0.5, 0.96, "LLM + Ontology 시너지",
            ha="center", va="center",
            color=WHITE, fontsize=17, fontweight="bold",
            transform=ax.transAxes)
    ax.text(0.5, 0.92, "일반 LLM vs AIP+Ontology  /  피드백 루프",
            ha="center", va="center", color=DIM, fontsize=9.5,
            transform=ax.transAxes)

    # ── 상단: 일반 LLM vs AIP+Ontology 비교 카드 ──
    def draw_comparison_card(x, y_top, w, h, title, subtitle, items, color):
        rect = mpatches.FancyBboxPatch(
            (x, y_top - h), w, h,
            boxstyle="round,pad=0.010",
            facecolor=BG2,
            edgecolor=color, linewidth=1.5,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        # 헤더 배경
        hdr_h = 0.05
        hdr = mpatches.FancyBboxPatch(
            (x, y_top - hdr_h), w, hdr_h,
            boxstyle="square,pad=0",
            facecolor=color, alpha=0.12,
            transform=ax.transAxes
        )
        ax.add_patch(hdr)

        ax.text(x + w / 2, y_top - hdr_h / 2,
                title, ha="center", va="center",
                color=color, fontsize=10, fontweight="bold",
                transform=ax.transAxes)
        ax.text(x + w / 2, y_top - hdr_h - 0.02,
                subtitle, ha="center", va="center",
                color=DIM, fontsize=7.5,
                transform=ax.transAxes)

        for i, item in enumerate(items):
            y = y_top - hdr_h - 0.05 - i * 0.035
            ax.text(x + 0.03, y, ">" if color == GREEN else "-",
                    ha="left", va="center",
                    color=color, fontsize=8,
                    transform=ax.transAxes)
            ax.text(x + 0.06, y, item,
                    ha="left", va="center",
                    color=WHITE if color == GREEN else DIM,
                    fontsize=7.8,
                    transform=ax.transAxes)

    # 좌측: 일반 LLM
    draw_comparison_card(
        0.04, 0.87, 0.44, 0.27,
        "일반 LLM", "\"공급업체 리스크를 분석해줘\"",
        [
            "일반론 응답: \"재무 안정성,",
            "  납기 이력, 지정학적 위험 등을",
            "  고려해야 합니다\"",
            "정확하지만 무용하다",
            "이미 아는 것만 반복",
        ],
        RED
    )

    # 우측: AIP + Ontology
    draw_comparison_card(
        0.52, 0.87, 0.44, 0.27,
        "AIP + Ontology", "같은 질문, 전혀 다른 답",
        [
            "이 회사의 리스크 정의로 조회",
            "SLA 위반 12회, 위반율 18.5%",
            "과거 유사 결정 제시 (선례 학습)",
            "대체 공급업체 목록 + 단가 비교",
            "즉시 실행 가능한 액션 옵션",
        ],
        GREEN
    )

    # VS 중간
    ax.text(0.50, 0.735, "VS",
            ha="center", va="center",
            color=WHITE, fontsize=12, fontweight="bold",
            transform=ax.transAxes)

    # ── 하단: 피드백 루프 (순환 다이어그램) ──
    ax.text(0.5, 0.545, "Ontology 피드백 루프 — 의사결정의 복리",
            ha="center", va="center",
            color=WHITE, fontsize=12, fontweight="bold",
            transform=ax.transAxes)

    # 4단계 순환 플로우 (좌→우→우하→좌하→좌)
    steps = [
        {"label": "에이전트\n실행", "desc": "AIP가 액션 수행",
         "x": 0.15, "y": 0.40, "color": BLUE},
        {"label": "결과\n발생", "desc": "성공/실패 기록",
         "x": 0.45, "y": 0.40, "color": YELLOW},
        {"label": "Ontology\n축적", "desc": "지식으로 저장",
         "x": 0.75, "y": 0.40, "color": GREEN},
        {"label": "다음 에이전트\n더 정확", "desc": "선례 학습 완료",
         "x": 0.45, "y": 0.17, "color": PURPLE},
    ]

    BOX_W = 0.22
    BOX_H = 0.11

    for step in steps:
        x, y = step["x"], step["y"]
        color = step["color"]

        rect = mpatches.FancyBboxPatch(
            (x - BOX_W / 2, y - BOX_H / 2), BOX_W, BOX_H,
            boxstyle="round,pad=0.010",
            facecolor=BG2,
            edgecolor=color, linewidth=1.3,
            transform=ax.transAxes
        )
        ax.add_patch(rect)

        ax.text(x, y + 0.015,
                step["label"], ha="center", va="center",
                color=color, fontsize=9, fontweight="bold",
                multialignment="center",
                transform=ax.transAxes)
        ax.text(x, y - 0.035,
                step["desc"], ha="center", va="center",
                color=DIM, fontsize=7.5,
                transform=ax.transAxes)

    # 화살표: step0 → step1
    ax.annotate("", xy=(0.34, 0.40), xytext=(0.26, 0.40),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.5,
                                mutation_scale=14))
    # step1 → step2
    ax.annotate("", xy=(0.64, 0.40), xytext=(0.56, 0.40),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.5,
                                mutation_scale=14))
    # step2 → step3 (아래로)
    ax.annotate("", xy=(0.68, 0.21), xytext=(0.78, 0.33),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.5,
                                mutation_scale=14,
                                connectionstyle="arc3,rad=0.2"))
    # step3 → step0 (왼쪽으로 + 위로)
    ax.annotate("", xy=(0.22, 0.33), xytext=(0.33, 0.21),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.5,
                                mutation_scale=14,
                                connectionstyle="arc3,rad=0.2"))

    # 순환 중심 메시지
    ax.text(0.45, 0.295,
            "6개월 vs 5년 — 격차는 좁혀지지 않는다",
            ha="center", va="center",
            color=GREEN, fontsize=8.5, fontweight="bold",
            transform=ax.transAxes)

    # 하단 인사이트
    rect = mpatches.FancyBboxPatch(
        (0.10, 0.03), 0.80, 0.06,
        boxstyle="round,pad=0.008",
        facecolor=GREEN, alpha=0.06,
        edgecolor=GREEN, linewidth=0.8,
        transform=ax.transAxes
    )
    ax.add_patch(rect)
    ax.text(0.5, 0.06,
            "복리: 의사결정의 결과가 다시 지식이 된다",
            ha="center", va="center",
            color=GREEN, fontsize=10, fontweight="bold",
            transform=ax.transAxes)

    return _save(fig, "02_llm_synergy.png")


# ══════════════════════════════════════════════════════════════════════════════
# QA
# ══════════════════════════════════════════════════════════════════════════════
def qa_check() -> None:
    from PIL import Image
    files = [
        OUT / "01_ontology_structure.png",
        OUT / "02_llm_synergy.png",
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
    print("1 Ontology visuals ...\n")
    make_ontology_structure()
    print("  + 01 ontology structure")
    make_llm_synergy()
    print("  + 02 llm synergy")
    qa_check()
    print(f"\nSaved to: {OUT}\n")
