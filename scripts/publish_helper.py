#!/usr/bin/env python3
"""X Notes 게시 헬퍼 — 클립보드 복사 + 이미지 체크리스트 + 예약 큐

Usage:
    python scripts/publish_helper.py prepare 012     # 클립보드 복사 + 브라우저 + 체크리스트
    python scripts/publish_helper.py queue 012 --date "2026-04-07 09:00"
    python scripts/publish_helper.py status
    python scripts/publish_helper.py done 012
    python scripts/publish_helper.py run-scheduled   # cron/Task Scheduler용
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
ARTICLES_ROOT = REPO_ROOT / "data" / "articles"
QUEUE_FILE = REPO_ROOT / "data" / "publish_queue.json"
POWERSHELL = Path("/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
CMD_EXE = Path("/mnt/c/Windows/System32/cmd.exe")

X_NOTES_URL = "https://x.com/compose/articles"


# ── 아티클 탐색 ─────────────────────────────────────────────────────────────

def find_article_dir(article_id: str) -> Path:
    """아티클 폴더 탐색. 우선순위: data/articles/ → data/articles/published/"""
    for base in [ARTICLES_ROOT, ARTICLES_ROOT / "published"]:
        if not base.exists():
            continue
        matches = [d for d in base.iterdir()
                   if d.is_dir() and d.name.startswith(article_id + "_")]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            print(f"[오류] 중복 매칭: {[m.name for m in matches]}", file=sys.stderr)
            sys.exit(1)
    print(f"[오류] 아티클 폴더 없음: {article_id}", file=sys.stderr)
    sys.exit(1)


def find_x_publish(article_dir: Path) -> Path:
    """x_publish.md 탐색. 우선순위: 루트 → drafts/ → published/"""
    for p in [
        article_dir / "x_publish.md",
        article_dir / "drafts" / "x_publish.md",
        article_dir / "published" / "x_publish.md",
    ]:
        if p.exists():
            return p
    print(f"[오류] x_publish.md 없음: {article_dir}", file=sys.stderr)
    sys.exit(1)


def find_image_guide(article_dir: Path) -> Path | None:
    """X_IMAGE_GUIDE.md 탐색. 없으면 None."""
    for p in [
        article_dir / "X_IMAGE_GUIDE.md",
        article_dir / "drafts" / "X_IMAGE_GUIDE.md",
    ]:
        if p.exists():
            return p
    return None


# ── 파싱 ────────────────────────────────────────────────────────────────────

def parse_image_guide(guide_path: Path) -> list[dict]:
    """이미지 삽입 순서 테이블 파싱."""
    lines = guide_path.read_text(encoding="utf-8").splitlines()
    in_table = False
    images = []
    for line in lines:
        if "이미지 삽입 순서" in line:
            in_table = True
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            if images:   # 테이블 끝
                break
            continue
        if re.match(r"\|[-\s|]+\|", line):  # 구분선
            continue
        cols = [c.strip().strip("`") for c in line.split("|")[1:-1]]
        if len(cols) < 3 or "번호" in cols[0]:   # 헤더
            continue
        # 소스 파일명에서 "(CC BY 2.0)" 같은 주석 제거
        file_raw = re.sub(r"\s*\(.*?\)\s*", "", cols[1]).strip().strip("`")
        images.append({"file": file_raw, "location": cols[2]})
    return images


def extract_intro_tweet(guide_path: Path) -> str | None:
    """X_IMAGE_GUIDE.md 의 소개 트윗 섹션 추출."""
    text = guide_path.read_text(encoding="utf-8")
    m = re.search(r"## 소개 트윗.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if not m:
        return None
    # blockquote(>) 기호 제거하고 트윗 텍스트만 추출
    lines = [l.lstrip("> ").rstrip() for l in m.group(1).strip().splitlines()]
    return "\n".join(lines).strip() or None


# ── WSL2 클립보드 / 브라우저 ─────────────────────────────────────────────────

def copy_to_clipboard(text: str) -> bool:
    """WSL2: clip.exe + utf-16-le 인코딩 (한글 정상 동작 확인됨)."""
    try:
        subprocess.run(
            [str(Path("/mnt/c/Windows/System32/clip.exe"))],
            input=text.encode("utf-16-le"),
            check=True
        )
        return True
    except Exception as e:
        print(f"[경고] 클립보드 복사 실패: {e}", file=sys.stderr)
        return False


def open_browser(url: str) -> bool:
    """WSL2: explorer.exe 로 Windows 브라우저 오픈 (UNC 경로 오류 없음)."""
    try:
        explorer = Path("/mnt/c/Windows/explorer.exe")
        subprocess.run([str(explorer), url], check=False,
                       stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"[경고] 브라우저 오픈 실패: {e}", file=sys.stderr)
        return False


# ── 커맨드: prepare ──────────────────────────────────────────────────────────

def cmd_prepare(article_id: str):
    article_dir = find_article_dir(article_id)
    x_publish = find_x_publish(article_dir)
    image_guide = find_image_guide(article_dir)

    content = x_publish.read_text(encoding="utf-8")
    char_count = len(content)

    print()
    print("─" * 50)
    print(f"  📁  {article_dir.name}")
    print("─" * 50)

    # 1단계: 본문 클립보드 복사
    ok = copy_to_clipboard(content)
    status = "✅ 클립보드 복사 완료" if ok else "⚠️  클립보드 복사 실패 — 수동으로 복사하세요"
    print(f"  📋  {status} ({char_count:,}자)")

    # 2단계: 브라우저 오픈
    ok = open_browser(X_NOTES_URL)
    print(f"  🌐  {'X Notes 창 열림' if ok else '브라우저 오픈 실패 — 수동으로 여세요'}")
    print(f"       → Write 버튼 클릭 → Ctrl+V")

    # 3단계: 이미지 체크리스트
    if image_guide:
        images = parse_image_guide(image_guide)
        if images:
            print()
            print("  📎  이미지 삽입 순서:")
            nums = ["1️⃣ ", "2️⃣ ", "3️⃣ ", "4️⃣ ", "5️⃣ "]
            for i, img in enumerate(images):
                num = nums[i] if i < len(nums) else f"{i+1}. "
                abs_path = article_dir / img["file"]
                print(f"       {num} {img['file']}")
                print(f"           위치: {img['location']}")
                print(f"           경로: {abs_path}")
        else:
            print("  📎  이미지 없음")
    else:
        print("  📎  X_IMAGE_GUIDE.md 없음 — 이미지 체크리스트 건너뜀")

    # 4단계: 소개 트윗
    intro_tweet = None
    if image_guide:
        intro_tweet = extract_intro_tweet(image_guide)

    print()
    print("─" * 50)
    if intro_tweet:
        try:
            input("  [Enter] 소개 트윗 클립보드 복사 > ")
            copy_to_clipboard(intro_tweet)
            print("  📋  소개 트윗 클립보드 복사 완료")
        except EOFError:
            pass
    else:
        print("  ℹ️   소개 트윗 없음 — 완료")
    print("─" * 50)
    print()


# ── 커맨드: queue ────────────────────────────────────────────────────────────

def load_queue() -> list[dict]:
    if QUEUE_FILE.exists():
        return json.loads(QUEUE_FILE.read_text(encoding="utf-8"))
    return []


def save_queue(queue: list[dict]):
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_FILE.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_queue(article_id: str, date_str: str):
    article_dir = find_article_dir(article_id)
    try:
        scheduled_at = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print(f"[오류] 날짜 형식: YYYY-MM-DD HH:MM (예: 2026-04-07 09:00)", file=sys.stderr)
        sys.exit(1)

    queue = load_queue()
    next_qid = max((q["qid"] for q in queue), default=0) + 1
    queue.append({
        "qid": next_qid,
        "article_id": article_id,
        "folder": article_dir.name,
        "scheduled_at": scheduled_at.isoformat(),
        "status": "PENDING"
    })
    save_queue(queue)
    print(f"✅  예약 등록 완료")
    print(f"   QID: {next_qid} | {article_dir.name}")
    print(f"   예약: {scheduled_at.strftime('%Y-%m-%d %H:%M')}")


# ── 커맨드: status ───────────────────────────────────────────────────────────

def cmd_status():
    queue = load_queue()
    if not queue:
        print("  큐가 비어 있습니다.")
        return

    print()
    print(f"{'QID':>4}  {'아티클ID':<8}  {'예약시간':<20}  {'상태':<10}  폴더")
    print("─" * 80)
    for q in queue:
        dt = datetime.fromisoformat(q["scheduled_at"]).strftime("%Y-%m-%d %H:%M")
        print(f"{q['qid']:>4}  {q['article_id']:<8}  {dt:<20}  {q['status']:<10}  {q['folder']}")
    print()


# ── 커맨드: done ─────────────────────────────────────────────────────────────

def cmd_done(article_id: str):
    queue = load_queue()
    updated = False
    for q in queue:
        if q["article_id"] == article_id and q["status"] != "DONE":
            q["status"] = "DONE"
            updated = True
            print(f"✅  QID {q['qid']} → DONE")
    if not updated:
        print(f"[경고] article_id={article_id} 인 PENDING/NOTIFIED 항목 없음")
    save_queue(queue)


# ── 커맨드: publish (게시 완료 → published/ 이동) ───────────────────────────

def cmd_publish(article_id: str):
    article_dir = find_article_dir(article_id)

    # 이미 published/ 안에 있으면 스킵
    if "published" in article_dir.parts:
        print(f"  이미 published/ 에 있습니다: {article_dir.name}")
        return

    dest = ARTICLES_ROOT / "published" / article_dir.name
    if dest.exists():
        print(f"[오류] 이미 존재: {dest}", file=sys.stderr)
        sys.exit(1)

    article_dir.rename(dest)
    print(f"✅  게시 완료 이동")
    print(f"    {article_dir} → {dest}")

    # 큐에서 DONE 처리
    queue = load_queue()
    for q in queue:
        if q["article_id"] == article_id and q["status"] != "DONE":
            q["status"] = "DONE"
    save_queue(queue)


# ── 커맨드: run-scheduled ────────────────────────────────────────────────────

def cmd_run_scheduled():
    queue = load_queue()
    now = datetime.now()
    triggered = False
    for q in queue:
        if q["status"] != "PENDING":
            continue
        scheduled = datetime.fromisoformat(q["scheduled_at"])
        if scheduled <= now:
            print(f"[{now.strftime('%H:%M')}] 예약 도달: QID {q['qid']} ({q['folder']})")
            cmd_prepare(q["article_id"])
            q["status"] = "NOTIFIED"
            triggered = True
    if triggered:
        save_queue(queue)
    else:
        print(f"[{now.strftime('%H:%M')}] 예약 도달 항목 없음")


# ── 메인 ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="X Notes 게시 헬퍼")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("prepare", help="클립보드 복사 + 브라우저 + 이미지 체크리스트")
    p.add_argument("article_id")

    p = sub.add_parser("queue", help="예약 큐 등록")
    p.add_argument("article_id")
    p.add_argument("--date", required=True, help="예약 시간 (YYYY-MM-DD HH:MM)")

    sub.add_parser("status", help="큐 상태 확인")

    p = sub.add_parser("done", help="게시 완료 처리")
    p.add_argument("article_id")

    p = sub.add_parser("publish", help="게시 완료 → published/ 디렉토리로 이동")
    p.add_argument("article_id")

    sub.add_parser("run-scheduled", help="예약 도달 항목 실행 (cron용)")

    args = parser.parse_args()

    if args.cmd == "prepare":
        cmd_prepare(args.article_id)
    elif args.cmd == "queue":
        cmd_queue(args.article_id, args.date)
    elif args.cmd == "status":
        cmd_status()
    elif args.cmd == "done":
        cmd_done(args.article_id)
    elif args.cmd == "publish":
        cmd_publish(args.article_id)
    elif args.cmd == "run-scheduled":
        cmd_run_scheduled()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
