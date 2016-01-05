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

#
# Partition manager service
#
class PartMgrService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.slm_bus_name = dbus.service.BusName('org.genivi.partition_manager', 
                                                 bus=self.bus)
        self.initiate_download_dbus = None
        self.installation_report_dbus = None
        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     '/org/genivi/partition_manager')




    def send_operation_result(self, transaction_id, result_code, result_text):
        #
        # Retrieve software loading manager bus name, object, 
        # and installation report method
        #
        slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', 
                                            bus=self.bus)
        slm_obj = self.bus.get_object(slm_bus_name.get_name(), 
                                      "/org/genivi/software_loading_manager")

        slm_operation_result = slm_obj.get_dbus_method("operation_result", 
                                                       "org.genivi.software_loading_manager")
        
        #
        # Send back operation result.
        # Software Loading Manager will distribute the report
        # to all interested parties.
        #
        print "Will send back {} {}/{}".format(transaction_id, result_code, result_text)
        slm_operation_result(transaction_id, result_code, result_text)
        print "Sent"
        return None

    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def create_disk_partition(self, 
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

        print "Partition Manager: create_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Partition Type:            {}".format(partition_type)
        print "  Start:                     {}".format(start)
        print "  Size:                      {}".format(size)
        print "  GUID:                      {}".format(guid)
        print "  Name:                      {}".format(name)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Creating partition :"
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   0,
                                   "Partition create successful")                                 

        return None
                 

    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def resize_disk_partition(self, 
                              transaction_id,
                              disk,
                              partition_number,
                              start,
                              size,
                              send_reply, 
                              send_error): 

        print "Partition Manager: resize_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Start:                     {}".format(start)
        print "  Size:                      {}".format(size)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Resizing partition :"
        for i in xrange(1,20):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   0,
                                   "Partition resize successful")                                 

        return None


    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def delete_disk_partition(self, 
                              transaction_id,
                              disk,
                              send_reply, 
                              send_error): 

        print "Partition Manager: delete_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Resizing partition :"
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   0,
                                   "Partition delete successful")                                 

        return None


    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def write_disk_partition(self, 
                             transaction_id,
                             disk,
                             partition_number,
                             image,
                             blacklisted_partitions,
                             send_reply, 
                             send_error): 

        print "Partition Manager: write_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Image Path:                {}".format(image)
        print "  Blacklisted Partitions:    {}".format(blacklisted_partitions)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Writing Partition :"
        for i in xrange(1,20):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   0,
                                   "Partition write successful")                                 

        return None
                 

    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def patch_disk_partition(self, 
                             transaction_id,
                             disk,
                             partition_number,
                             image,
                             blacklisted_partitions,
                             send_reply, 
                             send_error): 

        print "Partition Manager: patch_disk_partition()"
        print "  Operfation Transaction ID: {}".format(transaction_id)
        print "  Disk:                      {}".format(disk)
        print "  Partition Number:          {}".format(partition_number)
        print "  Image Path:                {}".format(image)
        print "  Blacklisted Partitions:    {}".format(blacklisted_partitions)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Patching partition :"
        for i in xrange(1,20):
            sys.stdout.patch('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   0,
                                   "Partition patch successful")                                 

        return None
                 

print 
print "Partition Manager."
print
DBusGMainLoop(set_as_default=True)
part_mgr = PartMgrService()

while True:
    gtk.main_iteration()
