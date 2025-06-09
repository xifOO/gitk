#!/bin/bash

set -e -o pipefail

LOCALES_DIR="i18n/locale"
TEMPLATE="$LOCALES_DIR/template.pot"

mkdir -p "$LOCALES_DIR"

check_xgettext() {
    if ! command -v xgettext >/dev/null 2>&1; then
        case "$OSTYPE" in
            "darwin"*)
                echo "Error: xgettext not found. Install with: brew install gettext"
                echo "And add to PATH: export PATH=\"/opt/homebrew/bin:\$PATH\""
                ;;
            "linux-gnu"*)
                echo "Error: xgettext not found. Install gettext-dev package"
                ;;
            "msys"|"cygwin")
                echo "Error: xgettext not found. Install with: pacman -S gettext-devel"
                ;;
            "freebsd"*)
                echo "Error: xgettext not found. Install with: sudo pkg install gettext-tools"
                ;;
            *)
                echo "Error: xgettext not found. Install gettext package."
                ;;
        esac
        return 1
    fi
    return 0
}

if ! check_xgettext; then
    exit 1
fi

SOURCE_FILES=$(find bin scripts -name "*.sh")

if [[ -z "$SOURCE_FILES" ]]; then
    echo "No shell files found in bin/ or scripts/"
    exit 1
fi

xgettext \
    --language=Shell \
    --keyword=t \
    --keyword=tln \
    --keyword=tf \
    --from-code=UTF-8 \
    --output="$TEMPLATE.tmp" \
    $SOURCE_FILES

{
    echo "# This file was generated on $(date) on $OSTYPE"
    echo "# xgettext version: $(xgettext --version | head -n1)"
    echo ""
    cat "$TEMPLATE.tmp"
} > "$TEMPLATE"

rm "$TEMPLATE.tmp"

echo "Template updated: $TEMPLATE"
echo "Generated on: $OSTYPE with $(xgettext --version | head -n1)"
