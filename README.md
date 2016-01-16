
Copyright (C) 2014-2015 Jaguar Land Rover

This document is licensed under Creative Commons
Attribution-ShareAlike 4.0 International.

# TODO
1. **Implement get installed packages use case**<br>
   ```module_loader_ecu1.py``` needs to correctly implement ```get_module_firmware_version()```.
   ```package_manager.py``` needs to correctly implement ```get_installed_packages()```.
   ```software_loading_manager.py``` needs to implement ```get_installed_software()```, which means
   invoking ```package_manager.get_installed_packages()``` and ```get_module_firmware_version()```
   of each module loader instance. There is today no tracking in ```software_loading_manager.py```
   of deployed module loaders. Maybe extend ```SoftwareOperation.operation_descriptor```?

2. Implement blacklists
Package Manager's ```install_package``` and ```update_package``` needs to verify that the package in the ```image_path``` 
argument is not present in the list of banned packages in the ```blacklist``` argument.

3. 
Signatures
Check confirmation
Local Media
Clean up manifest
get_installed_packages()
Parse and use show_progress and show_result
blacklist persistence, replacing with newever versions
abort_download
ReAdd user confirmation for local media case
install_pacakge(): Allow downgrade
2. 
# ACRONYM

Acronym  | Description
-------- | -----------
SWM      | Software Management
SC       | Sota Client
SLM      | Software Loading Managent
PkgMgr   | Package Manager
PartMgr  | Partition Manager
ML       | Module Loader
HMI      | Human Machine Interface
LCMgr    | Life Cycle Manager

# GENIVI SOFTWARE MANAGEMENT - PROOF OF CONCEPT #
This directory contains a set of python components that are used to
explore the API between the components forming the Software Management
system.

The components are outlined in the image below

