---
type: concept
title: "모바일 앱 보안·개인정보 및 스토어 정책 대응"
tags:
  - concept
  - security
  - compliance
sources:
  - "raw/assets/my_skplanet_업무히스토리1.pdf"
  - "raw/assets/my_skplanet_업무히스토리2.pdf"
related:
  - "[[android-app-development]]"
  - "[[ios-app-development]]"
  - "[[syrup-wallet]]"
created: "2026-11-26"
updated: "2026-11-26"
---

# 모바일 앱 보안·개인정보 및 스토어 정책 대응

## 정의
금융·멤버십·위치·광고 SDK를 탑재한 상용 모바일 앱에서 요구되는 단말 데이터 암호화, 앱 위변조/난독화, 외부 보안 진단 조치, 그리고 Google Play·Apple App Store·One Store 심사 정책 준수 역량이다.

## 설명
- **데이터·단말 보안**: Local DB 암호화(카드·사용자 인증정보·Preference), 백업 후 DB 복호화 방지(KISA 지적 대응), ProGuard/Allatori 난독화, FIDO 간편인증 및 비밀번호 복잡도·보안키패드, 앱위변조(LxShield 등)·백신 SDK 주기적 업데이트, 명시적 Intent 및 WebView WhiteList 검증.
- **보안 인증·점검 대응**: PIMS 인증 심사(v5.5.12), SKT 보안점검/정기 보안진단, 금융보안원(금보원) 취약점 대응(v5.7.10), SK스퀘어 모의해킹 취약점 조치(v5.8.06).
- **스토어·OS 컴플라이언스**: Google SMS 퍼미션 정책(SMS Retriever), `MANAGE_EXTERNAL_STORAGE` 제거, Baidu/AdQuality 등 정책 위반 SDK 신속 제거, **v5.7.19 Google Play 정책 거절 6회 연속 수정·승인 통과(2024.01~03)**, Apple Privacy Manifest 대응.

## 근거가 되는 자료·대상
- [[my-skplanet-업무히스토리-1]] — v5.1(DB암호화), v5.3.9(KISA/Allatori), v5.5.12(PIMS), v5.6.06(Baidu제거), v5.7.10(금보원)
- [[my-skplanet-업무히스토리-2]] — v5.7.19(Google 심사 6차 대응), v5.8.06(SK스퀘어 모의해킹)

## 관련 개념
- [[android-app-development]]
- [[ios-app-development]]
- [[fintech-mydata-syrup]]
