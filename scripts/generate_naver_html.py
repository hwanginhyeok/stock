"""
generate_naver_html.py — 마크다운 → 네이버 블로그 HTML 변환기

네이버 SmartEditor ONE 대응:
  - 인라인 CSS only (외부 CSS/style 블록 제거됨)
  - 투자 분석 블로그 스타일 (나눔고딕, 좌측정렬, 본문 15px)

사용법:
  1. 변환:
     python scripts/generate_naver_html.py <markdown_file>

  2. 브라우저에서 HTML 열기 → Ctrl+A → Ctrl+C

  3. 네이버 블로그 에디터에 Ctrl+V (리치텍스트 붙여넣기)
     또는 F12 DevTools → Inspector → Edit as HTML로 직접 주입

Output:
    같은 디렉토리에 {stem}_naver.html 생성
"""

import re
import sys
from pathlib import Path


# ── 인라인 스타일 정의 ────────────────────────────────────────────────────────
# 네이버 투자 분석 블로그 벤치마크:
#   본문: 15px (se-fs-fs15), 시스템 폰트 (나눔고딕)
#   소제목: 19px bold (se-fs-fs19)
#   정렬: 좌측
#   구분선: 가는 실선 (line1)
S = {
    # ── 레이아웃 ──
    "wrap":  ("font-size:16px; line-height:2.0; color:#333; "
              "word-break:keep-all; text-align:left; "
              "font-family:'나눔고딕','Nanum Gothic',sans-serif; "
              "max-width:720px; margin:0 auto; padding:0 16px;"),
    # ── 헤딩 (3단계 위계: h1=26, h2=21, h3=19) ──
    "h1":    ("font-size:26px; font-weight:700; color:#222; "
              "margin:48px 0 20px; padding-bottom:12px; "
              "border-bottom:2px solid #333; line-height:1.6;"),
    "h2":    ("font-size:21px; font-weight:700; color:#222; "
              "margin:40px 0 16px; line-height:1.6;"),
    "h3":    ("font-size:19px; font-weight:700; color:#333; "
              "margin:32px 0 12px; line-height:1.6;"),
    "h4":    ("font-size:16px; font-weight:700; color:#444; "
              "margin:24px 0 10px; line-height:1.6;"),
    # ── 본문 ──
    "p":     "margin:0 0 20px; line-height:2.0;",
    "bq":    ("margin:24px 0; padding:16px 20px; "
              "background:#f7f8fa; border-left:3px solid #333; "
              "color:#444; font-size:19px; line-height:2.0; "
              "text-align:center;"),
    "hr":    "border:none; border-top:1px solid #ddd; margin:36px 0;",
    # ── 목록 ──
    "ul":    "margin:0 0 20px; padding-left:24px;",
    "ol":    "margin:0 0 20px; padding-left:24px;",
    "li":    "margin-bottom:10px; line-height:2.0;",
    # ── 테이블 ──
    "table": ("border-collapse:collapse; width:100%; "
              "margin:24px 0; font-size:15px;"),
    "th":    ("background:#f7f8fa; border:1px solid #e0e0e0; "
              "padding:10px 14px; text-align:left; "
              "font-weight:700; color:#222;"),
    "td":    "border:1px solid #e0e0e0; padding:9px 14px; color:#444;",
    "td_ev": ("border:1px solid #e0e0e0; padding:9px 14px; "
              "color:#444; background:#fafbfc;"),
    # ── 인라인 ──
    "code":  ("background:#f2f3f5; padding:2px 6px; border-radius:3px; "
              "font-family:monospace; font-size:14px; color:#c7254e;"),
    "pre":   ("background:#f7f8fa; border:1px solid #e0e0e0; "
              "border-radius:6px; padding:16px 20px; overflow-x:auto; "
              "font-family:monospace; font-size:14px; "
              "line-height:1.8; margin:24px 0; white-space:pre;"),
    "strong": "font-weight:700; color:#222;",
    "em":    "font-style:italic; color:#555;",
    # ── 면책조항/출처 ──
    "disc":  ("margin-top:40px; padding:14px 18px; "
              "background:#f9f9f9; border:1px solid #eee; "
              "border-radius:6px; font-size:13px; "
              "color:#888; line-height:1.7;"),
    # ── 이미지 플레이스홀더 ──
    "img_ph": ("margin:24px 0; padding:20px; text-align:center; "
               "background:#f0f0f0; border:1px dashed #ccc; "
               "border-radius:6px; color:#999; font-size:13px;"),
}


