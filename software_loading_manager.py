# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python dbus service that faces the SOTA client.



import gtk
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
package_manager = None
partition_manager = None
module_loader = None
hmi = None
dbus_name="org.genivi.software_loading_manager"

            

#
# PackageProcessingBase, inherited by the package manager, the
# partition manager, and all module loaders, provides the
# class process() method used to execute all package operations.
#
# Process will look at target and call the correct subclass's
# process_impl() method to forward the package operation
# to the correct python process.
#
class PackageProcessingBase(dbus.service.Object):
    instances = {}

    #
    # Retrieve the subclass instance registered with
    # a name matching 'target' argument and invoke
    # its process_impl() metnod.
    # The sublcass (PackageProcessingBase, ECU1ModuleLoaderProcessor, etc)
    # and its process_impl() will forward the package operation to the
    # correct DBUS object (package_manager.py, ecu1_loading_mnager.py, etc),
    # and return the result.
    #
    @staticmethod
    def process(path,
                package_id,
                major, 
                minor, 
                patch, 
                command,
                size, 
                description,
                vendor,
                target): 
        print "process(): {}".format(target)
        print "process(): {}".format(PackageProcessingBase.instances)
        if target not in PackageProcessingBase.instances:
            print "PackageProcessingBase.process({}): Target not found"
            return (99, "Unknown target: {}".format(target))
            
        process = PackageProcessingBase.instances[target]
        print "process: found {}".format(type(process).__name__)
        return process.process_impl(path,
                                    package_id,
                                    major, 
                                    minor, 
                                    patch, 
                                    command,
                                    size, 
                                    description,
                                    vendor,
                                    target)


    def __init__(self, name):
        self.bus = dbus.SessionBus()
        self.name = name
        self.slm_bus_name = dbus.service.BusName(dbus_name, bus=self.bus)
        print "Base class constructor from {}: {}".format(type(self).__name__, name)
        PackageProcessingBase.instances[name] = self
        self.module_loader_bus_name = dbus.service.BusName(dbus_name,
                                                           bus=self.bus)

        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     "/org/genivi/software_loading_manager" + self.name)


    def __del__(self):
        del PackageProcessingBase.instances[self.name]
        
       

    # Baseclass implementation.
    # Fail out.
    def process_impl(self, 
                     path,
                     package_id,
                     major, 
                     minor, 
                     patch, 
                     command,
                     size, 
                     description,
                     vendor,
                     target): 
        print "ERROR: PackagingProcessBase.process_impl(): Base class called"
        assert(False)



class ECU1ModuleLoaderProcessor(PackageProcessingBase):
    def __init__(self):
        super(ECU1ModuleLoaderProcessor, self).__init__("ecu1_loader")

    def process_impl(self, 
                     path,
                     package_id,
                     major, 
                     minor, 
                     patch, 
                     command,
                     size, 
                     description,
                     vendor,
                     target): 
        print "{}: Got process_impl() call".format(type(self).__name__)
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        return (0, "ECU1 flashing successful")


class PackageManagerProcessor(PackageProcessingBase):
    def __init__(self):
        super(PackageManagerProcessor, self).__init__("package_manager")
        pkg_mgr_bus_name = dbus.service.BusName("org.genivi.package_manager",
                                                     bus=self.bus)
        pkg_mgr_obj = self.bus.get_object("org.genivi.package_manager",
                                          "/org/genivi/package_manager")

        self.process_package_dbus = pkg_mgr_obj.get_dbus_method("process_package", 
                                                                "org.genivi.package_manager")
        self.get_installed_packages_dbus = pkg_mgr_obj.get_dbus_method("get_installed_packages", 
                                                                       "org.genivi.package_manager")

    
    def process_impl(self, 
                     path,
                     package_id,
                     major, 
                     minor, 
                     patch, 
                     command,
                     size, 
                     description,
                     vendor,
                     target): 
        print "{}: Got process_impl() call".format(type(self).__name__)
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target) 

        # res = self.process_package_dbus(path,
        #                                 package_id,
        #                                 major, 
        #                                 minor, 
        #                                 patch, 
        #                                 command,
        #                                 size, 
        #                                 description,
        #                                 vendor,
        #                                 target)
        # return res
        return (0, "Package installation successful")
            
    
#
# SOTA Client-facing methods
#
class SLMService(dbus.service.Object):
    def __init__(self):
        self.bus = dbus.SessionBus()
        self.slm_bus_name = dbus.service.BusName(dbus_name, bus=self.bus)
        self.initiate_download_dbus = None
        self.installation_report_dbus = None
        dbus.service.Object.__init__(self, 
                                     self.slm_bus_name, 
                                     "/org/genivi/software_loading_manager")



    def handle_reply(self, r):
        #print "Got reply", r
        pass 

    def handle_error(self, e):
        #print "Got error", e
        pass

    def initiate_download(self, *args):
        print "initiate_download: {}".format(args)
        print "initiate_download self: {}".format(self)
        self.initiate_download_dbus("pkg_id", 4,5,6,
                                    reply_handler = self.handle_reply,
                                    error_handler = self.handle_error)
        # self.initiate_download_dbus(*args)
        print "done"

    def installation_report(self, *args):
        self.installation_report_dbus(*args,
                                      reply_handler = self.handle_reply,
                                      error_handler = self.handle_error)
        
    

    @dbus.service.method("org.genivi.software_loading_manager")
    def package_available(self, 
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
        # We need to defer the binding of our local sota client proxy object
        # until when we actually get called to make sure that
        # the sota client is available.
        #
        # We re-bind every time since the sota client (in this setup)
        # is a short-lived command line tool that re-registers its objects
        # every time it is invoked.
        #
        self.sota_client_bus_name = dbus.service.BusName("org.genivi.sota_client", bus=self.bus)
        sota_client_obj = self.bus.get_object(self.sota_client_bus_name.get_name(), 
                                              "/org/genivi/sota_client")

        self.initiate_download_dbus = sota_client_obj.get_dbus_method("initiate_download", 
                                                                      "org.genivi.sota_client")
        
        self.installation_report_dbus = sota_client_obj.get_dbus_method("installation_report", 
                                                                        "org.genivi.sota_client")

        print "Got package available"
        print "  ID:     {}".format(package_id)
        print "  ver:    {}.{}.{} ".format(major, minor, patch)
        print "  cmd:    {}".format(command)
        print "  size:   {}".format(size)
        print "  descr:  {}".format(description)
        print "  vendor: {}".format(vendor)
        print "  target: {}".format(target)
        self.initiate_download(package_id, major, minor, patch)
        print "Called initiate_download_dbus()"
        print "---"
        return True
        
    @dbus.service.method("org.genivi.software_loading_manager")
    def download_complete(self,
                          path,
                          package_id,
                          major, 
                          minor, 
                          patch, 
                          command,
                          size, 
                          description,
                          vendor,
                          target): 
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

        # Locate and invoke the correct package processor 
        # (ECU1ModuleLoaderProcessor.process_impl(), etc)
        #
        (res, res_desc) = PackageProcessingBase.process(path,
                                                        package_id,
                                                        major, 
                                                        minor, 
                                                        patch, 
                                                        command,
                                                        size, 
                                                        description,
                                                        vendor,
                                                        target)


        self.installation_report(package_id, major, minor, patch, res, res_desc)
        return True
        
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
                 




DBusGMainLoop(set_as_default=True)
slm_sota = SLMService()
package_manager = PackageManagerProcessor()
ecu1_module_loader = ECU1ModuleLoaderProcessor()
#
#
#
while True:
    gtk.main_iteration()
