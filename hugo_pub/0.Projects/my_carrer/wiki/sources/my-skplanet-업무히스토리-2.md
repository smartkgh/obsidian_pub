---
type: source
title: "SK 플래닛 Syrup App 배포 히스토리 2 (2023.01 ~ 2026.09)"
tags:
  - source
  - career
  - sk-planet
  - syrup
  - android
  - ios
sources:
  - "raw/assets/my_skplanet_업무히스토리2.pdf"
related:
  - "[[강기훈]]"
  - "[[sk-플래닛]]"
  - "[[syrup-wallet]]"
  - "[[my-skplanet-업무히스토리-1]]"
created: "2026-11-26"
updated: "2026-11-26"
---

# SK 플래닛 Syrup App 배포 히스토리 2 (2023.01 ~ 2026.09)

## 원본
- 파일: `raw/assets/my_skplanet_업무히스토리2.pdf`
- 작성자/출처: SK 플래닛 사내 Confluence/Wiki 등 `[#0_App 배포 내역]` 페이지 내보내기 문서 (추정)
- 작성일/기간: 2023/01/30 (v5.7.12) ~ 2026/09/17 (v5.8.17)
- 수집일: 2026-11-26

## 요약
2023년 1월부터 2026년 9월까지 Syrup 앱의 Android(AOS) 및 iOS 통합 배포 내역(v5.7.12 ~ v5.8.17)을 담은 10페이지(본문 9페이지) 문서다. 리워드/앱테크 서비스 전환(`아끼기`, `모으기(금돼지/금주머니)`, `지금 할 일(AI 추천 콘텐츠/식단기록)`, `경유쇼핑/쿠팡적립/네이버쇼핑 Adison OFW`), Planet AD(P.AD)·AdMob·ironSource·Tapjoy·CashButton/포인트홈 등 광고 미디에이션/리워드 플랫폼 연동, 마이데이터/오픈뱅킹/OWP 등 레거시 서비스 종료 정리, 그리고 Google Play 정책 거절 6회 연속 대응 및 SK스퀘어 모의해킹 취약점 조치 등 OS/스토어 컴플라이언스 및 앱 운영 내역이 상세히 기록되어 있다.

## 핵심 내용
- **2023년 (v5.7.12 ~ v5.7.17, pp.8~9)**:
  - 광고·리워드 확장: DFP 카카오 애드핏/Pubmatic/Fyber/Pangle 어댑터, Tapjoy 오퍼월, 네이버 광고 미디에이션, 내재화(버즈빌) SDK 업데이트 및 기존 버즈빌 SDK 제거, 쿠팡적립(경유쇼핑), 내재화 광고(오락) 쿠팡/네이버 웹배너, 보상형 동영상 광고 어댑터, In-App Custom Browser.
  - 서비스 개편 및 종료 대응: 메인화면 구조 변경, `아끼기(구 할인적립탭)` 개편, Syrup Wealth 멤버십/제로페이 종료, MyData SDK v1.5.5 및 정기 보안진단(22년) 패치.
  - AOS OS 13 Target 대응 / iOS Xcode 14.2 대응 및 백스와이프 제스처 도입.
- **2024년 (v5.7.18 ~ v5.8.01, pp.5~7)**:
  - **Google Play 정책 거절 연속 대응 (v5.7.19, 2024/01~03, p.7)**: SMS 권한, 위치정보·백그라운드 위치 엑세스, 전화번호 수집/전송 명시적 공개 관련 Google 정책 거절(268~273버전)을 6차례 수정·재승인 요청 끝에 통과.
  - 리워드/광고 고도화: 캐시버튼 SDK → CashButton PointHome 전환, AdMob 전면/저금통 광고 연동 및 AdMob 정책이슈 대비 ironSource 병행(돼지 뿌시기), P.AD(Planet AD) 챌린지/오락피드 동영상 자동재생, 출석체크 런컴 SDK, 미디에이션 광고(Cauly, FAN, MezzoMedia, Mobon) 추가.
  - OS·프라이버시 대응: AOS Target OS 14 대응, iOS Xcode 15 및 `PrivacyInfo.xcprivacy`(privacy manifest) 대응, AOS Room DB OOM 이슈 수정, OneStore 유해앱 탐지 긴급 재배포(v5.7.26).
