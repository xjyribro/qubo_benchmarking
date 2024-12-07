from dataclasses import dataclass
from amplify import solve
from model import create_qap_qp_model
import numpy as np

import time
import sys
import os
from math import ceil

# Add the project root directory to sys.path
if True:
    sys.path.append(os.path.abspath('..'))

print(os.getcwd())

# Prevent autopep8
if True:
    from Utils.graph import generate_random_symmetric_matrix
    from Utils.solvers import GetFixstarClient, GetGurobiClient, GetDWaveClient


@dataclass
class CompareResult:
    """Result of QAP Run"""

    nodes: int
    max_edge_weight: int
    avg_edge_weight: float

    distance_matrix: list[list[int]]
    interaction_matrix: list[list[int]]
    qp_weight: int

    time_model_formulation: float

    gurobi_objective: float | None
    gurobi_execution_time: float | None

    fixstars_objective: float | None
    fixstars_execution_time: float | None

    dwave_objective: float | None
    dwave_execution_time: float | None


def run_compare_solvers(
        nodes: int,
        max_edge_weight: int
):
    create_model_start = time.time()

    distance_matrix = generate_random_symmetric_matrix(
        nodes, 1, max_edge_weight)
    interaction_matrix = generate_random_symmetric_matrix(
        nodes, 1, max_edge_weight)

    avg_edge_weight = float(
        (np.average(distance_matrix) + np.average(interaction_matrix)) / 2)

    qp_weight = max(1_000_000, ceil(2 * avg_edge_weight * nodes ** 4))

    qp_model = create_qap_qp_model(
        distance_matrix, interaction_matrix, qp_weight)
    create_model_end = time.time()

    time_model_formulation = create_model_end - create_model_start

    # Gurobi

    clientG = GetGurobiClient()
    gurobi_objective = None
    gurobi_execution_time = None
    try:
        resultG = solve(qp_model["model"], clientG)
        gurobi_objective = resultG.best.objective
        gurobi_execution_time = resultG.execution_time.total_seconds()
    except:
        pass

    # Fixstars

    clientFS = GetFixstarClient()
    fixstars_objective = None
    fixstars_execution_time = None
    try:
        resultFS = solve(qp_model["model"], clientFS)
        fixstars_objective = resultFS.best.objective
        fixstars_execution_time = resultFS.execution_time.total_seconds()
    except:
        pass

    # DWave

    clientDWave = GetDWaveClient()
    dwave_objective = None
    dwave_execution_time = None
    try:
        resultDWave = solve(qp_model["model"], clientDWave)
        dwave_objective = resultDWave.best.objective
        dwave_execution_time = resultDWave.execution_time.total_seconds()
    except:
        pass

    return CompareResult(
        nodes=nodes,
        max_edge_weight=max_edge_weight,
        avg_edge_weight=avg_edge_weight,
        distance_matrix=distance_matrix,
        interaction_matrix=interaction_matrix,
        qp_weight=qp_weight,
        time_model_formulation=time_model_formulation,
        gurobi_objective=gurobi_objective,
        gurobi_execution_time=gurobi_execution_time,
        fixstars_objective=fixstars_objective,
        fixstars_execution_time=fixstars_execution_time,
        dwave_objective=dwave_objective,
        dwave_execution_time=dwave_execution_time
    )
