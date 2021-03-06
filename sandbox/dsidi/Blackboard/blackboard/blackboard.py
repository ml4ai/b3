BLACKBOARD = {}
"""
Contains the blackboard database.
Version 1: simple dictionary of blackboard objects stored by name
"""

EVENTS = []
"""
Contains the events generated by each KSA execution.
The events are buffered until execution of the KSA is completed.
Then the events are processed by the control components.
"""

AGENDA = []
"""
Contains the list of activated KSs awaiting execution.
"""

CREATION_EVENT_KSS = []
"""
Contains KS specifications for all KSs that are interested in 
blackboard-object creation events 
(which is the only type of events currently supported).  
The define_creation_ks macro manages this list.

..  todo: define_creation_ks (currently KS_spec appends every
    knowledge source to CREATION_EVENT_KSS)

"""

TRACE_LEVEL = 4
"""
The current trace level.
Trace levels from 0 (none) to 3 (highest) are supported.
"""

# --------------------------------------------------------------------------

# Would prefer to have gensym be a callable object, 
# so counter isn't a global, but this isn't quite working like a fn
# so go with global for now...
'''
class gensym(object):
    
    counter = 0
    
    def __call__(name = 'G'):
        g = '{0}{1}'.format(name, gensym.counter)
        gensym.counter += 1
        return g

    def get_counter():
        """
        Accessor for gensym counter
        """
        return gensym.counter

    def reset_counter(val = 0, verbose = False):
        """
        Reset the gensym counter, optionally to val
        """
        if isinstance(val, int):
            counter = val
        else:
            print "WARNING: gensym.reset_counter(val={0}): val not an integer".format(val)
            counter = 0
        if verbose:
            print "counter = {0}".format(counter)
'''

counter = 0

def gensym(name = 'G'):
    """
    Create a generic name with a guaranteed unique name
    """
    global counter
    g = '{0}{1}'.format(name, counter)
    counter += 1
    return g

def get_gensym_counter():
    """
    Accessor for gensym counter
    """
    global counter
    return counter

def reset_gensym_counter(val = 0, verbose = False):
    """
    Reset the gensym counter, optionally to val
    """
    global counter
    if isinstance(val, int):
        counter = val
    else:
        counter = 0
    if verbose:
        print "counter = {0}".format(counter)

# --------------------------------------------------------------------------

