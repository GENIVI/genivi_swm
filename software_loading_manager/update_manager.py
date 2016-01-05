# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Library to process updates



import json
import os
import subprocess
import dbus
manifest_processor = None
from collections import deque

class OperationException(Exception):
    pass


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
                               ("blacklisted_packages", dbus.Array(manifest.blacklisted_packages, "s"))
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
                                          ("blacklisted_firmware", dbus.Array(manifest.blacklisted_firmware, "s"))
                                        ])
        }

        print "  SoftwareOperation(): Called"
        # Retrieve unique id for sofware operation
        if not 'id' in op_obj:
            raise OperationException("SoftwareOperation(): 'id' not defined in: {}".format(op_obj))

        self.operation_id = op_obj['id']
        self.arguments = []
        self.time_estimate = op_obj.get('time_estimate', 0)
        self.hmi_message = op_obj.get('hmi_message', '')
        self.on_failure = op_obj.get('on_failure', 'continue')
        self.bus = dbus.SessionBus()
        
        # Retrieve operation
        if not 'operation' in op_obj:
            raise OperationException("'operation' not defined in operation {}.".format(self.operation_id))

        operation = op_obj['operation']
        
        # Retrieve the operation descriptor
        if operation not in self.operation_descriptor:
            raise OperationException("operation {} not supported.".format(operation))

        # Store the DBUS path (org.genivi.xxx), method, and elements from
        # software operations to provide with DBUS call.
        (self.path, self.method, arguments) = self.operation_descriptor[operation]

        print "  SoftwareOperation(): operation_id:  {}".format(self.operation_id)
        print "  SoftwareOperation(): operation:     {}".format(operation)
        print "  SoftwareOperation(): time_estimate: {}".format(self.time_estimate)
        print "  SoftwareOperation(): hmi_message:   {}".format(self.hmi_message)
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

                    raise OperationException("Element {} not defined in operation: {}".format(argument,self.operation_id))
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
            bus_name = dbus.service.BusName(self.path, bus=self.bus)

            obj = self.bus.get_object(bus_name.get_name(), "/{}".format(self.path.replace(".", "/")))
            remote_method = obj.get_dbus_method(self.method, self.path)
            print "send_transaction(): id {}".format(transaction_id)
            print "send_transaction(): method {}".format(self.method)
            print "send_transaction(): arg {}".format(self.arguments)
            remote_method(transaction_id, *self.arguments)
        except Exception as e:
            print "SoftwareOperation.send_transaction({}): Exception: {}".format(self.operation_id, e)
            return False

        return True
    

#
# Load and execute a single manifest
#
class Manifest:
    # There is a better way of doing this, but
    # this will work for now
    def __init__(self,
                 blacklisted_firmware,
                 blacklisted_packages,
                 blacklisted_partitions,
                 manifest_processor):
        #
        # The transaction we are waiting for a reply callback on
        #
        # FIXME: Multiple parallel transactions not supported,
        #        although the manifest file format does.
        #
        self.active_operation = None
        self.manifest_processor = manifest_processor
        self.mount_point = manifest_processor.mount_point

        # Store the blacklists to be injected as arguments
        # where the operation descriptor specifies it.
        self.blacklisted_partitions = blacklisted_partitions
        self.blacklisted_firmware = blacklisted_firmware
        self.blacklisted_packages = blacklisted_packages

        # Reset the update result
        self.operation_results = []

    # Load a manifest from a file
    def load_from_file(self, manifest_fname):
        print "Manifest:load_from_file({}): Called.".format(manifest_fname)
        try:
            with open(manifest_fname, "r") as f:
                print "Opened. Will load string"
                return self.load_from_string(f.read())
            
        except IOError as e:
            print "Could not open manifest {}: {}".format(manifest_fname, e)
            return False

            
    # Load a manifest from a string
    def load_from_string(self, manifest_string):

        print "Manifest.load_from_string(): Called"
        try:
            manifest = json.loads(manifest_string)
        except ValueError as e:
            print "Manifest: Failed to parse JSON string: {}".format(e)
            return False

        # Retrieve top-level elements
        self.update_id = manifest.get('update_id', False)
        self.name = manifest.get('name', False)
        self.description = manifest.get('description', False)
        self.get_user_confirmation = manifest.get('get_user_confirmation', False)
        self.show_hmi_progress = manifest.get('show_hmi_progress', False)
        self.show_hmi_result = manifest.get('show_hmi_result', False)
        self.allow_downgrade = manifest.get('allow_downgrade', False)
        self.operations = deque()
        print "Manifest.update_id: {}".format(self.update_id)
        print "Manifest.name: {}".format(self.name)
        print "Manifest.description: {}".format(self.description)
        print "Manifest.get_user_confirmation: {}".format(self.get_user_confirmation)
        print "Manifest.show_hmi_progress: {}".format(self.show_hmi_progress)
        print "Manifest.show_hmi_result: {}".format(self.show_hmi_result)
        print "Manifest.allow_downgrade: {}".format(self.allow_downgrade)

        # Traverse all operations and create / load up a relevant 
        # object for each one.
        try:
            for op in manifest.get('operations', []):
                # Check if this operation has already been executed
                if self.manifest_processor.is_operation_completed(op.get('id', False)):
                    print "Software operation {} already completed. Skip".format(op.get('id', False))
                    continue

                # Retrieve the class to instantiate for the given operation
                                

                # Instantiate an object and feed it the manifest file 
                # operation object so that the new object can initialize
                # itself correctly.
                try:
                    op_obj = SoftwareOperation(self, op)
                except OperationException as e:
                    print "Could not process softare operation {}: {}".format(op.get('id', None), e)
                    return False

                # Add new object to operations we need to process
                self.operations.append(op_obj)
        except Exception as e:
            print "Manifest exception: {}".format(e)
            return False

        # Check that we have all mandatory fields set
        if False in [ self.update_id, self.name, self.description ]:
            print "One of update_id, name, description, or operations not set"
            return False

        return True

    def start_next_operation(self):
        if len(self.operations) == 0:
            return False
        
        # Retrieve next operation to process.
        op = self.operations.popleft()
        transaction_id = self.manifest_processor.get_next_transaction_id()

        #
        # Invoke the software operation object, created by
        # the Manifest object
        #
        if op.send_transaction(transaction_id):
            # Store this as an active transaction for which we 
            # are waiting on a callback reply.
            self.active_operation = op
            return True

        return False

    def is_operation_active(self):
        if self.active_operation:
            return True

        return False

    def get_operation_results(self):
        return self.operation_results

    def get_update_id(self):
        return self.update_id

    #
    # Check if this operation has already been executed.
    #
    def complete_transaction(self, transaction_id, result_code, result_text):
        # Check that we have an active transaction to
        # work with.
        if not self.active_operation:
            print "complete_transaction(): Warning: No active transaction for {}.".format(transaction_id)
            return False

        # We have completed this specific transaction
        # Store it so that we don't run it again on restart
        self.manifest_processor.add_completed_operation(self.active_operation.operation_id)

        #
        # Add the result code from a software operation to self
        # All operation results will be reported to SOTA.
        #
        result = {
            'id': self.active_operation.operation_id,
            'result_code': result_code,
            'result_text': result_text
        }
        self.operation_results.append(result)

        self.active_operation = None
        return True

    
