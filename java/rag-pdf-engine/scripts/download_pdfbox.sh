#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
mkdir -p lib
JAR="lib/pdfbox-app-2.0.36.jar"
if [ -f "$JAR" ]; then
  echo "PDFBox gia presente: $JAR"
  exit 0
fi
echo "Scarico Apache PDFBox 2.0.36..."
curl -L -o "$JAR" "https://archive.apache.org/dist/pdfbox/2.0.36/pdfbox-app-2.0.36.jar"
echo "OK scaricato: $JAR"
