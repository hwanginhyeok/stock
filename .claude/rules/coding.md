# Coding Rules

## Python 컨벤션

- Python 3.11+ 필수
- PEP 8 준수 (black 포매터, ruff 린터)
- Type hints 모든 함수에 필수
- Google 스타일 docstring
- f-string 사용 (% 포매팅, .format() 금지)

## 코드 패턴

- **데이터 모델**: Pydantic BaseModel 사용
- **로깅**: structlog 사용, 구조화된 JSON 로깅
- **재시도**: tenacity 라이브러리로 API 호출 재시도 (max 3회, exponential backoff)
- **설정**: pydantic-settings로 환경변수 + YAML 통합 관리
- **DB**: SQLAlchemy ORM, 비동기 지원
- **상속**: 각 모듈은 base class를 정의하고 구체 구현은 상속

## Matplotlib 차트 작성 규칙

### 한글 폰트 (Linux/WSL)

```python
import matplotlib.font_manager as _fm
import matplotlib.pyplot as plt

# 주의: rcParams만으로는 안 됨 — addfont()로 파일 직접 등록 후 family 지정
_KOREAN_FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
if os.path.exists(_KOREAN_FONT_PATH):
    _fm.fontManager.addfont(_KOREAN_FONT_PATH)
    # addfont()은 .ttc 컬렉션의 첫 번째 폰트(JP)만 등록함 → 이름은 "Noto Sans CJK JP"
    # JP 폰트도 한글 글리프 포함 — 렌더링 정상 작동
    plt.rcParams["font.family"] = "Noto Sans CJK JP"
plt.rcParams["axes.unicode_minus"] = False  # 필수: 마이너스(−) 기호 깨짐 방지
```

- `addfont()` 없이 family 이름만 설정하면 matplotlib이 시스템 폰트를 인식 못 함
- `axes.unicode_minus = False` 미설정 시 음수 부호가 □로 출력됨
- 헤드리스 환경(서버/WSL 이메일 발송 등): `matplotlib.use("Agg")` 백엔드 필수

### Y축 스케일 규칙 (국룰)

**절대 금지**: Y축을 `0 ~ max`로 설정 — 변화량이 보이지 않음

**필수**: `min - 10% ~ max + 10%` 패딩 적용

```python
def _set_ylim_padded(ax, data_min, data_max, pad=0.10):
    rng = data_max - data_min
    if rng == 0:
        rng = abs(data_min) if data_min != 0 else 1.0
    ax.set_ylim(data_min - pad * rng, data_max + pad * rng)
```

- 여러 시리즈가 겹치는 축: 전체 min/max로 계산
- Flow(유입/유출) 바 차트: 0을 항상 포함한 후 패딩 (`lo = min(flow.min(), 0)`)
- 정규화 차트(기준=100): 모든 정규화 시리즈의 combined min/max 사용

## 작업 품질 체크리스트

작업 완료 시 아래 항목을 확인:

- [ ] Type hints 적용 여부
- [ ] Google 스타일 docstring 작성 여부
- [ ] 에러 처리 및 로깅 적용 여부
- [ ] 보안 규칙 준수 여부 (API 키 하드코딩 없음)
- [ ] 기존 base class 패턴 준수 여부
- [ ] 실행 테스트 통과 여부