class Base_Instance(object):
    """
    The top-level class for any id'd and named object 
    Any child class will have a class attribute
    """

    # ---------------------------
    # static members and methods
    # ---------------------------

    # set containing all instance_classes that have some instances
    instance_classes = set()

    @staticmethod
    def get_instance_classes():
        """
        Accessor that should be used to get Base_Instance.instance_classes
        """
        return Base_Instance.instance_classes

    # --------------------------
    # class members and methods
    # --------------------------

    instance_id_counter = 0
        
    @classmethod
    def get_new_instance_id(instance_class):
        instance_class.instance_id_counter += 1
        return instance_class.instance_id_counter

    @classmethod
    def get_instance_id_counter(instance_class):
        return instance_class.instance_id_counter
    
    @classmethod
    def reset_instance_id_counter(instance_class, val = 0):
        instance_class.instance_id_counter = val
    
    instances = {}
    instances_by_name = {}

    @classmethod
    def add_instance(instance_class, instance):
        """
        Add class instance to instances and instances_by_name
        """
        # add the instance_class to instance_types
        Base_Instance.instance_classes.add(instance_class)
        
        # the following is needed to create a class-wide attribute for 'instances'
        # but will be specific to the class caller
        if not instance_class.instances: instance_class.instances = {}
        instance_class.instances[instance.id] = instance
        if not instance_class.instances_by_name: instance_class.instances_by_name = {}
        instance_class.instances_by_name[instance.name] = instance

    @classmethod
    def remove_instance(instance_class, instance, verbose = False):
        """
        Remove class instances from instances and instances_by_name
        NOTE: does not delete the instance itself, it is just no longer globally stored
        """
        if instance in instance_class.instances.values():
            if verbose:
                print 'removing: {0}'.format(instance)
                print '   by id: {0}'.format(instance.id)
            del instance_class.instances[instance.id]
            if verbose:
                print '   {0}.instances: {1}'.format(instance_class.__class__.__name__, 
                                                     instance_class.instances)
                print '   by name: {0}'.format(instance.name)
            del instance_class.instances_by_name[instance.name]
            if verbose:
                print '   {0}.instances_by_name: {1}'.format(instance_class.__class__.__name__, 
                                                             instance_class.instances_by_name)

        # if no more remaining instances, remove instance_class from Base_Instance.instance_classes set
        if not instance_class.instances.values():
            Base_Instance.instance_classes.remove(instance_class)

    @classmethod
    def remove_all_instances(instance_class, verbose = False):
        if verbose:
            print "Removing all instances of {0}".format(instance_class.__class__.__name__)
        for instance in instance_class.instances.values():
            instance_class.remove_instance(instance, verbose)


    # -----------------
    # instance methods
    # -----------------
    
    def __init__(self, name=None):
        self.id = self.__class__.get_new_instance_id()
        if name:
            self.name = name
        else:
            self.name = gensym()
        self.__class__.add_instance(self)

        # print "init for class '{0}'\n   instances: {1}\n   instances_by_name: {2}" \
        #   .format(self.__class__.__name__, 
        #           self.__class__.instances,
        #           self.__class__.instances_by_name)
        
    def __repr__(self):
        return '{0}({1})'.format(self.__class__.__name__, self.name)
        
    def __str__(self):
        return '<{0}-{1}({2})>'.format(self.__class__.__name__, self.id, self.name)

    def remove(self):
        # print "Removing {0} : {1}".format(self.__class__.__name__, self)
        self.__class__.remove_instance(self)

# --------------------------------------------------------------------------

class Standard_Unit_Instance(Base_Instance):
    """
    The base class for blackboard Units - any object that can be placed on a blackboard space
    (the term 'units' used so as to not be confused with general python 'objects')
    """

    def __init__(self, name=None, space_instances=None):
        self.space_instances = space_instances
        Base_Instance.__init__(self, name)

    def __repr__(self):
        return '{0}({1},{2})'.format(self.__class__.__name__, self.name, self.space_instances)
        
    def __str__(self):
        return '<{0}-{1}({2},{3})>'.format(self.__class__.__name__, self.id,
                                           self.name, self.space_instances)
        
    def describe(self):
        print '{0}-{1}'.format(self.__class__.__name__, self.id)
        print '  id: {0}'.format(self.id)
        print '  name: {0}'.format(self.name)
        if self.space_instances:
            print '  spaces_instances: {0}'.format(self.space_instances)


