# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

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


    @dbus.service.method('org.genivi.partition_manager')
    def process_package(self, 
                        path,
                        package_id, 
                        major, 
                        minor, 
                        patch, 
                        command, 
                        size, 
                        description, 
                        vendor,
                        target): 

        print "Partion Manager: Got process_package()"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  path:   {}".format(path)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        print "---"
        return (0, "partition manager installed {} {}.{}.{}".format(package_id,
                                                                  major,
                                                                  minor,
                                                                  patch))
        
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
