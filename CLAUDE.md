# 주식부자프로젝트

> **테슬라 투자 인텔리전스** — 리서치 + 트레이딩 + 콘텐츠

## Tasks
- [CURRENT_TASK.md](CURRENT_TASK.md) | [PREPARED_TASK.md](PREPARED_TASK.md) | [FINISHED_TASK.md](FINISHED_TASK.md)

---

## 프로젝트 방향성

### 핵심 집중: Tesla (TSLA)

이 프로젝트는 **테슬라**에 대한 깊은 이해를 바탕으로:
1. 체계적 리서치 (온톨로지, 역사, 제품, 거시)
2. 데이터 기반 트레이딩 (기술적 지표, 옵션 흐름, 백테스트)
3. 콘텐츠 생성 (아티클, 카드뉴스, 시각화)

**왜 테슬라인가?**
- 수직통합 에너지 기업 (자동차 ↔ 에너지 ↔ 로봇)
- 일론 머스크의 리더십 실험실
- AI/Autonomy 복합체 (FSD, Optimus, 휴먼 로봇)
- 팬덤 커뮤니티 + 밈 문화 (다른 종목에 없는 특성)

### 두 축 분리 원칙

투자 판단을 **두 가지 축으로 명확히 분리**한다.

#### 축 1: 시장 흐름 읽기 — "언제 움직일까"
> 넘치는 데이터를 가시화하고, 거기서 시장의 흐름을 읽고 대응한다.

- **도구**: 유동성(FRED), FX, 섹터 ETF, 기술적 지표(RSI/ADX/MACD/Supertrend), 시장 레짐
- **산출물**: 모닥 이메일, 시그널 리포트 Excel, 지표 해석 체계
- **판단**: 지금 시장이 Risk-On인가 Risk-Off인가. 언제 포지션을 늘리고 줄일 것인가.

#### 축 2: 종목 분석 — "테슬라을 어떻게 볼까"
> 테슬라에 대한 심층 이해를 통해 인사이트를 얻고, 그것을 토대로 결정한다.

- **도구**: 펀더멘탈 리서치, 아티클 집필, 장기 테제 구축, 온톨로지 매핑
- **산출물**: 테슬라 리서치 허브 (`data/research/stocks/tesla/`), X 아티클, 인스타 카드뉴스
- **판단**: 이 기업의 방향성이 맞는가. 10년 뒤에도 보유할 수 있는가.

### 현재 집중 종목

- **Tesla (TSLA)** — 수직통합 + 에너지 + 로봇 테제
- **보류 중**: Bitcoin (BTC), Ethereum (ETH), 지정학 이슈, 한국 주식

### 미완성 연결 고리 (향후 과제)

두 축을 연결하는 **의사결정 체계**가 아직 없다:
- 시장이 Risk-On → 테슬라에 언제, 얼마나 진입?
- 시장이 Risk-Off → 포지션을 어떻게 줄일 것인가?
- 이 체계가 갖춰지면 진정한 시스템 트레이딩 완성.

---

## 세션 시작 규칙 (필수)

새 세션이 시작되면 코딩에 들어가기 전에 반드시 아래 순서를 따른다:

1. **TASK.md 확인** — `CURRENT_TASK.md`에서 현재 상태 점검, 블로커 보고
2. **데일리 미팅** — 진행 상황, 블로커, 이슈를 사용자와 공유
3. **방향성 논의** — 오늘 작업할 항목의 우선순위와 접근 방식을 사용자와 합의
4. **합의 후 착수** — 사용자가 동의한 작업만 진행

## 언어 규칙

- **코드**: 변수명, 함수명, 클래스명, 주석 → 영어
- **콘텐츠/문서**: 사용자 대면 콘텐츠, 문서, 커밋 메시지 → 한국어
- **설정 파일**: 키는 영어, 값은 용도에 따라 한국어/영어

## TASK 관리

