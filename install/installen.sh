#!/bin/bash

# Definition of variables
APP_NAME="ghub"
OPT_DIR="/opt/ghub"
SYSTEM_DESKTOP_FILE="/usr/share/applications/$APP_NAME.desktop"

# Function to display a question and wait for an answer
ask_question() {
    while true; do
        read -p "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer 'y' or 'n'.";;
        esac
    done
}

# Ask if the program should be installed
if ask_question "Do you want to install the program $APP_NAME?"; then
    INSTALL=true
else
    INSTALL=false
fi

# Ask if a shortcut should be created in the application menu
if ask_question "Do you want to create a shortcut in the application menu?"; then
    CREATE_SHORTCUT=true
else
    CREATE_SHORTCUT=false
fi

# Program installation
if [ "$INSTALL" = true ]; then
    sudo mkdir -p "$OPT_DIR"
    sudo cp -r ./* "$OPT_DIR/"
    echo "The program has been installed in $OPT_DIR."

    # Create .desktop file with dynamic path
    TEMP_DESKTOP_FILE="/tmp/$APP_NAME.desktop"
    cat <<EOL > "$TEMP_DESKTOP_FILE"
[Desktop Entry]
Version=1.0
Name=GHub
Comment=GitHub Utility Application
Exec=$OPT_DIR/install/starten.sh
Icon=$OPT_DIR/install/ghublogo.png
Terminal=false
Type=Application
Categories=Utility;
EOL

    chmod +x "$TEMP_DESKTOP_FILE"
    echo "The .desktop file has been created at $TEMP_DESKTOP_FILE."

    # Create a shortcut in the application menu
    if [ "$CREATE_SHORTCUT" = true ]; then
        sudo cp "$TEMP_DESKTOP_FILE" "$SYSTEM_DESKTOP_FILE"
        echo "The .desktop file has been copied to $SYSTEM_DESKTOP_FILE."
    fi
fi

echo "Installation process completed."
