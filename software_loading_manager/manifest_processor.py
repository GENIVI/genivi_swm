# -*- coding: utf-8 -*-
""" Database library to store update progress and results.

This module provides classes and methods to process a queue of manifests.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""



import json
import os
import subprocess
import dbus
from collections import deque
import manifest
import settings
import logging
import traceback

logger = logging.getLogger(settings.LOGGER)

    
#
# Simplistic storage of successfully completed
# operations
#
class ManifestProcessor:
    """Manifest Processing
    
    This class processes multiple images with their manifests.
    """
    
    def __init__(self, dbstore):
        """Constructor
        
        Create a new ManifestProcessor instance.
        
        @param dbstore Reference to the database store
        """

        #
        # A queue of Manifest objects waiting to be processed.
        #
        self.image_queue = deque()
        
        # File name we will use to read and store
        # all completed software operations.
        self.dbstore = dbstore

        self.current_manifest = None
        self.mount_point = None
        self.manifest_file = None


    def queue_image(self, image_path):
        """Place image into processing queue
        
        Add a new image to the processing queue. Images are squashfs
        archives.
        
        @param image_path Path to the image
        """
        logger.debug('SoftwareLoadingManager.ManifestProcessor.queue_image(%s): Called.', image_path)
        self.image_queue.appendleft(image_path)

    
    #
    # Load the next manifest to process from the queue populated
    # by queue_manifest()
    #
    def load_next_manifest(self):
        """Load next manifest from image
        
        Mount the squashfs image and load the manifest in it for processing.
        
        @return True if successful, False otherwise
        """
        
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
        if not settings.SQUASHFS_MOUNT_POINT.endswith('/'):
            self.mount_point = settings.SQUASHFS_MOUNT_POINT + '/' + str(os.getpid())
        else:
            self.mount_point = settings.SQUASHFS_MOUNT_POINT + str(os.getpid())
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
            self.current_manifest = manifest.Manifest(self.mount_point, self.manifest_file, self.dbstore)
        except Exception as e:
            logger.error('SoftwareLoadingManager.ManifestProcessor.load_next_manifest(): Failed loading manifest: %s.', e)
            traceback.print_exc()
    
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
    