- **인덱스**: `TASK.md` (루트) → Current / Prepared / Finished 3파일 분리
- **번호 체계**: `{분야코드}-{순번}` — 1=시스템, 2=코드, 3=분석, 4=아티클, 5=리서치
- **아카이브**: 완료 후 월 단위로 `TASK_ARCHIVE/YYYY-MM.md` 이동
- **갱신 규칙**: 상세 내용은 `.claude/rules/workflow.md` 참조
- **상세 로그**: 설계 결정이 포함된 작업은 `docs/프로젝트/task/{ID}.md`에 기록

## 상세 규칙 (세션 시작 시 자동 로딩)

| 파일 | 내용 |
|------|------|
| `.claude/rules/coding.md` | Python 컨벤션, 코드 패턴, 품질 체크리스트 |
| `.claude/rules/workflow.md` | 워크플로우 원칙, 보안 규칙, TASK 갱신 규칙 |
| `.claude/rules/architecture.md` | 디렉토리 구조, 에이전트 역할 |
| `.claude/rules/git.md` | Git 컨벤션 |

## 스킬 (반복 작업 시 참조)

| 파일 | 내용 | 트리거 |
|------|------|--------|
| `.claude/skills/README.md` | 스킬 작성 가이드 | 새 스킬 추가 시 |
| `.claude/skills/article-writing.md` | 아티클 구조·포맷·카테고리·시각화 규칙 | 아티클 작성 시 |
| `.claude/skills/writing-voice.md` | 저자의 목소리·문체·감정·논리 전개 패턴 + 퇴고 피드백 로그 | 아티클 초안 작성·퇴고 시 |
| `.claude/skills/naver-html.md` | 네이버 블로그 HTML 형식·스타일·색상·워크플로우 가이드 | 네이버 HTML 변환 시 |
| `.claude/skills/article-research.md` | 아티클 리서치 4단계 워크플로우 | 투자 아티클 기획/리서치 시 |
| `.claude/skills/generate-visuals.md` | 1080×1080 PNG 시각화 생성 (matplotlib + QA) | 아티클 시각화 생성 시 |
| `.claude/skills/publish-x.md` | X Notes 게시 체크리스트 + 주제별 해시태그 | 아티클 X 게시 시 |
| `.claude/skills/article-drafting.md` | 아티클 초안 — 아웃라인 작성 → 사용자 승인 → v1 초안 → 자가 점검 | 리서치 Phase 4 완료 후 / "초안 쓰자" 지시 시 |
| `.claude/skills/article-revision.md` | 아티클 퇴고 — 의사결정 트리 + 6항목 체크리스트 + v2/x_publish 변환 | 초안 완성 후 / 퇴고 피드백 수령 시 |
| `.claude/skills/feedback-tracking.md` | 퇴고 피드백 추적 — 기록·분류·패턴 감지·원칙 승격 | 퇴고 피드백 수령 시 / 세션 시작 시 |
| `.claude/skills/image-markers.md` | 📎 이미지 마커 배치 & 교차 검증 — 배치 원칙 + 매핑 + 파일 간 정합성 | v1 작성 시 / 시각화 후 / 퇴고·변환 시 |
| `.claude/skills/naver-packaging.md` | 네이버 변환 패키징 — HTML 변환 + 이미지 리네이밍 + README + QA | X 게시 완료 후 네이버 변환 시 |
| `.claude/skills/schedule-briefing.md` | 스케줄 브리핑 — 마스터 vs 실제폴더 2-way 검증 + 리포트 출력 | "스케줄 알려줘" / 세션 시작 시 |
| `.claude/skills/schedule-sync.md` | 스케줄 동기화 — 마스터 테이블 1곳 갱신 + 시각화 재생성 | 아티클 상태 변경 시 / 불일치 발견 시 |
| `.claude/skills/news-fact-extraction.md` | 뉴스 팩트 추출 — 규칙 기반 자동 + Claude Code 수동 하이브리드 | "팩트 추출", "뉴스 정리", 시황 브리핑 데이터 준비 시 |
| `.claude/skills/ontology-analysis.md` | 온톨로지 분석 + 제1원칙 사고 — 팩트→그래프→통념분해→Gap→기회 | "온톨로지 분석", "제1원칙 분석", 심층 뉴스 분석 시 |
| `.claude/skills/article-shipping.md` | 아티클 마감 — WIP 제한 + 타임박스 + 게시 후 학습 루프 | 게시 대기 마무리 시 / 세션 시작 시 WIP 체크 |
| `.claude/skills/publish-review.md` | 게시 리뷰 — 8차원 스코어카드 + 인터랙티브 수정 + SHIP/REVISE/HOLD 판정 | "리뷰해줘", "게시 리뷰", v1/v2 완료 후 |
| `.claude/skills/morning-email.md` | 모닥 이메일 실행 (데이터 수집→검수→dry-run→발송) | "모닥 이메일", "이메일 보내줘" |
| `.claude/skills/sigma-analysis.md` | IV 시그마 분석 (장중/장외 분기, IV/HV20 폴백) | "시그마 분석", "IV 분석", 종목 변동성 확인 시 |
| `.claude/skills/signal-report.md` | 시그널 리포트 + 대시보드 Excel 생성 + 이상치 검수 | "시그널 리포트", "대시보드", 주간 리포트 시 |

