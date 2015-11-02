#!/bin/sh
#
# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Ubuntu Software Manager Loader launch script
#


# We use xterm since there is no way of putting gnome-terminal in the
# foreground.
xterm -T "Package Manager" -e python package_manager.py &
xterm -T "Partition Manager" -e python partition_manager.py &
xterm -T "ECU1 Module Loader" -e python ecu1_module_loader.py &
xterm -T "Software Loading Manager" -e python software_loading_manager.py
xterm -T "HMI" -e python hmi.py

echo "Press Ctrl-C shut down Software Manager"
