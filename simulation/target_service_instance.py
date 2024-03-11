from __future__ import annotations
from datetime import datetime

from scaling_time_options import ScalingTimeOptions
from service_instance_state import ServiceInstanceState


class TargetServiceInstance:
    def __init__(
            self,
            current_time: datetime,
            handled_load: float,
            started_time: datetime | None = None,
            ready_time: datetime | None = None,
            terminated_time: datetime | None = None,
            off_time: datetime | None = None
    ):
        """
        Constructs a new instance of the TargetServiceInstance class.
        :param current_time: The current simulated time
        :param handled_load: The total load this instance is capable of processing.
        :param started_time: The time for when this instance was started, i.e.
        entered the STARTING state.
        :param ready_time: The time for when this ínstance was ready, i.e. entered
        the READY state.
        :param terminated_time: The time for when this instance was terminated, i.e.
        entered the TERMINATING state.
        :param off_time: The time for when this instance enterd the OFF state.
        """
        self.load_capability: float = handled_load
        self.started_time: datetime | None = started_time
        self.ready_time: datetime | None = ready_time
        self.terminate_time: datetime | None = terminated_time
        self.off_time: datetime | None = off_time
        self.state: ServiceInstanceState = ServiceInstanceState.PENDING
        self.current_time: datetime = current_time

    @property
    def current_time(self) -> datetime:
        return self._current_time

    @current_time.setter
    def current_time(self, new_time: datetime):
        self._current_time = new_time
        self.state = self._get_state()

    @staticmethod
    def start_new(
            current_time: datetime,
            options: ScalingTimeOptions,
            handled_load: float
    ) -> TargetServiceInstance:
        """
        Create a new instance, in the STARTING state.
        :param current_time: The current simulated time
        :param options: Options specifying how quickly the instance is started.
        :param handled_load: The load this instance is capable of processing.
        :return: The newly created instance
        """
        start_time = current_time
        ready_time = options.random(start_time=current_time)

        return TargetServiceInstance(
            current_time=current_time,
            started_time=start_time,
            ready_time=ready_time,
            handled_load=handled_load
        )

    def update(self, current_time: datetime):
        """
        Updates the instance with a new simulated time. The instances state is
        updated accordingly.
        :param current_time: The new simulated time to update the instance with
        :return:
        """
        self.current_time = current_time

    def start(self, options: ScalingTimeOptions):
        """
        Starts the instance if not already started.
        :param options: Options specifying how much time starting the instance takes.
        :return:
        """
        if self.started_time is not None:
            raise Exception('Service instance is already started.')

        self.started_time = self.current_time
        self.ready_time = options.random(start_time=self.current_time)

    def terminate(self, terminate_time: ScalingTimeOptions):
        """
        Terminates the service instance if not already terminated.
        :param terminate_time: Options specifying how much time terminating the
        instance takes.
        :return:
        """
        if self.terminate_time is not None:
            raise Exception('Service instance is already terminated.')

        self.terminate_time = self.current_time
        self.off_time = terminate_time.random(start_time=self.current_time)

    def _get_state(self) -> ServiceInstanceState:
        """
        Determine the current state of the instance based on the current time.
        :return: The current state of the instance
        """
        props = [
            (ServiceInstanceState.STARTING, self.started_time),
            (ServiceInstanceState.READY, self.ready_time),
            (ServiceInstanceState.TERMINATING, self.terminate_time),
            (ServiceInstanceState.OFF, self.off_time)
        ]

        last_state = ServiceInstanceState.PENDING
        for state, time in props:
            if time is None or self._current_time < time:
                continue

            last_state = state

        return last_state