- **2025년 (v5.8.02 ~ v5.8.12, pp.2~4)**:
  - 리워드/앱테크 고도화: `지금 할 일`(날짜 선택, 공휴일 제외, 금 받는 식단 기록), `모으기` 개편(네이티브 DA + 금주머니, 금돼지 두드리기 고도화), `P.AD` 리워드를 OCB에서 금 적립으로 변경, 세로형(Interstitial)/배너형 P.AD 추가, `Adison OFW`(네이버 쇼핑 연동), `PLACE SA`.
  - SDK 전환 및 보안: Branch SDK 제거 → AppsFlyer SDK 교체, SK스퀘어 모의해킹 취약점 조치(v5.8.06), firebase dynamic links 및 OWP 로직 제거.
  - **대규모 온보딩 개편 및 서비스 종료 정리 (v5.8.08~v5.8.10, p.3)**: '25.08 Syrup 온보딩 개편(불필요 권한 정리, 인증 개선), 직접등록 멤버십·마이데이터·텐큐브·T멤버십 T ID 로그인·오픈뱅킹 관련 영역 제거.
  - OS 대응: AOS Target 15 및 16KB 페이징 사이즈 지원, iOS Xcode 16 및 Scene-based lifecycle 전환.
- **2026년 (v5.8.13 ~ v5.8.17, pp.1~2)**:
  - v5.8.14(2026/03): `지금 할 일` 고도화, 전체 메뉴 UX 변경, ironSource 동영상 광고 업데이트, Google GMA SDK 24.7.0, 앱위변조 SDK 6.9.11, iOS Xcode 26 빌드 대응, OSS 검증 대응.
  - v5.8.15~v5.8.17(2026/04~09): P.AD 피드 동영상 자동재생·체류형 광고, 포인트홈/황금알 광고, `지금 할 일` 숏폼 UI 개편 + AI 추천 콘텐츠 + 전면 알림, `지금` 탭명 변경, CPL 참여적립(주황깃발) SDK 추가, AdMob 미디에이션 비딩 광고 추가, AOS Target OS 16 대응, FIDO·백신 SDK 보안 패치.

## 등장하는 개념·대상
- 개념: [[android-app-development]], [[ios-app-development]], [[ad-tech-mediation]], [[app-security-compliance]], [[fintech-mydata-syrup]], [[reward-apptech-syrup]]
- 사람·조직·프로젝트: [[강기훈]], [[sk-플래닛]], [[syrup-wallet]]

## 숫자·날짜·성과 (원문 그대로)
| 항목 | 값 | 위치 |
|---|---|---|
| 수록 기간 | 2023/01/30 (v5.7.12, AOS 262 / iOS 10244) ~ 2026/09/17 (v5.8.17, AOS 302 / iOS 10305) | p.9, p.1 |
| 주요 마일스톤 버전 | 5.7.15 (아끼기탭 개편), 5.7.19 (구글 정책 심사 6차례 수정 통과), 5.8.00~01 (PointHome·SKP AD SDK 전환), 5.8.08 (온보딩 개편·마이데이터 SDK 제거), 5.8.14~17 (지금 할 일 숏폼/AI콘텐츠·AdMob 비딩·AOS16) | p.9, p.7, p.5, p.3, p.1~2 |
| 구글 플레이 정책 심사 이력 | v5.7.19 (내부버전 268~273): 2024/01/30 거절 시작 → 6회 수정 요청 후 2024/03/05 승인 완료 | p.7 |

## 의문점 / 다른 자료와의 차이
- [[my-skplanet-업무히스토리-1]]은 Android(AOS) 전용 배포 내역이었으나, 이 문서는 **AOS와 iOS 통합 배포 내역**임. 강기훈 본인이 Android만 담당했는지, iOS까지 포함한 앱 개발/배포 리딩(PL/PM) 또는 개발/기획 브릿징 역할을 했는지 확인 필요.
- 문서에 JIRA 티켓(`SYRUPPROD-*`, `SYRUPW-*`, `BUZZOLOCK-*`, `PROXIMITY-*`), Crashlytics 링크, 타 부서 협업자 이름이 기재되어 있으나 본인의 직책/직급, 소속 팀명, 입사/퇴사 정확한 연월, 정량적 비즈니스 성과(매출/MAU/크래시율 등)는 별도 확인 필요.
