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
import getopt
import sys


# Default command line arguments
package_id='bluez'
major=1
minor=2
patch=3
target='package_manager'
command='install'
size=1000000
description='bluez stack'
vendor='Bluez project'
path='/nev/dull'
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
        global target
        global command
        global size
        global description
        global vendor
        global path
        print "Got initiate_download"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "---"
        self.download_complete(path,
                               package_id, 
                               major, 
                               minor, 
                               patch, 
                               command,
                               size,
                               description,
                               vendor,
                               target)
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
                 


def usage():
    print "Usage:", sys.argv[0], "[-p package_id] [-v major.minor.patch] \\"
    print "                      [-t target] [-c command] [-s size] \\"
    print "                      [-d description] [-V vendor]"
    print
    print "  -p package_id        Pacakage id string. Default: 'bluez'"
    print "  -v major.minor.patch Version of package. Default: '1.2.3'"
    print "  -t target            Target installer. package | partition | module_loader"
    print "                       Default: 'package'"
    print "  -c command           install | upgrade | remove. Default: 'install'"
    print "  -s size              Package size in bytes. Default: '1000000'"
    print "  -d description       Package description. Default: 'Bluez stack'"
    print "  -V vendor            Package vendor. Default: 'Bluez project'"
    print
    print "Example:", sys.argv[0],"-n http://rvi1.nginfotpdx.net:8801 \\"
    print "                      jlr.com/vin/aaron/4711/test/ping \\"
    print "                      arg1=val1 arg2=val2"                    

    sys.exit(255)


opts, args= getopt.getopt(sys.argv[1:], "p:v:t:c:s:d:V:")

for o, a in opts:
    if o == "-p":
        package_id = a
    elif o == "-v":
        [major,minor,patch] = a
        major = int(major)
        minor = int(minor)
        patch = int(patch)
    elif o == "-t":
        target = a
    elif o == "-c":
        command = a
    elif o == "-s":
        size = int(a)
    elif o == "-d":
        description = a
    elif o == "-V":
        vendor = a
    else:
        usage()


    
print "Will simulate downloaded package:"
print "Package ID:  {} {}.{}.{}".format(package_id, major, minor, patch)
print "Description: {}".format(description)
print "Vendor:      {}".format(vendor)
print "Size:        {}".format(size)
print "Target:      {}".format(target)
print "Command:     {}".format(command)

DBusGMainLoop(set_as_default=True)
sota_svc = SOTAClientService()

# USE CASE
#
# This sota_client will send a package_available() call to the 
# software loading manager (SLM).
#
# SLM will pop an operation confirmation dialog on the HMI.
#
# If confirmed, SLM will make an initiate_download() callback to 
# this sota_client.
#
# The sota_client will, on simulated download completion, make a
# download_complete() call to the SLM to  indicate that the package is 
# ready to be processed.
#
# The SLM will look at the target parameter and forward the package to 
# module_loader, package_manager, or partition_manager.
# 
# Once the package has been processed by its target, a package operation
# report will be sent back to the SLM.
#
# The SLM will forward the package operation report to this sota client
# as an installation_report() call.


sota_svc.package_available(package_id, 
                           major,
                           minor, 
                           patch,
                           command,
                           size,
                           description,
                           vendor,
                           target)

while True:
    gtk.main_iteration()


