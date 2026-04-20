# Android App Scaffold (Kotlin + C++ + Jetpack Compose)

This Android app uses Kotlin with Jetpack Compose and integrates native C++ through JNI/CMake.

## Included mandatory build files
- `android/settings.gradle.kts`
- `android/build.gradle.kts`
- `android/gradle.properties`
- `android/gradlew`
- `android/gradlew.bat`
- `android/gradle/wrapper/gradle-wrapper.properties`
- `android/app/build.gradle.kts`
- `android/app/src/main/AndroidManifest.xml`
- `android/app/src/main/cpp/CMakeLists.txt`

## Native integration files
- `android/app/src/main/cpp/native-lib.cpp`
- `android/app/src/main/java/com/aiagent/MainActivity.kt`

## Build
```bash
cd android
./gradlew assembleDebug
```
