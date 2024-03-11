from enum import Enum


class ServiceInstanceState(Enum):
    """
    Enum of the different states of a service instance.
    """

    """
    Pending specifies that an instance has been created, but not yet started. An 
    instance in this state consumes no resources.
    """
    PENDING = 0

    """
    Starting specifies that an instance has been started, and is currently in the 
    starting phase. Hence, the instance is not yet capable of doing any work, but 
    will soon be. An instance in this state consumes resources, for example by 
    loading and initializing its dependencies.
    """
    STARTING = 1

    """
    The ready state specifies that an instance has been successfully started and that 
    the instance is ready to work. An instance in this state consumes resources.
    """
    READY = 2

    """
    The terminating state specifies that an instance is currently being terminated, 
    and is therefore shutting down. An instance cannot do any work in this state. 
    An instance in this state still consumes resources though, as it needs to safely 
    shut down, potentially save data and close connections.
    """
    TERMINATING = 3

    """
    The off state specifies that an instance is completely off, i.e. does not do any
    work and no longer consumes any resources.
    """
    OFF = 4