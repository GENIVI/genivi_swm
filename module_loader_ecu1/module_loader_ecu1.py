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

#
# ECU Module Loader service
#
class ECU1ModuleLoaderService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.ModuleLoaderEcu1', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/ModuleLoaderEcu1')

    @dbus.service.method('org.genivi.ModuleLoaderEcu1',
                         async_callbacks=('send_reply', 'send_error'))

    def flashModuleFirmware(self, 
                              transaction_id, 
                              image_path,
                              blacklisted_firmware,
                              allow_downgrade,
                              send_reply,
                              send_error): 


        print "Package Manager: Got flashModuleFirmware()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Image Path:               {}".format(image_path)
        print "  Blacklisted firmware:     {}".format(blacklisted_firmware)
        print "  Allow downgrade:          {}".format(allow_downgrade)
        print "---"

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        print "Intalling on ECU1: {} (5 sec):".format(image_path)
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        print  
        print "Done"
        swm.send_operation_result(transaction_id,
                                  swm.SWMResult.SWM_RES_OK,
                                  "Firmware flashing successful for ecu1. Path: {}".format(image_path))

        return None
        
    @dbus.service.method('org.genivi.moduleLoaderEcu1')
    def getModuleFirmwareVersion(self): 
        print "Got getModuleFirmwareVersion()"
        return ("ecu1_firmware_1.2.3", 1452904544)
                 
print 
print "ECU1 Module Loader."
print

DBusGMainLoop(set_as_default=True)
module_loader_ecu1 = ECU1ModuleLoaderService()

while True:
    gtk.main_iteration()
