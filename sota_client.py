# (C) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces SOTA interface 
# of Software Loading manager.


import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop



class SOTAClientService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.sota_bus_name = dbus.service.BusName('org.genivi.sota_client', bus=self.bus)
        dbus.service.Object.__init__(self, 
                                     self.sota_bus_name, 
                                     '/org/genivi/sota_client')

        self.slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', bus=self.bus)
        slm_obj = self.bus.get_object(self.slm_bus_name.get_name(), 
                                      '/org/genivi/software_loading_manager')

        self.package_available_dbus = slm_obj.get_dbus_method('package_available', 
                                                              'org.genivi.software_loading_manager')

        self.download_complete_dbus = slm_obj.get_dbus_method('download_complete', 
                                                              'org.genivi.software_loading_manager')

        self.installation_report = slm_obj.get_dbus_method('installation_report', 
                                                           'org.genivi.software_loading_manager')

        self.get_installed_packages_dbus = slm_obj.get_dbus_method('get_installed_packages', 
                                                                   'org.genivi.software_loading_manager')

    def handle_reply(self, r):
        print "Got reply", r

    def handle_error(self, e):
        print "Got error", e

    def package_available(self, *args):
        self.package_available_dbus(*args,
                                    reply_handler = self.handle_reply,
                                    error_handler = self.handle_error)


    def download_complete(self, *args):
        self.download_complete_dbus(*args)


    @dbus.service.method('org.genivi.sota_client')
    def initiate_download(self, 
                          package_id,
                          major,
                          minor,
                          patch): 
        print "Got initiate_download"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "---"
        self.download_complete("/nev/dull", 
                               package_id, 
                               major, 
                               minor, 
                               patch, 
                               "install", 
                               47114711, 
                               "Linux Kernel - Now with 6502 support",
                               "Linux Foundation",
                               "package_manager")
        return True
    
    @dbus.service.method('org.genivi.sota_client')
    def installation_report(self,
                            package_id, 
                            major,
                            minor,
                            patch,
                            result,
                            desc):
        print "Installation report"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  result: {}".format(result)
        print "  descr:  {}".format(desc)
        print "---"
        return True

    @dbus.service.method('org.genivi.sota_client')
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
                 



DBusGMainLoop(set_as_default=True)
sota_svc = SOTAClientService()

# Get things started
sota_svc.package_available('linux_kernel', 
                         7,8,9, 
                         "install", 
                         47114711, 
                         "Linux Kernel - Now with 6502 support",
                         "Linux Foundation",
                           "package_manager")

while True:
    gtk.main_iteration()


