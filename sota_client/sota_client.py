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
import swm
import traceback
import settings
import logging

logger = logging.getLogger(settings.LOGGER)


# Default command line arguments
update_id='media_player_1_2_3'
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

        # Define our own bus name
        bus_name = dbus.service.BusName('org.genivi.SotaClient', bus=dbus.SessionBus())

        # Define our own object on the sota_client bus
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/SotaClient')



    @dbus.service.method('org.genivi.SotaClient',
                         async_callbacks=('send_reply', 'send_error'))

    def initiateDownload(self, 
                          update_id,
                          send_reply,
                          send_error): 
        global target
        global command
        global size
        global description
        global vendor
        global path

        logger.debug('SotaClient.SotaClientService.initiateDownload(%s): Called.', update_id)

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        #  Simulate download
        sys.stdout.write("Downloading\n")
        for i in xrange(1,10):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\nDone.\n")

        swm.dbus_method('org.genivi.SoftwareLoadingManager', 'downloadComplete', self.image_file, self.signature)
        return None
    
    @dbus.service.method('org.genivi.SotaClient')
    def updateReport(self,
                      update_id, 
                      results):
        global active

        logger.debug('SotaClient.SotaClientService.updateReport(%s): Called.', update_id)
        for result in results:
            logger.debug('    operationId: %s, code: %s, text: %s',
                         result['id'], result['result_code'], result['result_text'])
        logger.debug('SotaClient.SotaClientService.updateReport(%s): Complete.', update_id)
        active = False
        return None

def usage():
    print "Usage:", sys.argv[0], "-u update_id -i image_file -d description \\"
    print "                       -s signature [-c]"
    print
    print "  -u update_id         Pacakage id string. Default: 'media_player_1_2_3'"
    print "  -i image_file        Path to update squashfs image."
    print "  -s signature         RSA encrypted sha256um of image_file."
    print "  -c                   Request user confirmation."
    print "  -d description       Description of update."
    print
    print "Example:", sys.argv[0],"-u boot_loader_2.10.9\\"
    print "                        -i boot_loader.img  \\"
    print "                        -s 2889ee...4db0ed22cdb8f4e -c"
    sys.exit(255)


try:  
    opts, args= getopt.getopt(sys.argv[1:], "u:d:i:s:c")
except getopt.GetoptError:
    print "Could not parse arguments."
    usage()

image_file = None

request_confirmation = False
for o, a in opts:
    if o == "-u":
        update_id = a
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
    logger.debug('SotaClient.SotaClientService: Could not open %s: %s.', image_file, e)
    sys.exit(255)
image_desc.close()

print "Will simulate downloaded update:"
print "Update ID:          {}".format(update_id)
print "Description:        {}".format(description)
print "Image file:         {}".format(image_file)
print "User Confirmation:  {}".format(request_confirmation)

try:
    DBusGMainLoop(set_as_default=True)
    sota_svc = SOTAClientService(image_file, signature)

    # USE CASE
    #
    # This sota_client will send a update_available() call to the 
    # software loading manager (SLM).
    #
    # If requested, SWLM will pop an operation confirmation dialog on the HMI.
    #
    # If confirmed, SWLM will make an initiate_download() callback to 
    # this sota_client.
    #
    # The sota_client will, on simulated download completion, make a
    # download_complete() call to the SLM to  indicate that the update is 
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
    swm.dbus_method('org.genivi.SoftwareLoadingManager', 'updateAvailable',
                    update_id, description, signature, request_confirmation)


    active = True

    # Active will be set to false by installation_report()
    while active:
        gtk.main_iteration()

except Exception as e:
    print "Exception: {}".format(e)
    traceback.print_exc()

