#!/bin/bash

set -e -o pipefail

if [ "$#" -gt 0 ]; then
    echo "Добавляю указанные файлы: $@"
    git add "$@"
elif [ "$#" -eq 1 ] && [ "$1" = "." ]; then
    echo "Добавляю все изменени (git add .)" 
    git add .
else 
    echo "Не переданы файлы для добавления в индекс."
fi

echo -e "\nФайлы в индексе:"
git diff --cached --name-only

