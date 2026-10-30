#!/bin/sh
# Download the fonts Kuronuri is built from into sources/.
#   Redaction 2.001 by MCKL: https://www.redaction.us
#   Noto Serif JP 2.003 (variable) from Google Fonts
set -eu
cd "$(dirname "$0")/.."

REDACTION_URL=https://www.redaction.us/static/redaction.zip
REDACTION_SHA256=3bc97cfd8e6a9611ab71e7288cdc564ec8f68d11fa461ad0be82f6d5e67bd585
NOTO_URL=https://raw.githubusercontent.com/google/fonts/8a7c74854f766ae441c7584925cc0ec626fc5aa6/ofl/notoserifjp
NOTO_SHA256=2fd527ba12b6a44ec30d796d633360da0aeba6c5d4af1304ce12bb4dc15a7dfc

check() {
	echo "$2  $1" | shasum -a 256 -c - >/dev/null || { echo "checksum mismatch: $1" >&2; exit 1; }
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

rm -rf sources/redaction sources/noto-serif-jp
mkdir -p sources/redaction sources/noto-serif-jp

echo "Downloading Redaction"
curl -fsSL -o "$tmp/redaction.zip" "$REDACTION_URL"
check "$tmp/redaction.zip" "$REDACTION_SHA256"
unzip -q "$tmp/redaction.zip" -d "$tmp" -x '__MACOSX/*'
unzip -q "$tmp/redaction/Redaction_2_001.zip" -d sources/redaction -x '__MACOSX/*' '*.DS_Store'
cp "$tmp/redaction/OFL.txt" sources/redaction/

echo "Downloading Noto Serif JP"
curl -fsSL -o "sources/noto-serif-jp/NotoSerifJP[wght].ttf" "$NOTO_URL/NotoSerifJP%5Bwght%5D.ttf"
check "sources/noto-serif-jp/NotoSerifJP[wght].ttf" "$NOTO_SHA256"
curl -fsSL -o sources/noto-serif-jp/OFL.txt "$NOTO_URL/OFL.txt"

echo "Sources ready in sources/"
