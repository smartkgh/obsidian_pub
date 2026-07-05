# Android 16 (API 36) OS Target 대응 조사 보고서

> **작성일**: 2026-07-05
> **작성자**: Hermes Agent
> **대상**: Android OS Target 16 대응 마이그레이션

---

## 1. 개요

Android 16 (API Level 36)은 AOSP에 출시되어 사용자에게 제공되고 있습니다. 기존 앱이 Android 16에서 안정적으로 동작하고 새로운 플랫폼 기능을 최대한 활용하기 위해서는 체계적인 마이그레이션 계획이 필요합니다.

### 1.1 핵심 원칙

| 구분 | 내용 |
|------|------|
| **Phase 1: 호환성 보장** | targetSdkVersion 변경 없이 Android 16에서 앱이 정상 동작하도록 보장 (최종 출시 전까지 완료) |
| **Phase 2: 타겟팅 업데이트** | targetSdkVersion 36으로 업데이트하고 새 API/기능 활용 (최종 출시 후) |

---

## 2. Phase 1: 모든 앱에 적용되는 동작 변경사항

> `targetSdkVersion`과 관계없이 Android 16에서 실행되는 모든 앱에 적용됩니다.

### 2.1 핵심 기능 변경사항

#### 2.1.1 JobScheduler 할당량 최적화
- **영향**: WorkManager, JobScheduler, DownloadManager 사용 모든 앱
- **변경 내용**:
  - 앱 대기 버킷(Standby Bucket) 기반 런타임 할당량 조정
  - 활성(Active) 대기 버킷 → 넉넉한 할당량 적용
  - 앱이 포그라운드(FGS) 상태에서 시작된 작업도 작업 런타임 할당량 준수
  - 사용자에게 표시되는 동안 시작된 작업, 표시되지 않게 된 후에도 할당량 적용
- **대응**: `WorkInfo.getStopReason()` / `JobParameters.getStopReason()` 로깅 추가
- **테스트 ADB 명령어**:
  ```
  # 할당량 최적화 비활성화
  adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_TOP_STARTED_JOBS <package>
  adb shell am compat enable OVERRIDE_QUOTA_ENFORCEMENT_TO_FGS_JOBS <package>
  
  # 앱 대기 버킷 설정
  adb shell am set-standby-bucket <package> active|working_set|frequent|rare|restricted
  ```
- **권장사항**: `getPendingJobReasonsHistory()` API 활용하여 작업 미실행 원인 파악

#### 2.1.2 비어 있는 작업 중지 이유 (STOP_REASON_TIMEOUT_ABANDONED)
- **영향**: JobScheduler 직접 사용 앱 (WorkManager/AsyncTask/DownloadManager는 영향 없음)
- **변경 내용**: GC된 JobParameters 객체는 `STOP_REASON_TIMEOUT` 대신 `STOP_REASON_TIMEOUT_ABANDONED` 수신
- **대응**: 새 중지 이유 코드 처리 로직 추가

#### 2.1.3 JobInfo#setImportantWhileForeground 지원 중단 완료
- **변경 내용**: Android 12부터 지원 중단되었으나, Android 16에서는 완전히 무시됨
- **대응**: `setImportantWhileForeground(true)` 호출 제거 또는 조건부 처리

#### 2.1.4 주문된 브로드캐스트 우선순위 범위 제한
- **영향**: 여러 프로세스 간 ordered broadcast 의존하는 앱
- **변경 내용**:
  - 브로드캐스트 우선순위는 **동일 프로세스 내에서만** 적용
  - 우선순위 범위는 `(SYSTEM_LOW_PRIORITY + 1, SYSTEM_HIGH_PRIORITY - 1)`로 자동 제한
- **대응**: 프로세스 간 조정이 필요한 경우 별도 통신 채널 구현

#### 2.1.5 ART 내부 변경사항
- **영향**: 비 SDK 인터페이스(내부 ART 구조) 사용 라이브러리/코드
- **변경 내용**: ART 성능 개선 및 새 Java 기능 지원 → 내부 구조 변경 가능성 높음
- **대응**:
  - 비 SDK 인터페이스 사용 여부 점검
  - 공개 API 대안 탐색
  - Issue Tracker에 기능 요청 제출

#### 2.1.6 16KB 페이지 크기 호환성 모드
- **영향**: 4KB 정렬 메모리 페이지로 빌드된 앱
- **변경 내용**:
  - Android 16에서 4KB 정렬 앱 감지 시 **자동 호환성 모드** 활성화
  - 사용자에게 알림 대화상자 표시됨
