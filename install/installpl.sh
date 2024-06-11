#!/bin/bash

# Definicja zmiennych
APP_NAME="ghub"
OPT_DIR="/opt/ghub"
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

# Zapytaj, czy zainstalować program
if ask_question "Czy chcesz zainstalować program $APP_NAME?"; then
    INSTALL=true
else
    INSTALL=false
fi

# Zapytaj, czy utworzyć skrót w menu aplikacji
if ask_question "Czy chcesz utworzyć skrót w menu aplikacji?"; then
    CREATE_SHORTCUT=true
else
    CREATE_SHORTCUT=false
fi

# Instalacja programu
if [ "$INSTALL" = true ]; then
    sudo mkdir -p "$OPT_DIR"
    sudo cp -r ./* "$OPT_DIR/"
    echo "Program został zainstalowany w $OPT_DIR."

    # Tworzenie pliku .desktop z dynamiczną ścieżką
    TEMP_DESKTOP_FILE="/tmp/$APP_NAME.desktop"
    cat <<EOL > "$TEMP_DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Name=GHub
Comment=GitHub Utility Application
Exec=$OPT_DIR/install/startpl.sh
Icon=$OPT_DIR/install/ghublogo.png
Terminal=false
Type=Application
Categories=Utility;
EOL

    chmod +x "$TEMP_DESKTOP_FILE"
    echo "Plik .desktop został utworzony w $TEMP_DESKTOP_FILE."

    # Tworzenie skrótu w menu aplikacji
    if [ "$CREATE_SHORTCUT" = true ]; then
        sudo cp "$TEMP_DESKTOP_FILE" "$SYSTEM_DESKTOP_FILE"
        echo "Plik .desktop został skopiowany do $SYSTEM_DESKTOP_FILE."
    fi
fi

echo "Proces instalacji zakończony."
