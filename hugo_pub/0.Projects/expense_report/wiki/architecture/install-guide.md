---
type: architecture
title: 설치 안내 (맥북, 안드로이드 USB)
tags: [설치, adb, PWA]
sources: []
related: [[ADR-0001-앱-형태-PWA-USB-설치]], [[system]]
created: 2026-11-25
updated: 2026-11-25
---

# 설치 안내

## 맥북 (처음 한 번)
1. Node.js 설치 확인 (`node -v`)
2. 코드 폴더에서 `npm install`, `npm run build`
3. `npm run serve` → 크롬에서 `http://localhost:8080` 열기
   - 영수증 인식은 맥 내장 엔진(Apple Vision)을 쓴다. 오른쪽 아래에 "맥 인식 엔진"이 보이면 정상
   - **`npm run serve`를 켜 둔 상태에서 써야** 맥 엔진이 동작한다. 서버 없이 설치된 앱만 열면 기본 인식(정확도 낮음)으로 동작
4. (선택) 크롬 주소창의 설치 아이콘 → 앱처럼 실행

## 안드로이드 폰 (처음 한 번)
1. **폰**: 설정 → 휴대전화 정보 → 소프트웨어 정보 → 빌드번호 7번 누르기 → 개발자 옵션 → **USB 디버깅** 켜기
2. **맥**: `brew install --cask android-platform-tools` (adb 설치)
3. 폰을 맥에 USB로 연결 → 폰에 뜨는 "USB 디버깅 허용" 누르기
4. **맥**: 코드 폴더에서 `npm run phone` (= `adb reverse tcp:8080 tcp:8080` + 로컬 서버 실행)
5. **폰**: 크롬에서 `http://localhost:8080` 열기 → "오프라인 준비 완료" 표시 확인
6. **폰**: 크롬 메뉴 → **홈 화면에 추가**(앱 설치)
7. 케이블을 빼고 비행기 모드에서 아이콘을 눌러 동작 확인

## 업데이트
- 위 3~5번을 다시 하면 새 버전을 받는다. 작성 중인 결의서는 유지된다.

## 주의
- 크롬 → 설정 → 사이트 설정에서 `localhost:8080` 데이터를 지우면 앱과 작성 중인 결의서가 지워진다.
- USB 디버깅은 설치가 끝나면 꺼도 된다.