- **대응**:
  - `AndroidManifest.xml`에 `android:pageSizeCompat` 속성 설정 (Android 16 SDK로 컴파일 필요)
  - 장기적으로 16KB 정렬로 앱 업데이트 (성능/안정성 최적)

### 2.2 사용자 환경 및 시스템 UI

#### 2.2.1 접근성 announceForAccessibility 지원 중단
- **영향**: `announceForAccessibility()` 또는 `TYPE_ANNOUNCEMENT` 사용 앱
- **대안**:
  - UI 창 변경: `Activity.setTitle()` / `setAccessibilityPaneTitle()` / Compose `paneTitle`
  - 중요 변경 알림: `setAccessibilityLiveRegion()` / Compose `liveRegion`
  - 오류 알림: `AccessibilityEvent.CONTENT_CHANGE_TYPE_ERROR` / `setError()`

#### 2.2.2 3버튼 탐색 뒤로 예측 지원
- **영향**: 뒤로 탐색 예측을 구현한 앱
- **변경 내용**: 3버튼 탐색 모드에서도 뒤로 버튼 길게 누르면 예측 애니메이션 지원

#### 2.2.3 자동 테마 앱 아이콘
- **변경 내용**: Android 16 QPR2부터 자체 테마 아이콘이 없는 앱에 시스템이 자동 테마 적용
- **대응**: 적응형 아이콘 내 단색 레이어 포함하여 디자인 제어

### 2.3 기기 폼 팩터

#### 2.3.1 가상 기기 소유자 재정의
- **영향**: 가상 기기(Virtual Device)에서 실행되는 앱
- **변경 내용**: 가상 기기 소유자가 앱 설정(방향, 가로세로 비율, 크기 조정) 재정의 가능

### 2.4 보안 변경사항

#### 2.4.1 인텐트 리디렉션 공격 기본 보안 강화
- **영향**: Intent 객체를 extra로 전달/실행하는 모든 앱
- **변경 내용**:
  - Intent 리디렉션 공격에 대한 기본 보안 제공
  - 불필요한 `removeLaunchSecurityProtection()` 호출은 취약점 유발
- **선택 해제 방법** (꼭 필요한 경우만):
  ```kotlin
  // Android 16 SDK 컴파일
  intent.getParcelableExtra<Intent>("sub_intent")?.removeLaunchSecurityProtection()
  
  // Android 15 이하 SDK 컴파일 (리플렉션, 비권장)
  val method = Intent::class.java.getDeclaredMethod("removeLaunchSecurityProtection")
  method.invoke(subIntent)
  ```

#### 2.4.2 컴패니언 기기 검색 타임아웃 알림 변경
- **영향**: Companion Device Manager(CDM) 사용 앱
- **변경 내용**:
  - `RESULT_DISCOVERY_TIMEOUT` 대신 사용자 대화상자 → `RESULT_USER_REJECTED`
  - 검색 시간 20초로 연장
  - 첫 20초 내 기기 발견 시 검색 중지

### 2.5 연결 변경사항

#### 2.5.1 블루투스 결합 손실 처리 개선
- **영향**: 블루투스 사용 앱
- **변경 내용**:
  - 자동 결합 삭제 → 로컬 페어링 정보 유지 + 사용자 대화상자 표시
  - 재페어링 로직 변경 필요성 검토

---

## 3. Phase 2: Android 16 타겟팅 시 추가 변경사항

> `targetSdkVersion`을 36으로 업데이트하는 앱에만 추가로 적용됩니다.

### 3.1 필요 작업

1. **SDK 설정**
   - Android Studio 최신 버전 설치
   - `compileSdkVersion` → 36
   - `targetSdkVersion` → 36

2. **Android 16 타겟팅 동작 변경사항 검토**
   - [behavior-changes-16](https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko) 전체 검토
   - 개인정보 보호 변경사항 대응 (코드/아키텍처 수정)
   - 호환성 전환(Compat Toggles) 활용하여 변경사항별 테스트

3. **새 API 도입**
   - Android 16 API 활용 가능 영역 분석
   - 새 기능 도입 계획 수립

### 3.2 호환성 전환 (Compat Toggles)

Android 16에서 타겟팅된 각 동작 변경사항별로 고유 ID가 제공됩니다.
- `adb` 명령어로 개별 변경사항 on/off 테스트 가능
- `targetSdkVersion` 변경 없이 영향 평가 가능

