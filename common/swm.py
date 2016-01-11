# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0

#
# Result constants
#
import dbus
import traceback

SWM_RES_OK = 0
SWM_RES_ALREADY_PROCESSED = 1
SWM_RES_DEPENDENCY_FAILURE = 2
SWM_RES_SIGNATURE_FAILURE = 3
SWM_RES_INSTALL_FAILED = 4
SWM_RES_UPGRADE_FAILIED = 5
SWM_RES_REMOVAL_FAILED = 6
SWM_RES_USER_DECLINED = 7
SWM_RES_INTERNAL_ERROR = 8
SWM_RES_GENERAL_ERROR = 9
_SWM_RES_FIRST_UNUSED = 10

def result(operation_id, code, text):
    if code < SWM_RES_OK or code >= _SWM_RES_FIRST_UNUSED:
        code = SWM_RES_GENERAL_ERROR
    
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
    dbus_method("org.genivi.software_loading_manager", "operation_result",
                transaction_id, result_code, result_text)
    return None
