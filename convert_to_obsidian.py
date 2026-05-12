#!/usr/bin/env python3
"""
주식부자프로젝트 → Obsidian Vault 변환 스크립트
대상: md 파일만 (briefings, research, reports, articles, bio_series)
"""

import os
import re
import shutil
import json
from datetime import datetime
from pathlib import Path

# === CONFIG ===
SRC = Path("/home/gint_pcd/projects/주식부자프로젝트/data")
DST = Path("/home/gint_pcd/projects/주식부자프로젝트/stock-tycoon-vault")
ASSETS = DST / "00_Assets"

# Obsidian 플러그인 설치 대상
PLUGIN_SRC = Path("/home/gint_pcd/projects/HIH_2/HIH_Obsidian_Vault/.obsidian/plugins")

def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)

def clean_frontmatter(content: str) -> str:
    """기존 frontmatter 제거"""
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            return content[end+3:].strip()
    return content

def parse_briefing(filepath: Path) -> dict:
    """브리핑 파일에서 날짜, 타입 파싱"""
    name = filepath.stem  # e.g. "2026-03-23_morning"
    parts = name.split("_")
    date = parts[0]
    btype = parts[1] if len(parts) > 1 else "daily"
    return {"date": date, "type": btype}

def parse_article_dir(dirpath: Path) -> dict:
    """아티클 디렉토리에서 번호, 종목, 제목 파싱"""
    name = dirpath.name  # e.g. "001_TSLA_마스터플랜-20년의-논리"
    parts = name.split("_", 2)
    num = parts[0]
    ticker = parts[1] if len(parts) > 1 else "GENERAL"
    title = parts[2] if len(parts) > 2 else dirpath.name
    return {"num": num, "ticker": ticker, "title": title}

def copy_images(src_dir: Path, dst_dir: Path, prefix: str):
    """이미지 파일을 Assets에 복사하고 경로 매핑 반환"""
    mapping = {}
    if not src_dir.exists():
        return mapping
    
    img_exts = {'.png', '.jpg', '.jpeg', '.webp', '.avif', '.gif', '.svg'}
    for f in src_dir.iterdir():
        if f.suffix.lower() in img_exts and not f.name.endswith(':Zone.Identifier'):
            dst_name = f"{prefix}_{f.name}"
            shutil.copy2(f, ASSETS / dst_name)
            mapping[f.name] = dst_name
    return mapping

def fix_image_links(content: str, img_mapping: dict) -> str:
    """마크다운 이미지 링크를 Obsidian 경로로 수정"""
    for orig, new in img_mapping.items():
        content = content.replace(f"]({orig})", f"](../00_Assets/{new})")
        content = content.replace(f"![]({orig})", f"![](../00_Assets/{new})")
    return content

# ========================================
# STEP 1: Vault 초기 구조 생성
# ========================================
def init_vault():
    print("[1/7] Vault 초기 구조 생성...")
    folders = [
        "01_Briefings",
        "02_Research/Stocks/Tesla",
        "02_Research/Stocks/Palantir",
        "02_Research/Stocks/HIMS",
        "02_Research/Stocks/HOOD",
        "02_Research/Stocks/Healthcare_AI",
        "02_Research/Stocks/Screening",
        "02_Research/Crypto/Bitcoin",
        "02_Research/Crypto/Ethereum",
        "02_Research/Crypto/Ecosystem",
        "02_Research/Korea/Semiconductor",
        "02_Research/Korea/Auto",
        "02_Research/Geopolitics",
        "02_Research/Articles",
        "03_Published",
        "04_Reports",
        "05_Bio_Series/Easy",
        "05_Bio_Series/Medium",
        "05_Bio_Series/Hard",
        "00_Assets",
        "00_Templates",
    ]
    for f in folders:
        ensure_dir(DST / f)

