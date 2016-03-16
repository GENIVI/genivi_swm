# -*- coding: utf-8 -*-
""" Database library to store update progress and results.

This module provides classes and methods to process a manifest with
software updates.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""


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
import database

logger = logging.getLogger(settings.LOGGER)


#
# Load and execute a single manifest
#
class Manifest:
    """Load a manifest and execute the operations
    
    This class loads a manifest from file and executes the operations
    it contains.
    """

    def __init__(self, mount_point, manifest_file, dbstore):
        """Constructor
        
        Initialize a Manifest object and kick off processing.
        
        @param mount_point Mount point of the software update squashfs archive
        @param manifest_file Path to the file containing the manifest
        @param dbstore Database store to log operations
        
        @return Manifest object if successful or None otherwise
        """
        #
        # The transaction we are waiting for a reply callback on
        #
        # FIXME: Multiple parallel transactions not supported,
        #        although the manifest file format does.
        #
        self.active_operation = None
        self.mount_point = mount_point
        self.manifest_file = manifest_file
        self.dbstore = dbstore
        self.software_update = None

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
        
        # Load manifest file
        if not self.load_from_file(self.manifest_file):
            return None


    def get_next_transaction_id(self):
        """Get next transaction number for software operations
        
        Each software operation is dispatched to an execution module via
        dbus. A transaction id is used to identify the operation.
        
        @return Next transaction id.
        """
        self.next_transaction_id = self.next_transaction_id + 1
        return self.next_transaction_id


    def load_from_file(self, manifest_fname):
        """Load manifest file and process it
        
        Loads a manifest from file and processes it.
        
        @param manifest_fname Path to the manifest file
        
        @return True if loading and processing of the manifest file was successful,
                False otherwise
        """

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
        """Load manifest from string and process it
        
        Loads a manifest from a string and processes it.
        
        @param manifest_string String containing the manifest
        
        @return True if processing the manifest string was successful,
                False otherwise
        """

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

        # Query database
        self.software_update = database.SWUpdate.getSWUpdate(self.dbstore, self.update_id, self.name)
        self.software_update.start()

        # Traverse all operations and create / load up a relevant 
        # object for each one.
        try:
            for op in manifest.get('operations', []):

                # Grab opearation id. 
                op_id = op.get('id', False)
                op_operation = op.get('operation', False)

                # Skip entire operation if operation_id is not defined.
                if not op_id:
                    logger.warning('SoftwareLoadingManager.Manifest.load_from_string(%s): Manifest operation is missing operationId. Skipped.', manifest_string)
                    continue
                    
                # Get operation from database or create a new one if id does not exist
                swo = self.software_update.getSWOperation(op_id)
                if not swo:
                    swo = self.software_update.addSWOperation(op_id, op_operation)

                # Check if this operation has already been executed
                if swo.isfinished():
                    # Add the result code for the given operation id
                    self.operation_results.append(
                        swm.result(op_id,
                                   swm.SWMResult.SWM_RES_ALREADY_PROCESSED,
                                   "Operation already processed")
                        )
                    logger.info('SoftwareLoadingManager.Manifest.load_from_string(%s): Manifest operation %s already completed. Deleted from manifest.', manifest_string, op_id)
                    # Continue with the next operation
                    continue

                # Start the operation
                swo.start()

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
        """Process the next software operation
        
        Take the next operation off the queue and process it.
        
        @return True if processing the operation was successful
                False otherwise
        """
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
    def complete_operation(self, transaction_id, result_code, result_text):
        """Complete currently pending operation
        
        Callback in response to an operation started with start_next_operation.
        
        @param transaction_id Id of the transaction
        @param result_code Code indicating the result of the operation
        @param result_text Text with result details
        
        @return True Sucessfully completed operation
                False No active operation
        """
        # Check that we have an active operation to
        # work with.
        if not self.active_operation:
            logger.warning('SoftwareLoadingManager.Manifest.complete_operation: No active operation.')
            return False

        # We have completed this specific transaction
        # Store it so that we don't run it again on restart
        swo = self.software_update.getSWOperation(self.active_operation.operation_id)
        swo.finish(result_code)
        self.software_update.finish()
        self.software_update.update()

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
        


