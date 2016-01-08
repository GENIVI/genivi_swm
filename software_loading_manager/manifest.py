# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Library to process updates



import json
import os
import subprocess
import dbus
from collections import deque
import software_operation

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
                    op_obj = software_operation.SoftwareOperation(self, op)
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

