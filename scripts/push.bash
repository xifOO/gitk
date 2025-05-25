#!/bin/bash

set -e -o pipefail

remotes=($(git remote))
remote_count=${#remotes[@]}

if [ "$remote_count" -eq 0 ]; then
    echo "Нет настроенных удаленных репозиториев (remotes)."
    exit 1
elif [ "$remote_count" -eq 1]; then
    remote=${remotes[0]}
    echo "Используется remote: $remote"
else 
    echo "Найдено несколько remotes:"
    for i in "${!remotes[@]}"; do 
        echo "$((i + 1)) ${remotes[@i]}"
    done


    while true; do
        read -p "Выберите номер remote для push: " index
        if [[ "$index" =~ ^[0-9]+$ ]] && [ "$index" -ge 1 ] && [ "$index" -le "$remote_count" ]; then
            remote=${remotes[$((index - 1))]}
            echo "Выбран remote: $remote"
            break
        else
            echo "Неверный ввод"
        fi
    done
fi

default_branch=$(git remote show origin | grep 'HEAD branch' | awk '{print $NF}')

flags=()
branch=""

for arg in "$@"; do
    if [[ "$arg" == --* ]]; then
        flags+=("$arg")
    elif [ -z "$branch" ]; then
        branch="$arg"
    fi
done

if [ -z "$branch" ]; then
    read -p "Введите имя ветки для push [по умолчанию: $default_branch]: " branch
    branch=${branch:-$default_branch}
    echo "Ветка не указана. Используем: $branch"
else
    branch=$1
    echo "Используем ветку: $branch"
fi

echo "git push $remote $branch ${flags[*]}"
git push "$remote" "$branch" "${flags[@]}"


