import numpy as np
import pytest

from deposition import enums, postprocessing, state

NUM_ATOMS = 20

TEST_STATE = state.State(
    coordinates=np.transpose(np.tile(np.arange(0, 20), [3, 1])),
    elements=["H" for _ in range(NUM_ATOMS)],
    velocities=np.zeros((NUM_ATOMS, 3)),
)

SIMULATION_CELL_ORTHOGONAL = {
    enums.SimulationCellEnum.A.value: 10.0,
    enums.SimulationCellEnum.B.value: 10.0,
    enums.SimulationCellEnum.C.value: 10.0,
    enums.SimulationCellEnum.ALPHA.value: 90.0,
    enums.SimulationCellEnum.BETA.value: 90.0,
    enums.SimulationCellEnum.GAMMA.value: 90.0,
}

SIMULATION_CELL_NONORTHOGONAL = {
    enums.SimulationCellEnum.A.value: 10.0,
    enums.SimulationCellEnum.B.value: 10.0,
    enums.SimulationCellEnum.C.value: 10.0,
    enums.SimulationCellEnum.ALPHA.value: 90.0,
    enums.SimulationCellEnum.BETA.value: 120.0,
    enums.SimulationCellEnum.GAMMA.value: 120.0,
}


@pytest.mark.parametrize("routine", postprocessing.PostProcessingEnum)
@pytest.mark.parametrize(
    "simulation_cell", [SIMULATION_CELL_ORTHOGONAL, SIMULATION_CELL_NONORTHOGONAL]
)
def test_routines_return_state(routine, simulation_cell):
    result = postprocessing.run(routine.name, TEST_STATE, simulation_cell)
    assert type(result) is state.State
