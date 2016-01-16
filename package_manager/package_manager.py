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

#
# Package manager service
#
class PkgMgrService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.genivi.package_manager', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/genivi/package_manager')


    @dbus.service.method('org.genivi.package_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def install_package(self, 
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        send_reply, 
                        send_error): 

        try:
            print "Package Manager: Install Package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            print "Intalling package: {} (5 sec)".format(image_path)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print  
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Installation successful. Path: {}".format(image_path))
        except Exception as e:
            print "install_package() Exception: {}".format(e)
            traceback.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
        
            

    @dbus.service.method('org.genivi.package_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def upgrade_package(self, 
                        transaction_id,
                        image_path,
                        blacklisted_packages,
                        allow_downgrade,
                        send_reply, 
                        send_error): 

        try:
            print "Package Manager: Upgrade package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Image Path:               {}".format(image_path)
            print "  Allow downgrade:          {}".format(allow_downgrade)
            print "  Blacklisted packages:     {}".format(blacklisted_packages)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate install
            print "Upgrading package: {} (5 sec)".format(image_path)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print  
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Upgrade successful. Path: {}".format(image_path))

        except Exception as e:
            print "upgrade_package() Exception: {}".format(e)
            traceback.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None

    @dbus.service.method('org.genivi.package_manager',
                         async_callbacks=('send_reply', 'send_error'))
    def remove_package(self, 
                       transaction_id,
                       package_id,
                       send_reply, 
                       send_error): 
        try:
            print "Package Manager: Remove package"
            print "  Operation Transaction ID: {}".format(transaction_id)
            print "  Package ID:               {}".format(package_id)
            print "---"

            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # Simulate remove
            print "Upgrading package: {} (5 sec)".format(package_id)
            for i in xrange(1,50):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.1)
            print  
            print "Done"
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_OK,
                                      "Removal successful. Package_id: {}".format(package_id))
        except Exception as e:
            print "upgrade_package() Exception: {}".format(e)
            traceback.print_exc()
            swm.send_operation_result(transaction_id,
                                      swm.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None
        return None

    @dbus.service.method('org.genivi.package_manager')
    def get_installed_packages(self): 
        print "Got get_installed_packages()"
        return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]
                 


print 
print "Package Manager."
print


DBusGMainLoop(set_as_default=True)
pkg_mgr = PkgMgrService()

while True:
    gtk.main_iteration()