```
# 특정 변경사항 활성화 (targetSdk 변경 없이)
adb shell am compat enable CHANGE_ID <package>

# 특정 변경사항 비활성화
adb shell am compat disable CHANGE_ID <package>
```

---

## 4. 라이브러리/SDK 호환성

### 4.1 확인 사항
- 서드파티 SDK의 Android 16 호환성 확인
- 비 SDK 인터페이스 사용 여부 검증 (logcat 경고, StrictMode)
- 필요시 SDK 최신 버전으로 업데이트 또는 개발자 연락

### 4.2 주요 점검 라이브러리 (예시)
- Firebase SDK
- Crash reporting SDK (Firebase Crashlytics 등)
- 광고 SDK
- 결제 SDK
- 분석/로그 SDK

---

## 5. 전체 마이그레이션 로드맵

```mermaid
gantt
    title Android 16 마이그레이션 로드맵
    dateFormat  YYYY-MM-DD
    
    section Phase 1: 호환성 보장
    변경사항 분석 및 대응 계획         :p1a, 2026-07-05, 3d
    JobScheduler 할당량 대응            :p1b, after p1a, 5d
    비 SDK 인터페이스 점검              :p1c, after p1a, 5d
    보안 변경사항 대응                   :p1d, after p1a, 3d
    UI/접근성 변경사항 대응               :p1e, after p1a, 3d
    호환성 테스트 (에뮬레이터)            :p1f, after p1b, 5d
    호환 버전 릴리스                     :p1g, after p1f, 2d
    
    section Phase 2: 타겟팅 업데이트
    targetSdk 36 업데이트                :p2a, after p1g, 2d
    타겟팅 변경사항 대응                  :p2b, after p2a, 7d
    새 API 도입 검토 및 구현              :p2c, after p2b, 10d
    통합 테스트                          :p2d, after p2c, 5d
    최종 릴리스                          :p2e, after p2d, 2d
```

---

## 6. 참고 링크

| 자료명 | URL |
|-------|-----|
| Android 16 Migration Guide (한국어) | https://developer.android.com/about/versions/16/migration?hl=ko |
| 모든 앱 동작 변경사항 (한국어) | https://developer.android.com/about/versions/16/behavior-changes-all?hl=ko |
| Android 16 타겟팅 앱 동작 변경사항 (한국어) | https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko |
| 비 SDK 인터페이스 제한 (한국어) | https://developer.android.com/about/versions/16/changes/non-sdk-16?hl=ko |
| SDK 설정 가이드 (한국어) | https://developer.android.com/about/versions/16/setup-sdk?hl=ko |
| 호환성 프레임워크 (한국어) | https://developer.android.com/about/versions/16/reference/compat-framework-changes?hl=ko |

---

*본 보고서는 Android Developers 공식 문서와 Hermes Agent의 자동 분석을 기반으로 작성되었습니다.*

---

## 7. Orchestrator 작업 내역

| 항목 | 내용 |
|------|------|
| **Orchestrator 태스크** | t_9b3cf067 |
| **Orchestrator 프로필** | orchestrator |
| **작업 시작** | 2026-07-05 17:27 |
| **상태** | 하위 태스크 디스패치 완료 |

### 7.1 수행 작업
1. `req.md` 분석 — Android 16 OS Target 대응 조사 요구사항 파악
2. 기존 파일(task.md, result.md, report.md, raws.md) 상태 확인
3. Obsidian Clipping 문서(`Android 16으로 앱 이전`) 참조 자료 확인
4. `task.md` 업데이트 — 모든 작업 항목에 Agent Profile 컬럼 추가
5. Kanban 하위 태스크 4개 생성 및 디스패치

### 7.2 하위 태스크 현황

| Kanban ID | 작업명 | 담당 Agent | 상태 |
|-----------|-------|-----------|------|
| t_a365b140 | Phase 1: Android 16 호환성 보장 (Tasks 1-8) | coding-agent | todo |
| t_63e41af0 | Phase 2: Android 16 타겟팅 업데이트 (Tasks 9, 10, 12, 13) | coding-agent | todo |
| t_929b2e8e | Phase 2: Android 16 새 API 기능 도입 검토 (Task 11) | research-worker | todo |
| t_bc9c0436 | Android 16 테스트 계획 실행 (T1-T5) | coding-agent | todo |