# ========================================
# STEP 2: Briefings 변환
# ========================================
def convert_briefings():
    print("[2/7] Briefings 변환...")
    src = SRC / "briefings"
    dst = DST / "01_Briefings"
    count = 0
    
    for f in sorted(src.glob("*.md")):
        info = parse_briefing(f)
        content = f.read_text(encoding='utf-8')
        
        # frontmatter 생성
        fm = f"""---
type: briefing
date: {info['date']}
briefing_type: {info['type']}
tags:
  - briefing
  - {info['type']}
  - daily
created: {info['date']}T09:00:00
---
"""
        
        # 첫 줄이 # 으로 시작하면 제목으로 유지
        clean = clean_frontmatter(content)
        
        out = dst / f"{info['date']}_{info['type']}.md"
        out.write_text(fm + clean, encoding='utf-8')
        count += 1
    
    print(f"  → {count} 브리핑 변환 완료")

# ========================================
# STEP 3: Research 변환
# ========================================
def convert_research():
    print("[3/7] Research 변환...")
    count = 0
    
    # --- Tesla ---
    tesla_src = SRC / "research/stocks/tesla"
    tesla_dst = DST / "02_Research/Stocks/Tesla"
    count += convert_stock_dir(tesla_src, tesla_dst, "TSLA")
    
    # --- Palantir ---
    pltr_src = SRC / "research/stocks/palantir"
    pltr_dst = DST / "02_Research/Stocks/Palantir"
    count += convert_stock_dir(pltr_src, pltr_dst, "PLTR")
    
    # --- HIMS ---
    hims_src = SRC / "research/stocks/hims"
    hims_dst = DST / "02_Research/Stocks/HIMS"
    count += convert_stock_dir(hims_src, hims_dst, "HIMS")
    
    # --- HOOD ---
    hood_src = SRC / "research/stocks/hood"
    hood_dst = DST / "02_Research/Stocks/HOOD"
    count += convert_stock_dir(hood_src, hood_dst, "HOOD")
    
    # --- Healthcare AI ---
    hcai_src = SRC / "research/stocks/healthcare-ai"
    hcai_dst = DST / "02_Research/Stocks/Healthcare_AI"
    count += convert_stock_dir(hcai_src, hcai_dst, "HCAI")
    
    # --- Screening ---
    scr_src = SRC / "research/stocks/screening"
    scr_dst = DST / "02_Research/Stocks/Screening"
    count += convert_stock_dir(scr_src, scr_dst, "SCREEN")
    
    # --- Crypto: Bitcoin ---
    btc_src = SRC / "research/crypto/bitcoin"
    btc_dst = DST / "02_Research/Crypto/Bitcoin"
    count += convert_crypto_dir(btc_src, btc_dst, "BTC")
    
    # --- Crypto: Ethereum ---
    eth_src = SRC / "research/crypto/ethereum"
    eth_dst = DST / "02_Research/Crypto/Ethereum"
    count += convert_crypto_dir(eth_src, eth_dst, "ETH")
    
    # --- Crypto: Ecosystem ---
    eco_src = SRC / "research/crypto"
    eco_dst = DST / "02_Research/Crypto/Ecosystem"
    count += convert_generic_research(eco_src, eco_dst, "CRYPTO", ["bitcoin", "ethereum"])
    
    # --- Korea: Semiconductor ---
    krsemi_src = SRC / "research/korea/sectors/semiconductor"
    krsemi_dst = DST / "02_Research/Korea/Semiconductor"
    count += convert_generic_research(krsemi_src, krsemi_dst, "KR_SEMI")
    
    # --- Korea: Auto ---
    krauto_src = SRC / "research/korea/sectors/auto"
    krauto_dst = DST / "02_Research/Korea/Auto"
    count += convert_generic_research(krauto_src, krauto_dst, "KR_AUTO")
    
    # --- Geopolitics ---
    geo_src = SRC / "research/geopolitics"
    geo_dst = DST / "02_Research/Geopolitics"
    count += convert_geopolitics_dir(geo_src, geo_dst)
    
    # --- Research Articles (multi-stock) ---
    ra_src = SRC / "research/articles"
    ra_dst = DST / "02_Research/Articles"
    count += convert_research_articles(ra_src, ra_dst)
    
    # --- Ontology Foundation ---
    onto_file = SRC / "research/ontology_foundation.md"
    if onto_file.exists():
        content = onto_file.read_text(encoding='utf-8')
        fm = """---
type: research
category: ontology
tags:
  - ontology
  - foundation
  - framework
created: 2026-03-01
---
"""
        (DST / "02_Research" / "온톨로지_기반_체계.md").write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
    
    print(f"  → {count} 리서치 파일 변환 완료")

