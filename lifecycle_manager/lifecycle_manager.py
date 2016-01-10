# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based life cycle manager PoC



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm_result

#
# Lifecycle manager service
#
class LCMgrService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.slm_bus_name = dbus.service.BusName('org.genivi.lifecycle_manager', 
                                                 bus=self.bus)
        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     '/org/genivi/lifecycle_manager')




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
        # Send back installation report.
        # Software Loading Manager will distribute the report
        # to all interested parties.
        #
        slm_operation_result(transaction_id, result_code, result_text)

        return None

    @dbus.service.method('org.genivi.lifecycle_manager',
                         async_callbacks=('send_reply', 'send_error'))

    def start_components(self, 
                         transaction_id,
                         components,
                         send_reply, 
                         send_error):

        print "Lifecycle Manager: Got start_components()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Components:               {}".format(", ".join(components))
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Starting :"
        for i in components:
            print "    Starting: {} (3 sec)".format(i)
            time.sleep(3.0)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   swm_result.SWM_RES_OK,
                                   "Started components {}".format(", ".join(components)))
        return None
 
                                 
    @dbus.service.method('org.genivi.lifecycle_manager',
                         async_callbacks=('send_reply', 'send_error'))

    def stop_components(self, 
                        transaction_id,
                        components,
                        send_reply, 
                        send_error): 

        print "Lifecycle Manager: Got stop_components()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Components:               {}".format(", ".join(components))
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Stopping :"
        for i in components:
            print "    Stopping: {} (3 sec)".format(i)
            time.sleep(3.0)
        print  
        print "Done"
        self.send_operation_result(transaction_id,
                                   swm_result.SWM_RES_OK,
                                   "Stopped components {}".format(", ".join(components)))
        
        return None



print 
print "Lifecycle Manager."
print


DBusGMainLoop(set_as_default=True)
pkg_mgr = LCMgrService()

while True:
    gtk.main_iteration()
