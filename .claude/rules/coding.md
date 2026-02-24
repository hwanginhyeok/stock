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

## 작업 품질 체크리스트

작업 완료 시 아래 항목을 확인:

- [ ] Type hints 적용 여부
- [ ] Google 스타일 docstring 작성 여부
- [ ] 에러 처리 및 로깅 적용 여부
- [ ] 보안 규칙 준수 여부 (API 키 하드코딩 없음)
- [ ] 기존 base class 패턴 준수 여부
- [ ] 실행 테스트 통과 여부
