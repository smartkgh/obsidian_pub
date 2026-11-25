---
type: decision
title: ADR-0001 앱 형태 — 웹앱(PWA) + USB 설치
status: accepted
version: v1
tags: [PWA, 설치, adb]
sources: []
related: [[local-app-packaging]], [[ADR-0002-OCR-엔진-Tesseract-js]], [[system]]
created: 2026-11-25
updated: 2026-11-25
---

# ADR-0001 앱 형태 — 웹앱(PWA) + USB 설치

## 배경
REQ-014~016: 안드로이드 폰과 맥북에서 각각 로컬로만 동작해야 한다. 앱 코드나 데이터가 인터넷 주소를 거치지 않기를 원한다.

## 선택지
| 선택지 | 장점 | 단점 |
|---|---|---|
| A. PWA + 인터넷 주소에서 설치 | 가장 쉬움 | 앱 코드가 인터넷에 올라감 |
| **B. PWA + USB(adb reverse) 설치** | 완전 로컬, 맥 준비물이 작음(adb) | 폰 USB 디버깅 필요, 업데이트 시 재연결 |
| C. APK (Capacitor + ML Kit) | 파일 복사로 설치, 인식 정확 | 맥에 Android Studio 필요 |
| D. HTML 파일을 폰에 복사해 열기 | 단순 | 안드로이드 크롬의 로컬 파일 제한으로 인식 엔진, 저장이 동작하지 않음 |

## 결정
**B. 웹앱(PWA)을 만들고, 폰에는 USB 연결(adb reverse)로 설치한다.** 맥북은 같은 앱을 `localhost:8080`에서 사용한다.

## 이유
- 인터넷 주소 없이 설치할 수 있다. 폰 크롬은 `localhost`를 안전한 주소로 보므로 오프라인 기능(서비스 워커)이 동작한다.
- 맥 준비물이 adb(Homebrew 한 줄)뿐이다.
- 화면, 문서 생성 코드가 웹 하나로 통일된다.

## 영향
- 인식 엔진은 브라우저에서 도는 것을 써야 한다 → [[ADR-0002-OCR-엔진-Tesseract-js]]
- 폰 크롬의 사이트 데이터를 지우면 앱과 작성 중인 결의서가 지워진다. 영구 저장 요청(`navigator.storage.persist()`)으로 자동 삭제 위험을 줄인다.
- 나중에 인식 정확도가 부족하면 C(APK)로 옮길 수 있게 인식 부분을 교체 가능한 모듈로 둔다.
- 관련 요구사항: REQ-014, REQ-015, REQ-016, REQ-017

## 근거
- [[local-app-packaging]]
- 사용자 결정 (2026-11-25)
