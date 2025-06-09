#!/bin/bash

GITK_TEXTDOMAIN="gitk"

detect_os() {
    case "$OSTYPE" in
        darwin*) OS="macos" ;;
        linux-gnu*) OS="linux" ;;
        msys*|cygwin*) OS="windows" ;;
        freebsd*) OS="freebsd" ;;
        *) OS="unknown" ;;
    esac
}

setup_locale_paths() {
    detect_os

    case "$OS" in
        macos)
            POSSIBLE_LOCALE_DIRS=(
                "/opt/homebrew/share/locale"
                "/usr/local/share/locale"
                "$HOME/.local/share/locale"
            )
            ;;
        linux|freebsd)
            POSSIBLE_LOCALE_DIRS=(
                "/usr/share/locale"
                "/usr/local/share/locale"
                "$HOME/.local/share/locale"
            )
            ;;
        windows)
            POSSIBLE_LOCALE_DIRS=(
                "/usr/share/locale"
                "/mingw64/share/locale"
                "$HOME/.local/share/locale"
            )
            ;;
        *)
            POSSIBLE_LOCALE_DIRS=(
                "/usr/local/share/locale"
                "/usr/share/locale"
                "$HOME/.local/share/locale"
            )
            ;;
    esac
}

check_gettext_availability() {
    if command -v gettext > /dev/null 2>&1; then
        USE_GETTEXT=true
        return 0
    fi

    for path in /opt/homebrew/bin /usr/local/bin /mingw64/bin /usr/bin; do
        if [[ -x "$path/gettext" ]]; then
            export PATH="$path:$PATH"
            USE_GETTEXT=true
            return 0
        fi
    done

    USE_GETTEXT=false
    return 1
}


detect_language() {
    local lang_vars=("$LC_ALL" "$LANGUAGE" "$LC_MESSAGES" "$LANG" "$GITK_LANG")
    for var in "${lang_vars[@]}"; do
        if [[ -n "$var" ]]; then
            DETECTED_LANG="${var%%.*}"
            return 0
        fi
    done

    DETECTED_LANG="en" #default lang
}


init_i18n() {
    setup_locale_paths
    detect_language
    check_gettext_availability

    GITK_LOCALEDIR=""

    if [[ -d "./i18n/locale" ]]; then
        GITK_LOCALEDIR="$(pwd)/i18n/locale"
    else
        for dir in "${POSSIBLE_LOCALE_DIRS[@]}"; do
            if [[ -d "$dir" ]]; then
                GITK_LOCALEDIR="$dir"
                break
            fi
        done
    fi

    export TEXTDOMAIN="$GITK_TEXTDOMAIN"
    export TEXTDOMAINDIR="$GITK_LOCALEDIR"

    if [[ "$USE_GETTEXT" != "true" ]]; then
        echo "Warning: gettext not available — fallback to English"
    fi

    if [[ "$DETECTED_LANG" != "en" && -d "$GITK_LOCALEDIR/$DETECTED_LANG" ]]; then
        export LANG="${DETECTED_LANG}.UTF-8"
    fi
}

t() {
    if [[ "$USE_GETTEXT" == "true" ]]; then
        gettext "$1"
    else
        echo "$1"
    fi
}

tln() {
    if [[ -z "$1" ]]; then
        echo
    elif [[ "$USE_GETTEXT" == "true" ]]; then
        gettext "$1"
        echo
    else
        echo "$1"
    fi
}


tf() {
    local fmt="$1"; shift
    if [[ "$USE_GETTEXT" == "true" ]]; then
        printf "$(gettext "$fmt")" "$@"
    else
        printf "$fmt" "$@"
    fi
}

