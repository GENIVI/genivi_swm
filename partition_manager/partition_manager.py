# -*- coding: utf-8 -*-
""" Partition Management

This module provides classes and methods for managing partitions.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""

import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm
import settings
import logging
import os
import getopt
import daemon

logger = logging.getLogger(settings.LOGGER)

#
# Partition manager service
#
class PartMgrService(dbus.service.Object):
    """Partition Manager Service
    
    Handles creation, deletion, resizing etc. of partitions using the platform's
    native partition manager. The platform partition management commands are defined
    by the settings in common.
    """

    def __init__(self):
        """Constructor
        
        Initalize instance as a dbus service object.
        """
        bus_name = dbus.service.BusName('org.genivi.PartitionManager', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/PartitionManager')


    @dbus.service.method('org.genivi.PartitionManager',
                         async_callbacks=('send_reply', 'send_error'))
    def createDiskPartition(self, 
                              transaction_id,
                              disk,
                              partition_number,
                              partition_type,
                              start,
                              size,
                              guid,
                              name,
                              send_reply, 
                              send_error): 
        """Create a Partition on a Disk
        
        Dbus callback for creating a partition on a disk using the platform's
        partition management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param disk Disk to partition
        @param partition_number Number of the partition
        @param partition_type Type of the partition
        @param start Start sector of the partition
        @param size Size in bytes of the partition
        @param guid GUID for the partition
        @param name Name of the partition
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PartitionManager.PartMgrService.createDiskPartition(%s, %s, %s, %s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, partition_type, start, size, guid, name)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble partition creation command
            #cmd = settings.PKGMGR_INSTALL_CMD
            #cmd.append(image_path)
            #logger.info('PartitionManager.PartMgrService.createDiskPartition(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate creating the disk partition
                logger.info('PartitionManager.PartMgrService.createDiskPartition(): Creating disk partition simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Creating disk partition simulation successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.createDiskPartition(): Creating disk partition simulation successful.')
            else:
                # perform disk partition creation
                logger.info('PartitionManager.PartMgrService.createDiskPartition(): Creating disk partition...')
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Creating disk partition successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.createDiskPartition(): Creating disk partition successful.')

            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PartitionManager.PartMgrService.createDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
                 

    @dbus.service.method('org.genivi.PartitionManager',
                         async_callbacks=('send_reply', 'send_error'))
    def resizeDiskPartition(self, 
                              transaction_id,
                              disk,
                              partition_number,
                              start,
                              size,
                              send_reply, 
                              send_error): 
        """Resize a Partition on a Disk
        
        Dbus callback for resizing a partition on a disk using the platform's
        partition management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param disk Disk on which to resize the partition
        @param partition_number Number of the partition
        @param partition_type Type of the partition
        @param start Start sector of the partition
        @param size Size in bytes of the partition
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PartitionManager.PartMgrService.resizeDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, start, size)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble partition resize command
            #cmd = settings.PKGMGR_INSTALL_CMD
            #cmd.append(image_path)
            #logger.info('PartitionManager.PartMgrService.resizeDiskPartition(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate resizing the disk partition
                logger.info('PartitionManager.PartMgrService.resizeDiskPartition(): Resizing disk partition simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Resizeing disk partition simulation successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.createDiskPartition(): Resizing disk partition simulation successful.')
            else:
                # perform resizing the disk partition
                logger.info('PartitionManager.PartMgrService.resizeDiskPartition(): Resizing disk partition...')
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Resizing disk partition successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.resizeDiskPartition(): Resizing disk partition successful.')

            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PartitionManager.PartMgrService.resizeDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None


    @dbus.service.method('org.genivi.PartitionManager',
                         async_callbacks=('send_reply', 'send_error'))
    def deleteDiskPartition(self, 
                              transaction_id,
                              disk,
                              partition_number,
                              send_reply, 
                              send_error): 
        """Delete a Partition on a Disk
        
        Dbus callback for deleting a partition on a disk using the platform's
        partition management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param disk Disk from which to delete the partition
        @param partition_number Number of the partition
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PartitionManager.PartMgrService.deleteDiskPartition(%s, %s, %s): Called.',
                     transaction_id, disk, partition_number)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble partition delete command
            #cmd = settings.PKGMGR_INSTALL_CMD
            #cmd.append(image_path)
            #logger.info('PartitionManager.PartMgrService.deleteDiskPartition(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate deleting the disk partition
                logger.info('PartitionManager.PartMgrService.deleteDiskPartition(): Deleting disk partition simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Deleting disk partition simulation successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.deleteDiskPartition(): Deleting disk partition simulation successful.')
            else:
                # perform deleting the disk partition
                logger.info('PartitionManager.PartMgrService.deleteDiskPartition(): Deleting disk partition...')
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Deleting disk partition successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.deleteDiskPartition(): Deleting disk partition successful.')

            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PartitionManager.PartMgrService.deleteDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None


    @dbus.service.method('org.genivi.PartitionManager',
                         async_callbacks=('send_reply', 'send_error'))
    def writeDiskPartition(self, 
                             transaction_id,
                             disk,
                             partition_number,
                             image_path,
                             blacklisted_partitions,
                             send_reply, 
                             send_error): 
        """Write a Partition on a Disk
        
        Dbus callback for writing a partition on a disk using the platform's
        partition management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param disk Disk from which to delete the partition
        @param partition_number Number of the partition
        @param image_path Image to write to the partition
        @param blacklisted_partitions List of blacklisted partitions
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PartitionManager.PartMgrService.writeDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, image_path, blacklisted_partitions)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble partition write command
            #cmd = settings.PKGMGR_INSTALL_CMD
            #cmd.append(image_path)
            #logger.info('PartitionManager.PartMgrService.writeDiskPartition(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate writing the disk partition
                logger.info('PartitionManager.PartMgrService.writeDiskPartition(): Writing disk partition simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Writing disk partition simulation successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.writeDiskPartition(): Writing disk partition simulation successful.')
            else:
                # perform writing the disk partition
                logger.info('PartitionManager.PartMgrService.writeDiskPartition(): Writing disk partition...')
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Writing disk partition successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.writeDiskPartition(): Writing disk partition successful.')

            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PartitionManager.PartMgrService.writeDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
                 

    @dbus.service.method('org.genivi.PartitionManager',
                         async_callbacks=('send_reply', 'send_error'))
    def patchDiskPartition(self, 
                             transaction_id,
                             disk,
                             partition_number,
                             image_path,
                             blacklisted_partitions,
                             send_reply, 
                             send_error): 
        """Patch a Partition on a Disk
        
        Dbus callback for patching a partition on a disk using the platform's
        partition management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param disk Disk from which to delete the partition
        @param partition_number Number of the partition
        @param image_path Image to write to the partition
        @param blacklisted_partitions List of blacklisted partitions
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PartitionManager.PartMgrService.patchDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, image_path, blacklisted_partitions)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble partition patch command
            #cmd = settings.PKGMGR_INSTALL_CMD
            #cmd.append(image_path)
            #logger.info('PartitionManager.PartMgrService.patchDiskPartition(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate patching the disk partition
                logger.info('PartitionManager.PartMgrService.patchDiskPartition(): Patching disk partition simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Patching disk partition simulation successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.patchDiskPartition(): Patching disk partition simulation successful.')
            else:
                # perform patching the disk partition
                logger.info('PartitionManager.PartMgrService.patchDiskPartition(): Patching disk partition...')
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Patching disk partition successful. Disk: {}:{}".format(disk, partition_number)
                logger.info('PartitionManager.PartMgrService.patchDiskPartition(): Patching disk partition successful.')

            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PartitionManager.PartMgrService.patchDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

                 