def test_standard_unit_instance_inheritance(verbose = 0):
    """
    A verbose test that assures we can subclass Standard_Unit_Instance and get 
    desired behavior w.r.t. storing object by id and name in child class
    NOTE: This also tests the gensym and Standard_Unit_Instance.instance_id_counter
    and related functions/methods
    """
    gensym_counter_state = get_gensym_counter()
    standard_unit_instance_id_counter_state = Standard_Unit_Instance.get_instance_id_counter()

    if verbose > 1:
        print "Counters before local reset:"
        print "  gensym_counter:", get_gensym_counter()
        print "  Standard_Unit_Instance.instance_id_counter:", Standard_Unit_Instance.get_instance_id_counter()

    reset_gensym_counter()
    Standard_Unit_Instance.reset_instance_id_counter(standard_unit_instance_id_counter_state)

    if verbose > 1:
        print "Counters after local reset:"
        print "  gensym_counter:", get_gensym_counter()
        print "  Standard_Unit_Instance.instance_id_counter:", Standard_Unit_Instance.get_instance_id_counter()
    
    class __Test_Class_(Standard_Unit_Instance):
        """ Local test class to test inheritance with proper class-instances behavior """
        
    t1, t2 = __Test_Class_(), __Test_Class_('tu2')
    s1, s2 = Standard_Unit_Instance(), Standard_Unit_Instance('su2')

    assert "<__Test_Class_-1(G0,None)>;<__Test_Class_-2(tu2,None)>;<Standard_Unit_Instance-1(G1,None)>;<Standard_Unit_Instance-2(su2,None)>;[(1, __Test_Class_(G0,None)), (2, __Test_Class_(tu2,None))];[('G0', __Test_Class_(G0,None)), ('tu2', __Test_Class_(tu2,None))];[(1, Standard_Unit_Instance(G1,None)), (2, Standard_Unit_Instance(su2,None))];[('G1', Standard_Unit_Instance(G1,None)), ('su2', Standard_Unit_Instance(su2,None))]" \
      == '{0};{1};{2};{3};{4};{5};{6};{7}'\
      .format(t1,t2,s1,s2,
              sorted(__Test_Class_.instances.iteritems()),
              sorted(__Test_Class_.instances_by_name.iteritems()),
              sorted(Standard_Unit_Instance.instances.iteritems()),
              sorted(Standard_Unit_Instance.instances_by_name.iteritems())), \
      "test_standard_unit_instance_inheritance(): Inheritance test FAILED."

    if verbose > 2:
        print "Full test string:"
        print '{0};{1};{2};{3};{4};{5};{6};{7}'\
          .format(t1,t2,s1,s2,
                  sorted(__Test_Class_.instances.iteritems()),
                  sorted(__Test_Class_.instances_by_name.iteritems()),
                  sorted(Standard_Unit_Instance.instances.iteritems()),
                  sorted(Standard_Unit_Instance.instances_by_name.iteritems()))

    if verbose > 1:
        print "Counters after local activity:"
        print "  gensym_counter:", get_gensym_counter()
        print "  Standard_Unit_Instance.instance_id_counter:", Standard_Unit_Instance.get_instance_id_counter()

    # Cleanup...
    s1.remove()
    s2.remove()
    del __Test_Class_

    if verbose > 1:
        print 'Standard_Unit_Instance.instances:', Standard_Unit_Instance.instances
        print 'Standard_Unit_Instance.instances_by_name:', Standard_Unit_Instance.instances_by_name

    reset_gensym_counter(gensym_counter_state)
    Standard_Unit_Instance.reset_instance_id_counter(standard_unit_instance_id_counter_state)

    if verbose > 1:
        print "Counters after returning to original values:"
        print "  gensym_counter:", get_gensym_counter()
        print "  Standard_Unit_Instance.instance_id_counter:", Standard_Unit_Instance.get_instance_id_counter()

    if verbose > 0:
        print "test_standard_unit_instance_inheritance(): Inheritance test PASSED."

# --------------------------------------------------------------------------

# TODO
class Standard_Space_Instance(Base_Instance):
    """
    """
    def __init__(self, name=None):
        Base_Instance.__init__(self, name)

# --------------------------------------------------------------------------

# TODO
class Blackboard(object):
    """
    """
    def __init__(self):
        pass

    def add_space(self, space):
        self.spaces[space.name] = space
    
    def describe(self):
        pass

def get_instance_classes():
    """
    Global interface to extract current Base_Instance classes with some instances
    """
    return Base_Instance.get_instance_classes()

def describe_blackboard_repository():
    print 'Unit Class'
    print '----------'
    for c in sorted(get_instance_classes()):
        print '{0}: {1}'.format(c.__name__, len(c.instances))

def create_blackboard_repository():
    # TODO
    global BLACKBOARD
    BLACKBOARD = Blackboard()

def delete_blackboard_repository():
    # TODO
    pass


# --------------------------------------------------------------------------

def test_bb():
    class __Test_Class_(Standard_Unit_Instance):
        """ Local test class to test inheritance with proper class-instances behavior """
        
    __Test_Class_()
    __Test_Class_('tu2')
    Standard_Unit_Instance()
    Standard_Unit_Instance('su2')



# --------------------------------------------------------------------------
# Trivial blackboard -- the following will be deleted as above matures...
# --------------------------------------------------------------------------

