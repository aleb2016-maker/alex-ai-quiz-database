#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if [ "$#" -lt 2 ]; then
  echo "Uso: bash scripts/run_from_json.sh input.json output.pdf"
  exit 1
fi
bash scripts/build.sh
java -cp "build/classes:lib/pdfbox-app-2.0.36.jar" com.alex.pdf.Main "$1" "$2"
