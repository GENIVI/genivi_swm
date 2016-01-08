# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces the SOTA client.



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import manifest_processor
import traceback
import sys

#
# Define the DBUS-facing Software Loading Manager service
#
class SLMService(dbus.service.Object):
    def __init__(self):
        self.manifest_processor = manifest_processor.ManifestProcessor("/tmp/completed_operations.json")
        # Setup a update processor
        
        # Retrieve the session bus.
        self.bus = dbus.SessionBus()

        # Define our own bus name
        self.slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', 
                                                 bus=self.bus)
        
        # Define our own object on the software_loading_manager bus
        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     "/org/genivi/software_loading_manager")


    def dbus_method(self, path, method, *arguments):
        try:
            bus_name = dbus.service.BusName(path, bus=self.bus)
            obj = self.bus.get_object(bus_name.get_name(), "/{}".format(path.replace(".", "/")))
            remote_method = obj.get_dbus_method(method, path)
            print "Will send: {}:{}".format(path, method)
            print "Will send: {}".format(arguments)
            remote_method(*arguments)
        except Exception as e:
            print "dbus_method(): Exception: {}".format(e)
            traceback.print_exc()
            
    def initiate_download(self, package_id):
        #
        # Find the local sota client bus, object and method.
        #
        sota_client_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_client_obj = self.bus.get_object(sota_client_bus_name.get_name(), 
                                              "/org/genivi/sota_client")

        sota_initiate_download = sota_client_obj.get_dbus_method("initiate_download", 
                                                                 "org.genivi.sota_client")
        
        self.dbus_method("org.genivi.sota_client", "initiate_download", package_id)


    # 
    # Distribute a report of a completed installation
    # to all involved parties. So far those parties are
    # the HMI and the SOTA client
    #
    def distribute_update_result(self, 
                                 update_id, 
                                 results):
        # Send installation report to HMI
        print "Sending report to hmi.installation_report()"
        self.dbus_method("org.genivi.hmi", "update_report", update_id, results)

        # Send installation report to SOTA
        print "Sending report to sota.installation_report()"
        self.dbus_method("org.genivi.sota_client", "update_report", update_id, results)

    
    def get_current_manifest(self):
        print "proc: {}".format(self.manifest_processor)
        print "cur: {}".format(self.manifest_processor.current_manifest)

        return self.manifest_processor.current_manifest

    def start_next_manifest(self):
        if not self.manifest_processor.load_next_manifest():
            return False

        manifest = self.get_current_manifest()
        self.inform_hmi_of_new_manifest(manifest)
        manifest.start_next_operation()
        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True
        
    def inform_hmi_of_new_operation(self,op):
        self.dbus_method("org.genivi.hmi", "operation_started",
                         op.operation_id, op.time_estimate, op.hmi_message)
        return None
    
    def inform_hmi_of_new_manifest(self,manifest):
        total_time = 0
        for op in manifest.operations:
            total_time = total_time + op.time_estimate

        self.dbus_method("org.genivi.hmi", "manifest_started",
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
        print "1"
        manifest = self.get_current_manifest()
        if not manifest:
            print "2"
            return self.start_next_manifest()


        print "3"
        # We have an active manifest. Check if we have an active operation.
        # If so return success
        if  manifest.active_operation:
            print "4"
            return True

        # We have an active manifest, but no active operation.
        # Try to start the next operation.
        # If that fails, we are out of operations in the current
        # manifest. Try to load the next manifest, which
        # will also start its first operation.
        if not manifest.start_next_operation():
            print "6"
            return self.manifest_processor.load_next_manifest()

        # Inform HMI of active operation
        print "7"
        self.inform_hmi_of_new_operation(manifest.active_operation)
        return True



    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def update_available(self, 
                         update_id, 
                         description, 
                         request_confirmation,
                         send_reply,
                         send_error): 

        print "Got package available"
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
            self.dbus_method("org.genivi.hmi", "update_notification", update_id, description)
            print "  Called hmi.update_notification()"
            print "---"
            return None

        print "  No user confirmation requested. Will initiate download"
        print "---"
        self.initiate_download(update_id)

        return None

    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def package_confirmation(self,        
                             approved,
                             update_id, 
                             send_reply, 
                             send_error): 

        
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)


        print "Got package_confirmation()."
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
                { result_code: 10, result_text: "Installation declined by user"}
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
                                          manifest.operation_result)


                
    @dbus.service.method("org.genivi.software_loading_manager")
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ "bluez_driver", "bluez_apps" ]

print 
print "Software Loading Manager."
print
DBusGMainLoop(set_as_default=True)
slm_sota = SLMService()

while True:
    gtk.main_iteration()
