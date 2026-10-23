#!/bin/sh
# Добавляет «Заметки» в меню приложений текущего пользователя.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$APPS"
sed "s|@DIR@|$DIR|g" "$DIR/notes-paper.desktop.in" > "$APPS/notes-paper.desktop"
chmod +x "$APPS/notes-paper.desktop" "$DIR/Notes/Notes"
command -v update-desktop-database >/dev/null 2>&1 && update-desktop-database "$APPS" || true
echo "Готово: «Заметки» появились в меню приложений. / Done: Notes is now in your app menu."