def convert_stock_dir(src: Path, dst: Path, ticker: str) -> int:
    """개별 종목 리서치 디렉토리 변환"""
    count = 0
    if not src.exists():
        return count
    
    for md in sorted(src.rglob("*.md")):
        if md.name == "README.md":
            # README는 인덱스로 변환
            content = md.read_text(encoding='utf-8')
            fm = f"""---
type: research_index
ticker: {ticker}
tags:
  - research
  - {ticker}
  - index
---
"""
            out = dst / f"{ticker}_리서치_인덱스.md"
            out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
            count += 1
        elif md.stat().st_size > 0:
            rel = md.relative_to(src)
            subcategory = rel.parts[0] if len(rel.parts) > 1 else "general"
            
            content = md.read_text(encoding='utf-8')
            stem = md.stem
            
            # thesis 분류
            tags = ["research", ticker]
            if "bull" in stem:
                tags.append("bull_case")
            elif "bear" in stem:
                tags.append("bear_case")
            elif "fundamentals" in str(rel):
                tags.append("fundamentals")
            elif "thesis" in str(rel):
                tags.append("thesis")
            elif "earnings" in str(rel):
                tags.append("earnings")
            elif "financials" in str(rel):
                tags.append("financials")
            elif "timeline" in stem:
                tags.append("timeline")
            elif "semiconductor" in stem or "chip" in stem or "trm" in stem:
                tags.append("semiconductor")
            
            tags_str = "\n  - ".join(tags)
            fm = f"""---
type: research
ticker: {ticker}
subcategory: {subcategory}
tags:
  - {tags_str}
---
"""
            out_name = f"{ticker}_{subcategory}_{stem}.md"
            out = dst / out_name
            out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
            count += 1
    
    return count

def convert_crypto_dir(src: Path, dst: Path, ticker: str) -> int:
    """크립토 리서치 디렉토리 변환"""
    count = 0
    if not src.exists():
        return count
    
    for md in sorted(src.rglob("*.md")):
        if md.stat().st_size == 0:
            continue
        
        rel = md.relative_to(src)
        subcategory = rel.parts[0] if len(rel.parts) > 1 else "general"
        stem = md.stem
        
        tags = ["research", "crypto", ticker.lower()]
        if "bull" in stem:
            tags.append("bull_case")
        elif "bear" in stem:
            tags.append("bear_case")
        elif "fundamentals" in str(rel):
            tags.append("fundamentals")
        elif "on_chain" in stem:
            tags.append("on_chain")
        elif "adoption" in stem:
            tags.append("adoption")
        elif "ecosystem" in stem:
            tags.append("ecosystem")
        elif "roadmap" in stem:
            tags.append("roadmap")
        
        tags_str = "\n  - ".join(tags)
        fm = f"""---
type: research
ticker: {ticker}
subcategory: {subcategory}
tags:
  - {tags_str}
---
"""
        content = md.read_text(encoding='utf-8')
        out = dst / f"{ticker}_{subcategory}_{stem}.md"
        out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
    
    return count

