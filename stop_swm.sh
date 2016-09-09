#!/bin/bash
#
# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Software Manager Loader stop script
#

export PYTHONPATH="${PWD}/common/"

echo "Stopping SWM"
python ./package_manager/package_manager.py stop
python ./partition_manager/partition_manager.py stop
python ./module_loader_ecu1/module_loader_ecu1.py stop
python ./software_loading_manager/software_loading_manager.py ${SWLM_ARG} stop
python ./lifecycle_manager/lifecycle_manager.py stop
python ./hmi/hmi.py stop
