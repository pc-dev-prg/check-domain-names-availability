#!/usr/bin/env bash

set -e

echo "🔧 Kontroluji virtuální prostředí…"

if [ ! -d ".venv" ]; then
  echo "📦 Vytvářím .venv…"
  python3 -m venv .venv
else
  echo "✔️  .venv už existuje."
fi

echo "🚀 Aktivace virtuálního prostředí…"
source .venv/bin/activate

echo "⬆️  Aktualizuji pip…"
python -m pip install --upgrade pip

echo "📥 Instalování závislostí…"
python -m pip install python-whois colorama

echo ""
echo "🎉 Hotovo!"
echo "➡️  Pro aktivaci prostředí spusť:"
echo "   source .venv/bin/activate"