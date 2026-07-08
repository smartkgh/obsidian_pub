---
title: "Android 16으로 앱 이전"
source: "https://developer.android.com/about/versions/16/migration?hl=ko&_gl=1*33pdec*_up*MQ..*_ga*NTQ0ODA3MzIyLjE3ODMyMzYyNzU.*_ga_6HH9YJMN9M*czE3ODMyMzYyNzUkbzEkZzAkdDE3ODMyMzYyNzUkajYwJGwwJGgxNDY1Mzc2NDg5"
author:
published:
created: 2026-07-05
description: "앱을 Android 16으로 가져오는 단계를 간략히 알아봅니다."
tags:
  - "clippings"
---
이 문서에서는 플랫폼 출시 일정에 잘 맞춰 준비하도록 계획을 수립하는 데 도움을 주고 Android 16에서 사용자의 탁월한 경험을 보장하는 일반적인 개발 및 테스트 단계를 간략하게 보여줍니다.

Android 버전마다 Google은 Android의 유용성, 안전성, 성능을 개선할 수 있도록 새로운 기능과 동작 변경사항을 도입합니다. 대부분의 경우 앱은 처음부터 예상대로 정확하게 작동하지만 어떤 경우에는 개발자가 플랫폼 변경사항에 맞게 앱을 업데이트해야 할 수도 있습니다.

사용자는 소스 코드가 AOSP (Android 오픈소스 프로젝트)에 출시되는 즉시 새로운 플랫폼을 받을 수 있으므로, 앱이 준비되어 사용자를 위해 예상대로 실행되고 새로운 기능과 API를 적절히 활용하여 새로운 플랫폼을 최대한 활용하는 것이 중요합니다.

일반적인 이전에는 동시 실행할 수 있는 다음과 같은 두 단계가 있습니다.

- 앱 호환성 보장 (Android 16 최종 출시까지)
- 새로운 플랫폼 기능 및 API 타겟팅 (최종 출시 후 최대한 빨리)

## Android 16과의 호환성 보장

Android 16에서 기존 앱의 기능을 테스트하여 최신 버전의 Android로 업데이트하는 사용자에게 탁월한 경험을 보장하는 것이 중요합니다. 일부 플랫폼 변경사항은 앱이 동작하는 방식에 영향을 줄 수 있으므로 조기에 철저히 테스트한 다음 필요에 따라 앱을 조정해야 합니다.

일반적으로 앱의 `targetSdkVersion` 을 변경할 필요 없이 앱을 조정하고 업데이트를 게시할 수 있습니다. 마찬가지로 새 API를 사용하거나 앱의 `compileSdkVersion` 을 변경할 필요는 없지만 앱이 빌드된 방식과 앱에서 사용하는 플랫폼 기능에 따라 달라질 수 있습니다.