> 스킬은 반복적인 작업 절차를 정의한 파일. 해당 작업 수행 시 반드시 읽고 절차를 따른다.
> 새 스킬 추가 시 이 테이블도 함께 업데이트할 것.

## 자동화 현황

### 시황 브리핑
- **SSOT**: `projects.yaml` → `x-bot` 항목 참조
- x-bot systemd 서비스가 오전 6시 / 오후 6시 (KST) 텔레그램 브리핑 전송
- cron `run_briefing.sh`가 모닥/이브닝 브리핑 파일 생성 (x-bot과 별개)

### cron (주식부자 관련)
| 시간 | 스크립트 | 비고 |
|------|----------|------|
| 매 정각 | `scripts/collect_and_classify.py` | 뉴스 수집 + 분류 |
| 매 정시+10분 | `scripts/update_geoinvest.py` | ⏸️ **보류** — 지정학 엔티티 추출 (Ollama) |
| 매 정각 | `scripts/update_stockinvest.py` | 테슬라 엔티티 추출 (Ollama) |
| 05:30 KST | `scripts/deep_analysis.py` | ⏸️ **보류** — 심층분석 → 이벤트 생성 + 엔티티 피드백 |
| 06:00 KST | `scripts/run_briefing.sh morning` | 모닥 브리핑 |
| 17:30 KST | `scripts/deep_analysis.py` | ⏸️ **보류** — 심층분석 → 이벤트 생성 + 엔티티 피드백 |
| 18:00 KST | `scripts/run_briefing.sh evening` | 이브닝 브리핑 |
| 04:00 KST | `scripts/review_entities.py` | 엔티티 리뷰/정제 (Phase 0~4) |

### 모닝 이메일
- `scripts/send_morning_email.py` — 수동 실행 (cron 미등록)

## Skill routing

When the user's request matches an available skill, ALWAYS invoke it using the Skill
tool as your FIRST action. Do NOT answer directly, do NOT use other tools first.
The skill has specialized workflows that produce better results than ad-hoc answers.

Key routing rules:
- Product ideas, "is this worth building", brainstorming → invoke office-hours
- Bugs, errors, "why is this broken", 500 errors → invoke investigate
- Ship, deploy, push, create PR → invoke ship
- QA, test the site, find bugs → invoke qa
- Code review, check my diff → invoke review
- Update docs after shipping → invoke document-release
- Weekly retro → invoke retro
- Design system, brand → invoke design-consultation
- Visual audit, design polish → invoke design-review
- Architecture review → invoke plan-eng-review