![SWM Layout](https://github.com/magnusfeuer/genivi_software_management/raw/master/swm_illustration.png)
The components are as follows:

## SOTA Client - SC [sota\_client.py] ##
SC simulator, to be replaced by the real GENIVI Sota Client developed
by Advanced Telematic Systems, is a command line tool that launches
the SWM use cases.

The SC simulator has the following features

1. **Notify SWM of available updates**<br>
   A notification about the available package, specified at the command line,
   will be sent to SLM for user confirmation.

2. **Download the package**<br>
   Once a confirmation has been received from SLM, SC will be asked by SLM
   to initiate the download of the package. The download will be simulated
   with a 5 second progress bar.

3. **Send the package for processing**<br>
   Once the download has completed, the package is sent by SC to SLM for processing.

4. **Handle installation report**<br>
   Once the package operation has completed, SLM will forward an installation report to SC,
   which will present it as output before exitin.

5. **Get installed packages**<br>
   A separate use case allows the command line to request all currently installed
   packages in PkgMgr, PartMgr, or ML.

## Software Loading Manager - SLM [software\_loading\_manager.py] ##
SLM coordinates all use cases in SWM. SC Initiates these use cases
through command line parameters

SLM has the following features

1. **Retrieve user approval for packages**<br>
   When a package notification is received from SC, the notification will be
   forwarded to HMI for a user approval. 

2. **Signal SC to start download**<br>
   When SLM receives a package confirmation from HMI, the SC will be signalled to
   initiate the download.

3. **Process downloaded packages**<br>
   Once a download is complete, SC will send a process package command to SLM.
   SLM will forward the command to the approrpiate target, which can be
   PartMgr for partition operations, PackMgr fo package manager, or ML for
   the module loader

4. **Handle installation report**<br>
   When a target has processed a package it will wend back a installation report
   to SLM, which will forward it to HMI, to inform the user, and SC, to inform
   the server.

5. **Get installed packages**<br>
   When a get installed packages command is received from SC, it will be forwarded to
   the package manaager to retrieve a list of all installed packages.


## Human Machine Interface - HMI [hmi.py] ##
HMI is responsible for reqtrieving a user approval (or decline) on
a package installation, and to show the user the result of a package
operation.

HMI has the following features

1. **Retrieve user approval for packages**<br>
   SLM will send a package notification to HMI, which will
   ask the user if the package operation is to be carried out or not.
   The user input (approve or decline) is forwarded as a package confirmation
   to SLM

2. **Show package operation result**<br>
   Once a package operation has been carried out by PkgMgr, PartMgr, or ML,
   the result will be forwarded to HMI to inform the ser.


## Package Manager - PackMgr [package\_manager.py] ##
PackMgr is responsible for processing packages forwarded to it by SLM.
It can also report all currently installed packages.

PackMgr has the following features

1. **Process package**<br>
   SLM will send a process package command to PackMgr, which
   will simulate a five second install time and then send
   back a installation report.

2. **Get installed packages**<br>
   PackMgr will send back a static list of currently installed packages.


## Partition Manager - PartMgr [partition\_manager.py] ##
PartMgr is responsible for processing packages forwarded to it by SLM.
It can also report all currently installed packages.

PartMgr has the following features

1. **Process package**<br>
   SLM will send a process package command to PartMgr, which
   will simulate a five second partition update time and then send
   back a installation report.

2. **Get installed packages**<br>
   PartMgr will send back a static list of currently installed
   partitions


## Module Loader - ML [ecu1\_module\_loader.py] ##
ML, which can have multiple different instances for different ECUs
(SiriusXM, Telematics Control Unit, Body Control Unit, etc), is responsible
for reflashing external modules through CAN or other in-vehicle networks.

ML has the following features

1. **Process package**<br>
   SLM will send a process package command to ML, which
   will simulate a five second module flash time and then send
   back a installation report.

2. **Get installed packages**<br>
   ML will send back a static list of currently installed
   flash images in the module managed by ML.


# PACKAGE COMMAND ARGUMENTS
All package commands sent between the components have the following arguments:

Acronym     | Description                           | Note
----------- | ------------------------------------- | ---
package\_id | Package ID string.                    | 
major       | Package major version number          |
minor       | Package minor version number          |
patch       | Package patch version number          |
command     | Command to carry out on packages      | install, upgrade, or remove
path        | Path to package, as stored inside SWM | Not provided in package notification
size        | Size of package in bytes              | 0 on remove operations
description | Textual package description           |
vendor      | Package vendor                        |
target      | target module                         | ecu1\_module\_loader, package\_manager, or partition\_manager

# SEQUENCE DIAGRAM

The following MSC diagram outlines the main package handling use case.

![SWM Sequence Diagram](https://github.com/magnusfeuer/genivi_software_management/raw/master/swm.png)


# RUNNING THE PROOF OF CONCEPT

## Install python and add ons.

Make sure you have Python 2.7 (or later 2.X) installed.

Install the necessary python libraries

    sudo apt-get install python-gtk2


## Launch SWM components
In one terminal window, start all components using:

    sh start_swm.sh

Each launched component will get their own terminal window.


## Launch SC

    
In a second window, launch the SC simulator:

    python sota_client.py


The full usage for ```sota_client.py``` is:


    sota_client.py [-p package_id] [-v major.minor.patch] \
                   [-t target] [-c command] [-s size] \
                   [-d description] [-V vendor]
    
      -p package_id        Pacakage id string. Default: 'bluez'
      -v major.minor.patch Version of package. Default: '1.2.3'
      -t target            Target installer. package_manager |
                                             partition_manager |
                                             ecu1_module_loader
                           Default: 'package'
      -c command           install | upgrade | remove. Default: 'install'
      -s size              Package size in bytes. Default: '1000000'
      -d description       Package description. Default: 'Bluez stack'
      -V vendor            Package vendor. Default: 'Bluez project'
    
    Example: sota_client.py -p boot_loader -v 2.10.9\
                            -t partition_manager -c write_image \
                            -s 524288 -d 'GDP Boot loader' \ 
                            -v 'DENX Software'


## Confirm Package
In the HMI xterm window, a confirmation text will be displayed.
Answer ```yes``` to confirm the package operation.

## Wait for download
SC will execute a five second simulated download.

## Wait for installation
The target component (PackMgr by default) will simulate a five second
install

## View installation report
The installation report will be displayed both by SC and HMI.


# DBUS BUS NAMES AND OBJETCS
TBD
