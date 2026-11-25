---
type: module
title: storage — 기기 안 저장
tags: [모듈]
related: [[system]], [[ADR-0001-앱-형태-PWA-USB-설치]]
created: 2026-11-25
updated: 2026-11-25
---

# storage — 기기 안 저장

## 역할
작성 중인 결의서, 기본 정보(위원회명·팀명·이름), 영수증 사진을 IndexedDB에 저장한다. 외부 전송 없음.

## 코드 위치
- `~/my_projects/expense-report/src/storage/db.ts`

## 주요 구성
| 이름 | 설명 |
|---|---|
| `kv` 저장소 | `report`(작성 중 결의서), `profile`(기본 정보) |
| `images` 저장소 | 영수증 사진 (긴 변 1600px JPEG + 크기) |
| `requestPersist()` | 브라우저가 자동으로 지우지 않도록 요청 |

## 주의
- 폰 크롬에서 `localhost:8080` 사이트 데이터를 지우면 함께 지워진다. ([[install-guide]])

## 관련 요구사항 / 결정
- REQ-009, REQ-014, REQ-017

## 변경 이력
| 버전 | 변경 내용 |
|---|---|
| v1 | 최초 구현 |