def convert_generic_research(src: Path, dst: Path, cat_prefix: str, exclude_dirs=None) -> int:
    """일반 리서치 디렉토리 변환"""
    count = 0
    if not src.exists():
        return count
    if exclude_dirs is None:
        exclude_dirs = []
    
    for md in sorted(src.rglob("*.md")):
        if md.stat().st_size == 0:
            continue
        
        # exclude 하위 디렉토리
        rel = md.relative_to(src)
        if any(ex in rel.parts for ex in exclude_dirs):
            continue
        
        stem = md.stem
        tags = ["research", cat_prefix.lower()]
        
        # 태그 추론
        if "hbm" in stem.lower():
            tags.append("hbm")
        elif "semiconductor" in stem.lower() or "반도체" in stem:
            tags.append("semiconductor")
        elif "fab" in stem.lower() or "팹" in stem:
            tags.append("fab")
        elif "circle" in stem.lower() or "coinbase" in stem.lower():
            tags.append("coinbase")
        elif "bmnr" in stem.lower() or "bitmine" in stem.lower():
            tags.append("mining")
        elif "hyundai" in stem.lower() or "현대" in stem:
            tags.append("hyundai")
        elif "dr_am" in stem.lower():
            tags.append("dram")
        elif "coin" in stem.lower() and "ecosystem" not in str(rel).lower():
            tags.append("coinbase")
        
        tags_str = "\n  - ".join(tags)
        fm = f"""---
type: research
category: {cat_prefix}
tags:
  - {tags_str}
---
"""
        content = md.read_text(encoding='utf-8')
        out = dst / f"{stem}.md"
        out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
    
    return count

def convert_geopolitics_dir(src: Path, dst: Path) -> int:
    """지정학 리서치 변환"""
    count = 0
    if not src.exists():
        return count
    
    # iran_conflict만 있음
    for md in sorted(src.rglob("*.md")):
        if md.stat().st_size == 0:
            continue
        if md.name == "README.md":
            continue
        
        rel = md.relative_to(src)
        stem = md.stem
        
        tags = ["research", "geopolitics", "iran"]
        if "timeline" in stem:
            tags.append("timeline")
        elif "economic" in stem:
            tags.append("economic_impact")
        elif "nuclear" in stem:
            tags.append("nuclear")
        elif "proxy" in stem:
            tags.append("proxy_war")
        elif "ontology" in stem:
            tags.append("ontology")
        
        tags_str = "\n  - ".join(tags)
        fm = f"""---
type: research
category: geopolitics
region: iran
tags:
  - {tags_str}
---
"""
        content = md.read_text(encoding='utf-8')
        out = dst / f"iran_{stem}.md"
        out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
    
    return count

def convert_research_articles(src: Path, dst: Path) -> int:
    """멀티 종목 리서치 아티클 변환"""
    count = 0
    if not src.exists():
        return count
    
    for art_dir in sorted(src.iterdir()):
        if not art_dir.is_dir():
            continue
        
        info = parse_article_dir(art_dir)
        
        for md in sorted(art_dir.rglob("*.md")):
            if md.stat().st_size == 0:
                continue
            
            rel = md.relative_to(art_dir)
            subfolder = rel.parts[0] if len(rel.parts) > 1 else ""
            stem = md.stem
            
            # draft/raw/verified 구분
            if "verified" in str(rel):
                sub = "verified"
            elif "raw" in str(rel):
                sub = "raw"
            elif "drafts" in str(rel):
                sub = "draft"
            else:
                sub = "general"
            
            tags = ["research", "article", info['ticker'].lower()]
            if "thesis" in stem:
                tags.append("thesis")
            elif "thread" in stem:
                tags.append("x_thread")
            
            tags_str = "\n  - ".join(tags)
            fm = f"""---
type: research
category: article
article_num: {info['num']}
ticker: {info['ticker']}
title: "{info['title']}"
subcategory: {sub}
tags:
  - {tags_str}
---
"""
            content = md.read_text(encoding='utf-8')
            out_name = f"{info['num']}_{info['ticker']}_{stem}.md"
            out = dst / out_name
            out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
            count += 1
    
    return count

