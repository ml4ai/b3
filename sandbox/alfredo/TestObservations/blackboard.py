__author__ = 'clayton'
__project__ = 'Bayesian Blackboard'

# Base blackboard infrastructure for Bayesian Blackboard
# Inspiration from Dan Corkill's GBBopen: http://gbbopen.org
# Author: Clayton T. Morrison
# Date: 20140101

"""
General Notes:

Status: work in progress!

Inspired by (but not a port of) `Dan Corkill's GBBopen: <http://gbbopen.org>`_

Notes:
(1) CTM 20140108:
    A shortcoming of the previous approach to bookkeeping isntances in Base_Instance
    was that if we wanted to have multiple blackboard instances with their own registered units,
    the bookkeeping would have been global across blackboards.
    Now I've changed to the following
    (a) The class Base_Instance does:
        () is the parent class of all Standard_Unit_Instances and Standard_Space_Instances
        () keeps track of all subclasses of Base_Instance that have instances,
           indexed by instance.name (which is a gensym by default)
        () instances have id that is either INSTANCE.UNREGISTERED 
           or a unique id, per class, assigned by the blackboard it is registered with.
    (b) The Blackboard class now tracks 'registered' instances, which is
        done by the instance.id.
        NOTE: an instance can only be registered with ONE blackboard at a time.
(2) CTM 20140107: I'm aware that I'm breaking pythonic __repr__ rules in that the
    repr often cannot be used to recreate the class.
    Should I even be worrying about __repr__ ?

Criteria for (Basic_Instances):
() Have unique ID, integer, by type
() Can be retrieved by ID by type class
() Can be place on a blackboard
    from blackboard, 
       () can get instance by (type, ID)
       () can iterate over instances of type
       () can be placed on space
       () can iterate over instances in space
---- dropping for now:
() Have name and retrieve by name (default gensym)

"""

from abc import ABCMeta
from functools import wraps
import collections
import heapq
import itertools
import time

DEBUG = False

# --------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------

def TODO(fn):
    """
    Utility decorator
    Indicates at execution time that decorated fn is not yet implemented.
    NOTE: Currently just prints TODO message; probably should throw...
    """
    @wraps(fn)
    def not_yet_implemented(*args, **kwds):
        print "TODO: '{0}' not yet implemented".format(fn.__name__)
        return fn
    return not_yet_implemented


# --------------------------------------------------------------------------

