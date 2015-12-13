# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based hmi PoC for Software Loading Manager
#

import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop


    
#
# hmi service
#
class HMIService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        hmi_bus_name = dbus.service.BusName('org.genivi.hmi', 
                                            bus=self.bus)

        dbus.service.Object.__init__(self, 
                                     hmi_bus_name, 
                                     '/org/genivi/hmi')




    @dbus.service.method('org.genivi.hmi', 
                         async_callbacks=('send_reply', 'send_error'))
    def update_notification(self, 
                              package_id, 
                              major, 
                              minor, 
                              patch, 
                              command, 
                              size, 
                              description, 
                              vendor,
                              target, 
                              send_reply,
                              send_error): 

        print "HMI: Got update_notification()"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        print "---"

        #
        # Send back an async reply to the invoking software_loading_manager
        # so that we can continue with user interaction without
        # risking a DBUS timeout
        #
        send_reply(True)

        print
        print
        print "DIALOG:"
        print "DIALOG: Available update"
        print "DIALOG:   Description: {}".format(description)
        print "DIALOG:   Vendor:      {}".format(vendor)
        print "DIALOG:"
        resp = raw_input("DIALOG: Install? (yes/no): ")
        print 
        #
        # Setup DBUS call to software loading manager.
        #
        slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', 
                                            bus=self.bus)
        slm_obj = self.bus.get_object(slm_bus_name.get_name(), 
                                         "/org/genivi/software_loading_manager")

        package_confirmation = slm_obj.get_dbus_method("package_confirmation", 
                                                       "org.genivi.software_loading_manager")
    
        if len(resp) == 0 or (resp[0] != 'y' and resp[0] != 'Y'):
            approved = False
        else:
            approved = True

        #
        # Call software_loading_manager.package_confirmation() 
        # to inform it of user approval / decline.
        #
        package_confirmation(approved,
                             package_id, 
                             major, 
                             minor, 
                             patch, 
                             command, 
                             size, 
                             description, 
                             vendor,
                             target)

        return None
        

    @dbus.service.method('org.genivi.hmi')
    def installation_report(self,
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
                            result_code,
                            result_msg):
        print "Installation report"
        print "  ID:          {}".format(package_id)
        print "  ver:         {}.{}.{} ".format(major, minor, patch)
        print "  command:     {}".format(command)
        print "  path:        {}".format(path)
        print "  description: {}".format(description)
        print "  vendor:      {}".format(vendor)
        print "  target:      {}".format(target)
        print "  result_code: {}".format(result_code)
        print "  result_desc: {}".format(result_msg)
        print "---"
        return None


print 
print "HMI Simulator"
print "Please enter package installation approval when prompted"
print


DBusGMainLoop(set_as_default=True)
pkg_mgr = HMIService()

while True:
    gtk.main_iteration()
