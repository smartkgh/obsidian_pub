# Android 16 (API 36) 대응 작업 목록

> 조사 기준일: 2026-07-05
> 조사자: Hermes Agent (default profile)

---

## Phase 1: 호환성 보장 (targetSdkVersion 변경 없이)

| # | 작업 항목 | 상세 | 담당자 | 작업 에이전트 | 우선순위 |
|---|---------|------|-------|------------|---------|
|| 1 | JobScheduler 할당량 최적화 대응 | 앱 대기 버킷 기반 할당량 조정. 포그라운드 서비스 동시 작업 할당량 준수 확인. WorkManager/JobScheduler/DownloadManager 사용 코드 검토 | Android 개발팀 | coding-agent | 상 |
|| 2 | 비 SDK 인터페이스 제한 테스트 | logcat에서 비 SDK API 사용 경고 확인. StrictMode.detectNonSdkApiUsage()로 프로그래매틱 감지 | Android 개발팀 | coding-agent | 상 |
|| 3 | ART 내부 변경사항 대응 | 내부 ART 구조 사용 라이브러리/코드 확인. 공개 API 대안 탐색 | Android 개발팀 | coding-agent | 상 |
|| 4 | 인텐트 리디렉션 공격 대응 | Intent 리디렉션 취약점 점검. removeLaunchSecurityProtection() 불필요한 사용 제거 | Android 개발팀 | coding-agent | 상 |
|| 5 | 16KB 페이지 크기 호환성 | AndroidManifest.xml에 android:pageSizeCompat 속성 설정. 16KB 정렬로 앱 업데이트 계획 | Android 개발팀 | coding-agent | 중 |
|| 6 | 브로드캐스트 우선순위 제한 대응 | 프로세스 간 ordered broadcast 우선순위 의존성 확인. 필요시 다른 조정 채널로 대체 | Android 개발팀 | coding-agent | 중 |
|| 7 | 접근성 announceForAccessibility 지원 중단 대응 | setAccessibilityLiveRegion / setAccessibilityPaneTitle / setError로 마이그레이션 | Android 개발팀 | coding-agent | 중 |
|| 8 | 블루투스 결합 손실 처리 개선 대응 | 기존 페어링 로직 검토. 새 시스템 대화상자 동작 확인 | Android 개발팀 | coding-agent | 하 |

## Phase 2: Android 16 타겟팅 (targetSdkVersion 36 업데이트)

| # | 작업 항목 | 상세 | 담당자 | 작업 에이전트 | 우선순위 |
|---|---------|------|-------|------------|---------|
||| 9 | compileSdkVersion 및 targetSdkVersion 업데이트 | Android 16 SDK 설정. compileSdk 36, targetSdk 36으로 업데이트 | Android 개발팀 | coding-agent | 상 | ✅ 완료 |
||| 10 | Android 16 타겟팅 동작 변경사항 대응 | [behavior-changes-16](https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko) 전체 검토 및 코드 수정 | Android 개발팀 | coding-agent | 상 | ✅ 완료 |
||| 11 | 새 API 기능 도입 검토 | Android 16 API 활용 가능 영역 분석. 새 기능 도입 계획 | PM / Android 개발팀 | research-worker | 중 | |
||| 12 | 호환성 전환(Compat Toggles)을 사용한 테스트 | adb로 개별 변경사항 on/off 테스트. targetSdk 변경 없이 영향 평가 | Android 개발팀 | coding-agent | 상 | ✅ 완료 |
||| 13 | 라이브러리/SDK 호환성 테스트 | 서드파티 SDK가 Android 16에서 정상 작동하는지 확인. 필요시 SDK 업데이트 | Android 개발팀 | coding-agent | 상 | ✅ 완료 |

## 테스트 계획

| # | 항목 | 설명 | 작업 에이전트 |
|---|-----|------|------------|
|| T1 | Android 16 에뮬레이터/실기기 테스트 | Android 16 시스템 이미지 다운로드 후 전체 기능 테스트 | coding-agent |
|| T2 | 모든 앱 동작 변경사항 검증 | Phase 1 변경사항이 앱에 미치는 영향 확인 | coding-agent |
|| T3 | 비 SDK 인터페이스 테스트 | logcat/StrictMode로 사용 현황 모니터링 | coding-agent |
|| T4 | 타겟팅 변경사항 검증 | targetSdk 36 업데이트 후 동작 확인 | coding-agent |
|| T5 | 라이브러리 호환성 테스트 | 주요 SDK/라이브러리 Android 16 호환성 확인 | coding-agent |

---
## Orchestrator 할당 기록

- **오케스트레이터 프로필**: orchestrator
- **할당 일시**: 2026-07-05
- **할당 기준**:
  - Phase 1 (작업 1-8, 호환성 보장) 및 Phase 2 (작업 9-13 중 9, 10, 12, 13) → `coding-agent`: Android 코드 수정/설정 변경이 필요한 개발 작업
  - Phase 2 (작업 11, 새 API 기능 도입 검토) → `research-worker`: 새로운 API 영역 분석 및 조사 작업
  - 테스트 계획 (T1-T5) → `coding-agent`: Android 에뮬레이터/실기기 테스트, ADB 명령어 실행 등 개발 테스트
- **Kanban child tasks**: 아래에 생성된 Kanban 하위 태스크를 통해 각 agent가 실제 작업 수행
