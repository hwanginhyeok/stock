# 시각화 생성 스킬

## 목적
- 아티클용 PNG 이미지를 1080×1080 모바일 최적화 포맷으로 생성
- matplotlib + NotoSansCJK 기반 일관된 디자인 시스템 적용

## 실행 조건
- 아티클에 삽입할 시각화가 필요할 때
- `article-research` 스킬의 Phase 4 완료 후

## 절차

### Step 1: 스크립트 파일 생성
아티클 폴더 루트에 `generate_visuals.py` 생성.

**필수 헤더 패턴:**
```python
import os
from pathlib import Path
import matplotlib
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

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

FIG_SIZE = (8, 8)
DPI      = 135
```

### Step 2: 단일 axes 차트 (타임라인, 테이블 등)
단일 axes 차트는 반드시 `fig.subplots_adjust(left=0, right=1, top=1, bottom=0)` 적용.

```python
def make_chart() -> Path:
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)  # ← 필수
    ax.set_facecolor(BG)
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    # ... 콘텐츠 작성 (transform=ax.transAxes 사용)
    return _save(fig, "01_chart.png")
```

> **이유**: `plt.subplots()` 기본 axes 마진이 figure의 ~22%를 차지한다.
> `bbox_inches="tight"` 적용 시 마진이 잘려 863×858px이 된다.
> `subplots_adjust(0,0,1,1)`로 axes를 figure 전체로 확장해야 1107×1107px 달성.

### Step 3: 저장 함수
```python
def _save(fig: plt.Figure, name: str) -> Path:
    path = OUT / name
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=fig.get_facecolor(), pad_inches=0.1)
    plt.close(fig)
    return path
```

### Step 4: QA 함수 작성 및 실행
스크립트 마지막에 반드시 `qa_check()` 호출.

```python
def qa_check() -> None:
    from PIL import Image
    files = [OUT / "01_*.png", ...]  # 생성한 파일 목록
    for fp in files:
        issues = []
        if not fp.exists():
            print(f"  ❌ {fp.name} — 파일 없음"); continue
        size_kb = fp.stat().st_size / 1024
        if size_kb < 10:
            issues.append(f"파일 크기 너무 작음 ({size_kb:.1f} KB)")
        with Image.open(fp) as img:
            w, h = img.size
            ratio = w / h
            if w < 900 or h < 900:
                issues.append(f"해상도 부족 ({w}×{h}px, 최소 900px)")
            if not (0.85 <= ratio <= 1.15):
                issues.append(f"비율 이탈 ({ratio:.2f})")
        if issues:
            print(f"  ⚠️  {fp.name}"); [print(f"       → {i}") for i in issues]
        else:
            print(f"  ✅ {fp.name} ({size_kb:.0f} KB, {w}×{h}px)")

if __name__ == "__main__":
    make_chart()
    # ...
    qa_check()
```

### Step 5: 실행 및 QA 확인
```bash
source .venv-wsl/bin/activate && python data/articles/{폴더}/generate_visuals.py
```

QA 항목이 모두 ✅ 통과할 때까지 수정 후 재실행.

## 차트 유형별 가이드

| 유형 | 함수명 패턴 | 특이사항 |
|------|-------------|----------|
| 타임라인 | `make_timeline()` | xp() 함수로 연도→x좌표 변환, stem_len으로 up/down 배치 |
| 달성 테이블 | `make_achievement_table()` | sections 리스트 → 섹션헤더+행 순회, rh = body_h / row_count |
| 2×2 카드 | `make_mission_cards()` | `plt.subplots(2,2)` + `fig.subplots_adjust()` |
| 바 차트 | `make_bar_chart()` | `ax.barh()` 수평 바, `_set_ylim_padded()` 적용 |

## 이미지 소싱 원칙

| 유형 | 방법 | 담당 |
|------|------|------|
| 차트·비교카드·타임라인 | matplotlib로 직접 제작 | Claude |
| 제품 사진·앱 스크린샷·로고 | 사용자가 직접 검색·선별 | 사용자 |
| 히어로 이미지 (3사 비교 등) | matplotlib 다크 카드 레이아웃 | Claude |

**웹 이미지 검색을 Claude가 하지 않는 이유:**
- WebFetch로 페이지를 읽으면 한 페이지당 수천~수만 토큰 소모
- 이미지를 시각적으로 판단할 수 없음 (텍스트만 읽음)
- 3~4번 반복해도 적합한 이미지를 못 찾는 경우 많음

**워크플로우:**
1. Claude: 아티클 구조 보고 **어떤 이미지가 어디에 필요한지** + 검색 키워드 제안
2. 사용자: 구글/언스플래시에서 눈으로 보고 선별 → `images/`에 저장 (또는 URL 전달)
3. Claude: `curl`로 다운로드하거나 바로 사용

## 디자인 원칙
- 배경 `#0d1117` — 어두운 GitHub 스타일
- 텍스트 잘림 방지: bbox 좌표 x(0.05~0.95), y(0.04~0.96) 범위 내 배치
- 상태 색상: 완료=GREEN, 진행중=BLUE, 지연=YELLOW, 미완료=RED, 전략변경=ORANGE, 미착수=GRAY
- NotoSansCJK에 없는 특수문자 주의: ✗(U+2717)→×, ↻(U+21BB)→~ 등으로 대체

## QA 기준 (필수 통과 조건)
| 항목 | 기준 |
|------|------|
| 파일 크기 | > 10 KB |
| 해상도 | 가로·세로 모두 ≥ 900px |
| 비율 | 0.85 ~ 1.15 (정사각형 기준) |
| glyph 경고 | 저장 시 UserWarning 없어야 함 |
