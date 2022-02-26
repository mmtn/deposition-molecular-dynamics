import pytest
from deposition import distributions

POLYGON_COORDINATES = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
Z_PLANE = 5.0


@pytest.mark.parametrize("distribution", distributions.PositionDistributionEnum)
def test_position_distributions(distribution):
    distribution_class = distributions.get_position_distribution(
        distribution.name, POLYGON_COORDINATES, Z_PLANE
    )
    position = distribution_class.get_position()
    assert type(position) is tuple
    for value in position:
        assert type(value) is float


@pytest.mark.parametrize("distribution", distributions.VelocityDistributionEnum)
def test_velocity_distributions(distribution):
    distribution_class = distributions.get_velocity_distribution(distribution.name)
    velocity = distribution_class.get_velocity()
    assert type(velocity) is tuple
    for value in velocity:
        assert type(value) is float
