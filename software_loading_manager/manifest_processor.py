# (c) 2015,2016 - Jaguar Land Rover.
#
# Mozilla Public License 2.0
#
# Library to process updates



import json
import os
import subprocess
import dbus
from collections import deque
import manifest
import settings
import logging

logger = logging.getLogger(settings.LOGGER)

    
#
# Simplistic storage of successfully completed
# operations
#
class ManifestProcessor:
    def __init__(self, storage_fname):

        #
        # A queue of Manifest objects waiting to be processed.
        #
        self.image_queue = deque()
        
        # File name we will use to read and store
        # all completed software operations.
        self.storage_fname = storage_fname

        self.current_manifest = None
        self.mount_point = None
        self.manifest_file = None


    def queue_image(self, image_path):
        logger.debug('SoftwareLoadingManager.ManifestProcessor.queue_image(%s): Called.', image_path)
        self.image_queue.appendleft(image_path)

    
    #
    # Load the next manifest to process from the queue populated
    # by queue_manifest()
    #
    def load_next_manifest(self):
        #
        # Do we have any nore images to process?
        #
        logger.debug('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Called.')

        #
        # Unmount previous mount point
        #
        if self.mount_point:
            try:
                command = [settings.SQUASHFS_UNMOUNT_CMD, self.mount_point]
                if settings.SQUASHFS_UNMOUNT_ARGS:
                    command.insert(1, settings.SQUASHFS_UNMOUNT_ARGS) 
                subprocess.check_call(command)
            except subprocess.CalledProcessError:
                logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed to unmount %s: %s.',
                             self.mount_point, subprocess.CalledProcessError.returncode)
        self.mount_point = None
        self.current_manifest = None
        
        if len(self.image_queue) == 0:
            logger.debug('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Image queue is empty.')
            return False
        logger.debug('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Manifests in queue: %s.', len(self.image_queue))

        image_path = self.image_queue.pop()
        logger.debug('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Processing update image: %s.', image_path)

        # Mount the file system
        self.mount_point = "/tmp/swlm/{}".format(os.getpid())
        logger.debug('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Creating mount point: %s.', self.mount_point)
        try:
            os.makedirs(self.mount_point)
        except OSError as e:
            logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed creating mount point %s: %s.', self.mount_point, e)
            pass
        
        try:
            command = [settings.SQUASHFS_MOUNT_CMD, image_path, self.mount_point]
            if settings.SQUASHFS_MOUNT_ARGS:
                command.insert(1, settings.SQUASHFS_MOUNT_ARGS) 
            subprocess.check_call(command)
        except subprocess.CalledProcessError:
            logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed mounting %s on %s: %s.',
                         image_path, self.mount_point, subprocess.CalledProcessError.returncode)
            return False

        # Create the new manifest object
        # Specify manifest file to load
        self.manifest_file= "{}/update_manifest.json".format(self.mount_point)
        try:
            self.current_manifest = manifest.Manifest(self.mount_point, self.manifest_file, self.storage_fname)
        except Exception as e:
            logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed loading manifest: %s.', e)
    
        if not self.current_manifest:
            self.current_manifest = None
            # Unmount file system
            try:
                command = [settings.SQUASHFS_UNMOUNT_CMD, self.mount_point]
                if settings.SQUASHFS_UNMOUNT_ARGS:
                    command.insert(1, settings.SQUASHFS_UNMOUNT_ARGS) 
                subprocess.check_call(command)
            except subprocess.CalledProcessError:
                logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed unmounting %s: %s.',
                             self.mount_point, subprocess.CalledProcessError.returncode)
            self.mount_point = None
            return False

        return True
    
