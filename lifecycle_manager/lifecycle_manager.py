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
import swm

#
# Lifecycle manager service
#
class LCMgrService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.lifecycle_manager', dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/lifecycle_manager')


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
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
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
        swm.send_operation_result(transaction_id,
                                  swm.SWM_RES_OK,
                                  "Stopped components {}".format(", ".join(components)))
        
        return None



print 
print "Lifecycle Manager."
print


DBusGMainLoop(set_as_default=True)
pkg_mgr = LCMgrService()

while True:
    gtk.main_iteration()
