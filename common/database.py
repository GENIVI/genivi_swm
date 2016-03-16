# -*- coding: utf-8 -*-
""" Database library to store update progress and results.

This module provides the database library for Software Management.

(c) 2015, 2016 - Jaguar Land Rover.
Mozilla Public License 2.0
"""

from storm.locals import *
from datetime import datetime
import settings
import logging
import traceback

logger = logging.getLogger(settings.LOGGER)

DB_SCHEMA_VERSION = "0.0.1"
"""Database Schema Version
The database schema version of this module must match the schema version
of the settings, otherwise the database is not loaded to avoid inconsistencies
and destructive changes.
"""

class Persistance(Storm):
    """Core class for all data models
    
    This data model core class provides the basic functionality needed
    by all data models. All data model classes are derived from this
    class.
    """
    
    store = None
    """Reference to the database storage
    """
        
    def add(self, store):
        """ Add the data object to the database
        
        Data objects are not stored in the database untill they are
        persisted with this method.
        
        @param store Database store object for the database backend.
        @return True if successful, False otherwise
        """
        try:
            store.add(self)
            store.commit()
            self.store = store
            return True
        except Exception as e:
            logger.error('common.database.Persistance.add(): Exception: %s', e)
            return False
            
    def update(self):
        """ Update the data object in the database
        
        If the data object has changed this method updates it in the database.

        @return True if successful, False otherwise
        """
        try:
            self.store.commit()
            return True
        except Exception as e:
            logger.error('common.database.Persistance.update(): Exception: %s', e)
            return False
            
    def remove(self):
        """ Remove the data object from the database
        
        Removes this data object from the database. After it has been removed it
        can be added again to the same store or to a different one using the
        add method.

        @return True if successful, False otherwise
        """
        try:
            self.store.remove(self)
            self.store.commit()
            self.store = None
            return True
        except Exception as e:
            logger.error('common.database.Persistance.remove(): Exception: %s', e)
            return False
    
    @classmethod    
    def find(cls, store, key, value):
        """ Find the first data object in the database
        
        Searches the database for an object where the domain indicated by key
        matches value.
        
        @param key The name of the domain (database column)
        @param value The value of the domain to match.

        @return The data object if found, None otherwise
        """
        p = None
        try:
            d = {key: value}
            p = store.find(cls, **d).one()
            if p != None:
                p.store = store
        except Exception as e:
            logger.error('common.database.Persistance.find(): Exception: %s', e)
        return p
            
    @classmethod    
    def findAll(cls, store, key, value):
        """ Find all data objects in the database
        
        Searches the database for all objects where the domain indicated by key
        matches value.
        
        @param key The name of the domain (database column)
        @param value The value of the domain to match.

        @return: List with all matching data object
        """
        p = None
        try:
            d = {key: value}
            p = store.find(cls, **d)
            for i in p:
                i.store = store
        except Exception as e:
            logger.error('common.database.Persistance.findAll(): Exception: %s', e)
        return p


class System(Persistance):
    """Data model for key/value pairs for system configuration
    
    This data model class holds key/value pairs for system configuration
    settings.
    """
    
    __storm_table__ = "System"
    SQL_CREATE = "CREATE TABLE System (key VARCHAR PRIMARY KEY, value VARCHAR)"
    KEY_VERSION = u"SchemaVersion"
    KEY_MAGIC = u"Magic"
    key = Unicode(primary=True)
    value = Unicode()
    
    def __init__(self, key, value):
        """Constructor
        
        Initialize the model by setting key and value.
        
        @param key Name of the key
        @param value Assigned value
        """
        self.key = unicode(key)
        self.value = unicode(value)


