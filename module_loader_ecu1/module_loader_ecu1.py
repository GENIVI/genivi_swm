# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based partition manager PoC



import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm
import settings
import logging
import os
import getopt
import daemon

logger = logging.getLogger(settings.LOGGER)


#
# ECU Module Loader service
#
class ECU1ModuleLoaderService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.ModuleLoaderEcu1', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/ModuleLoaderEcu1')

    @dbus.service.method('org.genivi.ModuleLoaderEcu1',
                         async_callbacks=('send_reply', 'send_error'))

    def flashModuleFirmware(self, 
                              transaction_id, 
                              image_path,
                              blacklisted_firmware,
                              allow_downgrade,
                              send_reply,
                              send_error): 


        logger.debug('ModuleLoader.ECU1ModuleLoaderService.flashModuleFirmware(%s, %s, %s, %s): Called.',
                     transaction_id, image_path, blacklisted_firmware, allow_downgrade)

        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate install
        sys.stdout.write("Intalling on ECU1: {} (5 sec):\n".format(image_path))
        for i in xrange(1,50):
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\nDone\n")
        swm.send_operation_result(transaction_id,
                                  swm.SWMResult.SWM_RES_OK,
                                  "Firmware flashing successful for ecu1. Path: {}".format(image_path))

        return None
        
    @dbus.service.method('org.genivi.moduleLoaderEcu1')
    def getModuleFirmwareVersion(self): 
        logger.debug('ModuleLoader.ECU1ModuleLoaderService.getModuleFirmwareVersion(): Called.')
        return ("ecu1_firmware_1.2.3", 1452904544)
                 

class ECU1ModuleLoaderDaemon(daemon.Daemon):
    """
    """
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(ECU1ModuleLoaderDaemon, self).__init__(pidfile, stdin, stdout, stderr)

    def run(self):
        DBusGMainLoop(set_as_default=True)
        ecu1_module_loader = ECU1ModuleLoaderService()


def usage():
    print "Usage:", sys.argv[0], "foreground|start|stop|restart"
    print
    print "  foreground     Start in foreground"
    print "  start          Start in background"
    print "  stop           Stop daemon running in background"
    print "  restart        Restart daemon running in background"
    print
    print "Example:", sys.argv[0],"foreground"
    sys.exit(1)


if __name__ == "__main__":
    logger.debug('ECU1 Module Loader - Initializing')
    pid_file = settings.PID_FILE_DIR + os.path.splitext(os.path.basename(__file__))[0] + '.pid'

    try:  
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError:
        print "ECU1 Module Loader - Could not parse arguments."
        usage()
            
    ecu1_module_loader_daemon = ECU1ModuleLoaderDaemon(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
            
    for a in args:
        if a in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger.addHandler(logging._handlers['console'])
            logger.debug('ECU1 Module Loader - Running')
            ecu1_module_loader_daemon.run()
            mainloop = gobject.MainLoop()
            mainloop.run()
        elif a in ('start', 'st'):
            logger.debug('ECU1 Module Loader - Starting')
            #ecu1_module_loader_daemon.start()
            mainloop = gobject.MainLoop()
            mainloop.run()
        elif a in ('stop', 'sp'):
            logger.debug('ECU1 Module Loader - Stopping')
            ecu1_module_loader_daemon.stop()
        elif a in ('restart', 're'):
            logger.debug('ECU1 Module Loader - Restarting')
            ecu1_module_loader_daemon.restart()
        else:
            print "Unknown command: {}".format(a)
            usage()
            sys.exit(1)
