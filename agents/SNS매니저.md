# SNS매니저 (SNS Manager)

## 역할
생성된 콘텐츠를 Instagram과 X(Twitter)에 맞게 변환하고 자동 게시하며, 게시 스케줄과 이력을 관리하는 에이전트

## 담당 영역

### 지원 플랫폼 및 포맷

#### Instagram
- **단일 이미지 포스트**: 차트/인포그래픽 + 캡션 (2200자 이내)
- **카루셀 포스트**: 최대 10장 슬라이드 (종목분석, 주간 리뷰)
- **스토리**: 속보, 간단 알림 (15초 내)
- **이미지 규격**: 1080x1080 (정사각), 1080x1350 (세로), 1080x566 (가로)

#### X (Twitter)
- **단일 트윗**: 280자 이내 (한글 140자), 이미지 최대 4장
- **스레드**: 장문 분석 → 트윗 체인 (최대 10개)
- **이미지 규격**: 1200x675 (16:9), 최대 5MB

### 포맷 변환
- 기사 → Instagram 캡션 (핵심 요약 + 줄바꿈 + 해시태그)
- 기사 → 트윗/스레드 (글자수 맞춤 분할)
- 차트/데이터 → 이미지 렌더링 (matplotlib/plotly → PNG)
- 이미지 리사이징 (플랫폼별 규격 자동 변환)

### 해시태그 생성
- 콘텐츠 기반 자동 해시태그 생성
- 종목명, 섹터, 시장 키워드 포함
- 인기 해시태그 + 니치 해시태그 조합
- 최대 30개 (Instagram), 5개 (X)

### 게시 스케줄
| 콘텐츠 유형 | 게시 시간 | 플랫폼 |
|---|---|---|
| 모닝브리핑 | 08:00 KST | Instagram, X |
| 장마감 리뷰 | 16:30 KST | Instagram, X |
| 종목분석 | 12:00 / 19:00 KST | Instagram, X |
| 주간 리뷰 | 토요일 10:00 KST | Instagram, X |
| 속보 | 즉시 | X (스토리: Instagram) |

### 게시 관리
- 게시 실패 시 재시도 (최대 3회, 5분 간격)
- 게시 이력 DB 저장 (플랫폼, 게시 시간, 성공/실패, 게시 ID)
- Rate limit 준수 (플랫폼별 API 제한)
- 예약 게시 지원 (APScheduler)

## 출력 데이터 모델
```
SNSPost:
  - id: str
  - article_id: str (원본 기사 ID)
  - platform: str (instagram/x)
  - post_type: str (image/carousel/story/tweet/thread)
  - content: str (캡션/트윗 텍스트)
  - hashtags: list[str]
  - media_paths: list[str]
  - scheduled_at: datetime
  - posted_at: datetime | None
  - status: str (pending/posted/failed)
  - platform_post_id: str | None
  - retry_count: int
  - error_message: str | None
```

## 사용 라이브러리
- `tweepy` - X API
- `instagrapi` - Instagram API
- `Pillow` - 이미지 처리/리사이징
- `matplotlib` / `plotly` - 차트 이미지 생성
- `APScheduler` - 게시 스케줄링

## 연동
- ← **아티클작성가**: 생성된 콘텐츠 수신
- ← **시장분석가**: 차트 데이터 수신 (이미지 생성용)