# ========================================
# STEP 4: Published Articles 변환
# ========================================
def convert_published():
    print("[4/7] Published Articles 변환...")
    src = SRC / "articles/published"
    dst = DST / "03_Published"
    count = 0
    
    if not src.exists():
        print("  → published 디렉토리 없음, 스킵")
        return
    
    for art_dir in sorted(src.iterdir()):
        if not art_dir.is_dir():
            continue
        
        info = parse_article_dir(art_dir)
        
        # 이미지 복사
        img_dirs = [art_dir / "images", art_dir / "visuals", art_dir / "naver"]
        img_mapping = {}
        for img_dir in img_dirs:
            if img_dir.exists():
                prefix = f"{info['num']}_{info['ticker']}"
                mapping = copy_images(img_dir, ASSETS, prefix)
                img_mapping.update(mapping)
        
        # 최종본 아티클 찾기 (x_publish > v2 > v1 > 기타)
        publish_file = None
        candidates = list(art_dir.glob("*_x_publish.md"))
        if not candidates:
            candidates = list(art_dir.glob("*_v2.md"))
        if not candidates:
            candidates = list(art_dir.glob("*_v1.md"))
        if not candidates:
            candidates = list(art_dir.glob("*.md"))
            candidates = [c for c in candidates if "sources" not in c.name.lower() and "x_image" not in c.name.lower()]
        
        if not candidates:
            continue
        
        publish_file = candidates[0]
        content = publish_file.read_text(encoding='utf-8')
        content = fix_image_links(content, img_mapping)
        
        # sources.md도 있으면 별도 파일로
        sources_files = [f for f in art_dir.glob("*.md") if "sources" in f.name.lower()]
        
        title_clean = info['title'].replace("/", "-")
        tags = ["published", "article", info['ticker'].lower()]
        
        # 카테고리 태그
        if info['ticker'] == "KR":
            tags.append("korea")
        elif info['ticker'] in ("TSLA", "PLTR"):
            tags.append("us_stock")
        elif info['ticker'] in ("BTC", "ETH", "COIN", "HOOD"):
            tags.append("crypto")
        elif info['ticker'] == "HIMS":
            tags.append("healthcare")
        elif info['ticker'] == "GEOPO":
            tags.append("geopolitics")
        
        tags_str = "\n  - ".join(tags)
        fm = f"""---
type: published
article_num: {info['num']}
ticker: {info['ticker']}
title: "{info['title']}"
tags:
  - {tags_str}
status: published
---
"""
        
        out_name = f"{info['num']}_{info['ticker']}_{title_clean}.md"
        out = dst / out_name
        out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
        
        # Sources 파일도 변환
        for sf in sources_files:
            scontent = sf.read_text(encoding='utf-8')
            sfm = f"""---
type: sources
article_num: {info['num']}
ticker: {info['ticker']}
tags:
  - sources
  - {info['ticker'].lower()}
---
"""
            (dst / f"{info['num']}_{info['ticker']}_{title_clean}_sources.md").write_text(
                sfm + clean_frontmatter(scontent), encoding='utf-8')
            count += 1
    
    print(f"  → {count} 퍼블리시 아티클 변환 완료")

# ========================================
# STEP 5: Reports 변환
# ========================================
def convert_reports():
    print("[5/7] Reports (Entity Reviews) 변환...")
    src = SRC / "reports"
    dst = DST / "04_Reports"
    count = 0
    
    for f in sorted(src.glob("*.md")):
        if f.stat().st_size == 0:
            continue
        
        # 파일명에서 날짜 파싱: entity_review_20260404_160208.md
        name = f.stem
        match = re.search(r'(\d{8})', name)
        date = match.group(1) if match else "unknown"
        
        content = f.read_text(encoding='utf-8')
        
        # 내용에서 종목 티커 추론
        tickers_found = set()
        for ticker in ["TSLA", "PLTR", "NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", 
                       "BTC", "ETH", "COIN", "HOOD", "HIMS", "AVGO", "TSM", "JPM"]:
            if ticker in content:
                tickers_found.add(ticker)
        
        tags = ["report", "entity_review"]
        tags.extend([t.lower() for t in tickers_found])
        tags_str = "\n  - ".join(tags)
        
        fm = f"""---
type: report
report_type: entity_review
date: {date}
tickers: [{', '.join(tickers_found) if tickers_found else 'N/A'}]
tags:
  - {tags_str}
---
"""
        
        out = dst / f"entity_review_{date}.md"
        out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
        count += 1
    
    print(f"  → {count} 리포트 변환 완료")

