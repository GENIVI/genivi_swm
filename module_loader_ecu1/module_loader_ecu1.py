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
# ECU Module Loader service
#
class ECU1ModuleLoaderService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.ml_bus_name = dbus.service.BusName('org.genivi.module_loader_ecu1', 
                                                 bus=self.bus)
        dbus.service.Object.__init__(self, self.ml_bus_name, 
                                     '/org/genivi/module_loader_ecu1')


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
    @dbus.service.method('org.genivi.module_loader_ecu1',
                         async_callbacks=('send_reply', 'send_error'))

    def flash_module_firmware(self, 
                              transaction_id, 
                              image_path,
                              blacklisted_firmware,
                              send_reply,
                              send_error): 


        print "Package Manager: Got flash_module_firmware()"
        print "  Operation Transaction ID: {}".format(transaction_id)
        print "  Image Path:               {}".format(image_path)
        print "  Blacklisted firmware:     {}".format(blacklisted_firmware)
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
        self.send_operation_result(transaction_id,
                                   0,
                                   "Firmware flashing successful for ecu1")

        return None
        
    @dbus.service.method('org.genivi.module_loader_ecu1')
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ "ecu1_firmware_1.2.3" ]
                 
print 
print "ECU1 Module Loader."
print

DBusGMainLoop(set_as_default=True)
module_loader_ecu1 = ECU1ModuleLoaderService()

while True:
    gtk.main_iteration()
