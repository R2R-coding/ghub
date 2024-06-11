#!/bin/bash

# Variable definitions
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

# Ask if the user wants to uninstall the program
if ask_question "Do you want to uninstall the $APP_NAME program?"; then
    # Remove the application directory
    if [ -d "$OPT_DIR" ]; then
        sudo rm -rf "$OPT_DIR"
        echo "The directory $OPT_DIR has been removed."
    else
        echo "The directory $OPT_DIR does not exist."
    fi

    # Remove the .desktop file
    if [ -f "$SYSTEM_DESKTOP_FILE" ]; then
        sudo rm "$SYSTEM_DESKTOP_FILE"
        echo "The file $SYSTEM_DESKTOP_FILE has been removed."
    else
        echo "The file $SYSTEM_DESKTOP_FILE does not exist."
    fi
fi

echo "Uninstallation process completed."
