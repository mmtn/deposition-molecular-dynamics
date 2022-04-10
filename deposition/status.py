from datetime import datetime as dt

import yaml

from deposition.enums import StatusEnum


class Status:
    """Track the status of the deposition calculation"""

    def __init__(
        self,
        iteration_number,
        sequential_failures,
        total_failures,
        pickle_location,
        last_updated=dt.now(),
    ):
        self.iteration_number = iteration_number
        self.sequential_failures = sequential_failures
        self.total_failures = total_failures
        self.pickle_location = pickle_location
        self.last_updated = last_updated

    def as_dict(self):
        return {
            StatusEnum.ITERATION_NUMBER.value: self.iteration_number,
            StatusEnum.SEQUENTIAL_FAILURES.value: self.sequential_failures,
            StatusEnum.TOTAL_FAILURES.value: self.total_failures,
            StatusEnum.PICKLE_LOCATION.value: self.pickle_location,
            StatusEnum.LAST_UPDATED.value: self.last_updated,
        }

    def write(self, filename):
        """
        Writes the current time, current iteration number, number of sequential
        failures, and the most recent saved state of the deposition simulation to
        `status.yaml`.
        """
        self.last_updated = dt.now()
        with open(filename, "w") as file:
            yaml.dump(self.as_dict(), file)

    @staticmethod
    def from_file(filename):
        """Reads the status from the given file"""
        try:
            with open(filename) as file:
                status = yaml.safe_load(file)
            return Status(
                int(status[StatusEnum.ITERATION_NUMBER.value]),
                int(status[StatusEnum.SEQUENTIAL_FAILURES.value]),
                int(status[StatusEnum.TOTAL_FAILURES.value]),
                str(status[StatusEnum.PICKLE_LOCATION.value]),
                status[StatusEnum.LAST_UPDATED.value],
            )
        except FileNotFoundError:
            raise FileNotFoundError(f"status file not found: {filename}")
