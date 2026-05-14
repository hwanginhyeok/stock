# Handoff — 2026-05-14

## 작업 중이던 것

### 1-58: 차트 시그널 마커 통합 (코드 완료, 확인 대기)
- **완료된 것**: `src/analyzers/sma_signals.py`에 `historical_chart_signals()` 추가 (커밋 66d99f8)
- **완료된 것**: `src/web/chart_api.py` `/api/chart/strategy` 리팩토링 — SMA100→VWMA100 기준 통일
- **남은 것**: uvicorn 재시작 후 차트에서 PO/W/BR/PB 마커 실물 확인
- **재시작 명령**: `pkill -f 'uvicorn src.web.app' && uvicorn src.web.app:app --reload --port 8200 &`

### 1-52: 정배열/역배열 (계속 진행 중)
- 1-58 차트 마커 통합 완료로 비고 업데이트됨
- **남은 것**: 백테스트 결과 분석, 1H/4H 타임프레임 확장

## 컨텍스트

### 이번 세션 결정사항
- important 임계값 6→10으로 상향 (ecb9de5) — 타임라인 이벤트 노이즈 감소 목적
- `historical_chart_signals()`: lookback=5봉, tolerance=±0.5%, VWMA100 기준선 (SMA100 폐기)
- strategy API 리팩토링으로 pandas_ta→numba→coverage 호환성 버그 동시 해결 (서버가 500 던지던 문제)

### 마커 타입 (프론트 app.js 이미 처리됨)
- `PO` (녹색 ▲): 정배열 진입
- `W` (노랑 ▲): 과도기 진입 (점진 매도)
- `BR` (빨강 ▼): 추세 붕괴
- `PB` (파랑 ▲): 눌림목 매수

## 파일 변경 요약
- `src/analyzers/sma_signals.py`: historical_chart_signals() 함수 추가 (+186줄)
- `src/web/chart_api.py`: strategy 엔드포인트 리팩토링 (-156줄 순감)
- `src/web/tesla_api.py`: important 임계값 6→10

## 다음 세션 첫 액션
1. `pkill -f 'uvicorn src.web.app' && uvicorn src.web.app:app --reload --port 8200 &`
2. 브라우저에서 차트 열고 1y 기간 — PO/W/BR/PB 마커 17개 확인
3. 차트 확인 완료 시 1-58 FINISHED로 이동
4. 이후 1-52 백테스트 또는 1H/4H 확장 착수
