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
import time

# Default command line arguments
package_id='media_player'
major=1
minor=2
patch=3
description='Media Player Update'
signature='d2889ee6bc1fe1f3d7c5cdaca78384776bf437b7c6ca4db0e2c8b1d22cdb8f4e'
update_file=''
active=True
class SOTAClientService(dbus.service.Object):
    def __init__(self):
        
        # Retrieve the session bus.
        self.bus = dbus.SessionBus()

        # Define our own bus name
        self.sota_bus_name = dbus.service.BusName('org.genivi.sota_client', bus=self.bus)

        # Define our own object on the sota_client bus
        dbus.service.Object.__init__(self, self.sota_bus_name, '/org/genivi/sota_client')

        # Locate the bus of the software_loading_manager
        self.slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', bus=self.bus)

        # Retrieve the software_loading_manager proxy object.
        slm_obj = self.bus.get_object(self.slm_bus_name.get_name(), 
                                      '/org/genivi/software_loading_manager')

        # Retrieve the methods available on the software_loading_manager object.

        self.update_available = slm_obj.get_dbus_method('update_available', 
                                                         'org.genivi.software_loading_manager')

        self.download_complete = slm_obj.get_dbus_method('download_complete', 
                                                         'org.genivi.software_loading_manager')

        self.installation_report = slm_obj.get_dbus_method('installation_report', 
                                                           'org.genivi.software_loading_manager')

        self.get_installed_packages_dbus = slm_obj.get_dbus_method('get_installed_packages', 
                                                                   'org.genivi.software_loading_manager')




    @dbus.service.method('org.genivi.sota_client',
                         async_callbacks=('send_reply', 'send_error'))
    def initiate_download(self, 
                          package_id,
                          major,
                          minor,
                          patch,
                          send_reply,
                          send_error): 
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

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        #  Simulate download
        print "Downloading"
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.2)
        print 
        print "Done."

        self.download_complete(package_id, 
                               major, 
                               minor, 
                               patch, 
                               command,
                               path,
                               size,
                               description,
                               vendor,
                               target)
        return None
    
    @dbus.service.method('org.genivi.sota_client')
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
        global active
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
        active = False
        return None


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
    print "Usage:", sys.argv[0], "-p package_id -v major.minor.patch \\"
    print "                       -s signature [-c] \\"
    print
    print "  -p package_id        Pacakage id string. Default: 'bluez'"
    print "  -v major.minor.patch Version of package. Default: '1.2.3'"
    print "  -u update_file       Update squashfs image file."
    print "  -s signature         RSA encrypted sha256um of udpdate_file."
    print "  -c                   Request user confirmation."
    print
    print "Example:", sys.argv[0],"-p boot_loader -v 2.10.9\\"
    print "                        -u boot_loader.img  \\"
    print "                        -s 2889ee...4db0ed22cdb8f4e -c"
    sys.exit(255)


try:  
    opts, args= getopt.getopt(sys.argv[1:], "p:v:u:s:c")
except getopt.GetoptError:
    usage()

request_confirmation = False
for o, a in opts:
    if o == "-p":
        package_id = a
    elif o == "-v":
        [major,minor,patch] = a
        major = int(major)
        minor = int(minor)
        patch = int(patch)
    if o == "-d":
        description = a
    elif o == "-u":
        update_file = a
    elif o == "-s":
        signature = a
    elif o == "-c":
        request_confirmation = True
    else:
        usage()

if update_file == '':
    print
    print "No -u update_file provided."
    print
    usage()
    
# Can we open the confirmation file?
try:
   update_desc = open(update_file, "r")
except IOError as e:
    print "Could not open {} for reading: {}".format(update_file, e)
    sys.exit(255)
    
update_desc.close()

print "Will simulate downloaded package:"
print "Package ID:         {} {}.{}.{}".format(package_id, major, minor, patch)
print "Description:        {}".format(description)
print "Update file:        {}".format(update_file)
print "User Confirmation:  {}".format(request_confirmation)


DBusGMainLoop(set_as_default=True)
sota_svc = SOTAClientService()

# USE CASE
#
# This sota_client will send a update_available() call to the 
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


sota_svc.update_available(package_id, 
                          major,
                          minor, 
                          patch,
                          description,
                          update_file,
                          request_confirmation)


active = True

# Active will be set to false by installation_report()
while active:
    gtk.main_iteration()

print "Done"

