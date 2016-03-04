# (c) 2015 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Python-based package manager PoC



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
# Package manager service
#
class PkgMgrService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.PackageManager', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/PackageManager')


    @dbus.service.method('org.genivi.PackageManager',
                         async_callbacks=('send_reply', 'send_error'))
    def installPackage(self, 
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        send_reply, 
                        send_error): 

        logger.debug('PackageManager.PkgMgrService.installPackage(%s, %s, %s): Called.',
                     transaction_id, image_path, blacklisted_packages)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            sys.stdout.write("Intalling package: {} (5 sec)\n".format(image_path))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Installation successful. Path: {}".format(image_path))
        except Exception as e:
            logger.error('PackageManager.PkgMgrService.installPackage(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
        
            

    @dbus.service.method('org.genivi.PackageManager',
                         async_callbacks=('send_reply', 'send_error'))
    def upgradePackage(self, 
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        allow_downgrade,
                        send_reply, 
                        send_error): 

        logger.debug('PackageManager.PkgMgrService.upgradePackage(%s, %s, %s, %s): Called.',
                     transaction_id, image_path, blacklisted_packages, allow_downgrade)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            sys.stdout.write("Upgrading package: {} (5 sec)\n".format(image_path))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Upgrade successful. Path: {}".format(image_path))

        except Exception as e:
            logger.error('PackageManager.PkgMgrService.upgradePackage(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    @dbus.service.method('org.genivi.PackageManager',
                         async_callbacks=('send_reply', 'send_error'))
    def removePackage(self, 
                       transaction_id,
                       package_id,
                       send_reply, 
                       send_error): 

        logger.debug('PackageManager.PkgMgrService.removePackage(%s, %s): Called.',
                     transaction_id, package_id)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate remove
            sys.stdout.write("Upgrading package: {} (5 sec)\n".format(package_id))
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write("\nDone\n")
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_OK,
                                      "Removal successful. Package_id: {}".format(package_id))
        except Exception as e:
            logger.error('PackageManager.PkgMgrService.removePackage(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
        return None

    @dbus.service.method('org.genivi.PackageManager')
    def getInstalledPackages(self): 
        logger.debug('PackageManager.PkgMgrService.getInstalledPackages(): Called.')
        return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]
                 


logger.debug('Package Manager - Running')

DBusGMainLoop(set_as_default=True)
pkg_mgr = PkgMgrService()

while True:
    gtk.main_iteration()
