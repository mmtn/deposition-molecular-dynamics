import inspect

import pytest
from deposition.drivers import driver_enums


@pytest.mark.parametrize("driver", driver_enums.DriverEnum)
@pytest.mark.parametrize("method", ["write_inputs", "read_outputs"])
def test_drivers_provide_method(driver, method):
    assert method in driver.value.__dict__.keys()


@pytest.mark.parametrize("driver", driver_enums.DriverEnum)
@pytest.mark.parametrize(
    ["method", "expected"], [["write_inputs", 4], ["read_outputs", 1]]
)
def test_method_signatures(driver, method, expected):
    method_to_run = getattr(driver.value, method)
    assert (
        len(inspect.signature(method_to_run).parameters) == expected
    ), f"{method_to_run} does not have correct number of arguments"
