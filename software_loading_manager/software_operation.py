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
import settings
import logging

logger = logging.getLogger(settings.LOGGER)

#
# Software operation
# Contains a single software operation
# loaded from a manifest file.
#
class SoftwareOperation:
    def __init__(self, op_obj):
        logger.debug('SoftwareLoadingManager.SoftwareOperation: Called: %s', op_obj)
        # Retrieve unique id for sofware operation
        if not 'id' in op_obj:
            raise Exception("SoftwareOperation(): 'id' not defined in: {}".format(op_obj))

        self.operation_id = op_obj['id']
        self.arguments = []
        self.time_estimate = op_obj.get('timeEstimate', 0)
        self.description = op_obj.get('description', '')
        self.hmi_message = op_obj.get('hmiMessage', '')
        self.on_failure = op_obj.get('onFailure', 'continue')
        
        # Retrieve operation
        if not 'operation' in op_obj:
            raise Exception("'operation' not defined in operation {}.".format(self.operation_id))

        operation = op_obj['operation']
        
        # Retrieve the operation descriptor
        if operation not in settings.OPERATIONS:
            raise Exception("operation {} not supported.".format(operation))

        # Store the DBUS path (org.genivi.xxx), method, and elements from
        # software operations to provide with DBUS call.
        (self.path, self.method, arguments, parameters) = settings.OPERATIONS[operation]

        logger.debug('SoftwareLoadingManager.SoftwareOperation: operationId:  %s', self.operation_id)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: operation:    %s', operation)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: timeEstimate: %s', self.time_estimate)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: hmiMessage:   %s', self.hmi_message)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: description:  %s', self.description)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: onFailure:    %s', self.on_failure)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: path:         %s', self.path)
        logger.debug('SoftwareLoadingManager.SoftwareOperation: method:       %s', self.method)

        # Go through the list of arguments and extract them
        # from the manifest's software operation object
        # These arguments will be provided, in order, to the DBUS call
        for (argument, default_value) in arguments:
            if not argument in op_obj:
                # Argument was not present as element in software operation
                # and default was None, specifying that the argument
                # is mandatory.
                if default_value == None:
                    logger.error('SoftwareLoadingManager.SoftwareOperation: Mandatory element %s not defined in operation', argument)
                    raise Exception("Element {} not defined in operation: {}".format(argument,self.operation_id))
                else:
                    # Argument not found in software operation, but
                    # we have a default value
                    value = default_value
                    if isinstance(value, list) and not value:
                        # this is only necessary for empty lists as dbus won't be able to detect
                        # the type from an empty list, hence create an empty string list explicitly.
                        value = dbus.Array(value, 's')
                    logger.debug('SoftwareLoadingManager.SoftwareOperation: method_arg %s = %s (default)', argument, value)
            else:
                value = op_obj[argument]
                logger.debug('SoftwareLoadingManager.SoftwareOperation: method_arg %s = %s (manifest)', argument, value)

            #
            # Ugly workaround.
            # We need to prepend the image path with
            # the mount point so that the recipient (partition_manager, etc)
            # can open it.
            #
            if argument == "image":
                self.arguments.append("{}/{}".format(op_obj['mountPoint'], value))
            else:
                self.arguments.append(value)

        print "  ----"
    
    def send_transaction(self, transaction_id):
        try:
            swm.dbus_method(self.path, self.method, transaction_id, *self.arguments)
        except Exception as e:
            logger.error('SoftwareLoadingManager.SoftwareOperation.send_transaction(%s): Exception %s', transaction_id, e)
            return False

        return True
