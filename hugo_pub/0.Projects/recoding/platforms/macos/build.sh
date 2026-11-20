#!/bin/bash
# SpeechHelper 빌드 (macOS 26+ / Swift 6.3+)
set -euo pipefail
cd "$(dirname "$0")"

mkdir -p .build
swiftc -O -parse-as-library \
    -target arm64-apple-macosx26.0 \
    -o .build/SpeechHelper \
    SpeechHelper.swift

echo "built: $(pwd)/.build/SpeechHelper"