#
# Simplistic storage of successfully completed
# operations
#
class ManifestProcessor:
    def __init__(self, storage_fname):

        #
        # A queue of Manifest objects waiting to be processed.
        #
        self.image_queue = deque()
        
        # File name we will use to read and store
        # all completed software operations.
        self.storage_fname = storage_fname

        # Transaction ID to use when sending
        # out a DBUS transaction to another
        # conponent. The component, in its callback
        # to us, will use the same transaction ID, allowing
        # us to tie a callback reply to an originating transaction.
        #
        # Please note that this is not the same thing as an operation id
        # which is an element  of the manifest uniquely identifying each
        # software operation.
        self.next_transaction_id = 0

        # The stored result for all completed software operations
        # Each element contains the software operation id, the
        # result code, and a descriptive text.
        self.operation_results = []

        self.current_manifest = None

        self.mount_point = None

        try:
            ifile = open(storage_fname, "r")
        except:
            # File could not be read. Start with empty
            self.completed = []
            return

        # Parse JSON object
        self.completed = json.load(ifile)
        ifile.close()

    # Write self to file prior to destroying.
    def __del__(self):
        ofile = open(self.storage_fname, "w")
        json.dump(self.completed, ofile)
        ofile.close()

    def queue_image(self, image_path):
        print "ManifestProcessor:queue_image({}): Called".format(image_path)
        self.image_queue.appendleft(image_path)

    def add_completed_operation(self, operation_id):
        print "ManifestProcessor.add_completed_operation({}): Called".format(operation_id)
        self.completed.append(operation_id)

    #
    # Return true if the provided tranasaction id has
    # been completed.
    #
    def is_operation_completed(self, transaction_id):
        return not transaction_id or transaction_id in self.completed
        
    def get_next_transaction_id(self):
        self.next_transaction_id = self.next_transaction_id + 1
        return self.next_transaction_id

    def get_current_manifest(self):
        return self.current_manifest
    
    #
    # Load the next manifest to process from the queue populated
    # by queue_manifest()
    #
    def load_next_manifest(self):
        #
        # Do we have any nore images to process?
        #
        print "ManifestProcessor:load_next_manifest(): Called"

        #
        # Unmount previous mount point
        #
        if self.mount_point:
            try:
                subprocess.check_call(["/bin/umount", self.mount_point ])

            except subprocess.CalledProcessError:
                print "Failed to unmount {}: {}".format(self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
        self.mount_point = None
        self.current_manifest = None
        
        if len(self.image_queue) == 0:
            print "ManifestProcessor:load_next_manifest(): Image queue is empty"
            return False

        print "ManifestProcessor:load_next_manifest(): #{}".format(len(self.image_queue))
        image_path = self.image_queue.pop()
        print "Will process update image: {}".format(image_path)

        # Mount the file system
        self.mount_point = "/tmp/swlm/{}".format(os.getpid())
        print "Will create mount point: {}".format(self.mount_point)
    
        try:
            os.makedirs(self.mount_point)
        except os.OSError as e:
            print "Failed to create {}: {}".format(self.mount_point, e)
            pass
        
        try:
            subprocess.check_call(["/bin/mount", image_path, self.mount_point ])
        except subprocess.CalledProcessError:
            print "Failed to mount {} on {}: {}".format(image_path,
                                                        self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
            return False

        # Create the new manifest object
        print "1"
        try:
            self.current_manifest = Manifest([], [], [], self)
        except Exception as e:
            print "Manifest exception: {}".format(e)
        print "2"

        # Specify manifest file to load
        manifest_file= "{}/update_manifest.json".format(self.mount_point)
    
        if not self.current_manifest.load_from_file(manifest_file):
            print "Failed to load manifest {}".format(manifest_file)
            self.current_manifest = None
            # Unmount file system
            try:
                subprocess.check_call(["/bin/umount", self.mount_point ])

            except subprocess.CalledProcessError:
                print "Failed to unmount {}: {}".format(self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
            self.mount_point = None
            return False


        return True
    