### 7.3 GitHub 푸시
- **커밋**: e4b79f0
- **브랜치**: main
- **원격**: https://github.com/smartkgh/obsidian_pub.git
- **푸시 일시**: 2026-07-05 17:28
- **포함 파일**:
  - `hugo_pub/AI/Hermes/Working/work1/task.md` (Agent Profile 할당 업데이트)
  - `hugo_pub/AI/Hermes/Working/work1/result.md` (Orchestrator 작업 기록 추가)
  - `hugo_pub/AI/Hermes/Working/work1/report.md` (본 파일, Orchestrator 섹션 추가)
  - `hugo_pub/AI/Hermes/Working/work1/req.md`
  - `hugo_pub/Clippings/Android 16으로 앱 이전.md` (새 파일)
- **푸시 결과**: 성공

### 7.4 다음 단계
|- 각 하위 태스크가 dispatcher에 의해 자동으로 실행됨
|- 각 agent 완료 후 result.md 업데이트 예정
|- 모든 Phase 완료 후 추가 푸시 및 report.md 최종 업데이트 예정

---

## 8. 테스트 계획 실행 결과 (t_bc9c0436)

> **수행 Agent**: coding-agent | **수행일**: 2026-07-05

### 8.1 테스트 항목별 결과

| 테스트 | 항목 | 상태 | 산출물 |
|-------|------|------|--------|
| T1 | Android 16 에뮬레이터/실기기 테스트 | test-script.md 작성 완료 | 에뮬레이터 생성/앱 설치/기능 테스트 명령어 포함 |
| T2 | 모든 앱 동작 변경사항 검증 | test-script.md 작성 완료 | Phase 1 변경사항별 ADB 검증 명령어 |
| T3 | 비 SDK 인터페이스 테스트 | test-script.md 작성 완료 | StrictMode 설정 코드 + logcat 모니터링 |
| T4 | 타겟팅 변경사항 검증 | test-script.md 작성 완료 | Compat Toggles CHANGE_ID별 enable/disable |
| T5 | 라이브러리/SDK 호환성 테스트 | test-script.md 작성 완료 | 15개 주요 SDK 호환성 체크리스트 |

### 8.2 주요 산출물

- **test-script.md**: 완전한 Android 16 테스트 실행 스크립트 (13.8KB)
  - 경로: `kanban/boards/os16/workspaces/t_9b3cf067/test-script.md`
  - T1-T5 각각에 대한 상세 ADB 명령어, 설정 코드, 체크리스트 포함
  - 라이브러리 호환성 테이블 (Firebase, Crashlytics, AdMob, Play Billing, Compose 등 15종)

### 8.3 실행 제약사항

- 현재 머신에 Android SDK/ADB/안드로이드 프로젝트가 구성되어 있지 않아 실제 에뮬레이터/디바이스 테스트는 미실행
- 모든 ADB 명령어는 test-script.md에 준비되어 있으며, 안드로이드 개발 환경이 구성된 머신에서 즉시 실행 가능
- 라이브러리/SDK 호환성 정보는 Android 16 공식 문서 기준으로 정리

---

## 9. Phase 2: 타겟팅 업데이트 결과 (t_63e41af0)

> **수행 Agent**: coding-agent | **수행일**: 2026-07-05

### 9.1 Task 9: compileSdkVersion 및 targetSdkVersion 업데이트

Android 16 SDK 설정을 위한 요구사항 및 변경 방법을 정리했습니다.

| 항목 | 요구사항 |
|------|---------|
| **Android Studio** | Meerkat \| 2024.3.1+ (하위 버전과 SDK 호환 불가) |
| **AGP** | 8.9.0-rc01+ (AGP 업그레이드 어시스턴트 실행 권장) |
| **compileSdk** | 36 |
| **targetSdk** | 36 |

**build.gradle 변경 예시:**
```kotlin
android {
    compileSdk = 36
    defaultConfig {
        targetSdk = 36
    }
}
```

### 9.2 Task 10: Android 16 타겟팅 동작 변경사항 11종 분석

