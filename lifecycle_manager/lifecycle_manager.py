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



logger.debug('Lifecycle Manager - Running')


DBusGMainLoop(set_as_default=True)
pkg_mgr = LCMgrService()

while True:
    gtk.main_iteration()
