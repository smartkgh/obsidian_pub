
import os
import re
import yaml
import datetime
from pathlib import Path

def sanitize_filename(filename):
    return re.sub(r'\s+', '_', filename)  # 공백 → 언더스코어


def convert_obsidian_to_hugo(content: str, file_path: Path) -> str:
    """Obsidian 마크다운 콘텐츠를 Hugo 형식으로 변환합니다."""

    # frontmatter = {
    # "title": f'"{file_path.stem}"',
    # "date": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
    # "draft": "false",
    # "categories": [], # 리스트로 초기화
    # "tags": []       # 리스트로 초기화
    # }

    # # 기존 frontmatter 추출
    # fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    # if fm_match:
    #     existing_fm_str = fm_match.group(1)
    #     for line in existing_fm_str.split('\n'):
    #         if ':' in line:
    #             key, *value = line.split(':', 1)
    #             key = key.strip()
    #             val = value[0].strip()
                
    #             # 리스트 형태 파싱 (예: ["A", "B"] 또는 [A, B])
    #             if key in ["categories", "tags"]:
    #                 # 대괄호와 따옴표 제거 후 쉼표로 분리
    #                 val_clean = val.strip("[]").replace('"', '').replace("'", "")
    #                 frontmatter[key] = [v.strip() for v in val_clean.split(',') if v.strip()]
    #             else:
    #                 frontmatter[key] = val
        
    #     content = content[fm_match.end():]

    # # 새로운 frontmatter 생성 (Hugo 호환 형식)
    # new_fm_lines = []
    # for key, value in frontmatter.items():
    #     if isinstance(value, list):
    #         # 리스트인 경우 ["A", "B"] 형식으로 저장
    #         list_str = ", ".join([f'"{v}"' for v in value])
    #         new_fm_lines.append(f"{key}: [{list_str}]")
    #     else:
    #         new_fm_lines.append(f"{key}: {value}")

    # new_fm = "---\n" + "\n".join(new_fm_lines) + "\n---\n"


    # 1. 기존 content에서 Frontmatter 추출 및 분리
    fm_match = re.search(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

    if fm_match:
        existing_fm_str = fm_match.group(1)
        content_body = content[fm_match.end():] # 본문만 따로 저장
        
        # 2. YAML 파서로 안전하게 읽기 (여러 줄 리스트도 자동 처리됨)
        try:
            data = yaml.load(existing_fm_str, Loader=yaml.FullLoader)
        except Exception:
            data = {}
    else:
        data = {}
        content_body = content

    # 3. 데이터 업데이트
    data['title'] = data.get('title', file_path.stem)
    data['date'] = data.get('date', datetime.datetime.fromtimestamp(file_path.stat().st_mtime))
    data['draft'] = data.get('draft', False)
    data['categories'] = data.get('categories',"")
    data['tags'] = data.get('tags',"")

    # 4. YAML을 다시 문자열로 변환 (Hugo 스타일로 저장)
    # allow_unicode=True는 한글 깨짐 방지
    new_fm_content = yaml.dump(data, allow_unicode=True, default_flow_style=False)
    new_fm = "---\n" + new_fm_content + "---\n" 

    print(f"frontmatter: {new_fm}")


    
    body = content_body

    # --- Obsidian 링크 변환 ---

    #body = re.sub(r'!\[\[([^\]|]+\.(?:png|jpg|jpeg|gif|webp|svg))(?:\|\s*[^\]]*)*?\]\]', r'![](/images/\1)', body)

    body = re.sub(
    r'!\[\[([^\]|]+\.(?:png|jpg|jpeg|gif|webp|svg))(?:\|\s*[^\]]*)*?\]\]', 
    lambda m: f'![](/images/{sanitize_filename(m.group(1))})', body
    )

    # [[wikilink]] -> [wikilink]({{< ref "wikilink.md" >}})
    body = re.sub(r'\[\[([^\]|#]+)(?:\|[^\\\]]+)?(?:#[^\\]+)?\]\]', r'[\1]({{< ref "\1.md" >}})', body)
    
    # --- Obsidian 이미지/첨부파일 변환 ---
    # ![[image.png]] -> ![image.png](/images/image.png)
    # 이미지는 hugo_site/static/images/ 폴더에 위치해야 합니다.
    #body = re.sub(r'!\\\[([^\\]+)\\\]', r'![\\1](/images/\\1)', body)

    #body = re.sub(r'!\[\[([^\]|]+\.(?:png|jpg|jpeg|gif|webp|svg))([\|].*)?\]\]', r'![\1](/images/\1)', body)

    #body = re.sub(r'!\[\[([^\]|]+\.(?:png|jpg|jpeg|gif|webp|svg))(?:\|\s*[^\]]*)*?\]\]', r'![](/images/\1)', body)


    return new_fm + body

def main():
    """스크립트의 메인 실행 함수"""
    # 스크립트 파일의 위치를 기준으로 경로 설정
    # ~/obsidian_pub/hugo_pub/scripts -> /Users/1002207/obsidian_pub
    project_root = Path(__file__).parent.parent.parent
    
    source_dir = project_root / "hugo_pub" / "public"
    dest_dir = project_root / "hugo_site" / "content" / "posts"

    ## Local Test용
    #project_root = Path(__file__).parent.parent.parent.parent
    #
    #source_dir = project_root / "obsidian_pub" / "hugo_pub" / "public"
    #dest_dir = project_root / "hugo_site" / "content" / "posts"


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
