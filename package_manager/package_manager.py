# -*- coding: utf-8 -*-
""" Package Management

This module provides classes and methods for installing, upgrading and
removing packages on the target. It uses the native package management
system.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""


import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import sys
import time
import swm
import settings
import logging
import os.path
import subprocess
import os
import getopt
import daemon


logger = logging.getLogger(settings.LOGGER)


#
# Package manager service
#
class PkgMgrService(dbus.service.Object):
    """Package Manager Service
    
    Handles installation, upgrading and removing of packages using the platform's
    native package manager. The platform package management commands are defined
    by the settings in common.
    """

    def __init__(self):
        """Constructor
        
        Initalize instance as a dbus service object.
        """
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
        """Install Software Package
        
        Dbus callback for installing a software package using the platform's
        package management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param image_path Path to the software package to be installed
        @param blacklisted_packages List of packages that must not be installed
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PackageManager.PkgMgrService.installPackage(%s, %s, %s): Called.',
                     transaction_id, image_path, blacklisted_packages)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)
            
            # extract package and check for blacklisted
            pkg = os.path.basename(image_path)
            if pkg in blacklisted_packages:
                logger.warning('PackageManager.PkgMgrService.installPackage(): Blacklisted Package: %s', pkg)
                swm.send_operation_result(transaction_id,
                                            swm.SWMResult.SWM_RES_OPERATION_BLACKLISTED,
                                            "Blacklisted Package: {}".format(pkg))
                return None

            # assemble installation command
            cmd = list(settings.PKGMGR_INSTALL_CMD)
            cmd.append(image_path)
            logger.info('PackageManager.PkgMgrService.installPackage(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate installation
                logger.info('PackageManager.PkgMgrService.installPackage(): Installation Simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Installation Simulation successful. Command: {}".format(cmd)
                logger.info('PackageManager.PkgMgrService.installPackage(): Installation Simulation successful.')
            else:
                # perform installation
                sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if sp.wait() == 0:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_OK
                    resulttext = "Installation successful. Result: {}".format(stdout)
                    logger.info('PackageManager.PkgMgrService.installPackage(): Installation successful.')
                else:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_INSTALL_FAILED
                    resulttext = "Installation failed. Error: {}".format(stderr)
                    logger.error('PackageManager.PkgMgrService.installPackage(): Installation failed: %s.', stderr)
                
            swm.send_operation_result(transaction_id, resultcode, resulttext)

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
        """Upgrade Software Package
        
        Dbus callback for upgrading a software package using the platform's
        package management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param image_path Path to the software package to be installed
        @param blacklisted_packages List of packages that must not be installed
        @param allow_downgrade Permit downgrading of the package to a previous version
        @param send_reply DBus callback for a standard reply
        @param send_error DBus callback for error response
        """

        logger.debug('PackageManager.PkgMgrService.upgradePackage(%s, %s, %s, %s): Called.',
                     transaction_id, image_path, blacklisted_packages, allow_downgrade)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # extract package and check for blacklisted
            pkg = os.path.basename(image_path)
            if pkg in blacklisted_packages:
                logger.warning('PackageManager.PkgMgrService.upgradePackage(): Blacklisted Package: %s', pkg)
                swm.send_operation_result(transaction_id,
                                            swm.SWMResult.SWM_RES_OPERATION_BLACKLISTED,
                                            "Blacklisted Package: {}".format(pkg))
                return None

            # check if package is installed and compare versions
            pkglist = self.checkInstalledPackage(pkg)
            if len(pkglist) > 0 and not allow_downgrade:
                # only need to check package version if package is installed
                # and downgrading is not allowed
                if not self.isNewer(pkglist, pkg):
                    logger.info('PackageManager.PkgMgrService.upgradePackage(): Downgrade prohibited.')
                    swm.send_operation_result(transaction_id,
                                                swm.SWMResult.SWM_RES_OLD_VERSION,
                                                "Package downgrade prohibited.")
                    return None
                    

            # assemble upgrade command
            cmd = list(settings.PKGMGR_UPGRADE_CMD)
            cmd.append(image_path)
            logger.info('PackageManager.PkgMgrService.upgradePackage(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate upgrade
                logger.info('PackageManager.PkgMgrService.upgradePackage(): Upgrade Simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Upgrade Simulation successful. Command: {}".format(cmd)
                logger.info('PackageManager.PkgMgrService.upgradePackage(): Upgrade Simulation successful.')
            else:
                # perform upgrade
                sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if sp.wait() == 0:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_OK
                    resulttext = "Upgrade successful. Result: {}".format(stdout)
                    logger.info('PackageManager.PkgMgrService.upgradePackage(): Upgrade successful.')
                else:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_UPGRADE_FAILED
                    resulttext = "Upgrade failed. Error: {}".format(stderr)
                    logger.error('PackageManager.PkgMgrService.upgradePackage(): Upgrade failed: %s.', stderr)
                
            swm.send_operation_result(transaction_id, resultcode, resulttext)

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
        """Remove Software Package
        
        Dbus callback for installing a software package using the platform's
        package management system.
        
        @param transaction_id Software Loading Manager transaction id
        @param package_id Name of the software package
        @param send_error DBus callback for error response
        """


        logger.debug('PackageManager.PkgMgrService.removePackage(%s, %s): Called.',
                     transaction_id, package_id)

        try:
            #
            # Send back an immediate reply since DBUS
            # doesn't like python dbus-invoked methods to do 
            # their own calls (nested calls).
            #
            send_reply(True)

            # assemble remove command
            cmd = list(settings.PKGMGR_REMOVE_CMD)
            cmd.append(package_id)
            logger.info('PackageManager.PkgMgrService.removePackage(): Command: %s', cmd)

            if settings.SWM_SIMULATION:
                # simulate removal
                logger.info('PackageManager.PkgMgrService.removePackage(): Removal Simulation...')
                time.sleep(settings.SWM_SIMULATION_WAIT)
                resultcode = swm.SWMResult.SWM_RES_OK
                resulttext = "Removal Simulation successful. Command: {}".format(cmd)
                logger.info('PackageManager.PkgMgrService.removePackage(): Removal Simulation successful.')
            else:
                # perform removal
                sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if sp.wait() == 0:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_OK
                    resulttext = "Removal successful. Result: {}".format(stdout)
                    logger.info('PackageManager.PkgMgrService.removePackage(): Removal successful.')
                else:
                    (stdout, stderr) = sp.communicate()
                    resultcode = swm.SWMResult.SWM_RES_REMOVAL_FAILED
                    resulttext = "Removal failed. Error: {}".format(stderr)
                    logger.error('PackageManager.PkgMgrService.removePackage(): Removal failed: %s.', stderr)
                
            swm.send_operation_result(transaction_id, resultcode, resulttext)

        except Exception as e:
            logger.error('PackageManager.PkgMgrService.removePackage(): Exception: %s.', e)
            swm.send_operation_result(transaction_id,
                                      swm.SWMResult.SWM_RES_INTERNAL_ERROR,
                                      "Internal_error: {}".format(e))
        return None


    @dbus.service.method('org.genivi.PackageManager')
    def getInstalledPackages(self):
        """Get a list of installed packages
        """
        try:
            # assemble list command
            cmd = list(settings.PKGMGR_LIST_CMD)
            logger.debug('PackageManager.PkgMgrService.getInstalledPackages(): Command: %s', cmd)
            
            if settings.SWM_SIMULATION:
                # simulate package list
                return [ 'bluez_driver_1.2.2', 'bluez_apps_2.4.4' ]
            else:
                # return package list
                sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout, stderr) = sp.communicate()
                if sp.returncode == 0:
                    pl = stdout.split("\n")[:-1]
                    logger.debug('PackageManager.PkgMgrService.getInstalledPackages(): Package List: %s.', pl)
                    return pl
                else:
                    logger.error('PackageManager.PkgMgrService.getInstalledPackages(): Error: %s.', stderr)
                    return None

        except Exception as e:
            logger.error('PackageManager.PkgMgrService.getInstalledPackages(): Exception: %s.', e)
            return None
             
             
    def checkInstalledPackage(self, package):
        """Check if a package is installed
        
        @param package Name of package to check.
        @return List of packages that match, empty list otherwise
        """
        try:
            # assemble check command
            name = self.splitPackageName(package)[0]
            cmd = list(settings.PKGMGR_CHECK_CMD)
            cmd.append(name)
            logger.debug('PackageManager.PkgMgrService.checkInstalledPackage(): Command: %s', cmd)
            
            if settings.SWM_SIMULATION:
                # simulate package list
                return [ splitext(package)[0] ]
            else:
                # check if package is installed
                sp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                (stdout, stderr) = sp.communicate()
                if sp.returncode == 0:
                    pl = stdout.split("\n")[:-1]
                    logger.info('PackageManager.PkgMgrService.checkInstalledPackages(): Package List: %s.', pl)
                    return pl
                else:
                    logger.info('PackageManager.PkgMgrService.checkInstalledPackages(): Package not installed.')
                    return []
            
        except Exception as e:
            logger.error('PackageManager.PkgMgrService.checkInstalledPackage(): Exception: %s.', e)
            return []
            
            
    def splitPackageName(self, package):
        """Split a package name into its parts
        
        @param package Name of the package
        @return Tuple of (name,ver,rel,arch,ptype)
        """
        ptype = None
        arch = None
        rel = None
        ver = None
        name = None
        try:
            out = package.rsplit('.', 1)
            if len(out) > 1:
                ptype = out[1]
            out = out[0].rsplit(settings.PKGMGR_DEL_ARCH, 1)
            if len(out) > 1:
                arch = out[1]
            out = out[0].rsplit(settings.PKGMGR_DEL_REL, 1)
            if len(out) > 1:
                rel = out[1]
            out = out[0].rsplit(settings.PKGMGR_DEL_VER, 1)
            if len(out) > 1:
                ver = out[1]
            name = out[0]
            return (name, ver, rel, arch, ptype)
        except Exception as e:
            logger.error('PackageManager.PkgMgrService.splitPackageName(): Exception: %s.', e)
            return None
            
            
    def getPackageVersion(self, package):
        """Extract version from a package name
        
        @param package Name of the package
        @return Package version
        """
        (name, ver, rel, arch, ptype) = self.splitPackageName(package)
        return ver
        
        
    def isNewer(self, package_list, package):
        """Check if package is newer than all packages in a list
        of packages
        
        @param packagelist List of packages to check against
        @param package Package to check
        @return True if package is newer, False otherwise
        """
        
        version = self.getPackageVersion(package)
        for pkg in package_list:
            pver = self.getPackageVersion(pkg)
            if version <= pver:
                return False
        return True
            
            
class PkgMgrDaemon(daemon.Daemon):
    """
    """
    
    def __init__(self, pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        super(PkgMgrDaemon, self).__init__(pidfile, stdin, stdout, stderr)

    def run(self):
        DBusGMainLoop(set_as_default=True)
        pkg_mgr = PkgMgrService()


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
    logger.debug('Package Manager - Initializing')
    pid_file = settings.PID_FILE_DIR + os.path.splitext(os.path.basename(__file__))[0] + '.pid'

    try:  
        opts, args = getopt.getopt(sys.argv[1:], "")
    except getopt.GetoptError:
        print "Package Manager - Could not parse arguments."
        usage()
            
    pkgmgr_daemon = PkgMgrDaemon(pid_file, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null')
            
    for a in args:
        if a in ('foreground', 'fg'):
            # in foreground we also log to the console
            logger.addHandler(logging._handlers['console'])
            logger.debug('Package Manager - Running')
            pkgmgr_daemon.run()
            mainloop = gobject.MainLoop()
            mainloop.run()
        elif a in ('start', 'st'):
            logger.debug('Package Manager - Starting')
            #pkgmgr_daemon.start()
            mainloop = gobject.MainLoop()
            mainloop.run()
        elif a in ('stop', 'sp'):
            logger.debug('Package Manager - Stopping')
            pkgmgr_daemon.stop()
        elif a in ('restart', 're'):
            logger.debug('Package Manager - Restarting')
            pkgmgr_daemon.restart()
        else:
            print "Unknown command: {}".format(a)
            usage()
            sys.exit(1)
 