class KS_spec(object):
    """
    Contains the information about a KS needed by the control machinery.

    :param list object_types: object types of interest
    :param str ks_function: name of the function implementing the KS
    """
    global CREATION_EVENT_KSS
    def __init__(self, ks_type_name, object_types, ks_function):
        self.type_name = ks_type_name
        self.object_types = object_types
        self.ks_function = ks_function
        CREATION_EVENT_KSS.append(self)

class BB_object(object):
    """
    Contains the name and data of a blackboard object.
    """
    def __init__(self, name, data):
        self.name = name
        self.data = data
    def __repr__(self):
        return 'BB_object({0},{1})'.format(self.name, self.data)
    def __str__(self):
        return '<BB_object({0},{1})>'.format(self.name, self.data)

def reset_bb_system():
    """
    Resets the system to the initial state.
    """
    global BLACKBOARD, EVENTS, AGENDA
    BLACKBOARD = {}
    EVENTS = []
    AGENDA = []

def undefine_all_kss():
    """
    Removes all KS definitions
    """
    global CREATION_EVENT_KSS
    CREATION_EVENT_KSS = {}

def get_bb_object(name):
    """
    Trivial retrieval of blackboard object by name.
    'Name' must be a string.

    .. todo:: This is not actually used in the example below.

    Also, this _could_ be much more fancy kind of pattern-based lookup
    depending on the blackboard repository structure.
    """
    global BLACKBOARD
    return BLACKBOARD[name].data

def creation_event(bb_object):
    """
    Control component code for processing a creation event.
    Determines which KSs are interested in the event and adds them to the agenda.

    .. todo:: Does not evaluate the relative importance of activated KSs.
    """
    global CREATION_EVENT_KSS, AGENDA, TRACE_LEVEL
    
    bb_object_type = bb_object.type_name # bb_object.data.ks_type_name
    for ks_spec in CREATION_EVENT_KSS:
        if bb_object_type in ks_spec.object_types:
            ksa = ( ks_spec.ks_function, bb_object )
            if TRACE_LEVEL > 1:
                print "\tActivating {0}".format(ksa)
            AGENDA.append(ksa)

def signal_creation_event(bb_object):
    """
    Signals that 'bb_object' has been created.
    """
    global EVENTS
    EVENTS.append( (creation_event, bb_object.data) )

def make_bb_object(name, data):
    """
    Makes 'object' a blackboard object with name 'name' and signals a 
    creation event.  'Name' must be a string.

    :param str name: the name of the bb object
    :param str data: the bb object's data
    """
    global BLACKBOARD, TRACE_LEVEL
    bb_obj = BB_object(name, data)
    if TRACE_LEVEL > 2:
        print "\tCreating {0} object: {1}".format( type(data), bb_obj )
    BLACKBOARD[name] = bb_obj
    signal_creation_event(bb_obj)
    return bb_obj

EVENT_LIMIT = 10

def control_loop():
    """
    A trivial control loop.
    No opportunistic control is performed, simply LIFO stack (last-in, first-out) scheduling.
    The loop terminates when the agenda is empty.
    """
    global EVENTS, AGENDA, TRACE_LEVEL
    
    epoch = 0
    go = True
    while go:
        if TRACE_LEVEL > 0:
            print "[epoch {0}]".format(epoch)

        event_count = 0
        
        # process events
        for event in EVENTS:
            event_fn, event_data = event[0], event[1]
            if TRACE_LEVEL > 3:
                print "\t\tEvaluating event: ({0} {1})".format(event_fn, event_data)
            event_fn(event_data) # eval the function
            if TRACE_LEVEL > 3:
                print "\t\tEvent eval success."

            if event_count > EVENT_LIMIT:
                break
            event_count += 1
            
        EVENTS = []
        
        # check for stopping condition
        if AGENDA:
            # run the top KSA; LIFO stack agenda
            ksa = AGENDA.pop()
            if TRACE_LEVEL > 0:
                print "\tAGENDA Running: {0}".format(ksa)
            ksa_fn, ksa_data = ksa[0], ksa[1]
            if TRACE_LEVEL > 3:
                print "\t\tEvaluating KSA: ({0} {1})".format(ksa_fn, ksa_data)
            ksa_fn(ksa_data)
            if TRACE_LEVEL > 3:
                print "\t\tKSA eval success."
        else:
            go = False

        epoch += 1
    
    print("\n\nAgenda is empty.  Stopping.")