# ── 인라인 변환 ──────────────────────────────────────────────────────────────
def inline(text: str) -> str:
    """굵게, 기울임, 인라인코드, 링크 → HTML"""
    # 인라인 코드 (먼저 처리해서 내부 ** 등 보호)
    text = re.sub(
        r"`([^`]+)`",
        lambda m: f'<code style="{S["code"]}">{m.group(1)}</code>',
        text,
    )
    # 굵게
    text = re.sub(
        r"\*\*([^*\n]+)\*\*",
        lambda m: f'<strong style="{S["strong"]}">{m.group(1)}</strong>',
        text,
    )
    # 기울임 (단독 *)
    text = re.sub(
        r"(?<!\*)\*([^*\n]+)\*(?!\*)",
        lambda m: f'<em style="{S["em"]}">{m.group(1)}</em>',
        text,
    )
    # ~~취소선~~
    text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)
    return text


# ── 테이블 변환 ──────────────────────────────────────────────────────────────
def convert_table(table_lines: list[str]) -> str:
    rows = []
    for line in table_lines:
        cells = [c.strip() for c in line.strip().split("|")]
        cells = [c for c in cells if c != ""]
        if cells:
            rows.append(cells)

    # 구분선 행(---|---) 제거
    rows = [r for r in rows if not all(re.match(r"^[-: ]+$", c) for c in r)]
    if not rows:
        return ""

    headers = rows[0]
    data = rows[1:]

    th_html = "".join(f'<th style="{S["th"]}">{inline(c)}</th>' for c in headers)
    thead = f"<thead><tr>{th_html}</tr></thead>"

    tbody_rows = []
    for idx, row in enumerate(data):
        style = S["td_ev"] if idx % 2 == 1 else S["td"]
        td_html = "".join(f'<td style="{style}">{inline(c)}</td>' for c in row)
        tbody_rows.append(f"<tr>{td_html}</tr>")
    tbody = f"<tbody>{''.join(tbody_rows)}</tbody>"

    return f'<table style="{S["table"]}">{thead}{tbody}</table>'


# ── 이미지 플레이스홀더 감지 ─────────────────────────────────────────────────
def is_image_placeholder(text: str) -> bool:
    """📎 *[이미지: ...]* 패턴 감지"""
    return bool(re.match(r"^>\s*📎", text)) or bool(re.match(r"^📎", text))


# ── 메인 변환기 ──────────────────────────────────────────────────────────────

# 네이버 에디터는 margin을 일부 무시하므로 물리적 빈 줄(<p>&nbsp;</p>)이 가장 신뢰할 수 있는 간격 수단.
# 의미 단위 경계(h2/h3 앞, blockquote/table 뒤)에 자동 삽입한다.
SPACER = f'<p style="{S["p"]}">&nbsp;</p>'


def _add_spacer(out: list[str]) -> None:
    """이전 출력이 이미 스페이서가 아닌 경우에만 빈 줄 추가."""
    if out and "&nbsp;" not in out[-1]:
        out.append(SPACER)