# ========================================
# STEP 6: Bio Series 변환
# ========================================
def convert_bio_series():
    print("[6/7] Bio Series 변환...")
    src = SRC / "articles/bio_series"
    count = 0
    
    if not src.exists():
        print("  → bio_series 없음, 스킵")
        return
    
    difficulty_map = {"easy": "쉬움", "medium": "보통", "hard": "어려움"}
    
    for diff_dir in sorted(src.iterdir()):
        if not diff_dir.is_dir():
            continue
        
        difficulty = diff_dir.name  # easy, medium, hard
        dst = DST / f"05_Bio_Series/{difficulty.capitalize()}"
        
        for md in sorted(diff_dir.glob("*.md")):
            if md.stat().st_size == 0:
                continue
            
            stem = md.stem  # e.g. "01_hormone"
            num = stem.split("_")[0]
            topic = stem.split("_", 1)[1] if "_" in stem else stem
            
            # 한국어 주제명 매핑
            topic_names = {
                "hormone": "호르몬 치료", "targeted": "표적 치료", "immune": "면역 치료",
                "gene": "유전자 치료", "rna": "RNA 치료", "radio": "방사선 치료",
                "microbiome": "마이크로바이옴", "neurotech": "신경 기술",
                "regen": "재생 의학", "synbio": "합성 생물학", "epigenetics": "후성유전학",
                "digital": "디지털 헬스", "longevity": "수명 연장", "metabolomics": "대사체학",
                "ai": "AI 의료", "delivery": "약물 전달"
            }
            topic_kr = topic_names.get(topic, topic)
            
            content = md.read_text(encoding='utf-8')
            
            fm = f"""---
type: bio_article
series: bio_series
difficulty: {difficulty}
topic_en: {topic}
topic_kr: "{topic_kr}"
num: {num}
tags:
  - bio
  - biotech
  - {topic}
  - {difficulty}
  - 바이오시리즈
---
"""
            out = dst / f"{num}_{topic}.md"
            out.write_text(fm + clean_frontmatter(content), encoding='utf-8')
            count += 1
    
    print(f"  → {count} 바이오 시리즈 변환 완료")

