# -*- coding: utf-8 -*-
""" Database library to store update progress and results.

This module provides the configuration settings for Software Management.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Don't change this.
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Simulation
# If simulation is enabled all modules only simulate their operations
# rather than carrying them out. Simulation simply means outputting
# progress to the logging facilities.
SWM_SIMULATION = True
SWM_SIMULATION_WAIT = 5

# Database Settings
# SWM operations and their results are stored in a SQLite database.
DB_URL = "sqlite:/tmp/swlm.sqlite"

# Logging settings
LOGGER = 'swm.default'
LOGFILE = os.path.join(BASE_DIR, 'swm.log')

# Directory for the PID files for the various SWM processes
# It has to be an absolute path with a trailing '/'.
PID_FILE_DIR = "/tmp/"

# Don't change anything below this line unless you are familiar with the
# settings.

# Logger configuration
import logging.config
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
             'level': 'DEBUG',
             'class': 'logging.StreamHandler',
             'formatter': 'simple',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': LOGFILE,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'swm.default': {
            'handlers': ['file','console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'swm.console': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'swm.file': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
logging.config.dictConfig(LOGGING_CONFIG)


# Definitions of the operations that can be specified in an update manifest.
# This is a dictionary with the name of the operation as the key. The format is:
#
# "installPackage": (                       # name of the operation as used in the manifest
#     "org.genivi.PackageManager",          # the dbus object to call for the operation
#     "installPackage",                     # the dbus method for the operation provided by the dbus object
#     [                                     # array with argument tuples extracted from the manifest
#         ("image", None),                  # the first value is the argument name, the second the default value
#         ("blacklistedPackages", [])       # if the default value is None, the argument is mandatory
#     ],
#     [                                     # array with parameter tuples
#         ("timeEstimate", 5000),           # default time estimate for the operation
#         ("onFailure", "abort")            # default action if operation fails: abort or continue
#    ]
# )
#
# Default values can explictly be overridden by the manifest.
#
# Note: The number and type of paramters must match the signature of the dbus method.
#

OPERATIONS = {
    "installPackage": (
        "org.genivi.PackageManager",
        "installPackage",
        [
            ("image", None),
            ("blacklistedPackages", [])     # default list of package names that are blackedlisted by default
        ],
        [
            ("timeEstimate", 5000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "upgradePackage": (
        "org.genivi.PackageManager",
        "upgradePackage",
        [
            ("image", None),
            ("blacklistedPackages", []),    # enter list of package names that are blackedlisted by default
            ("allowDowngrade", False)       # downgrades are disabled by default
        ],
        [
            ("timeEstimate", 5000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "removePackage": (
        "org.genivi.PackageManager",
        "removePackage",
        [
            ("packageId", None)
        ],
        [
            ("timeEstimate", 5000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "startComponents": (
        "org.genivi.LifecycleManager",
        "startComponents",
        [
            ("components", None) 
        ],
        [
            ("timeEstimate", 3000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "stopComponents": (
        "org.genivi.LifecycleManager",
        "stopComponents",
        [
            ("components", None)
        ],
        [
            ("timeEstimate", 3000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "reboot": (
        "org.genivi.LifecycleManager",
        "reboot",
        [
            ("bootParameters", "")
        ],
        [
            ("timeEstimate", 3000),         # default time estimate for the operation
            ("onFailure", "continue")       # default action if operation fails: abort or continue
        ]
    ),

    "createDiskPartition": (
        "org.genivi.PartitionManager",
        "createDiskPartition",
        [
            ("disk", None),
            ("partitionNumber", None),
            ("type", None),
            ("start", None),
            ("size", None),
            ("guid", ""),
            ("name", "")
        ],
        [
            ("timeEstimate", 10000),        # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),
            
    "resizeDiskPartition": (
        "org.genivi.PartitionManager",
        "resizeDiskPartition",
        [
            ("disk", None),
            ("partitionNumber", None),
            ("start", None),
            ("size", None),
            ("blacklistedPartitions", [])
        ],
        [
            ("timeEstimate", 10000),        # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "deleteDiskPartition": (
        "org.genivi.PartitionManager",
        "deleteDiskPartition",
        [
            ("disk", None),
            ("partitionNnumber", None),
            ("blacklistedPartitions", [])
        ],
        [
            ("timeEstimate", 10000),        # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),

    "writeDiskPartition": (
        "org.genivi.PartitionManager",
        "writeDiskPartition",
        [
            ("disk", None),
            ("partitionNumber", None),
            ("image", None),
            ("blacklistedPartitions", [])
        ],
        [
            ("timeEstimate", 10000),        # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),
        
    "patchDiskPartition": (
        "org.genivi.PartitionManager",
        "patchDiskPartition",
        [
            ("disk", None),
            ("partition_number", None),
            ("image", None),
            ("blacklistedPartitions", [])
        ],
        [
            ("timeEstimate", 10000),        # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    ),
        
    # FIXME: We need to find a specific module loader
    #        that handles the target module. 
    #        org.genivi.module_loader needs to be replaced
    #        by org.genivi.module_loader_ecu1
    #        This should be done programmatically
    "flashModuleFirmwareEcu1": (
        "org.genivi.ModuleLoaderEcu1",
        "flashModuleFirmware",
        [
            ("image", None),
            ("blacklistedFirmware", []),
            ("allowDowngrade", False)
        ],
        [
            ("timeEstimate", 5000),         # default time estimate for the operation
            ("onFailure", "abort")          # default action if operation fails: abort or continue
        ]
    )
}


# Filesystem Commands
#
# SWM uses squashfs for update files that are mounted. Typically, only
# root is allowed to mount file systems. However, FUSE allows user
# mounting. The user-mount squashfs there is the squashfuse. It is not
# standard with any Linux distro but can be downloaded and installed from
# https://github.com/vasi/squashfuse. Squashfuse requires FUSE to be installed
# on the system.
#
# If a command does not need any arguments, other than the archive and the mount
# point which are provided programmatically, set the variable to None. Do not use
# an empty string or a string with spaces.
#
SQUASHFS_MOUNT_POINT = "/tmp/swlm"
SQUASHFS_FUSE = SWM_SIMULATION
if SQUASHFS_FUSE:
    # FUSE mount
    SQUASHFS_MOUNT_CMD = "/usr/local/bin/squashfuse {image_path} {mount_point}"
    SQUASHFS_UNMOUNT_CMD = ["/bin/fusermount", "-u"]
else:
    # Regular mount as root 
    SQUASHFS_MOUNT_CMD = "unsquashfs -f -d {mount_point} {image_path}"
    SQUASHFS_UNMOUNT_CMD = ["/bin/rm", "-r"]


# Package Management Commands
#
# SWM uses the platform's package management systems to install, upgrade and
# remove software packages.
#
PACKAGE_MANAGER = "rpm"
if PACKAGE_MANAGER == "rpm":
    PKGMGR_INSTALL_CMD = ["rpm", "--install"]
    PKGMGR_UPGRADE_CMD = ["rpm", "--upgrade", "--oldpackage"]
    PKGMGR_REMOVE_CMD = ["rpm", "--erase"]
    PKGMGR_LIST_CMD = ["rpm", "--query", "--all"]
    PKGMGR_CHECK_CMD = ["rpm", "--query"]
    PKGMGR_DEL_ARCH = '.'
    PKGMGR_DEL_REL = '-'
    PKGMGR_DEL_VER = '-'
elif PACKAGE_MANAGER == "deb":
    PKGMGR_INSTALL_CMD = ["dpkg", "--install"]
    PKGMGR_UPGRADE_CMD = ["dpkg", "--install"]
    PKGMGR_REMOVE_CMD = ["dpkg", "--purge"]
    PKGMGR_LIST_CMD = ["dpkg-query", "--show", "--showformat", "'${Package}-${Version}.${Architecture}\n'"]
    PKGMGR_CHECK_CMD = ["dpkg-query", "--list"]
    PKGMGR_DEL_ARCH = '_'
    PKGMGR_DEL_REL = '-'
    PKGMGR_DEL_VER = '_'
else:
    PKGMGR_INSTALL_CMD = ["echo", "Incorrect package manager defined."]
    PKGMGR_UPGRADE_CMD = ["echo", "Incorrect package manager defined."]
    PKGMGR_REMOVE_CMD = ["echo", "Incorrect package manager defined."]
    PKGMGR_LIST_CMD = ["echo", "Incorrect package manager defined."]
    PKGMGR_CHECK_CMD = ["echo", "Incorrect package manager defined."]
  
