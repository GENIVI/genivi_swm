# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based life cycle manager PoC



import gtk
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
# Lifecycle manager service
#
class LCMgrService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.LifecycleManager', dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/LifecycleManager')


    @dbus.service.method('org.genivi.LifecycleManager',
                         async_callbacks=('send_reply', 'send_error'))

    def startComponents(self, 
                         transaction_id,
                         components,
                         send_reply, 
                         send_error):

        logger.debug('LifecycleManager.LCMgrService.startComponents(%s, %s): Called.', transaction_id, components)

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate starting components
        for i in components:
            logger.debug('LifecycleManager.LCMgrService.startComponents(): Starting: %s', i)
            time.sleep(3.0)
        swm.send_operation_result(transaction_id,
                                  swm.SWMResult.SWM_RES_OK,
                                  "Started components {}".format(", ".join(components)))
        return None
 
                                 
    @dbus.service.method('org.genivi.LifecycleManager',
                         async_callbacks=('send_reply', 'send_error'))

    def stopComponents(self, 
                        transaction_id,
                        components,
                        send_reply, 
                        send_error): 

        logger.debug('LifecycleManager.LCMgrService.stopComponents(%s, %s): Called.', transaction_id, components)

        #
        # Send back an immediate reply since DBUS
        # doesn't like python dbus-invoked methods to do 
        # their own calls (nested calls).
        #
        send_reply(True)

        # Simulate stopping components
        for i in components:
            logger.debug('LifecycleManager.LCMgrService.stopComponents(): Stopping: %s', i)
            time.sleep(3.0)
        swm.send_operation_result(transaction_id,
                                  swm.SWMResult.SWM_RES_OK,
                                  "Stopped components {}".format(", ".join(components)))
        
        return None


class LCMgrDaemon(daemon.Daemon):
    """
    """
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(LCMgrDaemon, self).__init__(pidfile, stdin, stdout, stderr)

    def run(self):
        DBusGMainLoop(set_as_default=True)
        lc_mgr = LCMgrService()
        while True:
            gtk.main_iteration()


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
    logger.debug('Lifecycle Manager - Initializing')
    pid_file = settings.PID_FILE_DIR + os.path.splitext(os.path.basename(__file__))[0] + '.pid'

    try:  
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError:
        print "Lifecycle Manager - Could not parse arguments."
        usage()
            
    lcmgr_daemon = LCMgrDaemon(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
            
    for a in args:
        if a in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger.addHandler(logging._handlers['console'])
            logger.debug('Lifecycle Manager - Running')
            lcmgr_daemon.run()
        elif a in ('start', 'st'):
            logger.debug('Lifecycle Manager - Starting')
            lcmgr_daemon.start()
        elif a in ('stop', 'sp'):
            logger.debug('Lifecycle Manager - Stopping')
            lcmgr_daemon.stop()
        elif a in ('restart', 're'):
            logger.debug('Lifecycle Manager - Restarting')
            lcmgr_daemon.restart()
        else:
            print "Unknown command: {}".format(a)
            usage()
            sys.exit(1)
