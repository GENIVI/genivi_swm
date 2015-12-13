# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces the SOTA client.



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

            
    
#
# Define the DBUS-facing Software Loading Manager service
#
class SLMService(dbus.service.Object):
    def __init__(self):
        
        # Retrieve the session bus.
        self.bus = dbus.SessionBus()

        # Define our own bus name
        self.slm_bus_name = dbus.service.BusName('org.genivi.software_loading_manager', 
                                                 bus=self.bus)
        
        # Define our own object on the software_loading_manager bus
        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     "/org/genivi/software_loading_manager")




    # 
    # Distribute a report of a completed installation
    # to all involved parties. So far those parties are
    # the HMI and the SOTA client
    #
    def distribute_installation_report(self, 
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
        #
        # Retrieve HMI bus name, object, and installation report method
        #

        hmi_bus_name = dbus.service.BusName("org.genivi.hmi", bus=self.bus)
        hmi_obj = self.bus.get_object(hmi_bus_name.get_name(), "/org/genivi/hmi")
        hmi_installation_report = hmi_obj.get_dbus_method("installation_report", 
                                                          "org.genivi.hmi")


        # Send installation report to HMI
        print "Sending report to hmi.installation_report()"
        hmi_installation_report(package_id, 
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
                                result_msg)


        #
        # Retrieve SOTA bus name, object, and installation report method
        #
        sota_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_obj = self.bus.get_object(sota_bus_name.get_name(), "/org/genivi/sota_client")
        sota_installation_report = sota_obj.get_dbus_method("installation_report", 
                                                            "org.genivi.sota_client")
        
        # Send installation report to SOTA
        print "Sending report to sota.installation_report()"
        sota_installation_report(package_id, 
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
                                 result_msg)


        
    

    @dbus.service.method("org.genivi.software_loading_manager")
    def update_available(self, 
                         package_id, 
                         major, 
                         minor, 
                         patch, 
                         command, 
                         size, 
                         description, 
                         vendor,
                         target): 

        #
        # Locate HMI bus, object, and update_notification() call.
        #
        hmi_bus_name = dbus.service.BusName("org.genivi.hmi", bus=self.bus)
        hmi_obj = self.bus.get_object(hmi_bus_name.get_name(), "/org/genivi/hmi")

        hmi_update_notification = hmi_obj.get_dbus_method("update_notification", 
                                                            "org.genivi.hmi")


        print "Got package available"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)

        #
        # Send a notification to the HMI to get user approval / decline
        # Once user has responded, HMI will invoke self.package_confirmation()
        # to drive the use case forward.
        #
        hmi_update_notification(package_id, 
                                  major, 
                                  minor, 
                                  patch, 
                                  command, 
                                  size, 
                                  description, 
                                  vendor,
                                  target)

        print "Called hmi.update_notification()"
        print "---"
        return None
        
        
    @dbus.service.method("org.genivi.software_loading_manager",
                         async_callbacks=('send_reply', 'send_error'))
    def package_confirmation(self,        
                             approved,
                             package_id, 
                             major, 
                             minor, 
                             patch, 
                             command, 
                             size, 
                             description, 
                             vendor,
                             target, 
                             send_reply, 
                             send_error): 

        
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        #
        # Find the local sota client bus, object and method.
        #
        sota_client_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_client_obj = self.bus.get_object(sota_client_bus_name.get_name(), 
                                              "/org/genivi/sota_client")

        sota_initiate_download = sota_client_obj.get_dbus_method("initiate_download", 
                                                                 "org.genivi.sota_client")
        
        print "Got package_confirmation()."
        print "  Approved: {}".format(approved)
        print "  ID:       {}".format(package_id)
        print "  ver:      {}.{}.{} ".format(major, minor, patch)
        print "  cmd:      {}".format(command)
        print "  size:     {}".format(size)
        print "  descr:    {}".format(description)
        print "  vendor:   {}".format(vendor)
        print "  target:   {}".format(target)
        if approved:
            #
            # Call the SOTA client and ask it to start the download.
            # Once the download is complete, SOTA client will call 
            # download complete on this process to actually
            # process the package.
            #
            print "Approved: Will call initiate_download()"
            sota_initiate_download(package_id, major, minor, patch)
            print "Approved: Called sota_client.initiate_download()"
            print "---"
        else:
            # User did not approve. Send installation report
            print "Declined: Will call installation_report()"
            self.distribute_installation_report(package_id, 
                                                major, 
                                                minor, 
                                                patch, 
                                                command, 
                                                '', # No path yet since it was declined
                                                size,
                                                description, 
                                                vendor, 
                                                target,
                                                2, 
                                                'Package declined by user')
            print "Declined. Called sota_client.installation_report()"
            print "---"

            
        return None
        
    @dbus.service.method("org.genivi.software_loading_manager", 
                         async_callbacks=('send_reply', 'send_error'))
    def download_complete(self,
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
                          send_reply,
                          send_error): 
            
        print "Got download complete"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  path:   {}".format(path)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        print "---"

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        target_bus_name = dbus.service.BusName('org.genivi.'+target,
                                               bus=self.bus)
        
        target_obj = self.bus.get_object(target_bus_name.get_name(), 
                                         "/org/genivi/" + target)
            

        process_update = target_obj.get_dbus_method("process_update", 
                                                     "org.genivi." + target)


        #
        # Locate and invoke the correct package processor 
        # (ECU1ModuleLoaderProcessor.process_impl(), etc)
        #
        process_update(package_id,
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

        
    #
    # Receive and process a installation report.
    # Called by package_manager, partition_manager, or ecu_module_loader
    # once they have completed their process_update() calls invoked
    # by software_loading_manager
    #
    @dbus.service.method("org.genivi.software_loading_manager")
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
                            result_text): 

        print "Got intstallation_report()"
        print "  ID:          {}".format(package_id)
        print "  ver:         {}.{}.{} ".format(major, minor, patch)
        print "  cmd:         {}".format(command)
        print "  path:        {}".format(path)
        print "  size:        {}".format(size)
        print "  descr:       {}".format(description)
        print "  vendor:      {}".format(vendor)
        print "  target:      {}".format(target)
        print "  result_code: {}".format(result_code)
        print "  result_text: {}".format(result_text)
        print "---"

        # Send out the report to interested parties
        self.distribute_installation_report(package_id, 
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
                                            result_text)

    @dbus.service.method("org.genivi.software_loading_manager")
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ { "package_id": "bluez_driver", 
                   "major": 1,
                   "minor": 2,
                   "patch": 3 },
                 { "package_id": "bluez_apps", 
                   "major": 3,
                   "minor": 2,
                   "patch": 1 } ]
                 

print 
print "Software Loading Manager."
print

DBusGMainLoop(set_as_default=True)
slm_sota = SLMService()

while True:
    gtk.main_iteration()
