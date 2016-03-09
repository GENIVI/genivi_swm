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
import swm
import traceback
import settings
import logging

logger = logging.getLogger(settings.LOGGER)


#
# Load and execute a single manifest
#
class Manifest:

    def __init__(self, mount_point, manifest_file, database_file):
        #
        # The transaction we are waiting for a reply callback on
        #
        # FIXME: Multiple parallel transactions not supported,
        #        although the manifest file format does.
        #
        self.active_operation = None
        self.mount_point = mount_point
        self.manifest_file = manifest_file
        self.database_file = database_file

        # Transaction ID to use when sending
        # out a DBUS transaction to another
        # component. The component, in its callback
        # to us, will use the same transaction ID, allowing
        # us to tie a callback reply to an originating transaction.
        #
        # Please note that this is not the same thing as an operation id
        # which is an element  of the manifest uniquely identifying each
        # software operation.
        self.next_transaction_id = 0

        # Reset the update result
        self.operation_results = []
        
        # load database file            
        self.completed = []
        try:
            ifile = open(self.database_file, "r")
            self.completed = json.load(ifile)
            ifile.close()
        except IOError as e:
			pass

        # Load manifest file
        if not self.load_from_file(self.manifest_file):
            return None

    # Get next transaction id for dbus message
    def get_next_transaction_id(self):
        self.next_transaction_id = self.next_transaction_id + 1
        return self.next_transaction_id


    # Load a manifest from a file
    def load_from_file(self, manifest_fname):
        logger.debug('SoftwareLoadingManager.Manifest.load_from_file(%s): Called.', manifest_fname)
        try:
            with open(manifest_fname, "r") as f:
                logger.debug('SoftwareLoadingManager.Manifest.load_from_file(%s): File opened, loading strings.', manifest_fname)
                return self.load_from_string(f.read())
        except IOError as e:
           logger.error('SoftwareLoadingManager.Manifest.load_from_file(%s): Could not open manifest: %s.', manifest_fname, e)
           return False

            
    # Load a manifest from a string
    def load_from_string(self, manifest_string):

        logger.debug('SoftwareLoadingManager.Manifest.load_from_string(%s): Called.', manifest_string)
        try:
            manifest = json.loads(manifest_string)
        except ValueError as e:
            logger.error('SoftwareLoadingManager.Manifest.load_from_string(%s): Failed to parse JSON string: %s.', manifest_string, e)
            return False

        # Retrieve top-level elements
        self.update_id = manifest.get('updateId', False)
        self.name = manifest.get('name', False)
        self.description = manifest.get('description', False)
        self.show_hmi_progress = manifest.get('showHmiProgress', False)
        self.show_hmi_result = manifest.get('showHmiResult', False)
        self.get_user_confirmation = manifest.get('getUserConfirmation', False)
        self.operations = deque()
        logger.debug('SoftwareLoadingManager.Manifest.updateId:            %s', self.update_id)
        logger.debug('SoftwareLoadingManager.Manifest.name:                %s', self.name)
        logger.debug('SoftwareLoadingManager.Manifest.description:         %s', self.description)
        logger.debug('SoftwareLoadingManager.Manifest.getUserConfirmation: %s', self.get_user_confirmation)
        logger.debug('SoftwareLoadingManager.Manifest.showHmiProgress:     %s', self.show_hmi_progress)
        logger.debug('SoftwareLoadingManager.Manifest.showHmiResult:       %s', self.show_hmi_result)

        # Traverse all operations and create / load up a relevant 
        # object for each one.
        try:
            for op in manifest.get('operations', []):

                # Grab opearation id. 
                op_id = op.get('id', False)

                # Skip entire operation if operation_id is not defined.
                if not op_id:
                    logger.warning('SoftwareLoadingManager.Manifest.load_from_string(%s): Manifest operation is missing operationId. Skipped.', manifest_string)
                    continue

                # Check if this operation has already been executed
                if self.is_operation_completed(op_id):
                    # Add the result code for the given operation id
                    self.operation_results.append(
                        swm.result(op_id,
                                   swm.SWMResult.SWM_RES_ALREADY_PROCESSED,
                                   "Operation already processed")
                        )

                    logger.info('SoftwareLoadingManager.Manifest.load_from_string(%s): Manifest operation %s already completed. Deleted from manifest.', manifest_string, op_id)
                    # Continue with the next operation
                    continue

                # Retrieve the class to instantiate for the given operation
                                

                # Instantiate an object and feed it the manifest file 
                # operation object so that the new object can initialize
                # itself correctly.
                try:
                    op['mountPoint'] = self.mount_point
                    op_obj = software_operation.SoftwareOperation(op)
                except Exception as e:
                    logger.error('SoftwareLoadingManager.Manifest.load_from_string(%s): Could not process manifest operation: %s.\nSkipped', manifest_string, e)
                    return False

                # Add new object to operations we need to process
                self.operations.append(op_obj)
        except Exception as e:
            logger.error('SoftwareLoadingManager.Manifest.load_from_string(%s): Manifest exception: %s.', manifest_string, e)
            return False

        # Check that we have all mandatory fields set
        if False in [ self.update_id, self.name, self.description ]:
            logger.error('SoftwareLoadingManager.Manifest.load_from_string(%s): One of mandatory updateId, name, description. or operations not set.', manifest_string)
            return False

        return True

    def start_next_operation(self):
        if len(self.operations) == 0:
            return False
        
        # Retrieve next operation to process.
        op = self.operations.popleft()
 
        transaction_id = self.get_next_transaction_id()

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
            logger.warning('SoftwareLoadingManager.Manifest.complete_transaction(%s): No active transaction.', transaction_id)
            return False

        # We have completed this specific transaction
        # Store it so that we don't run it again on restart
        self.add_completed_operation(self.active_operation.operation_id)

        #
        # Add the result code from a software operation to self
        # All operation results will be reported to SOTA.
        #
        self.operation_results.append(
            swm.result(
                self.active_operation.operation_id,
                result_code,
                result_text)
        )

        self.active_operation = None
        return True
        
    #
    # Return true if the provided tranasaction id has
    # been completed.
    #
    def is_operation_completed(self, transaction_id):
        return not transaction_id or transaction_id in self.completed
        
    def add_completed_operation(self, operation_id):
        logger.debug('SoftwareLoadingManager.Manifest.add_completed_operation(%s): Called.', operation_id)
        self.completed.append(operation_id)
        # Slow, but we don't care.
        ofile = open(self.database_file, "w")
        json.dump(self.completed, ofile)
        ofile.close()



