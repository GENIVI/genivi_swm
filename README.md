Copyright (C) 2014-2015 Jaguar Land Rover

This document is licensed under Creative Commons
Attribution-ShareAlike 4.0 International.

# TODO
1. Rename package to update in most commands.
2. Rename installation report to update report.
3. Implement get installed packages use case.

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


# GENIVI SOFTWARE MANAGEMENT - PROOF OF CONCEPT #
This directory contains a set of python components that are used to
explore the API between the components forming the Software Management
system.

The components are outlined in the image below

![SWM Layout](https://github.com/magnusfeuer/genivi_software_management/raw/master/swm_illustration.png)

The components are as follows:


# SOTA Client - SC [sota_client.py] ##
The SC simulator, to be replaced by the real GENIVI Sota
Client developed by Advanced Telematic Systems, is a command line tool
that launches the SWM use cases.

The SOTA client simulator has the following features

1. **Notify SWM of available packages**<br>
   Information about the available package, specified at the command line,
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