class PartMgrDaemon(daemon.Daemon):
    """
    """
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(PartMgrDaemon, self).__init__(pidfile, stdin, stdout, stderr)

    def run(self):
        DBusGMainLoop(set_as_default=True)
        part_mgr = PartMgrService()
        while True:
            gtk.main_iteration()


def usage():
    print "Usage:", sys.argv[0], "foreground|start|stop|restart"
    print
    print "  foreground     Start in foreground"
    print "  start          Start in background"
    print "  stop           Stop daemon running in background"
    print "  restart        Restart daemon running in background"
    print
    print "Example:", sys.argv[0],"foreground"
    sys.exit(1)


if __name__ == "__main__":
    logger.debug('Partition Manager - Initializing')
    pid_file = settings.PID_FILE_DIR + os.path.splitext(os.path.basename(__file__))[0] + '.pid'

    try:  
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError:
        print "Partition Manager - Could not parse arguments."
        usage()
            
    partmgr_daemon = PartMgrDaemon(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
            
    for a in args:
        if a in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger.addHandler(logging._handlers['console'])
            logger.debug('Partition Manager - Running')
            partmgr_daemon.run()
        elif a in ('start', 'st'):
            logger.debug('Partition Manager - Starting')
            partmgr_daemon.start()
        elif a in ('stop', 'sp'):
            logger.debug('Partition Manager - Stopping')
            partmgr_daemon.stop()
        elif a in ('restart', 're'):
            logger.debug('Partition Manager - Restarting')
            partmgr_daemon.restart()
        else:
            print "Unknown command: {}".format(a)
            usage()
            sys.exit(1)
 
