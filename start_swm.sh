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
xterm -geometry 80x15+0+0 -T "Package Manager" -e "cd package_manager;python package_manager.py" &
xterm -geometry 80x15+0+300 -T "Partition Manager" -e "cd partition_manaer; python partition_manager.py" &
xterm -geometry 80x15+0+600 -T "ECU1 Module Loader" -e "cd module_loader; python ecu1_module_loader.py" &
xterm -geometry 80x24+800+000 -T "Software Loading Manager" -e "cd software_loading_manager; python software_loading_manager.py" &
echo "Please run"
echo
echo "   python sota_client.py"
echo
echo "to start package use case."
echo 
echo "Press Ctrl-C shut down Software Manager"

xterm -geometry 80x20+800+400 -T "HMI" -e "cd hmi;python hmi.py"



