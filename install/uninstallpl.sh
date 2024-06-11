#!/bin/bash

# Definicja zmiennych
APP_NAME="ghub"
OPT_DIR="/opt/$APP_NAME"
SYSTEM_DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"

# Funkcja wyświetlająca pytanie i oczekująca na odpowiedź
ask_question() {
    while true; do
        read -p "$1 (t/n): " yn
        case $yn in
            [Tt]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Proszę odpowiedzieć 't' lub 'n'.";;
        esac
    done
}

# Zapytaj, czy odinstalować program
if ask_question "Czy chcesz odinstalować program $APP_NAME?"; then
    # Usuń katalog z aplikacją
    if [ -d "$OPT_DIR" ]; then
        sudo rm -rf "$OPT_DIR"
        echo "Katalog $OPT_DIR został usunięty."
    else
        echo "Katalog $OPT_DIR nie istnieje."
    fi

    # Usuń plik .desktop
    if [ -f "$SYSTEM_DESKTOP_FILE" ]; then
        sudo rm "$SYSTEM_DESKTOP_FILE"
        echo "Plik $SYSTEM_DESKTOP_FILE został usunięty."
    else
        echo "Plik $SYSTEM_DESKTOP_FILE nie istnieje."
    fi
fi

echo "Proces deinstalacji zakończony."