테스트를 시작하기 전에 [모든 앱의 동작 변경사항](https://developer.android.com/about/versions/16/behavior-changes-all?hl=ko) 을 숙지하시기 바랍니다. 이러한 변경사항은 `targetSdkVersion` 을 변경하지 않더라도 앱에 영향을 미칠 수 있습니다.

Android 16 시스템 이미지를 기기에 플래시하거나 Android Emulator용 시스템 이미지를 다운로드합니다.

시스템 동작 변경사항을 검토하여 앱이 영향을 받을 수 있는 영역을 파악합니다.

기기나 에뮬레이터에 앱을 설치하고 테스트를 실행합니다. 시스템 동작 변경사항에 초점을 맞춰 앱의 모든 흐름을 작동해 봅니다.

동작 변경사항을 적용하거나 문제를 해결하는 데 필요한 코드만 변경합니다. 앱에서 원래 타겟팅한 동일한 API 수준으로 다시 컴파일합니다. Android 16을 타겟팅하지 않아도 됩니다.

게시

업데이트한 Android App Bundle 또는 APK에 서명하고 이를 업로드 및 게시합니다.

### 호환성 테스트

대부분의 경우 Android 16과의 호환성 테스트는 일반 앱 테스트와 유사합니다. 이 시점에서 [핵심 앱 품질 가이드라인](https://developer.android.com/docs/quality-guidelines/core-app-quality?hl=ko) 과 [테스트 권장사항](https://developer.android.com/training/testing?hl=ko) 을 검토하는 것이 좋습니다.

테스트하려면 Android 16을 실행하는 기기에 현재 게시된 앱을 설치하고 문제를 찾는 동안 모든 흐름과 기능을 살펴봅니다. 테스트에 집중할 수 있도록 앱의 작동 방식에 영향을 미치거나 앱이 비정상 종료될 수 있는 Android 16에서 도입된 **[모든 앱의 동작 변경사항](https://developer.android.com/about/versions/16/behavior-changes-all?hl=ko) 을 검토** 합니다.

또한 **[제한된 비 SDK 인터페이스](https://developer.android.com/about/versions/16/changes/non-sdk-16?hl=ko) 사용을 검토하고 테스트** 해야 합니다. 앱에서 사용하는 제한된 인터페이스를 상응하는 공개 SDK 또는 NDK로 바꿔야 합니다. 이러한 액세스를 강조표시하는 logcat 경고가 있는지 살펴보고 `StrictMode` 메서드 [`detectNonSdkApiUsage()`](https://developer.android.com/reference/android/os/StrictMode.VmPolicy.Builder?hl=ko#detectNonSdkApiUsage\(\)) 를 사용하여 프로그래매틱 방식으로 포착합니다.

마지막으로 **앱에서 라이브러리와 SDK를 완전히 테스트** 하여 Android 16에서 예상대로 작동하는지 확인하고 개인 정보 보호, 성능, UX, 데이터 처리, 권한에 관한 권장사항을 준수해야 합니다. 문제를 발견하면 SDK의 최신 버전으로 업데이트하거나 SDK 개발자에게 연락하여 도움을 받으세요.

테스트를 마치고 모든 업데이트를 완료했으면 즉시 호환 가능한 앱을 게시하는 것이 좋습니다. 이렇게 하면 사용자가 앱을 조기에 테스트할 수 있고 사용자가 Android 16으로 업데이트할 때 순조롭게 전환할 수 있습니다.

## 앱의 타겟팅 업데이트 및 새 API로 빌드

호환되는 버전의 앱을 게시하고 나면 다음 단계는 `targetSdkVersion` 을 업데이트하고 Android 16의 새 API와 기능을 활용하여 Android 16을 완벽하게 지원하는 것입니다. 준비가 완료되는 대로 이러한 업데이트를 실행할 수 있으므로 새 플랫폼을 타겟팅하는 [Google Play 요구사항](https://developer.android.com/distribute/play-policies?hl=ko) 을 염두에 두어야 합니다.

Android 16을 완벽하게 지원하는 작업을 계획할 때 [Android 16을 타겟팅하는 앱에 영향을 미치는 동작 변경사항](https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko) 을 검토하세요. 이러한 *타겟팅된 동작 변경사항* 으로 발생할 수 있는 기능 문제를 해결해야 할 수 있습니다. 때에 따라서는 이러한 변경사항에 중요한 개발이 필요하므로 최대한 빨리 변경사항을 알아보고 해결하는 것이 좋습니다. 앱에 영향을 미치는 특정 동작 변경사항을 식별할 수 있도록 [호환성 전환](https://developer.android.com/about/versions/16/migration?hl=ko#using_app_compatibility_toggles) 을 사용하여 선택한 변경사항을 사용 설정한 상태에서 앱을 테스트합니다.

다음 단계에서는 Android 16을 완벽하게 지원하는 방법을 설명합니다.

Android 16으로 빌드하려면 최신 버전의 Android 스튜디오 미리보기를 설치하세요. Android 16 기기 또는 에뮬레이터가 있는지 확인합니다.  
`targetSdkVersion` 및 기타 빌드 구성을 업데이트합니다.

Android 16을 타겟팅하는 앱에 적용되는 동작 변경사항을 검토합니다. 앱이 영향을 받을 수 있는 영역을 식별하고 이를 지원할 방법을 계획합니다.

Android 16의 사용자 개인 정보 보호 변경사항을 지원하는 데 필요한 코드와 아키텍처를 변경합니다.

Android 16 API를 활용하여 앱에 새로운 기능을 추가합니다. Android 16용으로 다시 컴파일합니다.

Android 16 기기 또는 에뮬레이터에서 테스트합니다. 동작 변경사항이 앱에 영향을 미칠 수 있는 영역에 중점을 둡니다. 새 API를 사용하는 기능을 사용해 보고 플랫폼 및 API 관련 의견을 제공합니다. 플랫폼이나 API, 서드 파티 SDK 문제를 신고합니다.

Android 16 API가 최종 완료되면 `targetSdkVersion` 과 기타 빌드 구성을 다시 업데이트하고 추가 업데이트를 실행한 후 앱을 테스트합니다.

게시

업데이트한 Android App Bundle 또는 APK에 서명하고 이를 업로드 및 게시합니다.

### SDK 가져오기, 타겟팅 변경, 새 API로 빌드

완벽한 Android 16 지원 테스트를 시작하려면 최신 미리보기 버전의 Android 스튜디오를 사용하여 Android 16 SDK 및 기타 필요한 도구를 다운로드하세요. 다음으로 앱의 `targetSdkVersion` 과 `compileSdkVersion` 을 업데이트하고 앱을 다시 컴파일합니다. 자세한 내용은 [SDK 설정 가이드](https://developer.android.com/about/versions/16/setup-sdk?hl=ko) 를 참고하세요.

### Android 16 앱 테스트

앱을 컴파일하고 Android 16을 실행하는 기기에 설치했다면 테스트를 시작하여 앱이 Android 16을 타겟팅할 때 적절하게 작동하는지 확인합니다. 일부 동작 변경사항은 앱이 새 플랫폼을 타겟팅하는 경우에만 적용되므로 시작하기 전에 [변경사항을 검토](https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko) 하는 것이 좋습니다.

기본 호환성 테스트와 마찬가지로 문제를 찾는 모든 흐름과 기능을 살펴봅니다. 테스트에서 **[Android 16을 타겟팅하는 앱의 동작 변경사항](https://developer.android.com/about/versions/16/behavior-changes-16?hl=ko)** 에 초점을 둡니다. [핵심 앱 품질 가이드라인](https://developer.android.com/docs/quality-guidelines/core-app-quality?hl=ko) 과 [테스트 권장사항](https://developer.android.com/training/testing?hl=ko) 에 따라 앱을 확인하는 것도 좋습니다.

적용할 수 있는 **[제한된 비 SDK 인터페이스](https://developer.android.com/about/versions/16/changes/non-sdk-16?hl=ko) 의 사용을 검토하고 테스트** 해야 합니다. 이러한 액세스를 강조 표시하는 logcat 경고가 있는지 살펴보고 StrictMode 메서드 [`detectNonSdkApiUsage()`](https://developer.android.com/reference/android/os/StrictMode.VmPolicy.Builder?hl=ko#detectNonSdkApiUsage\(\)) 를 사용하여 프로그래매틱 방식으로 포착합니다.

마지막으로 **앱에서 라이브러리와 SDK를 완전히 테스트** 하여 Android 16에서 예상대로 작동하는지 확인하고 개인 정보 보호, 성능, UX, 데이터 처리, 권한에 관한 권장사항을 준수해야 합니다. 문제를 발견하면 SDK의 최신 버전으로 업데이트하거나 SDK 개발자에게 연락하여 도움을 받으세요.

### 앱 호환성 전환을 사용하여 테스트

Android 16에는 타겟팅된 동작 변경사항으로 쉽게 앱을 테스트할 수 있는 호환성 전환이 포함되어 있습니다. 디버그 가능한 앱의 경우 전환을 통해 다음을 실행할 수 있습니다.

- **앱의 targetSdkVersion을 실제로 변경하지 않고 타겟팅된 변경사항을 테스트합니다**. 전환을 사용해 타겟팅된 특정 동작 변경사항을 강제로 사용 설정하여 기존 앱에 미치는 영향을 평가할 수 있습니다.
- **테스트에서 특정 변경사항에만 중점을 둡니다**. 타겟팅된 모든 변경사항을 한 번에 처리할 필요 없이 전환을 사용하면 테스트하려는 변경사항을 제외하고 타겟팅된 모든 변경사항을 사용 중지할 수 있습니다.
- **adb를 통해 전환을 관리합니다**. adb 명령어를 사용하여 자동화된 테스트 환경에서 전환 가능한 변경사항을 사용 설정하거나 사용 중지할 수 있습니다.
- **표준 변경 ID를 사용하여 더 빠르게 디버그합니다**. 전환 가능한 각 변경사항에는 로그 출력에서 근본 원인을 빠르게 디버그하는 데 사용할 수 있는 고유 ID와 이름이 있습니다.

앱의 타겟팅 변경을 준비할 때 또는 Android 16 지원을 개발하는 동안 전환이 도움이 될 수 있습니다. 자세한 내용은 [호환성 프레임워크 변경사항 (Android 16)](https://developer.android.com/about/versions/16/reference/compat-framework-changes?hl=ko) 을 참고하세요.