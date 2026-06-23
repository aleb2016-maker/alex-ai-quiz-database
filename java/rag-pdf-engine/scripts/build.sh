#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
bash scripts/download_pdfbox.sh
rm -rf build
mkdir -p build/classes
echo "Compilo motore PDF Java V19..."
javac -encoding UTF-8 -cp lib/pdfbox-app-2.0.36.jar -d build/classes $(find src/main/java -name "*.java")
echo "OK compilazione completata."
