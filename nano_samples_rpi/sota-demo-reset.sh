#!/bin/bash

echo "Resetting SOTA demo..."

# Remove GENIVI SWM database and restart systemd service
echo "Removing GENIVI SWM database..."

if [ -e /var/run/swlm.sqlite ]; then
    systemctl stop software_loading_manager
    rm /var/run/swlm.sqlite
    systemctl start software_loading_manager
fi

# Remove nano and ncurses-terminfo
echo "Removing installed packages..."

if rpm -q nano 2>&1 > /dev/null; then
    rpm -e nano
fi

if rpm -q ncurses-terminfo 2>&1 > /dev/null; then
    rpm -e ncurses-terminfo
fi

echo "Done."