class SWUpdate(Persistance):
    """Data model for software updates
    
    This data model class holds software update information. Each software update
    has associated software operations which represent the individual steps to
    be carried out during the software update.
    """
    
    __storm_table__ = "SWUpdate"
    SQL_CREATE = "CREATE TABLE SWUpdate (id VARCHAR PRIMARY KEY, name VARCHAR, startTime VARCHAR, finishTime VARCHAR, status VARCHAR)"
    SQL_CLEAR = "DELETE FROM SWUpdate"
    ST_PENDING = u"PENDING"
    ST_STARTED = u"STARTED"
    ST_FINISHED = u"FINISHED"
    ST_ABORTED = u"ABORTED"
    ST_ERROR = u"ERROR"
    id = Unicode(primary=True)
    name = Unicode()
    startTime = DateTime()
    finishTime = DateTime()
    status = Unicode()
    swOperations = []
    
    def __init__(self, id, name):
        """Constructor
        
        Initialize the model by with the given id. The status is set
        to ST_PENDING.
        
        @param id Unique identifier for the software update
        @param name Name of the software update
        """
        self.id = unicode(id)
        self.name = unicode(name)
        self.status = SWUpdate.ST_PENDING
        
    def start(self):
        """Start the software update
        
        The software update is started by setting the startTime timestamp
        and changing the status to ST_STARTED. This action does not actually
        carry out an operations but simply changes the database status.
        """
        if self.status == SWUpdate.ST_PENDING:
            self.startTime = datetime.utcnow()
            self.status = SWUpdate.ST_STARTED

    def finish(self):
        """Finish the software update
        
        If the status of the software update is ST_STARTED, the method
        checks if all associated software operations have been completed.
        If so, the finishTime timestamp is set and the status is set to
        ST_FINISHED.
        """
        if self.status == SWUpdate.ST_STARTED:
            for swo in self.swOperations:
                if not swo.isfinished():
                    return
            self.finishTime = datetime.utcnow()
            self.status = SWUpdate.ST_FINISHED

    def abort(self):
        """Abort the software update
        
        If the status of the software update is ST_PENDING or ST_STARTED,
        the methods set the finishTime timestamp and the status to ST_ABORTED.
        """
        if self.status == SWUpdate.ST_STARTED or self.status == SWUpdate.ST_PENDING:
            self.finishTime = datetime.utcnow()
            self.status = SWUpdate.ST_ABORTED
        
    def error(self):
        """Set the status of this software update to error.
        
        If the status of the software update is ST_STARTED, the method
        checks if any of the associated software operations has encountered
        an error conditions. If so, the finishTime timestamp is set and the
        status is set to ST_ERROR.
        """
        if self.status == SWUpdate.ST_STARTED:
            for swo in self.swOperations:
                if not swo.error():
                    return
            self.finishTime = datetime.utcnow()
            self.status = SWUpdate.ST_ERROR
        
    def getSWOperations(self):
        """Retrieve all assiciated software operations
        
        This method retrieves all software operations associated with this software
        update from the database and stores them in a local list.
        
        @return List with software operations associated with this software update
        """
        if not self.swOperations:
            swo = SWOperation.findAll(self.store, "updateId", self.id)
            for i in range(0, swo.count()):
                self.swOperations.append(swo[i])
        return self.swOperations
        
    def getSWOperation(self, id):
        """Retrieve a particular software operation identified by id
        
        Searches the local list of software operations for one with the
        matching id. As software operations id's are unique a simple linear
        search is sufficient.
        
        @param id Id of the software operation
        
        @return The software operation instance or None if not found
        """
        for swo in self.swOperations:
            if swo.id == unicode(id):
                return swo
        return None
        
    def addSWOperation(self, id, operation):
        """Add a software operation to this software update
        
        The method add the software operation identifed by id to the
        list of software operations assciated with this software update.
        The new software operation instance is returned.
        
        @param id Id of the software operation
        @param operation Name of the software operatoin
        
        @return Instance of the new software operation
        """
        swo = SWOperation(id, self.id, operation)
        self.swOperations.append(swo)
        swo.add(self.store)
        return swo
        
    def checkSWOperationComplete(self, id):
        """Check if the software operation identified by id is finished
        
        Verifies if the software operation identified by id has been
        completed.
        
        @param id Id of the software operation
        
        @return True if the software operation is complete, False otherwise        
        """
        swo = self.getSWOperation(id)
        if swo and swo.isfinished():
            return True
        return False
        
    def update(self):
        """Store this software update and all associated software operations
        
        The method stores this software update and all software operations
        associated with it in the database. The method first iterates over
        the local list of software operations and stores them in the database
        and then stores the software update itself.
        """
        for swo in self.swOperations:
            swo.update()
        super(SWUpdate, self).update()
        
    @classmethod
    def getSWUpdate(cls, store, id, name):
        """Retrieve a software update
    
        This method first searches the database for the software update matching
        id. If a matching software update is found in the database the instance
        is returned. If no matching software update was found a new instance is
        created and returned.
    
        @param id Id of the software update
        @param name Name of the software update
    
        @return Instance of the software update
        """
        swu = cls.find(store, u"id", unicode(id))
        if not swu:
            swu = SWUpdate(id, name)
            swu.add(store)
        else:
            swu.getSWOperations()
        return swu
        


