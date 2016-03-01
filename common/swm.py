# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0

#
# Result constants
#
import dbus
import traceback

# enum implementation not official until Python 3.4
class SWMResult():
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
        return (code >= self.SWM_RES_OK) and (code <= self.SWM_RES_GENERAL_ERROR)


def result(operation_id, code, text):
    if not SWMResult.isValid(code):
        code = SWMResult.SWM_GENERAL_ERROR
    
    return {
        'id': dbus.String(operation_id, variant_level=1),
        'result_code': dbus.Int32(code, variant_level=1),
        'result_text': dbus.String(text, variant_level=1)
    }


def dbus_method(path, method, *arguments):
    try:
        bus = dbus.SessionBus()
        bus_name = dbus.service.BusName(path, bus=bus)
        obj = bus.get_object(bus_name.get_name(), "/{}".format(path.replace(".", "/")))
        remote_method = obj.get_dbus_method(method, path)
        remote_method(*arguments)
    except Exception as e:
        print "dbus_method({}, {}): Exception: {}".format(e, path, method)
        traceback.print_exc()

    return None

            
def send_operation_result(transaction_id, result_code, result_text):
    #
    # Send back operation result.
    # Software Loading Manager will distribute the report to all interested parties.
    #
    dbus_method("org.genivi.SoftwareLoadingManager", "operationResult",
                transaction_id, result_code, result_text)
    return None