def convert(md: str) -> str:
    lines = md.splitlines()
    out: list[str] = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()

        # ── 빈 줄 (연속 2줄 이상 → 의도적 시각 간격)
        if not line:
            blank_count = 0
            while i < len(lines) and not lines[i].strip():
                blank_count += 1
                i += 1
            if blank_count >= 2:
                for _ in range(blank_count - 1):
                    out.append(SPACER)
            continue

        # ── 헤딩
        if line.startswith("#### "):
            out.append(f'<h4 style="{S["h4"]}">{inline(line[5:])}</h4>')
            i += 1
            continue
        if line.startswith("### "):
            _add_spacer(out)
            out.append(f'<h3 style="{S["h3"]}">{inline(line[4:])}</h3>')
            i += 1
            continue
        # ── 면책조항 (## 면책조항 → disc 스타일 div)
        if line == "## 면책조항":
            _add_spacer(out)
            disc_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("#"):
                disc_lines.append(inline(lines[i].strip()))
                i += 1
            content = "<br>".join(disc_lines)
            out.append(f'<div style="{S["disc"]}">{content}</div>')
            continue

        if line.startswith("## "):
            _add_spacer(out)
            out.append(f'<h2 style="{S["h2"]}">{inline(line[3:])}</h2>')
            i += 1
            continue
        if line.startswith("# "):
            _add_spacer(out)
            out.append(f'<h1 style="{S["h1"]}">{inline(line[2:])}</h1>')
            i += 1
            continue

        # ── 구분선
        if re.match(r"^-{3,}$", line) or re.match(r"^\*{3,}$", line):
            _add_spacer(out)
            out.append(f'<hr style="{S["hr"]}">')
            i += 1
            continue

        # ── 펜스드 코드블록
        if line.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 닫는 ``` 스킵
            code_text = "\n".join(code_lines)
            out.append(f'<pre style="{S["pre"]}"><code>{code_text}</code></pre>')
            continue

        # ── 이미지 플레이스홀더 (📎 마커)
        if is_image_placeholder(line):
            # 이미지 설명 추출
            desc = re.sub(r"[>📎*\[\]]+", "", line).strip()
            out.append(
                f'<div style="{S["img_ph"]}">'
                f"📷 {desc}<br>"
                f'<span style="font-size:12px;">'
                f"(네이버 에디터에서 이미지를 직접 삽입해주세요)</span></div>"
            )
            i += 1
            continue

        # ── 블록쿼트
        if line.startswith("> "):
            _add_spacer(out)
            bq_lines = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                bq_text = lines[i].strip()[2:]
                # "상태:" 메타데이터 제거 (v2 blockquote에 포함된 작업 상태)
                if re.match(r"^\*{0,2}상태\*{0,2}\s*:", bq_text):
                    i += 1
                    continue
                bq_lines.append(inline(bq_text))
                i += 1
            if bq_lines:
                content = "<br>".join(bq_lines)
                out.append(f'<blockquote style="{S["bq"]}">{content}</blockquote>')
                _add_spacer(out)
            continue

        # ── 순서 없는 목록
        if re.match(r"^[-*] ", line):
            items = []
            while i < len(lines) and re.match(r"^[-*] ", lines[i].strip()):
                items.append(
                    f'<li style="{S["li"]}">{inline(lines[i].strip()[2:])}</li>'
                )
                i += 1
            out.append(f'<ul style="{S["ul"]}">{"".join(items)}</ul>')
            continue

        # ── 순서 있는 목록
        if re.match(r"^\d+\. ", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i].strip()):
                text = re.sub(r"^\d+\. ", "", lines[i].strip())
                items.append(f'<li style="{S["li"]}">{inline(text)}</li>')
                i += 1
            out.append(f'<ol style="{S["ol"]}">{"".join(items)}</ol>')
            continue

        # ── 테이블
        if line.startswith("|"):
            tbl_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl_lines.append(lines[i])
                i += 1
            out.append(convert_table(tbl_lines))
            _add_spacer(out)
            continue

        # ── 일반 문단
        out.append(f'<p style="{S["p"]}">{inline(line)}</p>')
        i += 1

    return "\n".join(out)


# ── HTML 래퍼 ────────────────────────────────────────────────────────────────
def wrap_html(body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<div style="{S["wrap"]}">
{body}
</div>
</body>
</html>"""


# ── 진입점 ────────────────────────────────────────────────────────────────────
def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python scripts/generate_naver_html.py <markdown_file>")
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        print(f"파일을 찾을 수 없습니다: {src}")
        sys.exit(1)

    md_text = src.read_text(encoding="utf-8")
    body = convert(md_text)
    html = wrap_html(body)

    out = src.parent / f"{src.stem}_naver.html"
    out.write_text(html, encoding="utf-8")

    size_kb = out.stat().st_size / 1024
    print(f"변환 완료: {out}  ({size_kb:.1f} KB)")
    print(f"\n사용법:")
    print(f"  1. 브라우저에서 HTML 열기 → Ctrl+A → Ctrl+C")
    print(f"  2. 네이버 블로그 에디터에 Ctrl+V")
    print(f"  3. 이미지는 에디터에서 직접 삽입")


if __name__ == "__main__":
    main()