class SWOperation(Persistance):
    """Data model for software operations
    
    This data model class holds software operation information. A software
    operation is associated with a software update trough a foreign key.
    """
    __storm_table__ = "SWOperation"
    SQL_CREATE = "CREATE TABLE SWOperation (id VARCHAR PRIMARY KEY, operation VARCHAR, updateId VARCHAR, startTime VARCHAR, finishTime VARCHAR, status VARCHAR, resultCode INTEGER)"
    SQL_CLEAR = "DELETE FROM SWOperation"
    ST_PENDING = u"PENDING"
    ST_STARTED = u"STARTED"
    ST_FINISHED = u"FINISHED"
    ST_ABORTED = u"ABORTED"
    ST_ERROR = u"ERROR"
    id = Unicode(primary=True)
    operation = Unicode()
    updateId = Unicode()
    updateRef = Reference(updateId, SWUpdate.id)
    startTime = DateTime()
    finishTime = DateTime()
    status = Unicode()
    resultCode = Int()
    
    def __init__(self, id, updateId, operation):
        """Constructor
        
        Initialize the new software operation.
        
        @param id Id of the software operation
        @param updateId Id of the software update
        @param operation Name of the operation carried out
        """
        self.id = unicode(id)
        self.updateId = unicode(updateId)
        self.operation = unicode(operation)
        self.status = SWOperation.ST_PENDING
        
    def start(self):
        """Start the software operation
        
        Sets the startTime timestamp and the status to ST_STARTED.
        This method does not actually carry out the software operation
        but merely changes its database status.
        """
        self.startTime = datetime.utcnow()
        self.status = SWOperation.ST_STARTED

    def finish(self, resultCode):
        """Finish the software operation
        
        Sets the finishTime timestamp and the status to ST_FINISHED.
        
        @param resultCode Result code
        """
        self.finishTime = datetime.utcnow()
        self.resultCode = resultCode
        self.status = SWOperation.ST_FINISHED

    def abort(self, resultCode):
        """Abort the software operation
        
        Sets the finishTime timestamp and the status to ST_ABORTED.

        @param resultCode Result code
        """
        self.finishTime = datetime.utcnow()
        self.resultCode = resultCode
        self.status = SWOperation.ST_ABORTED
        
    def error(self, resultCode):
        """Set this software operation to error status
        
        Sets the finishTime timestamp and the status to ST_ERROR.

        @param resultCode Result code
        """
        self.finishTime = datetime.utcnow()
        self.resultCode = resultCode
        self.status = SWOperation.ST_ERROR
        
    def isfinished(self):
        """Checks if this software operation has been completed
        
        Checks if the status of this software operation is set to
        ST_FINISHED and returns True if so.
        
        @return True if this software operation is finished, False otherwise
        """
        return self.status == SWOperation.ST_FINISHED

    def iserror(self):
        """Checks if this software operation has encountered an error
        
        Checks if the status of this software operation is set to
        ST_ERROR and returns True if so.
        
        @return True if this software operation has encountered an error, False otherwise
        """
        return self.status == SWOperation.ST_ERROR


def openDatabase():
    """Open the database
    
    Opens the database at the URL specified by settings.DB_URL. If the database
    does not exist or the schema has not been initialized the database will
    be created and the schema initialized.
    
    This method also checks if the schema has the correct version. If the version
    does not match then the reference to the store will not be returned to avoid
    data inconsistency and/or corruption.
    
    @return Reference to the database store if successfully opened.
    """
    try:
        database = create_database(settings.DB_URL)
        store = Store(database)
        vc = checkDatabaseSchema(store)
        if not vc:
            logger.info('common.database.openDatabase(): Creating database schema')
            if not createDatabaseSchema(store):
                return None
        else:
            if vc == False:
                return None
        return store
    except Exception as e:
        logger.error('common.database.openDatabase(): Exception: %s', e)
        return None

def createDatabaseSchema(store):
    """Create the database schema
    
    Create the database schema for an empty database.
    
    @param store Reference to the database store
    
    @return True if database schema was successfully created, False otherwise
    """
    try:
        store.execute(System.SQL_CREATE)
        store.execute(SWUpdate.SQL_CREATE)
        store.execute(SWOperation.SQL_CREATE)
        store.commit()
        System(System.KEY_VERSION, unicode(DB_SCHEMA_VERSION)).add(store)
        return True
    except Exception as e:
        logger.error('common.database.createDatabaseSchema(): Exception: %s', e)
        return False

def checkDatabaseSchema(store):
    """Check the database schema
    
    Simply compares the schema stored in the database to the global DB_SCHEMA_VERSION
    of this module.
    
    @param store Reference to the database store
    
    @return None if the database has not yet been initialized
    @return True if the version matches
    @return False if the version does not match
    """
    version = System.find(store, u"key", System.KEY_VERSION)
    if not version:
        logger.info('common.database.checkDatabaseSchema(): Database not initialized')
        return None
    else:
        if version.value == unicode(DB_SCHEMA_VERSION):
            return True
        else:
            logger.error('common.database.checkDatabaseSchema(): Database schema version %s does not match settings: %s',
                        version.value, DB_SCHEMA_VERSION)
            return False
        
def resetDatabaseSchema(store):
    """Reset the database schema
    
    Clears all data from all tables.

    @param store Reference to the database store

    @return True if succesful, False otherwise
    """
    try:
        store.execute(SWUpdate.SQL_CLEAR)
        store.execute(SWOperation.SQL_CLEAR)
        store.commit()
        return True
    except Exception as e:
        logger.error('common.database.resetDatabase(): Exception: %s', e)
        return False
    

