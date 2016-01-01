# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces the SOTA client.



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import update_manager

    
#
# Define the DBUS-facing Software Loading Manager service
#
class SLMService(dbus.service.Object):
    def __init__(self):
        self.manifest_processor = update_manager.ManifestProcessor("/tmp/completed_operations.json")
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



        
    def initiate_download(self, package_id):
        #
        # Find the local sota client bus, object and method.
        #
        sota_client_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_client_obj = self.bus.get_object(sota_client_bus_name.get_name(), 
                                              "/org/genivi/sota_client")

        sota_initiate_download = sota_client_obj.get_dbus_method("initiate_download", 
                                                                 "org.genivi.sota_client")
        
        sota_initiate_download(package_id)

    # 
    # Distribute a report of a completed installation
    # to all involved parties. So far those parties are
    # the HMI and the SOTA client
    #
    def distribute_installation_report(self, 
                                       package_id, 
                                       results):
        #
        # Retrieve HMI bus name, object, and installation report method
        #
        hmi_bus_name = dbus.service.BusName("org.genivi.hmi", bus=self.bus)
        hmi_obj = self.bus.get_object(hmi_bus_name.get_name(), "/org/genivi/hmi")
        hmi_installation_report = hmi_obj.get_dbus_method("installation_report", 
                                                          "org.genivi.hmi")


        # Send installation report to HMI
        print "Sending report to hmi.installation_report()"
        hmi_installation_report(package_id, results)

        #
        # Retrieve SOTA bus name, object, and installation report method
        #
        sota_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_obj = self.bus.get_object(sota_bus_name.get_name(), "/org/genivi/sota_client")
        sota_installation_report = sota_obj.get_dbus_method("installation_report", 
                                                            "org.genivi.sota_client")
        
        # Send installation report to SOTA
        print "Sending report to sota.installation_report()"
        sota_installation_report(package_id, results)

    

    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def update_available(self, 
                         package_id, 
                         description, 
                         request_confirmation,
                         send_reply,
                         send_error): 

        #
        # Locate HMI bus, object, and update_notification() call.
        #
        hmi_bus_name = dbus.service.BusName("org.genivi.hmi", bus=self.bus)
        hmi_obj = self.bus.get_object(hmi_bus_name.get_name(), "/org/genivi/hmi")

        hmi_update_notification = hmi_obj.get_dbus_method("update_notification", 
                                                            "org.genivi.hmi")


        print "Got package available"
        print "  ID:      {}".format(package_id)
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
            hmi_update_notification(package_id, description)
            print "  Called hmi.update_notification()"
            print "---"
            return None

        print "  No user confirmation requested. Will initiate download"
        print "---"
        self.initiate_download(package_id)

        return None


    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def package_confirmation(self,        
                             approved,
                             package_id, 
                             send_reply, 
                             send_error): 

        
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)


        print "Got package_confirmation()."
        print "  Approved: {}".format(approved)
        print "  ID:       {}".format(package_id)
        if approved:
        
            #
            # Call the SOTA client and ask it to start the download.
            # Once the download is complete, SOTA client will call 
            # download complete on this process to actually
            # process the package.
            #
            print "Approved: Will call initiate_download()"
            self.initiate_download(package_id)
            print "Approved: Called sota_client.initiate_download()"
            print "---"
        else:
            # User did not approve. Send installation report
            print "Declined: Will call installation_report()"
            self.distribute_installation_report(package_id, [
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

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        print "FIXME: Check signature of update image"
        #
        # Queue the image.
        #
        self.manifest_processor.queue_image(update_image)

        #
        # If we are currently not processing an image, load
        # the one we just queued.
        #
        if not self.manifest_processor.get_current_manifest():
            self.manifest_processor.load_next_manifest()

        # If we either have a current manifest, or just succeeded
        # in loaded one, and we have no active software operations,
        # start the next
        manifest = self.manifest_processor.get_current_manifest() 

        if manifest and not manifest.is_operation_active():
            manifest.start_next_operation()

        return None

    #
    # Receive and process a installation report.
    # Called by package_manager, partition_manager, or ecu_module_loader
    # once they have completed their process_update() calls invoked
    # by software_loading_manager
    #
    @dbus.service.method("org.genivi.software_loading_manager")
    def operation_result(self, 
                         transaction_id, 
                         result_code, 
                         result_text): 

        print "Got intstallation_report()"
        print "  transaction_id: {}".format(transaction_id)
        print "  result_code:    {}".format(result_code)
        print "  result_text:    {}".format(result_text)
        print "---"

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        manifest = self.manifest_processor.get_current_manifest() 
        if not manifest:
            print "Warning: No manifest to handle callback reply"
            return None

        manifest.complete_transaction(transaction_id, result_code, result_text)

        #
        # Try to start next operation
        # 
        if not manifest.start_next_operation():
            #
            # We are done with the current manifest. Send the
            # result back to SOTA for reporting to backend server.
            #

            #
            # Send out the report to interested parties
            #
            self.distribute_installation_report(manifest.get_operation_results())

            #
            # Load the next manifest file.
            #
            self.manifest_processor.load_next_manifest()

            # If we either have a current manifest, or just succeeded
            # in loaded one, and we have no active software operations,
            # start the next operation
            manifest = self.manifest_processor.get_current_manifest() 
            if manifest:
                manifest.start_next_operation()
            

    @dbus.service.method("org.genivi.software_loading_manager")
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ { "package_id": "bluez_driver" },
                 { "package_id": "bluez_apps" } ]

print 
print "Software Loading Manager."
print
DBusGMainLoop(set_as_default=True)
slm_sota = SLMService()

while True:
    gtk.main_iteration()