'''    
def test_def(fn_name):
    fn = lambda: "'{0}' is my name".format(fn_name)
    return fn_name, fn

def define_creation_ks(ks_name, obj_types, ks_function, docstring = None):
    """
    Define KSs interested in creation events.
    'ks_name'   : must be a string and is the name to be given to the 
                  created KS function.
    'obj_types' : is a list of the types of objects for which creation 
                  events are of interest to the KS.
    'ks_function' : 'arglist' and 'body'
                    the argument list and body of the ks function
    """
    CREATION_EVENT_KSS[ks_name] = KS_spec(obj_types, ks_function, docstring)
'''

# --------------------------------------------------------------------------
# A simple "blackboard" application that generates integer values,
# computes their squares, and prints the squares.
# --------------------------------------------------------------------------

"""
Specifies the last integer generated by the generate_integers KS.
"""
STOP_VALUE = 5

class Integer_object(object):
    """
    A blackboard object containing a generated integer.
    """
    type_name = 'Integer_object'
    def __init__(self, value):
        self.value = value
        self.square = None
    def __repr__(self):
        return 'Integer_object({0})'.format(self.value)
    def __str__(self):
        # print '<Integer_object {0}>'.format(self.value)
        return '<Integer_object {0}>'.format(self.value)

class Square_object(object):
    """
    A blackboard object containing a squared integer.
    """
    type_name = 'Square_object'
    def __init__(self, value, integer):
        self.value = value
        self.integer = integer
    def __repr__(self):
        return 'Square_object({0})'.format(self.value)
    def __str__(self):
        # print '<Square_object {0}>'.format(self.value)
        return '<Square_object {0}>'.format(self.value)

# --------------------------------------------------------------------------
# The KS Definitions:
# NOTE: Because the SBB control scheme implements a simple LIFO ordering and
#       the KSs interested in a single type of event are activated in the
#       order in which they appear in the CREATION_EVENT_KSS list, changing
#       the order of definitions below will change the behavior of the app
# NOTE: A bit of a HACK: I define the KS's 'type_name' in the inherited 
#       KS_spec and passing the 'type_name' value as self.__class__.__name__
# --------------------------------------------------------------------------

class Compute_Squares_KS(KS_spec):
    """ KS that computes the square of its 'bb_obj' argument. """
    def __init__(self):
        KS_spec.__init__(self, self.__class__.__name__, ( Integer_object.type_name, ), self)
    def __call__(self, bb_obj):
        value = bb_obj.value
        square_obj = Square_object(value * value, bb_obj)
        make_bb_object(gensym(), square_obj)
        bb_obj.square = square_obj

class Generate_Integers_KS(KS_spec):
    """ 
    KS that creates new Integer_objects with a value that is 1 larger
    than its 'bb_obj' argument.  Creation stops when the value exceeds 
    STOP_VALUE.
    """
    def __init__(self):
        KS_spec.__init__(self, self.__class__.__name__, ( Integer_object.type_name, ), self)
    def __call__(self, bb_obj):
        if bb_obj.value < STOP_VALUE:
            make_bb_object(gensym(), Integer_object(bb_obj.value + 1))

class Print_Squares_KS(KS_spec):
    """
    KS that prints the value of the created Square_object (contained
    in the 'bb_obj' argument).
    """
    def __init__(self):
        KS_spec.__init__(self, self.__class__.__name__, ( Square_object.type_name, ), self)
    def __call__(self, bb_obj):
        print "** Square: {0}".format(bb_obj.value)

# Instantiate KSs
Compute_Squares_KS()
Generate_Integers_KS()
Print_Squares_KS()

# --------------------------------------------------------------------------

def run_application():
    """
    The top-level application function that runs (and reruns) the simple
    BB application.
    """
    reset_bb_system()
    make_bb_object(gensym(), Integer_object(1))
    control_loop()

