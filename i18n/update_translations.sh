#!/bin/bash

set -e 

LOCALES=("ru", "en")
LOCALES_DIR="i18n/locales"
TEMPLATE="$LOCALES_DIR/template.pot"


check_tools() {
    local missing=()

    for tool in msgmerge msginit msgfmt; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            missing+=("$tool")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "Missing tools: ${missing[*]}"
        case "$OSTYPE" in
            darwin*) echo "Install with: brew install gettext" ;;
            linux*) echo "Install gettext package" ;;
            msys*|cygwin) echo "pacman -S gettext-devel" ;;
            *) echo "Install gettext manually" ;;
        esac
        return 1

    fi
    return 0
}

LOCALES_DIR="i18n/locale"
TEMPLATE="$LOCALES_DIR/template.pot"


if ! check_tools; then
    exit 1
fi


if [[ ! -f "$TEMPLATE" ]]; then
    echo "Error: Template file not found: $TEMPLATE"
    echo "Run ./i18n/extract_strings.sh first"
    exit 1
fi


for lang in ru en; do
    lang_dir="$LOCALES_DIR/$lang/LC_MESSAGES"
    po_file="$lang_dir/gitk.po"
    mo_file="$lang_dir/gitk.mo"
    
    mkdir -p "$lang_dir"
    
    if [[ -f "$po_file" ]]; then
        cp "$po_file" "$po_file.backup"
        
        if msgmerge --update "$po_file" "$TEMPLATE"; then
            echo "Updated: $po_file"
            rm "$po_file.backup"
        else
            echo "Error updating $po_file, restoring backup"
            mv "$po_file.backup" "$po_file"
            continue
        fi
    else
        if msginit --input="$TEMPLATE" --output-file="$po_file" --locale="$lang" --no-translator; then
            echo "Created: $po_file"
        else
            echo "Error creating $po_file"
            continue
        fi
    fi
    
    if msgfmt "$po_file" --output-file="$mo_file"; then
        echo "Compiled: $mo_file"
    else
        echo "Error compiling $po_file"
    fi
done

echo "Translation update completed on $OSTYPE"