| # | 변경사항 | 영향 영역 | 필수 대응 |
|---|---------|----------|---------|
| 1 | **Edge-to-Edge 강제 적용** | UI/전체 화면 | `windowOptOutEdgeToEdgeEnforcement` 제거 |
| 2 | **뒤로 탐색 예측 의무화** | 탐색/키 이벤트 | `OnBackInvokedCallback` 마이그레이션 |
| 3 | **elegant font API 지원 중단** | 텍스트 렌더링 | 복합 스크립트 레이아웃 조정 |
| 4 | **scheduleAtFixedRate 최적화** | 작업 예약 | 1회로 제한된 누락 실행 영향 분석 |
| 5 | **적응형 레이아웃 (대형 화면)** | 레이아웃/방향 | 고정 방향/크기 제한 제거 또는 `PROPERTY_COMPAT_ALLOW_RESTRICTED_RESIZABILITY` |
| 6 | **건강/피트니스 권한 세분화** | 권한 | `BODY_SENSORS` → `READ_HEART_RATE` 등 |
| 7 | **블루투스 연결 손실 인텐트** | 블루투스 | `ACTION_KEY_MISSING` / `ACTION_ENCRYPTION_CHANGE` 처리 |
| 8 | **Intent Matching 강화** | 보안/인텐트 | `intentMatchingFlags="enforceIntentFilter"` |
| 9 | **GPU syscall 필터링** | Mali GPU(Pixel 6~9) | SELinux 로그 모니터링 |
| 10 | **로컬 네트워크 권한 (예고, 26Q2)** | 네트워크 | `RESTRICT_LOCAL_NETWORK` 선택 테스트 |
| 11 | **앱 소유 사진 보호** | 미디어 | 사진 선택 도구 연동 |

### 9.3 Task 12: 호환성 전환(Compat Toggles) 목록

Android 16의 호환성 프레임워크 CHANGE_ID를 모두 정리했습니다.

**SDK 36 타겟팅 시 기본 활성화되는 CHANGE_ID (2개):**
| 이름 | CHANGE_ID | 설명 |
|------|-----------|------|
| STPE_SKIP_MULTIPLE_MISSED_PERIODIC_TASKS | 288912692 | scheduleAtFixedRate 누락 실행 1회 제한 |
| UNIVERSAL_RESIZABLE_BY_DEFAULT | 357141415 | 600dp+ 대형 화면 방향/크기 제한 무시 |

**주요 테스트용 CHANGE_ID 그룹 (30+개):**
- **방향/크기 재정의** (7개): 265464455, 310816437, 266124927, 265451093, 265452344, 236283604, 332679525
- **최소 가로세로비** (6개): 174042980, 180326787, 180326845, 203647190, 218959984, 325586858
- **크기 조절** (2개): 174042936(FORCE_RESIZE_APP), 181146395(FORCE_NON_RESIZE_APP)
- **카메라 호환성** (3개): 314961188, 191514214, 189229956
- **HEVC** (2개): 174228127(enable), 174227820(disable)
- **화면 축소** (12개): 168419799(DOWNSCALED 게이트키퍼), 273564678(INVERSE), DOWNSCALE_30~90
- **메모리 디버깅** (4개): 145634846(GWP-ASAN), 145772972(MTE ASYNC), 177438394(MTE SYNC), 178038272(HEAP_ZERO_INIT)

### 9.4 Task 13: 라이브러리/SDK 호환성 점검

주요 서드파티 SDK에 대한 Android 16 호환성 점검 항목을 정리했습니다.

| SDK 카테고리 | 점검 항목 |
|-----------|---------|
| **Firebase / Crashlytics** | compileSdk 36 빌드, 비 SDK 인터페이스 로그 확인 |
| **광고 SDK (AdMob 등)** | targetSdk 36에서 광고 게재/수익화 정상 동작 |
| **결제 SDK (Play Billing)** | 최신 버전으로 업데이트 필요 가능성 |
| **네트워킹 (OkHttp/Retrofit/Cronet)** | 16KB 페이지 크기 호환성 |
| **이미지 (Glide/Coil/Picasso)** | 네이티브 메모리 정렬 확인 |
| **Compose** | BOM 버전 확인, Compose 1.7+ 권장 |
| **WorkManager** | JobScheduler 할당량 최적화(Phase 1) 영향 확인 |
| **DI (Hilt/Dagger/Koin)** | 컴파일 SDK 변경 이슈 없음 |
| **블루투스 SDK** | 새 인텐트 기반 결합 손실 처리 |

### 9.5 산출물

| 파일 | 경로 | 설명 |
|------|------|------|
| `result.md` | `kanban/boards/os16/workspaces/t_9b3cf067/result.md` | Phase 2 상세 분석 보고서 (17KB) |
| `result.md` | 본 저장소 `work1/result.md` (Section 6) | 작업 요약 기록 |
