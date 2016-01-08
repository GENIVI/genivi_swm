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
    def __init__(self, image_file, signature):

        # Store where we have the image file
        self.image_file = image_file

        # Store signature
        self.signature = signature

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
            time.sleep(0.1)
        print 
        print "Done."

        self.download_complete(self.image_file, self.signature)
        return None
    
    @dbus.service.method('org.genivi.sota_client')
    def update_report(self,
                      update_id, 
                      results):
        global active
        print "Update report"
        print "  ID:          {}".format(update_id)
        for result in results:
            print "    operation_id: {}".format(result['id'])
            print "    code:         {}".format(result['result_code'])
            print "    text:         {}".format(result['result_text'])
            print "  ---"
        print "---"
        active = False
        return None

    @dbus.service.method('org.genivi.sota_client')
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ { 'package_id': 'bluez_driver' },
                 { 'package_id': 'bluez_apps' } ]

def usage():
    print "Usage:", sys.argv[0], "-p package_id -i image_file -d description \\"
    print "                       -s signature [-c]"
    print
    print "  -p package_id        Pacakage id string. Default: 'bluez'"
    print "  -i image_file        Path to update squashfs image."
    print "  -s signature         RSA encrypted sha256um of image_file."
    print "  -c                   Request user confirmation."
    print "  -d description       Description of update."
    print
    print "Example:", sys.argv[0],"-p boot_loader -v 2.10.9\\"
    print "                        -u boot_loader.img  \\"
    print "                        -s 2889ee...4db0ed22cdb8f4e -c"
    sys.exit(255)


try:  
    opts, args= getopt.getopt(sys.argv[1:], "p:d:i:s:c")
except getopt.GetoptError:
    print "Could not parse arguments."
    usage()

image_file = None

request_confirmation = False
for o, a in opts:
    if o == "-p":
        package_id = a
    elif o == "-d":
        description = a
    elif o == "-i":
        image_file = a
    elif o == "-s":
        signature = a
    elif o == "-c":
        request_confirmation = True
    else:
        print "Unknown option: {}".format(o)
        usage()

if not image_file:
    print
    print "No -i image_file provided."
    print
    usage()
    
# Can we open the confirmation file?
try:
   image_desc = open(image_file, "r")
except IOError as e:
    print "Could not open {} for reading: {}".format(image_file, e)
    sys.exit(255)
    
image_desc.close()

print "Will simulate downloaded package:"
print "Package ID:         {}".format(package_id)
print "Description:        {}".format(description)
print "Image file:         {}".format(image_file)
print "User Confirmation:  {}".format(request_confirmation)


DBusGMainLoop(set_as_default=True)
sota_svc = SOTAClientService(image_file, signature)

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
# The SLM will mount the provided image file as a loopback file system
# and execute its update_manifest.json file. Each software operation in
# the manifest file will be fanned out to its correct target (PackMgr,
# ML, PartMgr)
# 
# Once the update has been processed by SLM, an update operation
# report will be sent back to SC and HMI.
#

sota_svc.update_available(package_id, 
                          description,
                          request_confirmation)


active = True

# Active will be set to false by installation_report()
while active:
    gtk.main_iteration()

print "Done"

