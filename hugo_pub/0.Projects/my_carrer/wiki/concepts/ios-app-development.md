---
type: concept
title: "iOS 앱 배포 및 멀티플랫폼 운영"
tags:
  - concept
  - ios
  - mobile
sources:
  - "raw/assets/my_skplanet_업무히스토리2.pdf"
related:
  - "[[android-app-development]]"
  - "[[syrup-wallet]]"
created: "2026-11-26"
updated: "2026-11-26"
---

# iOS 앱 배포 및 멀티플랫폼 운영

## 정의
2023년 이후 [[sk-플래닛]] [[syrup-wallet]] 통합 배포 내역에서 확인되는 iOS 앱 빌드·SDK 통합·OS/Xcode 대응 및 AOS·iOS 동시 릴리즈 운영 영역이다.

## 설명
- [[my-skplanet-업무히스토리-2]]에 따르면 v5.7.12(2023/01)부터 v5.8.17(2026/09)까지 AOS와 iOS(App Store / TestFlight) 배포가 단일 통합 배포 이력으로 관리되었다.
- Xcode 14.2 → 15 → 16 → 26 빌드 대응, Apple Privacy Manifest(`PrivacyInfo.xcprivacy`) 대응, Scene-based life cycle 전환, iOS Google Mobile Ads/PlanetAD/ironSource/CashButton PointHome/LxShield/AppsFlyer/Rake SDK 탑재 및 메모리 누수·화면 전환 개선 등이 포함된다.
- 단, 강기훈 본인이 iOS 개발까지 직접 수행했는지, AOS 리딩 및 AOS/iOS 통합 배포·릴리즈 관리(PL/PM)를 담당했는지는 사용자 확인이 필요하다.

## 근거가 되는 자료·대상
- [[my-skplanet-업무히스토리-2]] — pp.1~9 (iOS 배포일, 내부버전 10244~10305, iOS 전용 작업 항목)

## 관련 개념
- [[android-app-development]]
- [[app-security-compliance]]
