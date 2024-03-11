import random
from datetime import timedelta, datetime


class ScalingTimeOptions:
    def __init__(self, mean_time: float, std_dev: float):
        self.mean_time: float = mean_time
        self.std_dev: float = std_dev

    def random(self, start_time: datetime | None = None) -> float | datetime:
        """
        Randomize a new time based on the mean and standard deviation of this
        options instance.
        :param start_time: A starting time to add the randomized time to.
        :return: The start time with the randomized time added if a start time is
        specified. Otherwise a float of the number of generated seconds is returned.
        """
        dt = max(
            0.,
            random.normalvariate(
                mu=self.mean_time,
                sigma=self.std_dev
            )
        )

        return dt if start_time is None else start_time + timedelta(seconds=dt)
