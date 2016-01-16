# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Library to process updates


import json
import os
import subprocess
import dbus
import swm
#
# Software operation
# Contains a single software operation
# loaded from a manifest file.
#
class SoftwareOperation:
    def __init__(self, manifest, op_obj):
        self.operation_descriptor = {
            'install_package': (
                # Path to DBUS and object. 
            "org.genivi.package_manager",

            # Method to call
            "install_package",
            # Elements to extract fron software operations object and to
            # provide as DBUS call arguments.
            # Second element in tupe is default value. None -> Mandatory 
            [ ("image", None),
              ("blacklisted_packages", dbus.Array(manifest.blacklisted_packages, "s"))

            ]),

        'upgrade_package': ( "org.genivi.package_manager",
                             "upgrade_package",
                             [ ("image", None),
                               ("blacklisted_packages", dbus.Array(manifest.blacklisted_packages, "s")),
                               ("allow_downgrade", manifest.allow_downgrade)
                             ]),

        'remove_package': ( "org.genivi.package_manager",
                            "remove_package",
                            [ ("package_id", None) ]),

        'start_components': ( "org.genivi.lifecycle_manager",
                              "start_components",
                              [ ("components", None) ]),

        'stop_components': ( "org.genivi.lifecycle_manager",
                             "stop_components",
                             [ ("components", None) ]),

        'reboot': ( "org.genivi.lifecycle_manager",
                    "reboot",
                    [ ("boot_parameters", "") ]),

        'create_disk_partition': ( "org.genivi.partition_manager",
                                   "create_disk_partition",
                                   [ ("disk", None), ("partition_number", None),
                                     ("type", None), ("start", None), ("size", None),
                                     ("guid", ""), ("name", "") ]),
            
        'resize_disk_partition': ( "org.genivi.partition_manager", "resize_disk_partition",
                                   [ ("disk", None), ("partition_number", None),
                                     ("start", None), ("size", None) ]),

        'delete_disk_partition': ( "org.genivi.partition_manager", "delete_disk_partition",
                                   [ ("disk", None), ("partition_number", None) ]),


        'write_disk_partition': ( "org.genivi.partition_manager", "write_disk_partition",
                                  [ ("disk", None), ("partition_number", None),
                                    ("image", None),
                                    ("blacklisted_partitions", dbus.Array(manifest.blacklisted_partitions, "s"))
        ]),
        
        'patch_disk_partition': ( "org.genivi.partition_manager", "patch_disk_partition",
                                  [ ("disk", None), ("partition_number", None),
                                    ("image", None),
                                    ("blacklisted_partitions", dbus.Array(manifest.blacklisted_partitions, "s"))
                                  ]),
        
        # FIXME: We need to find a specific module loader
        #        that handles the target module. 
        #        org.genivi.module_loader needs to be replaced
        #        by org.genivi.module_loader_ecu1
        #        This should be done programmatically
        'flash_module_firmware_ecu1': ( "org.genivi.module_loader_ecu1", "flash_module_firmware",
                                        [ ("image", None),
                                          ("blacklisted_firmware", dbus.Array(manifest.blacklisted_firmware, "s")),
                                          ("allow_downgrade", manifest.allow_downgrade)
                                        ])
        }

        print "  SoftwareOperation(): Called"
        # Retrieve unique id for sofware operation
        if not 'id' in op_obj:
            raise Exception("SoftwareOperation(): 'id' not defined in: {}".format(op_obj))

        self.operation_id = op_obj['id']
        self.arguments = []
        self.time_estimate = op_obj.get('time_estimate', 0)
        self.description = op_obj.get('description', '')
        self.on_failure = op_obj.get('on_failure', 'continue')
        
        # Retrieve operation
        if not 'operation' in op_obj:
            raise Exception("'operation' not defined in operation {}.".format(self.operation_id))

        operation = op_obj['operation']
        
        # Retrieve the operation descriptor
        if operation not in self.operation_descriptor:
            raise Exception("operation {} not supported.".format(operation))

        # Store the DBUS path (org.genivi.xxx), method, and elements from
        # software operations to provide with DBUS call.
        (self.path, self.method, arguments) = self.operation_descriptor[operation]

        print "  SoftwareOperation(): operation_id:  {}".format(self.operation_id)
        print "  SoftwareOperation(): operation:     {}".format(operation)
        print "  SoftwareOperation(): time_estimate: {}".format(self.time_estimate)
        print "  SoftwareOperation(): description:   {}".format(self.description)
        print "  SoftwareOperation(): on_failure:    {}".format(self.on_failure)
        print "  SoftwareOperation(): dbus path:     {}".format(self.path)
        print "  SoftwareOperation(): dbus method:   {}".format(self.method)
        # Go through the list of arguments and extract them
        # from the manifest's software operation object
        # These arguments will be provided, in order, to the DBUS call
        for (argument, default_value) in arguments:
            if not argument in op_obj:
                # Argument was not present as element in software operation
                # and default was None, specifying that the argument
                # is mandatory.
                if default_value == None:
                    print "  SoftwareOperation(): Mandatory element {} not defined in operation".format(argument)

                    raise Exception("Element {} not defined in operation: {}".format(argument,self.operation_id))
                else:
                    # Argument not found in software operation, but
                    # we have a default value
                    value = default_value
                    print "  SoftwareOperation(): method_arg {} = {} (default)".format(argument, value)
            else:
                value = op_obj[argument]
                print "  SoftwareOperation(): method_arg {} = {} (from manifest)".format(argument, value)

            #
            # Ugly workaround.
            # We need to prepend the image path with
            # the mount point so that the recipient (partition_manager, etc)
            # can open it.
            #
            if argument == "image":
                self.arguments.append("{}/{}".format(manifest.mount_point, value))
            else:
                self.arguments.append(value)

        print "  ----"
    
    def send_transaction(self, transaction_id):
        try:
            swm.dbus_method(self.path, self.method, transaction_id, *self.arguments)
        except Exception as e:
            print "SoftwareOperation.send_transaction({}): Exception: {}".format(self.operation_id, e)
            return False

        return True