def enum(*sequential, **named):
    """
    `see here
    <http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python>`_
    answer by `Alec Thomas: <http://stackoverflow.com/users/7980>`_

    A heavier-duty way to approximate lisp keywords in python
    
    Usage:
    >>> Numbers = enum('ZERO', 'ONE', FIVE=5, SEVEN='seven')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1
    >>> Numbers.FIVE
    5
    >>> Numbers.reverse_mapping[5]
    'FIVE'
    >>> Numbers.SEVEN
    'seven'
    >>> Numbers.reverse_mapping['seven']
    'SEVEN'
    >>>  Numbers.TWO
    AttributeError: type object 'Enum' has no attribute 'TWO'
    >>> Numbers.reverse_mapping[2]
    KeyError: 2
    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)


# -------------------------------------------------------------------------

# Would prefer to have gensym be a callable object, 
# so counter isn't a global, but this isn't quite working like a fn
# so go with global for now...

class Gensym(object):

    counter = itertools.count()

    @staticmethod
    def gensym(name='G'):
        """
        Create a generic name with a guaranteed unique name
        """
        g = '{0}{1}'.format(name, next(Gensym.counter))
        return g

    @staticmethod
    def get_gensym_counter():
        """
        Accessor for gensym counter
        """
        return Gensym.counter

    @staticmethod
    def reset_gensym_counter(val=0, verbose=False):
        """
        Reset the gensym counter, optionally to val
        """
        if isinstance(val, int):
            Gensym.counter = itertools.count(val)
        else:
            Gensym.counter = itertools.count()
        if verbose:
            print "counter = {0}".format(Gensym.counter)


def gensym(name='G'):
    return Gensym.gensym(name=name)


def reset_gensym_counter(val=0, verbose=False):
    Gensym.reset_gensym_counter(val,verbose)


# --------------------------------------------------------------------------

def all_subclasses(cls):
    """ 
    Return list of all class descendants of a class cls.
    `See here
    http://stackoverflow.com/questions/3862310/how-can-i-find-all-subclasses-of-a-given-class-in-python`_
    """
    return cls.__subclasses__() + [g for s in cls.__subclasses__()
                                   for g in all_subclasses(s)]


# --------------------------------------------------------------------------

class PriorityQueue(object):

    def __init__(self):
        self.pq = []                         # list of entries arranged in a heap
        self.entry_finder = {}               # mapping of tasks to entries
        self._removed = '<removed-task>'     # placeholder for a removed task
        self.counter = itertools.count()     # unique sequence count

    def add_task(self, task, priority=0):
        """
        Add a new task or update the priority of an existing task.
        """
        if task in self.entry_finder:
            self.remove_task(task)
        count = next(self.counter)
        entry = (priority, count, task)
        self.entry_finder[task] = entry
        heapq.heappush(self.pq, entry)

    def remove_task(self, task):
        """
        Mark an existing task as REMOVED.  Raise KeyError if not found.
        """
        entry = self.entry_finder.pop(task)
        entry[-1] = self._removed

    def pop_task(self):
        """
        Remove and return the lowest priority task. Raise KeyError if empty.
        """
        while self.pq:
            priority, count, task = heapq.heappop(self.pq)  # @UnusedVariable
            if task is not self._removed:
                del self.entry_finder[task]
                return task
        raise KeyError('pop from an empty priority queue')


# --------------------------------------------------------------------------
# Blackboard Repository
# --------------------------------------------------------------------------

class Class_Instance_Record(object):
    """
    Implements the following class and instance bookkeeping functionalities:
    (1) Store classes that have at least one instance
    (2) For each such class
        () keep id counter ('counter') and update when new instances are added
        () index instances by id ('instances_by_id') in dict

    Instance attribute record stores data as follows:
    dict: { <instance_class> : { 'counter' : <class_counter> , 
                                 'instances_by_id' : { <instance.id> : <instance> } } }
    """

    # TODO:
    # Consider using collections.defaultdict for record, where default
    # value sets up 'counter' and 'instance_by_id' dict

    def __init__(self):
        self.record = {}
    
    def add_instance(self, instance):
        """
        Add class instance to record:
        (1) Ensures that subclass with first instance gets its own 
            'counter' integer (starts at 0) and 'instances_by_id' dict
        (2) Assign new id to instance (increments counter first)
        (3) Add the instance to instances_by_id dict

        NOTE: should only add instance once; 
              should assert check that it doesn't already exist?
        """

        instance_class = instance.__class__

        #: (1) subclass with first instance gets own 'counter' and 'instance_by_id' dict
        if instance_class not in self.record:
            # print "add_instance(): first time '{0}'".format(instance_class)
            self.record[instance_class] = dict(counter=itertools.count(), instances_by_id={})

        #: (2) Assign new id to instance (increments counter first)
        # self.record[instance_class]['counter'] += 1
        instance.id = next(self.record[instance_class]['counter'])

        #: (3) Add the instance to 'instances_by_id' dict
        self.record[instance_class]['instances_by_id'][instance.id] = instance

    def remove_instance(self, instance):
        """
        Remove class instance from 
        """
        instance_class = instance.__class__
        
        if instance_class not in self.record.keys():
            print "Class '{0}' of instance '{1}' not found.".format(instance_class, instance)
            return None
        if instance.id not in self.record[instance_class].keys():
            print "Instance '{1}' not found.".format(instance)
            return None
        
        del self.record[instance_class][instance.id]

        if not self.record[instance_class]:
            del self.record[instance_class]

    def get_all_classes_with_instances(self):
        """
        Returns list of _all_ classes with instances.
        """
        return self.record.keys()

    def get_classes_with_instances(self, instance_class, subclasses=True):
        """
        Returns list of classes with instances.
        if subclasses=True (default), includes subclasses of instance_class,
        otherwise just returns list with instance_class (if it has instances,
        otherwise None).
        """
        classes_with_instances = []
        target_instance_classes = [instance_class]
        all_classes_with_instances = self.record.keys()
        if subclasses:
            target_instance_classes = target_instance_classes + all_subclasses(instance_class)
        for cls in target_instance_classes:
            if cls in all_classes_with_instances:
                classes_with_instances.append(cls)
        return classes_with_instances

    def get_class_instances_by_id_dict(self, instance_class):
        if instance_class in self.record:
            return self.record[instance_class]['instances_by_id']
        else:
            print "'{0}' has no instances".format(instance_class)

    def get_instances_of_classes(self, instance_classes):
        """
        Returns list of all instances of classes in instance_classes
        WARNING: This can return duplicate instances (e.g., if same instance_class
            is in instance_classes, or same instance somehow appears in more than
            one instance_class instance_by_id dict.
        """
        instances = []
        for instance_class in instance_classes:
            instances += self.get_class_instances_by_id_dict(instance_class).values()
        return instances

    def delete_all_instance_bookkeeping(self):
        """
        Returns bookkeeping to original initial state.
        NOTE: does not delete instances, if they still have other references.
        """
        self.record = {}

    def get_instance_bookkeeping_state(self, instance_class):
        """
        DEBUGGING
        Returns tuple of:
        (1) instance_class
        (2) All registered classes with instances
        (3) instance_class instance id counter
        (4) All instances of instance_class
        """
        instance_id_counter, class_instances_by_id = 'nil', 'nil'
        classes_with_instances = sorted(self.get_classes_with_instances(instance_class))
        if instance_class in self.record:
            instance_id_counter = self.record[instance_class]['counter']
            class_instances_by_id = \
                sorted(self.record[instance_class]['instances_by_id'].iteritems())
        return (instance_class, 
                classes_with_instances, 
                instance_id_counter, 
                class_instances_by_id)

    def describe(self):
        print "Class Instance Record"
        for kr, vr in sorted(self.record.iteritems()):
            cntr = vr['counter']
            instances_by_id = vr['instances_by_id']
            print "{0} [{1}]:\n  {2}".format(kr, cntr, sorted(instances_by_id.iteritems()))
            
# --------------------------------------------------------------------------
            
# Instance Constants

INSTANCE = enum(UNREGISTERED=':unregistered')
"""
Blackboard instance constants
"""

CURRENT_BLACKBOARD = None
"""
Global indexing current blackboard store instance.
If more than one blackboard instance, could either pass instance reference
   to generic functions, or reassign CURRENT_BLACKBOARD reference as needed.
"""


# TODO
class Blackboard(object):
    """
    A blackboard repository.
    """
    
    def __init__(self, name=gensym('BB')):
        """
        Constructor to create instance of a blackboard
        """

        self.name = name
 
        self.signalled_event_queue = collections.deque()
        """
        Queue containing all currently signalled events
        Use: 
            append(event_instance) to enqueue
            popleft() to deque
        """

        self.currently_processing_events_queue = None
        """
        Queue containing all signalled events that are currently being processed
        This is a collections.deque
        """

        self.inactive_event_queue = []
        """
        Queue containing all inactive events (processed signalled events)
        Represented as a list.
        """

        self.cir = Class_Instance_Record()
        """
        Class_Instance_Record member instance for bookkeeping 
            ALL instance_classes that have some instances.
        """

    def __repr__(self):
        return "<Blackboard:{0}>".format(self.name)

    # ---------------------------------------
    # member Class_Instance_Record interface
    # ---------------------------------------

    def get_class_instance_record(self):
        """
        Interface to get current Class_Instance_Record
        """
        return self.cir

    def set_class_instance_record(self, new_cir):
        """
        Interface to set cir Class_Instance_Record with new_cir
        """
        self.cir = new_cir
    
    def add_instance(self, instance):
        """
        Calls member Class_Instance_Record cir:
            Base_Instance.cir.add_instance(instance)
        """
        self.cir.add_instance(instance)

    def remove_instance(self, instance):
        """
        Calls member Class_Instance_Record cir:
            cir.remove_instance(instance)
        """
        self.cir.remove_instance(instance)
    
    def get_all_classes_with_instances(self):
        """
        Calls member Class_Instance_Record cir:
            cir.get_all_classes_with_instances()
        """
        return self.cir.get_all_classes_with_instances()

    def get_classes_with_instances(self, instance_class, subclasses=True):
        """
        Calls member Class_Instance_Record cir:
            cir.get_classes_with_instances()
        Returns list of classes with instances.
        if subclasses=True (default), includes subclasses of instance_class,
        otherwise just returns list with instance_class (if it has instances,
        otherwise None).
        """
        return self.cir.get_classes_with_instances(instance_class,
                                                   subclasses=subclasses)

    def get_class_instances_by_id_dict(self, instance_class):
        """
        Calls member Class_Instance_Record cir:
            cir.get_class_counter_value(instance_class)
        """
        return self.cir.get_class_instances_by_id_dict(instance_class)

    def get_instances_of_classes(self, instance_classes, subclasses=True):
        """
        Calls member Class_Instance_Record cir:
            cir.get_instances_of_classes(instance_classes)
        Returns list of all instances of classes in instance_classes
        NOTE: Assumes instance_classes is a list of classes
        WARNING: This can return duplicate instances; e.g., if an instance_class
            appears more than one in instance_classes, or same instance somehow
            appears in more than one instance_class instance_by_id dict.
        """
        return self.cir.get_instances_of_classes(instance_classes)

    def delete_all_instance_bookkeeping(self):
        """
        Calls member Class_Instance_Record cir:
            cir.delete_all_instance_bookkeeping()
        NOTE: This deletes the bookkeeping but any other references 
              to objects remain.
        """
        self.cir.delete_all_instance_bookkeeping()

    def get_instance_bookkeeping_state(self, instance_class):
        """
        Calls member Class_Instance_Record cir:
            cir.get_instance_bookkeeping_state(instance_class)
        """
        return self.cir.get_instance_bookkeeping_state(instance_class)

    # --------------------------------
    # Event Management
    # --------------------------------
    
    def signal_event(self, event_class, name=gensym('E'), **payload):
        """
        Signal an Event on the Blackboard.  
        Events should only be signalled on a blackboard instance.
        Stores signaled event on Blackboard.signalled_event_queue
        """
        assert isinstance(event_class, type), \
            "signal_event(): event_class arg '{0}' is not a class.".format(event_class)
        assert issubclass(event_class, Standard_Event_Instance), \
            "signal_event(): event_class arg '{0}' is not subclass".format(event_class) \
            + "of Standard_Event_Instance"

        #: Create event instance, which in turn will
        #: execute any event functions and possibly print.
        event = event_class(name=name, **payload)

        #: Place event instance in signalled_event_queue
        self.signalled_event_queue.append(event)

        if event.event_functions:
            for fn in event.event_functions:
                fn(event)
        
        return event

    def enable_event_printing(self, *specs):
        """
        Enable printing of event signaling according on spec
        specs: list of event_class or (event_class, True)
            if (event_class, True), the True indicates all subclasses
        """
        for spec in specs:
            if isinstance(spec, tuple):
                classname, subp = spec
                classname.enable_event_printing(subp)
            else:
                spec.enable_event_printing()

    def disable_event_printing(self, *specs):
        """
        Disable printing of event signaling according to spec
        specs: list of event_class or (event_class, True)
            if (event_class, True), the True indicates all subclasses
        """
        for spec in specs:
            if isinstance(spec, tuple):
                classname, subp = spec
                classname.disable_event_printing(subp)
            else:
                spec.disable_event_printing()

    def get_signalled_event_queue_to_be_processed(self):
        """
        Because new events can be signalled while iterating currently signalled
        events, this method is used to safely move the signalled events up to this
        point and to be processed into the self.currently_processing_events_queue
        and the self.signalled_event_queue is reset so new events are placed there
        to be processed in the next iteration.
        """
        self.currently_processing_events_queue = self.signalled_event_queue
        self.signalled_event_queue = collections.deque()
        return self.currently_processing_events_queue

    def clear_currently_processing_events_queue(self):
        """
        Once the currently_processing_events_queue has been processed,
        move any signalled_events from the currently_processing_events_queue to the
        inactive_event_queue and set the currently_processing_events_queue to None.
        """
        self.inactive_event_queue += list(self.currently_processing_events_queue)
        self.currently_processing_events_queue = None

    # --------------------------------
    # Space Management
    # --------------------------------
    
    @TODO
    def add_space(self, space):
        self.spaces[space.name] = space

    # --------------------------------
    # Clear Blackboard
    # --------------------------------

    def clear_blackboard(self):
        """
        Resets all bookkeeping to initial state
        """
        self.signalled_event_queue = collections.deque()
        self.currently_processing_events_queue = None
        self.inactive_event_queue = []
        self.cir = Class_Instance_Record()

    # --------------------------------
    # Describe
    # --------------------------------

    def describe(self, verbose=False):
        print "\n| Blackboard repository {0}:".format(self)
        if self.cir:
            print '|\n| Unit Class'
            print '| ----------'
            for instance_class in sorted(self.cir.get_all_classes_with_instances(),
                                         key=lambda elm: elm.__name__):
                v = self.cir.get_class_instances_by_id_dict(instance_class)
                if verbose:
                    print '| {0}: {1} : {2}'.format(instance_class.__name__, len(v), v)
                else:
                    print '| {0}: {1}'.format(instance_class.__name__, len(v))

        print '|\n| Event Queues'
        print '| ------------'
        for name, queue in (('signalled_event_queue', self.signalled_event_queue),
                            ('currently_processing_events_queue', self.currently_processing_events_queue),
                            ('inactive_event_queue', self.inactive_event_queue)):
            if queue:
                length = len(queue)
            else:
                length = 0
            if verbose:
                print '| {0}: {1} : {2}'.format(name, length, queue)
            else:
                print '| {0}: {1}'.format(name, length)


def get_current_blackboard():
    global CURRENT_BLACKBOARD
    if CURRENT_BLACKBOARD:
        return CURRENT_BLACKBOARD
    else:
        print "get_current_blackboard(): No blackboard context (none provided, and CURRENT_BLACKBOARD is empty)."
        return None


def signal_event(event_class, name=gensym('E'), blackboard=None, **payload):
    if not blackboard:
        blackboard = get_current_blackboard()
    if blackboard:
        blackboard.signal_event(event_class, name=name, **payload)
        return True
    print "signal_event(): No blackboard context (none provided, and CURRENT_BLACKBOARD is empty)."
    return False


def describe_blackboard_repository(blackboard=None):
    if not blackboard:
        blackboard = get_current_blackboard()
    if not blackboard:
        print "describe_blackboard_repository(): No blackboard context (none provided, and CURRENT_BLACKBOARD is empty)."
        return None
    blackboard.describe()


def create_blackboard_repository(make_current=True):
    """
    Generic function to create a blackboard.
    """
    global CURRENT_BLACKBOARD
    blackboard_instance = Blackboard()
    if make_current:
        CURRENT_BLACKBOARD = blackboard_instance

    return blackboard_instance


def clear_blackboard_repository(blackboard=CURRENT_BLACKBOARD):
    """
    Reinitializes all instance bookkeeping.
    """
    if not blackboard:
        blackboard = get_current_blackboard()
    if blackboard:
        blackboard.clear_blackboard()
    print "No blackboard instance to clear."

        
# --------------------------------------------------------------------------
# Instances
# --------------------------------------------------------------------------

class Base_Instance(object):
    """
    The top-level class for any id'd and named object.
    """

    #: Base_Instance is an abstract class
    __metaclass__ = ABCMeta
    
    def __init__(self, **kwargs):
        global CURRENT_BLACKBOARD

        verbose = None
        if 'verbose' in kwargs and kwargs['verbose']:
            verbose = True

        self.id = INSTANCE.UNREGISTERED
        
        if 'name' in kwargs:
            self.name = kwargs['name']
        else:
            self.name = gensym()
            
        if 'blackboard' in kwargs:
            if verbose:
                print "Registering to blackboard."
            kwargs['blackboard'].add_instance(self)
        elif CURRENT_BLACKBOARD:
            if verbose:
                print "Registering to CURRENT_BLACKBOARD."
            CURRENT_BLACKBOARD.add_instance(self)

        if verbose:
            print "INIT: {0}, id='{1}', name='{2}'".format(self.__class__.__name__, self.id, self.name)

    def __repr__(self):
        """
        Used for debugging/testing b/c address is avoided
        """
        return '<{0}-{1}({2})>'.format(self.__class__.__name__, self.id, self.name)

    def remove(self):
        # print "Removing {0} : {1}".format(self.__class__.__name__, self)
        self.__class__.remove_instance(self)

    
# --------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------

class Standard_Unit_Instance(Base_Instance):
    """
    The base class for blackboard Units - any object that can be placed on a blackboard space
    (the term 'units' used so as to not be confused with general python 'objects')
    """

    def __init__(self, **kwargs):

        Base_Instance.__init__(self, **kwargs)

        self.space_instances = None
        if 'space_instances' in kwargs:
            self.space_instances = kwargs['space_instances']
        
    def __repr__(self):
        return "<{0}-{1}('{2}',{3})>".format(self.__class__.__name__, self.id,
                                             self.name, self.space_instances)
        
    def describe(self):
        print '{0}-{1}'.format(self.__class__.__name__, self.id)
        print '  id: {0}'.format(self.id)
        print '  name: {0}'.format(self.name)
        if self.space_instances:
            print '  spaces_instances: {0}'.format(self.space_instances)


def make_unit_instance(class_name, **kwargs):
    """
    Create a unit_instance.
    Signals Instance_Created_Event in blackboard.
    Should be done in the context of a blackboard, which could either be
    passed as a keyword argument: blackboard=<bb-instance> (higher precendence)
    OR when global CURRENT_BLACKBOARD reference the current blackboard instance.
    """
    global CURRENT_BLACKBOARD
    if CURRENT_BLACKBOARD and 'blackboard' not in kwargs:
        unit_instance = class_name(blackboard=CURRENT_BLACKBOARD, **kwargs)
 
        CURRENT_BLACKBOARD.signal_event(Instance_Created_Event, unit_instance=unit_instance)
 
    else:
        unit_instance = class_name(**kwargs)
    return unit_instance
 
 
# def store_table(dataFrame, sTblName, **kwargs):
#     """
#     Stores a table 'dataFrame' with name 'sTblName' into the DB.
#     Signals a database transaction event in blackboard.
#     It should be done in the context of a blackboard, which could either be
#     passed as a keyword argument: blackboard=<bb-instance> (higher precendence)
#     OR when global CURRENT_BLACKBOARD reference the current blackboard instance. 
#     'sTblName' must be a string.
#     """
#     global DEBUG
#     if DEBUG:
#         print "Storing {0} table: {1}".format( sTblName, type(dataFrame) );
#     global CURRENT_BLACKBOARD
#     if CURRENT_BLACKBOARD and 'blackboard' not in kwargs:
#         bb_Detections.storeTable(dataFrame, sTblName);
#         CURRENT_BLACKBOARD.signal_DB_event("Update_Table_"+sTblName, sTblName);
#     else:
#         bb_Detections.storeTable(dataFrame, sTblName);


# --------------------------------------------------------------------------
# Spaces
# --------------------------------------------------------------------------

# TODO
class Standard_Space_Instance(Standard_Unit_Instance):
    """
    Spaces are containers for Standard_Unit_Instances (and their subclasses)
    In classic blackboards, these are hierarchically structured as tree,
       referenced by path (a path is a list of space names, from root to instance)
    NOTE: Let's only add structure here as needed (unclear tree structure is needed, yet)
    """

    def __init__(self, **kwargs):
        Base_Instance.__init__(self, **kwargs)

    @TODO
    def add_to_space(self, unit_instance):
        """
        Only Standard_Unit_Instances and subclasses can be added to a space
        Since spaces are Standard_Unit_Instances, the can be added to a space
        """
        pass

    @TODO
    def remove_from_space(self, unit_instance):
        """
        Removing does not delete the instance, just removes it from space bookkeeping
        """
        pass


# --------------------------------------------------------------------------
# Events
# --------------------------------------------------------------------------

# Currently reproducing a chunk of GBBopens Event hierarchy (perhaps overkill)
# http://gbbopen.org/hyperdoc/ref-event-entities.html

# TODO: 
# () determine where signaled events are located:
# Now thinking that Standard_Event_Instance should inherit from a modified
# version of Base_Instance where there is an "active" and "inactive" queue
# associated with each Class
# () create mechanism to search from given class through all children for
# event instances

def default_event_ks_trigger_function(event, ks):
    """
    Default event ks trigger function.
    Tests whether event class is in ks trigger_events spec list
    spec: list of event_class or (event_class, <additional specs>)
    if event.__class__ == spec event_class, then return True, else False
    """
    for ks_trigger_event_spec in ks.trigger_events:
        if isinstance(ks_trigger_event_spec, tuple):
            ks_trigger_event_spec = ks_trigger_event_spec[0]
        if event.__class__ == ks_trigger_event_spec:
            return True
    return False


class Standard_Event_Instance(Base_Instance):
    """
    Top-level Event.
    Implements default functionality of all events.
    """

    #: Standard_Event_Instance is an abstract class
    __metaclass__ = ABCMeta

    # --------------------------------
    # Class attributes adn methods
    # --------------------------------

    event_ks_trigger_function = default_event_ks_trigger_function
    """
    event_ks_trigger_function takes two arguments
        event instance
        ks instance
    and returns true if ks should be considered for activation.
    This function is stored at the class level for default event
        class behavior.
    Event instance references class function by default
        (could be specialized for event instance trigger functions,
         if desired)
    """

    event_functions = None  # possibly collections.queue ?
    """
    event_functions is a list of functions, each taking the event
    as an argument; the event provides the execution context (arguments)
    """

    event_printing_enabled = False
    """
    Boolean associated with all event classes determining whether
    event instance of class will be printed.
    """

    @classmethod
    def enable_event_printing(cls, subclasses=False):
        """
        Enable event printing for this event class and optionally
        for all subclasses of this event class.
        """
        cls.event_printing_enabled = True
        if subclasses:
            for c in all_subclasses(cls):
                c.enable_event_printing()

    @classmethod
    def disable_event_printing(cls, subclasses=False):
        """
        Disable event printing for this event class and optionally
        for all subclasses of this event class.
        """
        cls.event_printing_enabled = False
        if subclasses:
            for c in all_subclasses(cls):
                c.disable_event_printing()

    # --------------------------------
    # Instance methods
    # --------------------------------

    def __init__(self, name=gensym('E'), **payload):
        """
        :param str name: Optional name of the Event instance.  Default=gensym('E')
    
        :param keyword-list payload: Optional payload of the Event
        """

        # print 'SEI:', name, payload
        
        Base_Instance.__init__(self, name=name)

        self.event_ks_trigger_function = self.__class__.event_ks_trigger_function
        self.event_functions = self.__class__.event_functions
        
        self.payload = payload
        self.print_event()

    def __repr__(self):
        return "<Event:{0}-{1}('{2}',{3})>".format(self.__class__.__name__, self.id, self.name, self.payload)

    def triggers(self, ks):
        """
        Event instance interface to event_ks_trigger_function.
        Calls instance event_ks_trigger_function with self and ks.
        If returns True, then triggers ks.
        """
        return self.event_ks_trigger_function(self, ks)

    def print_event(self):
        """
        Prints event if event_printing_enabled for self.__class__ is True
        """
        if self.__class__.event_printing_enabled:
            print "Event signaled {0}: {1}".format(self.__class__.__name__, self)


# --------------------------------------------------------------------------
# Instance Events

def default_instance_event_ks_trigger_function(event, ks):
    """

    """

    for ks_trigger_event_spec in ks.trigger_events:
        if isinstance(ks_trigger_event_spec, tuple):
            # ks_trigger_event_spec[0] : event type
            # ks_trigger_event_spec[1] : unit type

            global DEBUG
            if DEBUG:
                print "----------- default_instance_event_ks_trigger_function()"
                print "<<<< event: {0}".format(event)
                print "<<<<    ks: {0}".format(ks)
                print "<<<< ks_trigger_event_spec[0] event type: {0}".format(ks_trigger_event_spec[0])
                print "<<<<                     event.__class__: {0}".format(event.__class__)
                print "<<<<  ks_trigger_event_spec[1] unit type: {0}".format(ks_trigger_event_spec[1])
                print "<<<<                       event.payload: {0}".format(event.payload)
                print "<<<<    'unit_instance' in event.payload: {0}".format('unit_instance' in event.payload)
                if 'unit_instance' in event.payload:
                    print "<<<<      event.payload['unit_instance']: {0}".format(event.payload['unit_instance'])
                    the_test = event.__class__ == ks_trigger_event_spec[0] and \
                        'unit_instance' in event.payload and \
                        event.payload['unit_instance'].__class__ == ks_trigger_event_spec[1]
                    print "<<<<                     the test result: {0}".format(the_test)
                print "-----------"

            if event.__class__ == ks_trigger_event_spec[0] and \
                'unit_instance' in event.payload and \
                    event.payload['unit_instance'].__class__ == ks_trigger_event_spec[1]:
                return True
        elif event.__class__ == ks_trigger_event_spec:
            return True
    return False


class Instance_Event(Standard_Event_Instance):
    """
    Top-level Event for all events involving a singe blackboard Unit Instances.

    """

    #: Instance_Event is an abstract class
    __metaclass__ = ABCMeta

    event_ks_trigger_function = default_instance_event_ks_trigger_function


class Multiple_Instance_Event(Instance_Event):
    """
    All Events that involve 1 or more instances.
    Use-case seems to be for triggering events that require multiple instances
    """

    #: Multiple_Instance_Event is an abstract class
    __metaclass__ = ABCMeta

    pass


class Single_Instance_Event(Instance_Event):
    """
    All Events that involve an instance.
    """

    #: Single_Instance_Event is an abstract class
    __metaclass__ = ABCMeta

    pass


class Instance_Created_Changed_Deleted_Event(Single_Instance_Event):
    """
    All Events involving creating, changing, or deleting instances.
    """

    #: Instance_Created_Changed_Deleted_Event is an abstract class
    __metaclass__ = ABCMeta

    pass


class Instance_Created_Event(Instance_Created_Changed_Deleted_Event):
    """
    Event that an Instance has been created.
    """
    pass


class DB_Event(Instance_Created_Changed_Deleted_Event):
    """
    Event that an Instance has been created.
    """
    pass


class Delete_Instance_Event(Instance_Created_Changed_Deleted_Event):
    """
    Event that a delete-instance has been initiated.
    """
    pass


class Instance_Deleted_Event(Instance_Created_Changed_Deleted_Event):
    """
    Event that a delete-instance has been completed
    and the instance is now deleted.
    """
    pass

"""
Additional Instance_Created_Changed_Deleted_Events:
Change_Instance_Class_Event(Instance_Created_Changed_Deleted_Event)
Instance_Changed_Class_Event(Instance_Created_Changed_Deleted_Event)
"""

# TODO
"""
Space Instance events:
Space_Instance_Event(Single_Instance_Event) : abstract
Instance_Added_To_Space_Instance_Event(Space_Instance_Event)
Instance_Moved_Within_Space_Instance_Event(Space_Instance_Event)
Instance_Removed_From_Space_Instance_Event(Space_Instance_Event)
"""

"""
Slot events (including links):
Link_Nonlink_Slot_Event(Single_Instance_Event) : abstract
Link_Slot_Event(Link_Nonlink_Slot_Event) : abstract
Link_Nonlink_Slot_Modified_Event(Link_Nonlink_Slot_Event) : abstract
Link_Event(Link_Slot_Event, Link_Nonlink_Slot_Modified_Event)
Unink_Event(Link_Slot_Event, Link_Nonlink_Slot_Modified_Event)
Nonlink_Slot_Updated_Event(Link_Nonlink_Slot_Modified_Event)
"""

# --------------------------------------------------------------------------
# Non_Instance Events

class Non_Instance_Event(Standard_Event_Instance):
    """
    Top-level Event for all non-instance events (e.g., control shell events).
    """

    #: Non_Instance_Event is an abstract class
    __metaclass__ = ABCMeta

    pass

"""
Timer_Interrupt_Event(Non_Instance_Event)
"""

# --------------------------------------------------------------------------
# Events particular to the Agenda Control Shell

class Control_Shell_Event(Non_Instance_Event):
    """
    Top-level Event for all control shell behaviors.
    """

    #: Control_Shell_Event is an abstract class
    __metaclass__ = ABCMeta

    pass


class Control_Shell_Started_Event(Control_Shell_Event):
    """
    Event triggered when control shell is started.
    """
    pass


def control_shell_immediate_stop_event_function(event):
    """
    Event Function
    Takes single argument: event
    Executes when event signaled.
    """
    print "!! control_shell_immediate_stop_event_function():"
    print "!!     Reason: {0}".format(event.payload['message'])
    if 'blackboard' in event.payload:
        bb = event.payload['blackboard']
    else:
        bb = get_current_blackboard()
    if bb:
        acs = bb.get_class_instances_by_id_dict(Agenda_Control_Shell).values()[0]
        acs.immediate_stop = True
    else:
        print "!! FAILURE control_shell_immediate_stop_event_function() found no blackboard"


class Control_Shell_Immediate_Stop_Event(Control_Shell_Event):
    """
    Event triggered when control shell is Stopped by ks.precondition_function().
    NOTE: Does not appear in GBBopen standard hierarchy.
        However, might be useful for handling some cleanup/bookkeeping
        activities before ACS control loop stops.
    """
    event_functions = [ control_shell_immediate_stop_event_function ]


class Control_Shell_Cycle_Event(Control_Shell_Event):
    """
    Event triggered when control shell starts a new cycle.
    """
    pass


class Control_Shell_Quiescence_Event(Control_Shell_Event):
    """
    Event triggered when control shell goes to quiescence.
    """
    pass

"""
Control_Shell_Restarting_Event(Control_Shell_Event)
Control_Shell_Hibernating_Awakening_Event(Control_Shell_event) : abstract
Control_Shell_Hibernating_Event(Control_Shell_Hibernating_Awakening_Event)
Control_Shell_Awakening_Event(Control_Shell_Hibernating_Awakening_Event)
"""


# --------------------------------------------------------------------------
# Events particular to KSAs

class KSA_Event(Control_Shell_Event, Instance_Event):
    """
    Top-level Event for all KSA activities
    """

    #: KSA_Event is an abstract class
    __metaclass__ = ABCMeta

    pass


class KSA_Activated_Event(KSA_Event):
    """
    """
    pass


class KSA_Executing_Event(KSA_Event):
    """
    """
    pass


class KSA_Obviated_Event(KSA_Event):
    """
    """
    pass


class KSA_Retriggered_Event(KSA_Event):
    """
    """
    pass


# --------------------------------------------------------------------------
# Agenda Control Shell
# --------------------------------------------------------------------------

# Agenda Control Shell Constants

ACS = enum(STOP=':stop', CONTINUE=':continue', QUIESCENCE=':quiesence')
"""
Agenda Control Shell Constants
"""

CONTROL_SHELL = None
"""
Global reference to control shell instance
"""

# --------------------------------------------------------------------------


class Agenda_Control_Shell(Standard_Unit_Instance):
    """
    (Inspired by KS definition in Agenda Control Shell of GBBopen: http://gbbopen.org)
    """
    def __init__(self,
                 name=gensym('ACS'),
                 execution_cycle=0,
                 minimum_KSA_execution_rating=0,
                 activity_printing=False,
                 **kwargs):
        """
        Agent Control Shell init
            activity_printing : when True, basic ACS activities are printed
        """
        Standard_Unit_Instance.__init__(self, name=name, **kwargs)

        global CURRENT_BLACKBOARD
        self.name = name
        if 'blackboard' in kwargs:
            self.blackboard = kwargs('blackboard')
        elif CURRENT_BLACKBOARD:
            self.blackboard = CURRENT_BLACKBOARD
        else:
            #: Need to do something here...
            print 'ACS __init__() FAIL: no blackboard instance'
        self.execution_cycle = execution_cycle
        self.minimum_KSA_execution_rating = minimum_KSA_execution_rating
        self.pending_KSAs = []   # priority queue
        self.obviated_KSAs = []  # queue
        self.executed_KSAs = []  # queue

        self.activity_printing = activity_printing

        self.epoch_start_time = 0  # start running of control shell

        self.immediate_stop = False

    def __repr__(self):
        return "<Agenda_Control_Shell:{0},{1}>".format(self.name, self.execution_cycle)

    def display_full_time(self, t):
        return time.strftime("%Z: %a, %d %b %Y %H:%M:%S", time.localtime(t))

    def test_for_stop_event(self):
        if self.immediate_stop:
            return True
        return False

    def start(self, iterations=None):
        """
        NOTE: this could be spawned as a threaded process
        For now it will be a single-process, static control loop
        """
        if self.activity_printing:
            print ';; Control Shell {0} started'.format(self.name)
            # print 'blackboard: {0}'.format(self.blackboard)

        self.blackboard.signal_event(Control_Shell_Started_Event,
                                     execution_cycle=self.execution_cycle)

        self.epoch_start_time = time.time()

        if self.activity_printing:
            print ';; Control shell started {0}'.format(self.display_full_time(self.epoch_start_time))

        self.run_control_loop(iterations=iterations)

    def run_control_loop(self, iterations=False):
        """
        Runs step_control_loop until
            interruption
            quiescence
            executed number of iterations (if specified)

        On quiescence signal, continues for an additional KS-execution cycle
        in case any executable KSAs resulted from the quiescence signal.
        """

        stopping_cycle = None
        exit_condition = None

        if iterations and isinstance(iterations, int):
            stopping_cycle = self.execution_cycle + iterations

        #: run until interruption, quiescence, or iterations (if specified)
        while not exit_condition and stopping_cycle != self.execution_cycle:

            # TODO Debugging
            if DEBUG:
                self.blackboard.describe(verbose=True)
                self.describe()

            exit_condition = self.step_control_loop()

            # TODO Debugging
            if DEBUG:
                self.blackboard.describe(verbose=True)
                self.describe()

        #: handle quiescence exit condition
        if exit_condition == ACS.QUIESCENCE:
            self.blackboard.signal_event(Control_Shell_Quiescence_Event,
                                         execution_cycle=self.execution_cycle)

            # TODO Debugging
            if DEBUG:
                self.blackboard.describe(verbose=True)
                self.describe()

            if self.activity_printing:
                print ';; Control shell {0} quiescence'.format(self.name)

            self.step_control_loop()

        # TODO Debugging
        if DEBUG:
            self.blackboard.describe(verbose=True)
            self.describe()

        if self.activity_printing:
            print ';; Control shell {0} exited'.format(self.name)
        epoch_end_time = time.time()
        elapsed_time = epoch_end_time - self.epoch_start_time
        if self.activity_printing:
            print ';; Elapsed epoch time: {0} seconds'.format(elapsed_time)

        return exit_condition

    def step_control_loop(self):
        """
        Execute one control cycle of the control loop
        """

        cycle_start_time = time.time()

        self.execution_cycle += 1
        csse_event = self.blackboard.signal_event(Control_Shell_Cycle_Event,
                                                  execution_cycle=self.execution_cycle,
                                                  execution_cycle_start_time=cycle_start_time)

        #: NOTE: this is somewhat expensive for what we want
        #:       maybe store stop even elsewhere?
        if self.test_for_stop_event():
            return ACS.STOP

        exit_condition = False

        #: Test for KS Activation (step 1)
        #  NOTE: could be faster if iterate over only lists of KSs stored by event
        ks_classes = self.blackboard.get_classes_with_instances(Knowledge_Source, subclasses=True)
        kss = self.blackboard.get_instances_of_classes(ks_classes)

        #: Get the currently signalled events for processing
        #: NOTE: As soon as the blackboard.get_signalled_event_queue_to_be_processed
        #: is called, any new newly signalled events are placed on a fresh
        #: blackboard.signalled_event_queue and the events being processed
        #: are stored temporarily (which being processed) blackboard.currently_processing_events_queue
        events_to_process = self.blackboard.get_signalled_event_queue_to_be_processed()

        for ks in kss:
            for event in events_to_process:

                ## Question CTM(20140119):
                # Should ks collect multiple triggering events?
                # More efficient that way?
                # Perhaps by Multiple_Instance_Event?
                #   But how does that get triggered?
                #   Seems to require a ks run that checks multiple instances...

                #: Test if event triggers KS using the event function event.triggers(ks)
                #: NOTE: event.triggers allows for events to specify how they might
                #: match and trigger a KS.
                # The test used to be: if event.__class__ in ks.trigger_events:
                if event.triggers(ks):
                    #: event triggers KS
                    #: test if has activation_predicate, and if so, does it return True...
                    if (not ks.activation_predicate) or ks.activation_predicate(ks, event):
                        #: by default, continue KS activation test if no ks.activation_predicate
                        #: if there is a ks.activation_predicate, only activate if it returns a value
                        precondition_result = True
                        if ks.precondition_function:
                            precondition_result = ks.precondition_function(ks, event)

                        if precondition_result == ACS.STOP:
                            #: Stop control shell immediately if precondition_result == ACS.STOP
                            if DEBUG:
                                print 'Control Shell {0}.step_control_loop: ks {1}.precondition_fn signaled STOP'\
                                    .format(self.name, ks)
                            self.blackboard.signal_event(Control_Shell_Immediate_Stop_Event,
                                                         execution_cycle=self.execution_cycle,
                                                         ks=ks,
                                                         ks_precondition_result=precondition_result)
                            return ACS.STOP

                        elif precondition_result:
                            #: ...either no ks.precondition_function, or it returned with a value...

                            if DEBUG:
                                print "Control Shell {0}: activating KS {1}".format(self, ks)

                            #: Activate KS! (step 2)
                            ksa = ks.activate(self.execution_cycle, precondition_result, [event])

                            #: Place KSA on pending_KSAs queue (step 3)
                            self.pending_KSAs.append(ksa)

                            self.blackboard.signal_event(KSA_Activated_Event,
                                                         execution_cycle=self.execution_cycle,
                                                         ksa=ksa)

                            if DEBUG:
                                print "pending_KSAs: {0}".format(self.pending_KSAs)

        # TODO
        # What to do here?
        # Check with new signaled events and/or processed events from events_to_process?
        #   E.g., signalling KSA_Activated_Event could lead to additional events
        # Do this for each of the following steps?

        #: Handle obviation (step 4)
        #: TODO

        #: Handle retriggering (step 5)
        #: TODO

        #: Handle revalidation (step 6)
        #: TODO

        if self.pending_KSAs:
            #: KSA execution (step 7)
            #  () The pending KSA is removed from the pending KSAs queue,
            #  () the current control shell cycle number is stored in the
            #     KSA.execution_cycle slot of the KSA unit instance, and
            #  () the KS.execution_function is called
            ksa = self.pending_KSAs.pop()
            ksa.execution_cycle = self.execution_cycle

            ksaee = self.blackboard.signal_event(KSA_Executing_Event,
                                                 execution_cycle=self.execution_cycle,
                                                 ksa=ksa)

            ksa_execution_start_time = time.time()
            ksaee.payload['ksa_execution_start_time'] = ksa_execution_start_time

            #: Execute KSA execution_function
            ksa.execution_function(ksa)

            ksa_execution_end_time = time.time()
            ksaee.payload['ksa_execution_end_time'] = ksa_execution_end_time

            #: The executed KSA is placed on the queue of executed KSAs (step 8)
            self.executed_KSAs.append(ksa)
        else:
            #: No pending KSAs, exit with quiescence
            if self.activity_printing:
                print ";; No executable KSAs remain, exiting control shell"
            exit_condition = ACS.QUIESCENCE

        #: Now that the current batch of signalled events has been processed,
        #: move them to inactive_events_queue and clear the currently_processing_events_queue
        self.blackboard.clear_currently_processing_events_queue()

        # record shell cycle end_time
        csse_event.payload['execution_cycle_end_time'] = time.time()

        return exit_condition

    def describe(self):
        print '\n| Agenda Control Shell {0}'.format(self)
        print '|   blackboard: {0}'.format(self.blackboard)
        print '|   execution_cycle: {0}'.format(self.execution_cycle)
        print '|   minimum_KSA_execution_rating: {0}'.format(self.minimum_KSA_execution_rating)
        print '|   pending_KSAs: {0}'.format(self.pending_KSAs)
        print '|   obviated_KSAs: {0}'.format(self.obviated_KSAs)
        print '|   executed_KSAs: {0}'.format(self.executed_KSAs)
        print


# --------------------------------------------------------------------------
# Knowledge Sources
# --------------------------------------------------------------------------

class Knowledge_Source_Activation(Standard_Unit_Instance):
    """
    (Inspired by KS definition in Agenda Control Shell of GBBopen: http://gbbopen.org)
    Primary role is to bookkeeping of specific KS activation instance
    This 'wraps' the parent KS attributes
    """
    def __init__(self, **kwargs):
        """
        Defaults:
        ks = knowledge source creating KSA
        activation_cycle = 0
        obviation_cycle = None
        execution_cycle = None
        """
        #: pointer to the KS instance of which this is an activation instance
        # if 'ks' not present, something went wrong in how this was called
        ks = kwargs['ks']
        self.ks = ks

        #: ksa_execution_context
        self.ksa_execution_context = None
        if 'ksa_execution_context' in kwargs:
            self.ksa_execution_context = kwargs['ksa_execution_context']

        #: control-shell cycle number
        self.activation_cycle = 0
        if 'activation_cycle' in kwargs:
            self.activation_cycle = kwargs['activation_cycle']
        #: the control_shell.cycle number when the KSA is obviated
        self.obviation_cycle = None
        if 'obviation_cycle' in kwargs:
            self.obviation_cycle = kwargs['obviation_cycle']
        #: the control_shell.cycle number when the KSA is executed
        self.execution_cycle = None
        if 'execution_cycle' in kwargs:
            self.execution_cycle = kwargs['execution_cycle']

        #: Use specified rating (possibly set by ks.precondition_function())
        #: or use default rating of ks
        if 'rating' in kwargs and isinstance(kwargs['rating'], int):
            self.rating = kwargs['rating']
        else:
            self.rating = ks.rating

        #: NOTE: CTM 20140107:
        #: the following _should_ just be references to the parent KS attributes
        #: to mimick the same interface to the KS
        #: These should be accessors, but NOT used for modification
        #: I'm not sure if python actually makes copies of primitive types
        self.enabled = ks.enabled
        # events:
        self.trigger_events = ks.trigger_events
        self.obviation_events = ks.obviation_events
        self.retrigger_events = ks.retrigger_events
        # predicates and functions:
        self.activation_predicate = ks.activation_predicate
        self.precondition_function = ks.precondition_function
        self.obviation_predicate = ks.obviation_predicate
        self.retrigger_function = ks.retrigger_function
        self.revalidation_predicate = ks.revalidation_predicate
        self.execution_function = ks.execution_function

        #: Call Standard_Unit_Instance.__init__()
        Standard_Unit_Instance.__init__(self, **kwargs)

    def __repr__(self):
        return "<KSA-{0}-{1}('{2}-{3}',{4})>".format(self.__class__.__name__, self.id,
                                                     self.ks.__class__.__name__, self.ks.id,
                                                     self.ks.rating)


class Knowledge_Source(Standard_Unit_Instance):
    """
    (Inspired by KS definition in Agenda Control Shell of 
     `GBBopen http://gbbopen.org http://gbbopen.org`_)
    A knowledge_Source (KS) is a unit instance (type of Standard_Unit_Instance) which
    specifies how activations of the KS are created and executed.
    The lifetime of each KS activation involves the following sequence:
    (1) When an Event matching one of the event specifications in trigger_events occurs,
        the KS is enabled
        () The KS.activation_predicate, if specified, is called and must return true
           for potential activation to continue
        () The KS.precondition_function, if specified, is called an must return an integer
           rating for potential activation to continue
    (2) The KS is activated, creating a unit instance of class ksa_class (KSA)
        () The KSA.rating is assigned based on precondition_function 
           or constant KS.rating value
        () The current control_shell cycle number is stored in the KSA.activation_cycle 
           slot of the KSA unit instance
    (3) The KSA is placed on the queue of pending KSAs
    (4) If an Event matching one of the event specifications in KS.obviation_events 
        occurs, the KS.obviation_predicate, if specified, is called.  If it returns true,
        the pending KSA is removed from the pending KSAs queue, the current control-shell
        cycle number is stored in the KSA.obviation_cycle attribute of the KSA, and
        the KSA is placed on the queue of obviated KSAs
    (5) If an Event matching one of the event specifications in KS.retriggering_events
        occurs, the KS.retrigger_function, if specified, is called.  
        A KS.retrigger_function is often used to change the triggering context of the
        KSA or its rating.
    (6) When a pending KSA is selected for execution (typically because it has the 
        highest rating above the minimum_KSA_execution_rating currently in effect
        for the control shell) then:
        () the KS.revalidation_predicate, if specified, is called.
           If the KS.revalidation_predicate returns False, then:
              () the pending KSA is removed from the pending KSAs queue
              () the current control shell cycle number is stored in the 
                 KSA.obviation_cycle slot of the KSA, and
              () the KSA is placed on the obviated KSAs queue
    (7) KSA execution
        () The pending KSA is removed from the pending KSAs queue, 
        () the current control shell cycle number is stored in the 
           KSA.execution_cycle slot of the KSA unit instance, and
        () the KS.execution_function is called
    (8) The executed KSA is placed on the queue of executed KSAs
    """
    def __init__(self, **kwargs):
        """
        Default values:
        ksa_class = Knowledge_Source_Activation
        rating = 1
        enabled = True
        trigger_events = None
        obviation_events = None
        retrigger_events = None
        activation_predicate = None
        precondition_function = None
        obviation_predicate = None
        retrigger_function = None
        revalidation_predicate = None
        execution_function = None
        """

        #: Default Knowledge_Source_Activation, or a subclass
        self.ksa_class = Knowledge_Source_Activation
        if 'ksa_class' in kwargs:
            self.ksa_class = kwargs['ksa_class']

        #: Base, constant rating of KS.  
        #: Default = 1
        self.rating = 1
        if 'rating' in kwargs:
            self.rating = kwargs['rating']

        #: Whether the KS is enabled, available for considering activation
        #: Default = True
        self.enabled = True
        if 'enabled' in kwargs:
            self.enabled = kwargs['enabled']

        #: The following are tuples of Event classes
        self.trigger_events = None
        if 'trigger_events' in kwargs:
            self.trigger_events = kwargs['trigger_events']
        self.obviation_events = None
        if 'obviation_events' in kwargs:
            self.obviation_events = kwargs['obviation_events']
        self.retrigger_events = None
        if 'retrigger_events' in kwargs:
            self.retrigger_events = kwargs['retrigger_events']

        #: function, 2 args: KS unit instance, triggering Event instance
        #: returns boolean indicated whether KS should continue to be
        #: considered for activation in response to the event
        #: Typically specified for a KS that does not require a precondition_function
        #: rating computation, but that does require an activate/don't-activate decision
        self.activation_predicate = None
        if 'activation_predicate' in kwargs:
            self.activation_predicate = kwargs['activation_predicate']

        #: function, 2 args: KS unit instance, triggering Event instance
        #: Should return one of the following sets of values:
        #: (1) False : indicating KS is not to be activated in response to the event
        #: (2) ACS.STOP (and, optionally, additional values to be returned by the
        #:               control shell)
        #:           : indicating that the control shell is to exit immediately
        #: (3) integer (and, optionally, initialization arguments to be used when
        #:              creating the KSA unit instance)
        #:           : representing execution rating for the KSA
        self.precondition_function = None
        if 'precondition_function' in kwargs:
            self.precondition_function = kwargs['precondition_function']

        #: function, 2 args: KSA unit instance, obviation Event instance
        #: Should return boolean that indicates whether KSA should be obviated
        self.obviation_predicate = None
        if 'obviation_predicate' in kwargs:
            self.obviation_predicate = kwargs['obviation_predicate']

        #: function, 2 args: KSA unit instance, retriggering Event instance
        #: Can perform whatever activities are needed in response to the event.
        #: Typically this involves augmenting the triggering context of the KSA
        #: or changing its execution rating.
        #: QUESTION(CTM,20140107): what is a 'triggering context'?
        #:    current ans (20140107):
        #:       I think it is any other blackboard state 
        #:       (e.g., any changes to BB units or other globals)
        self.retrigger_function = None
        if 'retrigger_function' in kwargs:
            self.retrigger_function = kwargs['retrigger_function']

        #: function, 1 arg: KSA unit instance
        #: Called immediately before a KSA is executed and should return a
        #: boolean that indicates whether the KSA shoud be executed (if True)
        #: or obviated (if False)
        self.revalidation_predicate = None
        if 'revalidation_predicate' in kwargs:
            self.revalidation_predicate = kwargs['revalidation_predicate']

        #: function, 1 arg: KSA unit instance
        #: Implements the KS.  When an activation of the KS (KSA) is executed,
        #: this function is called with one argument, the KSA
        #: If the execution function returns the value ACS.STOP (and, optionally,
        #: additional values to be returned by the control shell), the
        #: control shell will exit immediately
        self.execution_function = None
        if 'execution_function' in kwargs:
            self.execution_function = kwargs['execution_function']

        #: Call Standard_Unit_Instance.__init__()
        Standard_Unit_Instance.__init__(self, ks=self, **kwargs)

    def activate(self, activation_cycle, rating, ksa_execution_context, **kwargs):
        """
        Create a knowledge source activation (KSA) from this knowledge source (KS)
            activation_cycle : integer representing the activation_cycle number
            rating : the rating provided by the
            trigger_events : list (most often of one element) of trigger events instances
                             that led to triggering of KSA
        """

        global DEBUG
        if DEBUG:
            print ">>>>>>> ks.activate(): ksa_execution_context: {0}".format(ksa_execution_context)

        ksa = self.ksa_class(ks=self, activation_cycle=activation_cycle, rating=rating,
                             ksa_execution_context=ksa_execution_context, **kwargs)
        return ksa
        
    def __repr__(self):
        return "<KS-{0}-{1}('{2}',{3})>".format(self.__class__.__name__, self.id,
                                                self.name, self.enabled)
        
    def describe(self):
        """
        Describe the Knowledge_Source
        """
        print 'KS: {0}'.format(self.__class__.__name__)
        print '  ksa_class: {0}'.format(self.ksa_class.__name__)
        print '  rating:    {0}'.format(self.rating)
        print '  enabled:   {0}'.format(self.enabled)
        if self.trigger_events:
            print '  trigger_events:\n    {0}'.format(self.trigger_events)
        if self.obviation_events:
            print '  obviation_events:\n    {0}'.format(self.obviation_events)
        if self.retrigger_events:
            print '  retrigger_events:\n    {0}'.format(self.retrigger_events)
        if self.activation_predicate:
            print '  activation_predicate:   {0}'.format(self.activation_predicate)
        if self.precondition_function:
            print '  precondition_function:  {0}'.format(self.precondition_function)
        if self.obviation_predicate:
            print '  obviation_predicate:    {0}'.format(self.obviation_predicate)
        if self.retrigger_function:
            print '  retrigger_function:     {0}'.format(self.retrigger_function)
        if self.revalidation_predicate:
            print '  revalidation_predicate: {0}'.format(self.revalidation_predicate)
        if self.execution_function:
            print '  execution_function:     {0}'.format(self.execution_function)
        if self.space_instances:
            print '  space_instances:\n    {0}'.format(self.space_instances)


def define_knowledge_source(ks_class, **kwargs):
    """
    Top-level function to define a knowledge source instance given ks_class
    Mainly handles registering the ks instance with a blackboard.
    (either an explicitly specified blackboard in kwargs or default CURRENT_BLACKBOARD.)
    """
    global CURRENT_BLACKBOARD
    if CURRENT_BLACKBOARD and 'blackboard' not in kwargs:
        ks_class(blackboard=CURRENT_BLACKBOARD, **kwargs)
    else:
        ks_class(**kwargs)

# --------------------------------------------------------------------------


def delete_workspace_image(blackboard=CURRENT_BLACKBOARD):
    """
    WARNING: This will blow away any Blackboard and Instance bookkeeping, 
             reseting to initial state on first load.
    (1) Resets gensym counter
    (2) calls clear_blackboard_repository(blackboard)
    """
    reset_gensym_counter(0)
    clear_blackboard_repository(blackboard)



