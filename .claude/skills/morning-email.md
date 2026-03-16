# 모닝 이메일 실행 스킬 (morning-email)

> **트리거**: 아래 표현이 나오면 이 스킬을 즉시 실행한다.
> - "모닝 이메일" / "이메일 보내줘" / "morning email"
> - "이메일 테스트" / "이메일 확인"
> - 장 시작 전 자동 제안 가능

---

## 목적

매일 장 시작 전 시장 데이터를 수집하고, 분석 결과를 이메일로 발송한다.
데이터 수집 실패 시 분기 처리(폴백, 스킵)를 명확히 하여 빈 이메일 방지.

---

## 실행 순서 (순서 준수 필수)

### STEP 1 — 환경 확인

```bash
cd /home/gint_pcd/projects/주식부자프로젝트
source .venv-wsl/bin/activate

# .env 확인 (API 키들)
test -f .env && echo "✅ .env 존재" || echo "❌ .env 없음"
```

필요한 API 키:
- FRED API, Alpha Vantage, 이메일 SMTP 인증

### STEP 2 — 데이터 수집 상태 확인

이메일 발송 전에 각 데이터 소스의 가용성을 확인한다:

| 데이터 | 소스 | 장외시간 | 알려진 이슈 |
|--------|------|---------|------------|
| 주가/지수 | yfinance | ✅ 가용 (전일 종가) | — |
| FRED 유동성 | FRED API | ✅ 가용 | — |
| IV/시그마 | CBOE | ❌ 장외시간 미제공 | CBOE Put/Call CSV 404 |
| BTC 도미넌스 | CoinGecko /global | ✅ 24h | 무료 API, 키 없음 |
| 공포탐욕지수 | alternative.me /fng/ | ✅ 24h | 무료 API, 키 없음 |
| ETH/BTC 비율 | 가격에서 계산 | ✅ 24h | — |

### STEP 3 — 이메일 생성 (dry-run 우선)

```bash
python scripts/send_morning_email.py --dry-run
```

dry-run 출력에서 확인:
- 각 섹션의 데이터 채워짐 여부
- 빈 섹션이 있으면 해당 데이터 소스 확인
- 크립토 섹션(Section 5) 하단 3칸 카드 정상 여부

### STEP 4 — 이메일 내용 검토

dry-run 결과를 사용자에게 보여준다:

```
📧 모닝 이메일 프리뷰 — {날짜}

| 섹션 | 상태 | 비고 |
|------|------|------|
| 1. 시장 지수 | ✅ | S&P, NASDAQ, DJI, VIX |
| 2. 섹터 ETF | ✅ | 11개 섹터 |
| 3. FX/금리 | ✅ | DXY, 10Y, Gold |
| 4. 기술적 지표 | ✅ | RSI, ADX, 레짐 |
| 5. 크립토 | ✅ | BTC, ETH + 도미넌스/공포탐욕 |
| 6. 시그마 분석 | ⚠️ | IV 미제공(장외) → HV20 폴백 |

발송할까요? [Y/n]
```

### STEP 5 — 이메일 발송

```bash
python scripts/send_morning_email.py
```

### STEP 6 — 발송 확인

- 발송 성공/실패 로그 확인
- 실패 시 SMTP 인증, 네트워크, 수신자 주소 확인

---

## 판단 규칙

| 상황 | 행동 |
|------|------|
| 데이터 전체 정상 | 바로 발송 |
| IV 미제공 (장외) | HV20 폴백 — 정상 동작, 경고만 |
| CBOE Put/Call 404 | 해당 섹션 스킵 (알려진 이슈) |
| API 1개 실패 | 해당 섹션 "데이터 미수집" 표기 후 나머지 발송 |
| API 3개+ 실패 | 발송 보류, 원인 분석 |
| SMTP 실패 | 인증 정보 확인 (.env) |

---

## 주의사항

- 장외시간(한국 밤)에 실행 시 IV 데이터 없음 → HV20 폴백은 정상 동작
- 크립토 지표(BTC 도미넌스, 공포탐욕)는 24h 가용 — 별도 API 키 불필요
- 이메일 수신자 목록은 `.env` 또는 설정 파일에서 관리
- dry-run은 이메일을 보내지 않고 콘솔에 출력만 함
- matplotlib 차트 생성 시 `matplotlib.use("Agg")` 백엔드 필수 (헤드리스 환경)
