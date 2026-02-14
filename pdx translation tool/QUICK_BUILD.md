# Quick Build Guide - PDX Mod Translator

이 가이드는 PDX Mod Translator를 EXE 파일로 빌드하는 가장 빠른 방법을 설명합니다.

## Windows 사용자

### 단계 1: 필수 프로그램 설치
- Python 3.7 이상이 설치되어 있어야 합니다
- [Python 다운로드](https://www.python.org/downloads/)

### 단계 2: 빌드 실행
1. 명령 프롬프트(CMD)를 엽니다
2. 다음 명령을 실행합니다:
```cmd
cd "pdx translation tool"
build_exe.bat
```

### 단계 3: 완료!
- `dist\PDX_Mod_Translator.exe` 파일이 생성됩니다
- 이 파일을 원하는 곳에 복사하여 사용하세요

## Linux / macOS 사용자

### 단계 1: 빌드 실행
터미널에서 다음 명령을 실행합니다:
```bash
cd "pdx translation tool"
chmod +x build_exe.sh
./build_exe.sh
```

### 단계 2: 완료!
- `dist/PDX_Mod_Translator` 파일이 생성됩니다

## 자동 빌드 (GitHub Actions)

태그를 푸시하면 자동으로 빌드됩니다:

```bash
git tag v1.0.0
git push origin v1.0.0
```

빌드된 파일은 GitHub Release 페이지에서 다운로드할 수 있습니다.

---

더 자세한 정보는 [BUILD.md](BUILD.md)를 참조하세요.