# ========================================
# STEP 7: Home.md + Templates + Plugins
# ========================================
def create_home():
    print("[7/7] Home.md, Templates, Plugins 생성...")
    
    # --- Home.md ---
    home = """---
type: home
---

# 주식부자프로젝트 Vault

> 테슬라 투자 인텔리전스 — 리서치 + 트레이딩 + 콘텐츠

## 빠른 접근

| 항목 | 설명 |
|------|------|
| [[01_Briefings]] | 데일리 모닝/이브닝 브리핑 |
| [[02_Research/Stocks/Tesla/TSLA_리서치_인덱스]] | 테슬라 심층 리서치 |
| [[02_Research/Stocks/Palantir/PLTR_리서치_인덱스]] | 팔란티어 리서치 |
| [[03_Published]] | 발행 완료 아티클 모음 |
| [[04_Reports]] | 엔티티 리뷰 리포트 |
| [[05_Bio_Series]] | 바이오테크 시리즈 (3난이도) |

---

## 최근 브리핑 (최근 7일)

```dataview
TABLE briefing_type AS "타입"
FROM "01_Briefings"
WHERE type = "briefing"
SORT date DESC
LIMIT 7
```

## 퍼블리시 아티클

```dataview
TABLE ticker AS "종목", status AS "상태"
FROM "03_Published"
WHERE type = "published"
SORT article_num DESC
```

## 종목별 리서치 현황

```dataview
TABLE length(rows) AS "문서 수"
FROM "02_Research"
WHERE type = "research"
GROUP BY ticker
SORT rows.file.link DESC
```

## 카테고리별 문서 수

```dataview
TABLE length(rows) AS "문서 수"
FROM ""
WHERE type
GROUP BY type
SORT length(rows) DESC
```

## 바이오 시리즈

```dataview
TABLE difficulty AS "난이도", topic_kr AS "주제"
FROM "05_Bio_Series"
WHERE type = "bio_article"
SORT num ASC
```

## 엔티티 리뷰

```dataview
TABLE tickers AS "관련 종목"
FROM "04_Reports"
WHERE type = "report"
SORT date DESC
LIMIT 10
```
"""
    (DST / "Home.md").write_text(home, encoding='utf-8')
    
    # --- Research 템플릿 ---
    tmpl = """---
type: {{type}}
ticker: {{ticker}}
tags:
  - research
  - {{ticker}}
---
# {{title}}

## 핵심 요약


## 상세 분석


## 데이터 포인트


## 인사이트


## 출처

"""
    (DST / "00_Templates" / "Research_Template.md").write_text(tmpl, encoding='utf-8')
    
    # --- Briefing 템플릿 ---
    btmpl = """---
type: briefing
date: {{date}}
briefing_type: {{morning/evening}}
tags:
  - briefing
  - daily
---

## 시장 요약


## 핵심 이슈


## 주요 지표


## 포지션/전략


"""
    (DST / "00_Templates" / "Briefing_Template.md").write_text(btmpl, encoding='utf-8')
    
    # --- Obsidian 기본 설정 ---
    obsidian_dir = DST / ".obsidian"
    ensure_dir(obsidian_dir)
    
    app_json = {
        "attachmentFolderPath": "00_Assets",
        "newFileLocation": "folder",
        "newFileLocationPath": "02_Research",
        "readableLineLength": True,
        "defaultViewMode": "source",
        "showLineNumber": True
    }
    (obsidian_dir / "app.json").write_text(json.dumps(app_json, indent=2, ensure_ascii=False), encoding='utf-8')
    
    # --- 플러그인 복사 ---
    if PLUGIN_SRC.exists():
        plugins_dst = obsidian_dir / "plugins"
        for plugin in ["dataview", "templater-obsidian"]:
            plugin_src = PLUGIN_SRC / plugin
            plugin_dst = plugins_dst / plugin
            if plugin_src.exists() and not plugin_dst.exists():
                shutil.copytree(plugin_src, plugin_dst)
                print(f"  → {plugin} 플러그인 복사 완료")
        
        # community-plugins.json
        cp_json = {"dataview": "", "templater-obsidian": ""}
        (obsidian_dir / "community-plugins.json").write_text(json.dumps(cp_json, indent=2), encoding='utf-8')
    else:
        print("  ⚠ 플러그인 소스 없음 — 수동 설치 필요 (Dataview + Templater)")
    
    print("  → Home.md, Templates 생성 완료")

# ========================================
# MAIN
# ========================================
def main():
    print("=" * 50)
    print("주식부자프로젝트 → Obsidian Vault 변환")
    print("=" * 50)
    
    # 기존 vault 있으면 삭제 후 재생성
    if DST.exists():
        print(f"\n기존 vault 삭제: {DST}")
        shutil.rmtree(DST)
    
    init_vault()
    convert_briefings()
    convert_research()
    convert_published()
    convert_reports()
    convert_bio_series()
    create_home()
    
    # 최종 통계
    total_md = len(list(DST.rglob("*.md")))
    total_img = len(list(ASSETS.glob("*")))
    
    print("\n" + "=" * 50)
    print(f"변환 완료!")
    print(f"  Vault 경로: {DST}")
    print(f"  MD 파일: {total_md}개")
    print(f"  이미지: {total_img}개")
    print("=" * 50)

if __name__ == "__main__":
    main()
