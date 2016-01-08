#!/bin/bash
#
# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Ubuntu Software Manager Loader launch script
#

PID_FNAME=/tmp/swm_pidlist

killswm () {
	for i in $(cat $PID_FNAME); do
		kill $i
	done
	exit 0
}

if [ "$(id -u)" != "0" ]
then
	echo "How about sudo..."
	exit 1
fi

rm -f $PID_FNAME
gnome-terminal --geometry 80x15+0+0 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Package Manager\007\"; cd package_manager;python package_manager.py" 

gnome-terminal --geometry 80x15+0+500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Partition Manager\007\";cd partition_manager; python partition_manager.py" 

gnome-terminal --geometry 80x15+0+1000 -x \bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;ECU1 Module Loader\007\"; cd module_loader_ecu1; python module_loader_ecu1.py" 


gnome-terminal --geometry 80x24+0+1500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Software Loading Manager\007\";cd software_loading_manager; python software_loading_manager.py" 

gnome-terminal --geometry 80x15+0+2000  -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Lifecycle Manager\007\";cd lifecycle_manager; python lifecycle_manager.py" 

gnome-terminal --geometry 80x20+0+2500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;HMI\007\";cd hmi;python hmi.py" 

if [ "$1" != "-i" ]
then
	cd sota_client
	python sota_client.py -p test_package -i ../sample_update.upd -s xxx -d "Sample Update Description"
	killswm
	exit 0
fi

echo "Please run"
echo
echo "   cd sota_client"
echo "   sudo python sota_client.py -p test_package -i ../sample_update.upd -s xxx -d "Sample Update Description""
echo
echo "to start package use case."
echo 
echo "Press Enter shut down Software Manager"

trap killswm INT

read x
killswm
