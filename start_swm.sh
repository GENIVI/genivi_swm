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

export PYTHONPATH="${PWD}/common/"

python -c "import settings,sys; sys.exit(settings.SQUASHFS_FUSE)"
if [ "$?" == "0" ] ; then
    echo "Using root mount..."
    if [ "$(id -u)" != "0" ] ; then
        echo "How about sudo..."
        exit 1
    fi
else
    echo "Using user mount..."
    MOUNT_CMD=`python -c "import settings; print settings.SQUASHFS_MOUNT_CMD"`
    UNMOUNT_CMD=`python -c "import settings; print settings.SQUASHFS_UNMOUNT_CMD"`
    command -v $MOUNT_CMD >/dev/null 2>&1 && command -v $UNMOUNT_CMD >/dev/null 2>&1
    if [ $? != 0 ] ; then
        echo "Need $MOUNT_CMD and $UNMOUNT_CMD for user mount."
        exit 1
    fi
fi

usage() {
	echo "Usage: ${0} [-r] [-i]"
	echo "  -r    Reset completed operation database"
	echo "  -i    Run in interactive mode. Start sota_client separately"
	exit 255
}

SWLM_ARG=""
INTERACTIVE=false
while getopts ":ri" opt; do
  case $opt in
    r)
		SWLM_ARG="-r"
		;;
	i)
		INTERACTIVE="true"
		;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      ;;
  esac
done

rm -f $PID_FNAME
gnome-terminal --geometry 80x15+0+0 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Package Manager\007\"; cd package_manager;python package_manager.py" &

gnome-terminal --geometry 80x15+0+500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Partition Manager\007\";cd partition_manager; python partition_manager.py"

gnome-terminal --geometry 80x15+0+1000 -x \bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;ECU1 Module Loader\007\"; cd module_loader_ecu1; python module_loader_ecu1.py"

gnome-terminal --geometry 80x24+0+1500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Software Loading Manager\007\";cd software_loading_manager; python software_loading_manager.py ${SWLM_ARG}"

gnome-terminal --geometry 80x15+0+2000  -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;Lifecycle Manager\007\";cd lifecycle_manager; python lifecycle_manager.py"

gnome-terminal --geometry 80x20+0+2500 -x bash -c "echo \$BASHPID >> $PID_FNAME; echo -ne \"\033]0;HMI\007\";cd hmi;python hmi.py"

trap killswm INT

if [ "${INTERACTIVE}" = "false" ]
then
	cd sota_client
	echo "Running SOTA client with HMI user confirmation turned off. Use -c to turn on"
	python sota_client.py -u sample_app_1.2.3 -i ../sample_update.upd -s xxx -d "Sample Update Description"
	read x
	killswm
	exit 0
fi

echo "Please run"
echo
echo "   cd sota_client"
echo "   sudo PYTHONPATH=\"\${PWD}/../common/\" python sota_client.py -u sample_app_1.2.3 -c -i ../sample_update.upd -s xxx -d \"Sample Update Description\""
echo
echo "to start package use case."
echo 
echo "Press Enter shut down Software Manager"



read x
killswm


