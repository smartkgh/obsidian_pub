#!/bin/bash

echo "1. 파이썬 마크다운 변환 시작..."
python3 ../hugo_pub/scripts/obsidian_to_hugo.py


echo "2. Hugo 로컬 서버 실행..."
hugo -D server 
