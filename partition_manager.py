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


    @dbus.service.method('org.genivi.partition_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def process_update(self, 
                        package_id, 
                        major, 
                        minor, 
                        patch, 
                        command, 
                        path,
                        size, 
                        description, 
                        vendor,
                        target,
                        send_reply,
                        send_error): 

        print "Partion Manager: Got process_update()"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  path:   {}".format(path)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        print "---"
        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Writing Partition:"
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print  
        print "Done"

        #
        # Retrieve software loading manager bus name, object, 
        # and installation report method
        #
        slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', 
                                            bus=self.bus)
        slm_obj = self.bus.get_object(slm_bus_name.get_name(), 
                                      "/org/genivi/software_loading_manager")

        slm_installation_report = slm_obj.get_dbus_method("installation_report", 
                                                          "org.genivi.software_loading_manager")
        
        #
        # Send back installation report.
        # Software Loading Manager will distribute the report
        # to all interested parties.
        #
        slm_installation_report(path,
                                package_id, 
                                major, 
                                minor, 
                                patch, 
                                command, 
                                size, 
                                description, 
                                vendor,
                                target,
                                0,
                                "Partition Manager - Successfully installed {} {}.{}.{}".
                                format(package_id,
                                       major,
                                       minor,
                                       patch))


        return None
        
    @dbus.service.method('org.genivi.partition_manager')
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ { 'package_id': 'bluez_driver', 
                   'major': 1,
                   'minor': 2,
                   'patch': 3 },
                 { 'package_id': 'bluez_apps', 
                   'major': 3,
                   'minor': 2,
                   'patch': 1 } ]
                 

print 
print "Partition Manager."
print
DBusGMainLoop(set_as_default=True)
part_mgr = PartMgrService()

while True:
    gtk.main_iteration()
