
import os
import re
import datetime
from pathlib import Path

def convert_obsidian_to_hugo(content: str, file_path: Path) -> str:
    """Obsidian 마크다운 콘텐츠를 Hugo 형식으로 변환합니다."""

    # --- Frontmatter 처리 ---
    frontmatter = {
        "title": f'"{file_path.stem}" ',
        "date": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
        "draft": "false",
    }
    
    # 기존 frontmatter 추출 및 업데이트
    fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if fm_match:
        existing_fm_str = fm_match.group(1)
        # 간단한 key: value 파싱
        for line in existing_fm_str.split('\n'):
            if ':' in line:
                key, *value = line.split(':', 1)
                key = key.strip()
                val = value[0].strip()
                if key and val:
                    frontmatter[key] = val
        # 기존 frontmatter를 내용에서 제거
        content = content[fm_match.end():]

    # 새로운 frontmatter 생성
    new_fm_lines = [f"{key}: {value}" for key, value in frontmatter.items()]
    new_fm = "---\n" + "\n".join(new_fm_lines) + "\n---\n"
    
    body = content

    # --- Obsidian 링크 변환 ---
    # [[wikilink]] -> [wikilink]({{< ref "wikilink.md" >}})
    body = re.sub(r'\[\[([^\]|#]+)(?:\|[^\\\]]+)?(?:#[^\\]+)?\]\]', r'[\1]({{< ref "\1.md" >}})', body)
    
    # --- Obsidian 이미지/첨부파일 변환 ---
    # ![[image.png]] -> ![image.png](/images/image.png)
    # 이미지는 hugo_site/static/images/ 폴더에 위치해야 합니다.
    body = re.sub(r'!\\\[([^\\]+)\\\]', r'![\\1](/images/\\1)', body)

    return new_fm + body

def main():
    """스크립트의 메인 실행 함수"""
    # 스크립트 파일의 위치를 기준으로 경로 설정
    # /Users/1002207/obsidian_pub/hugo_pub/scripts -> /Users/1002207/obsidian_pub
    # project_root = Path(__file__).parent.parent.parent
    
    # source_dir = project_root / "hugo_pub" / "public"
    # dest_dir = project_root / "hugo_site" / "content" / "posts"


    project_root = Path(__file__).parent.parent.parent.parent
    
    source_dir = project_root / "obsidian_pub" / "hugo_pub" / "public"
    dest_dir = project_root / "hugo_site" / "content" / "posts"


    # 대상 디렉토리가 없으면 생성
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"소스 디렉토리: {source_dir}")
    print(f"대상 디렉토리: {dest_dir}")
    print("-" * 20)

    # 소스 디렉토리에서 모든 .md 파일 찾기
    markdown_files = list(source_dir.glob("**/*.md"))

    if not markdown_files:
        print("변환할 마크다운 파일을 찾을 수 없습니다.")
        return

    for md_file in markdown_files:
        print(f"변환 중: {md_file.name}")
        
        try:
            # 파일 내용 읽기
            with open(md_file, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Obsidian -> Hugo 변환
            hugo_content = convert_obsidian_to_hugo(original_content, md_file)

            # 대상 파일 경로 설정
            dest_file_path = dest_dir / md_file.name

            # 변환된 내용 저장
            with open(dest_file_path, 'w', encoding='utf-8') as f:
                f.write(hugo_content)
                
        except Exception as e:
            print(f"  [오류] {md_file.name} 파일 처리 중 오류 발생: {e}")

    print("-" * 20)
    print(f"총 {len(markdown_files)}개의 파일 변환 완료.")


if __name__ == "__main__":
    main()
