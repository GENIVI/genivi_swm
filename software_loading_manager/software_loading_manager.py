# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that coordinates all use cases.
#
import gtk
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import manifest_processor
import traceback
import sys
import getopt
import os
import swm

#
# Define the DBUS-facing Software Loading Manager service
#
class SLMService(dbus.service.Object):
    def __init__(self, db_path):
        self.manifest_processor = manifest_processor.ManifestProcessor(db_path)
        # Define our own bus name
        bus_name = dbus.service.BusName('org.genivi.software_loading_manager', bus=dbus.SessionBus())        
        # Define our own object on the software_loading_manager bus
        dbus.service.Object.__init__(self, bus_name, "/org/genivi/software_loading_manager")

            
    def initiate_download(self, package_id):
        swm.dbus_method("org.genivi.sota_client", "initiate_download", package_id)

    # 
    # Distribute a report of a completed installation
    # to all involved parties. So far those parties are
    # the HMI and the SOTA client
    #
    def distribute_update_result(self, 
                                 update_id, 
                                 results):
        # Send installation report to HMI
        print "Sending report to hmi.update_report()"
        swm.dbus_method("org.genivi.hmi", "update_report", dbus.String(update_id), results)

        # Send installation report to SOTA
        print "Sending report to sota.update_report()"
        swm.dbus_method("org.genivi.sota_client", "update_report", dbus.String(update_id), results)

    def get_current_manifest(self):
        return self.manifest_processor.current_manifest

    def start_next_manifest(self):
        if not self.manifest_processor.load_next_manifest():
            return False

        manifest = self.get_current_manifest()
        self.inform_hmi_of_new_manifest(manifest)
        # 
        # This whole manifest may already have been executed and stored
        # as completed by the manifest_processor. If so, distribute the
        # given result
        # 
        if not manifest.start_next_operation():
            self.distribute_update_result(manifest.update_id,
                                          manifest.operation_results)
            # Recursively call self to engage next manifest.
            return self.start_next_manifest()

        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True
        
    def inform_hmi_of_new_operation(self,op):
        swm.dbus_method("org.genivi.hmi", "operation_started",
                        op.operation_id, op.time_estimate, op.hmi_message)
        return None
    
    def inform_hmi_of_new_manifest(self,manifest):
        total_time = 0
        for op in manifest.operations:
            total_time = total_time + op.time_estimate

        swm.dbus_method("org.genivi.hmi", "manifest_started",
                        manifest.update_id, total_time, manifest.description)
        return None
    
    def start_next_operation(self):
        #
        # If we are currently not processing an image, load
        # the one we just queued.
        #
        
        #
        # No manifest loaded.
        # Load next manifest and, if successful, start the
        # fist operation in said manifest
        #
        manifest = self.get_current_manifest()
        if not manifest:
            return self.start_next_manifest()

        # We have an active manifest. Check if we have an active operation.
        # If so return success
        if  manifest.active_operation:
            return True


        # We have an active manifest, but no active operation.
        # Try to start the next operation.
        # If that fails, we are out of operations in the current
        # manifest. Try to load the next manifest, which
        # will also start its first operation.
        if not manifest.start_next_operation():
            return self.manifest_processor.load_next_manifest()

        # Inform HMI of active operation
        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True

    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def update_available(self, 
                         update_id, 
                         description, 
                         signature,
                         request_confirmation,
                         send_reply,
                         send_error): 

        print "Got download available"
        print "  ID:      {}".format(update_id)
        print "  descr:   {}".format(description)
        print "  confirm: {}".format(request_confirmation)
        
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        #
        # Send a notification to the HMI to get user approval / decline
        # Once user has responded, HMI will invoke self.package_confirmation()
        # to drive the use case forward.
        #
        if request_confirmation:
            swm.dbus_method("org.genivi.hmi", "update_notification", update_id, description)
            print "  Called hmi.update_notification()"
            print "---"
            return None

        print "  No user confirmation requested. Will initiate download"
        print "---"
        self.initiate_download(update_id)
        return None


    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def update_confirmation(self,        
                            update_id, 
                            approved,
                            send_reply, 
                            send_error): 

        
        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        print "Got update_confirmation()."
        print "  Approved: {}".format(approved)
        print "  ID:       {}".format(update_id)
        if approved:
            #
            # Call the SOTA client and ask it to start the download.
            # Once the download is complete, SOTA client will call 
            # download complete on this process to actually
            # process the package.
            #
            print "Approved: Will call initiate_download()"
            self.initiate_download(update_id)
            print "Approved: Called sota_client.initiate_download()"
            print "---"
        else:
            # User did not approve. Send installation report
            print "Declined: Will call installation_report()"
            self.distribute_update_result(update_id, [
                swm.result('N/A',
                           swm.SWM_RES_USER_DECLINED,
                           "Installation declined by user")
            ]) 

            print "Declined. Called sota_client.installation_report()"
            print "---"

        return None

    @dbus.service.method("org.genivi.software_loading_manager", 
                         async_callbacks=('send_reply', 'send_error'))
    def download_complete(self,
                          update_image,
                          signature,
                          send_reply,
                          send_error): 
            
        print "Got download complete"
        print "  path:      {}".format(update_image)
        print "  signature: {}".format(signature)
        print "---"

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)
        print "FIXME: Check signature of update image"

        #
        # Queue the image.
        #
        try:
            self.manifest_processor.queue_image(update_image)
            self.start_next_operation()
        except Exception as e:
            print "Failed to process downloaded update: {}".format(e)
            traceback.print_exc()

        return None

    #
    # Receive and process a installation report.
    # Called by package_manager, partition_manager, or ecu_module_loader
    # once they have completed their process_update() calls invoked
    # by software_loading_manager
    #
    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def operation_result(self, 
                         transaction_id, 
                         result_code, 
                         result_text,
                         send_reply,
                         send_error): 

        try:
            print "Got operation_result()"
            print "  transaction_id: {}".format(transaction_id)
            print "  result_code:    {}".format(result_code)
            print "  result_text:    {}".format(result_text)
            print "---"

            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            manifest = self.get_current_manifest()
            if not manifest:
                print "Warning: No manifest to handle callback reply"
                return None

            manifest.complete_transaction(transaction_id, result_code, result_text)
            if not self.start_next_operation():
                self.distribute_update_result(manifest.update_id,
                                              manifest.operation_results)
        except Exception as e:
            print "Failed to process operation result: {}".format(e)
            traceback.print_exc()


    @dbus.service.method("org.genivi.software_loading_manager")
    def get_installed_packages(self, include_packegs, include_module_firmware): 
        print "Got get_installed_packages()"
        return [ "bluez_driver", "bluez_apps" ]

def usage():
    print "Usage:", sys.argv[0], "[-r] [-d database_file] "
    print
    print "  -r                Reset the completed operations database prior to running"
    print "  -d database_file  Path to database file to store completed operations in"
    print
    print "Example:", sys.argv[0],"-r -d /tmp/database"
    sys.exit(255)


print 
print "Software Loading Manager."
print

try:  
    opts, args= getopt.getopt(sys.argv[1:], "rd:")

except getopt.GetoptError:
    print "Could not parse arguments."
    usage()

db_path = "/tmp/completed_operations.json"
reset_db = False

for o, a in opts:
    if o == "-r":
        reset_db = True
    elif o == "-d":
        db_path = a
    else:
        print "Unknown option: {}".format(o)
        usage()

DBusGMainLoop(set_as_default=True)

# Check if we are to delete the old database.
if reset_db:
    try:
        os.remove(db_path)
    except:
        pass


slm_sota = SLMService(db_path)

while True:
    gtk.main_iteration()
