# -*- coding: utf-8 -*-
""" Database library to store update progress and results.

This module provides the core library for Software Management.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""

import dbus
import traceback
import settings
import logging

logger = logging.getLogger(settings.LOGGER)


# enum implementation not official until Python 3.4
class SWMResult():
    """Result Codes for Operations
    
    This class defines the result codes for operations. The result codes
    are shared across all SWM components.
    
    This would be a perfect candidate for the new Python enum type but that
    is not official until Python 3.4.
    """
    SWM_RES_OK = 0
    SWM_RES_ALREADY_PROCESSED = 1
    SWM_RES_DEPENDENCY_FAILURE = 2
    SWM_RES_VALIDATION_FAILED = 3
    SWM_RES_INSTALL_FAILED = 4
    SWM_RES_UPGRADE_FAILIED = 5
    SWM_RES_REMOVAL_FAILED = 6
    SWM_RES_FLASH_FAILED = 7
    SWM_RES_CREATE_PARTITION_FAILED = 8
    SWM_RES_DELETE_PARTITION_FAILED = 9
    SWM_RES_RESIZE_PARTITION_FAILED = 10
    SWM_RES_WRITE_PARTITION_FAILED = 11
    SWM_RES_PATCH_PARTITION_FAILED = 12
    SWM_RES_USER_DECLINED = 13
    SWM_RES_OPERATION_BLACKLISTED = 14
    SWM_RES_DISK_FULL = 15
    SWM_RES_NOT_FOUND = 16
    SWM_RES_OLD_VERSION = 17
    SWM_RES_INTERNAL_ERROR = 18
    SWM_RES_GENERAL_ERROR = 19
    
    
    @classmethod
    def isValid(self, code):
        """Check if a code is valid
        """
        return (code >= self.SWM_RES_OK) and (code <= self.SWM_RES_GENERAL_ERROR)


def result(operation_id, code, text):
    """Encode a result
    
    This method encodes operation id, result code and result text into
    a dictionary of dbus types.
    
    @param operation_id Id of the operation for which the result is reported
    @param code Result code of the operation (one of SWMResult)
    @param text Text message
    
    @return Result dictionary using dbus types.
    """
    if not SWMResult.isValid(code):
        code = SWMResult.SWM_GENERAL_ERROR
    
    return {
        'id': dbus.String(operation_id, variant_level=1),
        'result_code': dbus.Int32(code, variant_level=1),
        'result_text': dbus.String(text, variant_level=1)
    }


def dbus_method(path, method, *arguments):
    """Invokes dbus method
    
    Invokes method with arguments via dbus.
    
    @param method Dbus method
    @param arguments Dictionary of arguments for the method
    
    @return Always None
    """
    try:
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(path, bus=bus)
        obj = bus.get_object(bus_name.get_name(), "/{}".format(path.replace(".", "/")))
        remote_method = obj.get_dbus_method(method, path)
        remote_method(*arguments)
    except Exception as e:
        logger.error('common.swm: dbus_method(%s, %s): Exception: %s', path, method, e)
    return None

            
def send_operation_result(transaction_id, result_code, result_text):
    """Send back operation result
    
    Software Loading Manager will distribute the report to all interested parties.
    
    @param transaction_id Id of the transaction for which to report results
    @param result_code Result code of the operation (one of SWMResult)
    @param result_text Text message
    
    @return Always None
    """
    dbus_method("org.genivi.SoftwareLoadingManager", "operationResult",
                transaction_id, result_code, result_text)
    return None
