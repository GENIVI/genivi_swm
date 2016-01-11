# (c) 2015 - Jaguar Land Rover.
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

        # Transaction ID to use when sending
        # out a DBUS transaction to another
        # conponent. The component, in its callback
        # to us, will use the same transaction ID, allowing
        # us to tie a callback reply to an originating transaction.
        #
        # Please note that this is not the same thing as an operation id
        # which is an element  of the manifest uniquely identifying each
        # software operation.
        self.next_transaction_id = 0

        # The stored result for all completed software operations
        # Each element contains the software operation id, the
        # result code, and a descriptive text.
        self.operation_results = []

        self.current_manifest = None

        self.mount_point = None

        try:
            ifile = open(storage_fname, "r")
        except:
            # File could not be read. Start with empty
            self.completed = []
            return

        # Parse JSON object
        self.completed = json.load(ifile)
        ifile.close()

    def queue_image(self, image_path):
        print "ManifestProcessor:queue_image({}): Called".format(image_path)
        self.image_queue.appendleft(image_path)

    def add_completed_operation(self, operation_id):
        print "ManifestProcessor.add_completed_operation({})".format(operation_id)
        self.completed.append(operation_id)
        # Slow, but we don't care.
        ofile = open(self.storage_fname, "w")
        json.dump(self.completed, ofile)
        ofile.close()

    #
    # Return true if the provided tranasaction id has
    # been completed.
    #
    def is_operation_completed(self, transaction_id):
        return not transaction_id or transaction_id in self.completed
        
    def get_next_transaction_id(self):
        self.next_transaction_id = self.next_transaction_id + 1
        return self.next_transaction_id
    
    #
    # Load the next manifest to process from the queue populated
    # by queue_manifest()
    #
    def load_next_manifest(self):
        #
        # Do we have any nore images to process?
        #
        print "ManifestProcessor:load_next_manifest(): Called"

        #
        # Unmount previous mount point
        #
        if self.mount_point:
            try:
                subprocess.check_call(["/bin/umount", self.mount_point ])

            except subprocess.CalledProcessError:
                print "Failed to unmount {}: {}".format(self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
        self.mount_point = None
        self.current_manifest = None
        
        if len(self.image_queue) == 0:
            print "ManifestProcessor:load_next_manifest(): Image queue is empty"
            return False

        print "ManifestProcessor:load_next_manifest(): #{}".format(len(self.image_queue))
        image_path = self.image_queue.pop()
        print "Will process update image: {}".format(image_path)

        # Mount the file system
        self.mount_point = "/tmp/swlm/{}".format(os.getpid())
        print "Will create mount point: {}".format(self.mount_point)
    
        try:
            os.makedirs(self.mount_point)
        except os.OSError as e:
            print "Failed to create {}: {}".format(self.mount_point, e)
            pass
        
        try:
            subprocess.check_call(["/bin/mount", image_path, self.mount_point ])
        except subprocess.CalledProcessError:
            print "Failed to mount {} on {}: {}".format(image_path,
                                                        self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
            return False

        # Create the new manifest object
        try:
            self.current_manifest = manifest.Manifest([], [], [], self)
        except Exception as e:
            print "Manifest exception: {}".format(e)

        # Specify manifest file to load
        manifest_file= "{}/update_manifest.json".format(self.mount_point)
    
        if not self.current_manifest.load_from_file(manifest_file):
            print "Failed to load manifest {}".format(manifest_file)
            self.current_manifest = None
            # Unmount file system
            try:
                subprocess.check_call(["/bin/umount", self.mount_point ])

            except subprocess.CalledProcessError:
                print "Failed to unmount {}: {}".format(self.mount_point,
                                                        subprocess.CalledProcessError.returncode)
            self.mount_point = None
            return False


        return True
    
