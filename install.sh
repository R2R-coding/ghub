#!/bin/bash

# Check if dialog is installed
if ! command -v dialog &> /dev/null
then
    echo "Dialog is not installed. Please install it using: sudo apt-get install dialog"
    exit 1
fi

# Unzip ghubenv.zip
if [ -f "ghubenv.zip" ]; then
    unzip -o ghubenv.zip
    if [ $? -ne 0 ]; then
        echo "Failed to unzip ghubenv.zip. Exiting."
        exit 1
    fi
else
    echo "ghubenv.zip not found. Exiting."
    exit 1
fi

# Create a menu using dialog
CHOICE=$(dialog --clear --backtitle "Language Selection" \
--title "Choose language" \
--menu "Select an option:" 15 40 4 \
1 "english" \
2 "polish" \
3>&1 1>&2 2>&3 3>&-)

# Capture the exit status of dialog (e.g., if the user presses ESC)
EXIT_STATUS=$?
clear

if [ $EXIT_STATUS -eq 1 ]; then
    echo "No option selected. Exiting."
    exit 1
fi

# Execute the appropriate script based on the user's choice
case $CHOICE in
    1)
        ./install/installen.sh
        ;;
    2)
        ./install/installpl.sh
        ;;
    *)
        echo "Invalid option selected. Exiting."
        exit 1
        ;;
esac
