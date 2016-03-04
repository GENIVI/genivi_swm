# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm
import settings
import logging

logger = logging.getLogger(settings.LOGGER)

#
# Partition manager service
#
class PartMgrService(dbus.service.Object):
    def __init__(self):
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

        logger.debug('PartitionManager.PartMgrService.createDiskPartition(%s, %s, %s, %s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, partition_type, start, size, guid, name)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            sys.stdout.write("Create partition: disk({}) partiton({}) (3 sec)\n".format(disk, partition_number))
            for i in xrange(1,30):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Partition create successful. Disk: {}:{}".format(disk, partition_number))
        except Exception as e:
            logger.error('PartitionManager.PartMgrService.resizeDiskPartition(): Exception: %s.', e)
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

        logger.debug('PartitionManager.PartMgrService.resizeDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, start, size)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            sys.stdout.write("Resizing partition: disk({}) partiton({}) (10 sec)\n".format(disk, partition_number))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.2)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                       swm.SWMResult.SWM_RES_OK,
                                       "Partition resize success. Disk: {}:{}".format(disk, partition_number))
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
                              send_reply, 
                              send_error): 

        logger.debug('PartitionManager.PartMgrService.deleteDiskPartition(%s, %s, %s): Called.',
                     transaction_id, disk, partition_number)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            sys.stdout.write("Delete partition: disk({}) partiton({}) (5 sec)\n".format(disk, partition_number))
            for i in xrange(1,10):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.2)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                       swm.SWMResult.SWM_RES_OK,
                                       "Partition delete success. Disk: {}:{}".format(disk, partition_number))
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

        logger.debug('PartitionManager.PartMgrService.writeDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, image_path, blacklisted_partitions)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate write
            sys.stdout.write("Writing partition: disk({}) partition({}) (10 sec)\n".format(disk, partition_number))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.2)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Partition write success. Disk: {}:{} Image: {}".
                                      format(disk, partition_number, image_path))
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

        logger.debug('PartitionManager.PartMgrService.patchDiskPartition(%s, %s, %s, %s, %s): Called.',
                     transaction_id, disk, partition_number, image_path, blacklisted_partitions)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate patch
            sys.stdout.write("Patching partition: disk({}) partiton({}) (10 sec)\n".format(disk, partition_number))
            for i in xrange(1,50):
                sys.stdout.patch('.')
                sys.stdout.flush()
                time.sleep(0.2)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Partition patch success. Disk: {}:{} Image: {}".
                                      format(disk, partition_number, image_path))
        except Exception as e:
            logger.error('PartitionManager.PartMgrService.patchDiskPartition(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
                 
logger.debug('Partition Manager - Running')

DBusGMainLoop(set_as_default=True)
part_mgr = PartMgrService()

while True:
    gtk.main_iteration()
