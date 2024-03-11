from __future__ import annotations

import itertools
import random
from collections import deque
from datetime import datetime, timedelta
from enum import Enum
from typing import Generator, Callable

from scaling_time_options import ScalingTimeOptions
from service_instance_state import ServiceInstanceState
from target_service_instance import TargetServiceInstance


class TargetService:
    def __init__(
            self,
            current_time: datetime,
            applied_load: float,
            scale_up_time: ScalingTimeOptions,
            scale_down_time: ScalingTimeOptions,
            starting_instances: int = 0,
            ready_instances: int = 0,
            instance_load: float = 1,
            instance_baseline_load: float = 0.05,
            starting_load: float = 1,
            terminating_load: float = 1
    ):
        """
        Constructor for the target service class. Initializes the class with a
        specified current time, scaling times and starting/ready instances.
        :param current_time: The current simulated time.
        :param scale_up_time: Options specifying how long starting a new instance
        takes.
        :param scale_down_time: Options specifying how long terminating an instance
        takes.
        :param starting_instances: The number of already starting instances.
        :param ready_instances: The number of already ready instances.
        :param instance_load: How much load one instance of the service can handle.
        :param instance_baseline_load: The baseline load one instance of the service
        applies to the system without doing any work.
        :param starting_load: How much load an instance experiences during startup.
        During startup, an instance does not do any work and therefore does not
        contribute towards lowering the applied system load, but does still use
        system resources to load and initialize dependencies. This number specifies
        the load applied (i.e. resources used) by the instance uses when in this
        state.
        :param terminating_load: How much load an instance experiences during
        termination. During termination, an instance does not do any work and
        therefore does not contribute towards lowering the applied system load, but
        does still use system resources to shut down safely. This number specifies
        the load applied (i.e. resources used) by this instance when in this state.
        """
        self.current_time: datetime = current_time
        self.applied_load: float = applied_load
        self.scale_up_time: ScalingTimeOptions = scale_up_time
        self.scale_down_time: ScalingTimeOptions = scale_down_time
        self.instance_load_capability: float = instance_load
        self.instance_baseline_load: float = instance_baseline_load
        self.starting_load: float = starting_load
        self.terminating_load: float = terminating_load
        self.experienced_load: float = 0
        self.processed_load: float = 0

        starting = [
            TargetServiceInstance.start_new(
                current_time,
                scale_up_time,
                self.instance_load_capability
            )
            for _ in range(starting_instances)
        ]

        ready = [
            TargetServiceInstance(
                current_time=current_time,
                started_time=current_time,
                ready_time=current_time,
                handled_load=self.instance_load_capability
            )
            for _ in range(ready_instances)
        ]

        self.instances: deque[TargetServiceInstance] = deque(starting + ready)
        self.counts: dict[ServiceInstanceState, int] = {
            state: self.count(state)
            for state in ServiceInstanceState
        }

        self.total_load_capability: float = sum(
            instance.load_capability \
            for instance in self.instances \
            if instance.state == ServiceInstanceState.READY
        )

    def count(self, state: ServiceInstanceState):
        """
        Counts the current number of services of a specified state.
        :param state: The state to count service instances of.
        :return: The number of instances of the service with the specified state.
        """
        return sum(1 for instance in self.instances if instance.state == state)

    def get_victims(
            self,
            count: int
    ) -> Generator[TargetServiceInstance, None, None]:
        """
        Get the most viable instances to be terminated. Starts off by terminating
        starting instances in order of start time, i.e. newest instances are
        returned first. Then, ready (running) instances are returned in the same
        order, where younger instances are returned first.
        :param count: The number of instances to return
        :return: A generator yielding the victim instances in the mentioned order.
        """
        starting = sorted(
            filter(
                lambda instance: instance.state == ServiceInstanceState.STARTING,
                self.instances
            ),
            key=lambda instance: instance.started_time
        )

        running = sorted(
            filter(
                lambda instance: instance.state == ServiceInstanceState.READY,
                self.instances
            ),
            key=lambda instance: instance.ready_time
        )

        yield from itertools.islice(
            itertools.chain(
                starting,
                running
            ),
            count
        )

    def cleanup(self):
        """
        Remove instances in the OFF state from the instance list.
        :return:
        """
        off_instances = list(filter(
            lambda instance: instance.state == ServiceInstanceState.OFF,
            self.instances
        ))

        for off_instance in off_instances:
            self.instances.remove(off_instance)

    def _calculate_experienced_load(self):
        """
        Get the total and processed loads.
        :return: A tuple of the total load, and the processed load. The total load is
        the resource utilization of the system, while the processed load is how much
        of the applied load the system is able to process.
        """
        constant_loads = {
            ServiceInstanceState.STARTING: self.starting_load,
            ServiceInstanceState.READY: self.instance_baseline_load,
            ServiceInstanceState.TERMINATING: self.terminating_load
        }

        total_load = 0.
        total_load_capability = 0

        for instance in self.instances:
            constant_load = constant_loads.get(instance.state)
            if constant_load is None:
                constant_load = 0

            total_load += constant_load

            if instance.state == ServiceInstanceState.READY:
                total_load_capability += instance.load_capability - constant_load

        # We cant process more load than we have capability for. Therefore, disregard
        # any applied load exceeding the current processing capability
        processed_load = min(self.applied_load, total_load_capability)
        total_load += processed_load

        return total_load, processed_load, total_load_capability

    def update(self, current_time: datetime, applied_load: float,
               delta_instances: int | Callable[[TargetService], int]):
        """
        Updates the instances of the service with the current time, and scales the
        system if necessary.
        :param current_time: The current simulated time.
        :param applied_load: The current load applied to the system.
        :param delta_instances: The number of instances to add/remove, or a function
        receiving this class instance that returns the number of instances to
        add/remove. A negative number means that instances are removed, i.e. the
        system is scaled down. A positive number instead scales the system up. Note
        that it takes time to scale the system, this parameter only initiates the
        desired scaling.
        :return:
        """
        self.current_time = current_time
        self.applied_load = applied_load

        # Update all running instances with the current time
        for instance in self.instances:
            instance.update(current_time)

        # Calculate the experienced and processed loads
        self.experienced_load, self.processed_load, self.total_load_capability = \
            self._calculate_experienced_load()

        if not isinstance(delta_instances, int):
            delta_instances = delta_instances(self)

        # If we need to scale down, find some victims and terminate them
        if delta_instances < 0:
            victims = self.get_victims(abs(delta_instances))

            for victim in victims:
                victim.terminate(self.scale_down_time)
        elif delta_instances > 0:
            # If we need to scale up, add some new instances
            self.instances.appendleft(TargetServiceInstance.start_new(
                current_time=current_time,
                handled_load=self.instance_load_capability,
                options=self.scale_up_time
            ))

        # Update the state of all running instances to reflect the current time
        for state in ServiceInstanceState:
            self.counts[state] = self.count(state)

        # Remove instances in the OFF state
        self.cleanup()
