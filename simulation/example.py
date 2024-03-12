import math
import sys
from datetime import datetime, timedelta

from matplotlib import pyplot as plt

from scaling_time_options import ScalingTimeOptions
from service_instance_state import ServiceInstanceState
from target_service import TargetService

SCALE_UP_TIME = ScalingTimeOptions(mean_time=10, std_dev=5)
SCALE_DOWN_TIME = ScalingTimeOptions(mean_time=10, std_dev=5)

# If the desired service instance load is 0.5, no scaling will be done if the current
# average instance load is within this threshold of 0.5, i.e. 0.3 to 0.7
SCALING_THRESHOLD = 0.2

# The minutes of the simulation
SIMULATION_MINUTES = 35

# Generate a peak every 5 minutes
PEAK_FREQUENCY = 60 * 5

# A peak is present half the time
PEAK_DIVISOR = 2

# Peak phase, change to 0 for the start to be a peak
PEAK_PHASE = 1

# The applied load during a peak
HIGH_LOAD = 10

# The applied load when there is no peak
LOW_LOAD = 0.2


def calculate_instances(
        service: TargetService
) -> int:
    processed_load = service.processed_load
    process_capability = service.total_load_capability

    process_utilization = 0 if processed_load == 0 else \
        processed_load / process_capability

    desired_mean_load = 0.5
    upper_threshold = desired_mean_load + SCALING_THRESHOLD
    lower_threshold = desired_mean_load - SCALING_THRESHOLD

    if lower_threshold < process_utilization < upper_threshold:
        return 0

    scaling_factor = process_utilization / desired_mean_load
    current_instances = service.count(ServiceInstanceState.READY)
    starting_instances = service.count(ServiceInstanceState.STARTING)
    terminating_instances = service.count(ServiceInstanceState.TERMINATING)

    down_instances = math.ceil(
        (current_instances - terminating_instances) * scaling_factor
    )

    up_instances = math.ceil(
        (current_instances + starting_instances) * scaling_factor
    )

    if scaling_factor > 1:
        return up_instances
    elif current_instances - down_instances > 0:
        return -down_instances

    return 0


def plot_loads(
        minutes: list[int],
        applied_loads: list[float],
        experienced_loads: list[float],
        total_instances: list[int],
        ready_instances: list[int]
):
    fig, ax = plt.subplots()
    ax2 = ax.twinx()

    lines = []
    lines.extend(ax2.plot(minutes, ready_instances, '-', label='Ready instances'))
    # lines.extend(ax2.plot(minutes, total_instances, label='Total instances'))
    lines.extend(ax.plot(minutes, experienced_loads, '-r', label='Experienced load'))
    lines.extend(ax.plot(minutes, applied_loads, '-g', label='Applied load'))

    ax.set(xlabel='Time (minutes)', ylabel='Load', title='System load')
    ax2.set(ylabel='Instances')
    ax.grid()
    ax.legend(lines, [line.get_label() for line in lines], loc=0)
    ax2.set_ylabel('Instances')

    plt.savefig('example-result.png')

    if '--show' in sys.argv[1:]:
        plt.show()


def simulate_run():
    # High load for a minute every 5 minutes
    per_second_loads = [
        HIGH_LOAD if (i // PEAK_FREQUENCY) % PEAK_DIVISOR == PEAK_PHASE else LOW_LOAD
        for i in range(SIMULATION_MINUTES * 60)
    ]

    current_time = datetime.now()
    step = timedelta(seconds=1)

    service = TargetService(
        current_time=current_time,
        applied_load=per_second_loads[0],
        scale_up_time=SCALE_UP_TIME,
        scale_down_time=SCALE_DOWN_TIME,
        ready_instances=1
    )

    experienced_loads = []
    ready_instances = []
    instances = []

    for load in per_second_loads:
        current_time += step
        service.update(
            current_time=current_time,
            applied_load=load,
            delta_instances=calculate_instances
        )

        experienced_loads.append(service.experienced_load)
        ready_instances.append(service.count(ServiceInstanceState.READY))
        instances.append(len(service.instances))

    minutes = [
        i / 60
        for i in range(SIMULATION_MINUTES * 60)
    ]

    return minutes, per_second_loads, experienced_loads, instances, ready_instances


def main():
    args = simulate_run()
    plot_loads(*args)


if __name__ == '__main__':
    main()
