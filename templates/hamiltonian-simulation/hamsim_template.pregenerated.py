#!/usr/bin/env python
# coding: utf-8

# # Reducing the Trotter error of Hamiltonian dynamics with <span style="color:black">approximate quantum compilation</span>
#
# In this notebook, you will learn how to use **Approximate Quantum Compilation with Tensor Networks (AQC-Tensor)**.
#
# This notebook can be executed either directly or as a Qiskit Serverless program (see [accompanying notebook](serverless_demo.ipynb)).  In a few places it behaves differently based on how it is called (i.e., by branching on the value of `is_running_in_serverless()`).
#
# Our overall goal is to simulate time evolution of the above model Hamiltonian.  We do so by Trotter evolution, which we split into two portions:
#
# 1. An initial portion that is simulable with matrix product states (MPS).  We will "compile" this portion using AQC as presented in https://arxiv.org/abs/2301.08609.
# 2. A subsequent portion of the circuit that will be executed only on hardware.

# ### Set parameters for function template

# In[1]:


from qiskit_serverless import get_arguments, save_result, is_running_in_serverless


output = {}

if is_running_in_serverless():
    # Get the arguments passed to the program
    arguments = get_arguments()
else:
    # Use these arguments when running in a notebook
    arguments = {
        "dry_run": False,
        "backend_name": "ibm_fez",
        "aqc_evolution_time": 0.2,
        "aqc_ansatz_num_trotter_steps": 1,
        "aqc_target_num_trotter_steps": 32,
        "remainder_evolution_time": 0.2,
        "remainder_num_trotter_steps": 4,
    }


# ### Extract parameters from arguments
#
# We do this at the top of the notebook/program so we can fail early if any required arguments are missing.

# In[2]:


dry_run = arguments.get("dry_run", False)
backend_name = arguments["backend_name"]

aqc_evolution_time = arguments["aqc_evolution_time"]
aqc_ansatz_num_trotter_steps = arguments["aqc_ansatz_num_trotter_steps"]
aqc_target_num_trotter_steps = arguments["aqc_target_num_trotter_steps"]

remainder_evolution_time = arguments["remainder_evolution_time"]
remainder_num_trotter_steps = arguments["remainder_num_trotter_steps"]

aqc_stopping_fidelity = arguments.get(
    "aqc_stopping_fidelity", 1.0
)  # Stop if this fidelity is achieved
aqc_max_iterations = arguments.get(
    "aqc_max_iterations", 500
)  # Stop after this number of iterations, even if stopping fidelity is not achieved


# ### Perform parameter validation

# In[3]:


if not 0.0 < aqc_stopping_fidelity <= 1.0:
    raise ValueError(
        f"Invalid stopping fidelity: {aqc_stopping_fidelity} - must be positive float no greater than 1"
    )


# ### Configure ``EstimatorOptions``, to control the parameters of our hardware experiment
#
# For more information about the available execution options, see the [qiskit-ibm-runtime documentation](https://docs.quantum.ibm.com/api/qiskit-ibm-runtime/qiskit_ibm_runtime.options.EstimatorOptions).
#
# #### Set default options

# In[4]:


import numpy as np

estimator_default_options = {
    "resilience": {
        "measure_mitigation": True,
        "zne_mitigation": True,
        "zne": {
            "amplifier": "gate_folding",
            "noise_factors": [1, 2, 3],
            "extrapolated_noise_factors": list(np.linspace(0, 3, 31)),
            "extrapolator": ["exponential", "linear", "fallback"],
        },
        "measure_noise_learning": {
            "num_randomizations": 512,
            "shots_per_randomization": 512,
        },
    },
    "twirling": {
        "enable_gates": True,
        "enable_measure": True,
        "num_randomizations": 300,
        "shots_per_randomization": 100,
        "strategy": "active",
    },
}


# #### Merge with user-provided options

# In[5]:


import json
from mergedeep import merge

estimator_options = merge(
    arguments.get("estimator_options", {}), estimator_default_options
)

if is_running_in_serverless():
    print("estimator_options =", json.dumps(estimator_options, indent=4))


# ### Set up our Hamiltonian and observable
#
# If running as a Qiskit Serverless program, the user should have specified the Hamiltonian and observable, so we extract them from the arguments.

# In[6]:


from qiskit import QuantumCircuit

if is_running_in_serverless():
    hamiltonian = arguments["hamiltonian"]
    observable = arguments["observable"]
    initial_state = arguments.get(
        "initial_state", QuantumCircuit(hamiltonian.num_qubits)
    )


# Otherwise, i.e., for the purposes of this notebook, we use the XXZ model on a chain with open boundary conditions:
#
# $$
# \hat{\mathcal{H}}_{XXZ} = \sum_{i=1}^{L-1} J_{i,(i+1)}\left(X_i X_{(i+1)}+Y_i Y_{(i+1)}+ 2\cdot Z_i Z_{(i+1)} \right) \, ,
# $$
#
# where $J_{i,(i+1)}$ is a random coefficient corresponding to edge $(i, i+1)$

# In[7]:


from qiskit.quantum_info import SparsePauliOp, Pauli
from qiskit.transpiler import CouplingMap
from rustworkx.visualization import graphviz_draw

if not is_running_in_serverless():
    L = 50  # L = length of our 1D spin chain

    # Generate the edge-list for this spin-chain
    elist = [(i - 1, i) for i in range(1, L)]
    # Generate an edge-coloring so we can make hw-efficient circuits
    even_edges = elist[::2]
    odd_edges = elist[1::2]

    # Instantiate a CouplingMap object
    coupling_map = CouplingMap(elist)
    graphviz_draw(coupling_map.graph, method="circo")

    # Generate random coefficients for our XXZ Hamiltonian
    np.random.seed(0)
    Js = np.random.rand(L - 1) + 0.5 * np.ones(L - 1)

    hamiltonian = SparsePauliOp(Pauli("I" * L))
    for i, edge in enumerate(even_edges + odd_edges):
        hamiltonian += SparsePauliOp.from_sparse_list(
            [
                ("XX", (edge), Js[i] / 2),
                ("YY", (edge), Js[i] / 2),
                ("ZZ", (edge), Js[i]),
            ],
            num_qubits=L,
        )

    observable = SparsePauliOp.from_sparse_list(
        [("ZZ", (L // 2 - 1, L // 2), 1.0)], num_qubits=L
    )


# In[8]:


print("Hamiltonian:", hamiltonian)


# In[9]:


print("Observable:", observable)


# ## Step 1: Map to quantum problem

# ### Generate an initial state

# In[10]:


if not is_running_in_serverless():
    print("Initializing to Neel state")
    L = hamiltonian.num_qubits
    # Generate an initial state
    initial_state = QuantumCircuit(L)
    for i in range(L):
        if i % 2:
            initial_state.x(i)


# ### Construct the AQC target circuit
#
# Because this is being simulated by a tensor-network simulator, the number of layers affects execution time only by a constant factor, so we might as well use a generous number of layers to minimize Trotter error.

# In[11]:


from qiskit.synthesis import SuzukiTrotter
from qiskit_addon_utils.problem_generators import generate_time_evolution_circuit

aqc_target_circuit = initial_state.copy()
if aqc_evolution_time:
    aqc_target_circuit.compose(
        generate_time_evolution_circuit(
            hamiltonian,
            synthesis=SuzukiTrotter(reps=aqc_target_num_trotter_steps),
            time=aqc_evolution_time,
        ),
        inplace=True,
    )


# ### Generate an ansatz and initial parameters from a Trotter circuit with fewer steps
#
# First, we construct a "good" circuit that has the same evolution time as the target circuit, but with fewer Trotter steps (and thus fewer layers).
#
# Then we pass this "good" circuit to AQC-Tensor's `generate_ansatz_from_circuit` function.  This function analyzes the two-qubit connectivity of the circuit and returns two things:
# 1. a general, parametrized ansatz circuit with the same two-qubit connectivity as the input circuit; and,
# 2. parameters that, when plugged into the ansatz, yield the input (good) circuit.
#
# Soon we will take these parameters and iteratively adjust them to bring the ansatz circuit as close as possible to the target MPS.

# In[12]:


from qiskit_addon_aqc_tensor.ansatz_generation import (
    generate_ansatz_from_circuit,
    AnsatzBlock,
)

aqc_good_circuit = initial_state.copy()
if aqc_evolution_time:
    aqc_good_circuit.compose(
        generate_time_evolution_circuit(
            hamiltonian,
            synthesis=SuzukiTrotter(reps=aqc_ansatz_num_trotter_steps),
            time=aqc_evolution_time,
        ),
        inplace=True,
    )

aqc_ansatz, aqc_initial_parameters = generate_ansatz_from_circuit(aqc_good_circuit)
print("Number of AQC parameters:", len(aqc_initial_parameters))
output["num_aqc_parameters"] = len(aqc_initial_parameters)


# ### Choose settings for tensor network simulation
#
# Here, we use Quimb's matrix-product state (MPS) circuit simulator, along with [jax](https://github.com/jax-ml/jax) for providing the gradient.

# In[13]:


if is_running_in_serverless():
    import os

    os.environ["NUMBA_CACHE_DIR"] = "/data"

import quimb.tensor

from qiskit_addon_aqc_tensor.simulation.quimb import QuimbSimulator

simulator_settings = QuimbSimulator(quimb.tensor.CircuitMPS, autodiff_backend="jax")


# ### Construct matrix-product state representation of the AQC target state
#
# Next, we build a matrix-product representation of the state to be approximated by AQC.

# In[14]:


from qiskit_addon_aqc_tensor.simulation import tensornetwork_from_circuit

aqc_target_mps = tensornetwork_from_circuit(aqc_target_circuit, simulator_settings)
print("Target MPS maximum bond dimension:", aqc_target_mps.psi.max_bond())
output["target_bond_dimension"] = aqc_target_mps.psi.max_bond()


# ### Calculate fidelity of ansatz circuit vs. the target state, before optimization
#
# We can calculate the fidelity ($|\langle \psi_1 | \psi_2 \rangle|^2$) of the state prepared by the ansatz circuit vs. the target state:

# In[15]:


from qiskit_addon_aqc_tensor.simulation import compute_overlap

good_mps = tensornetwork_from_circuit(aqc_good_circuit, simulator_settings)
starting_fidelity = abs(compute_overlap(good_mps, aqc_target_mps)) ** 2
print("Starting fidelity of AQC portion:", starting_fidelity)
output["aqc_starting_fidelity"] = starting_fidelity


# ### Optimize the parameters of the ansatz using MPS calculations
#
# Here, we minimize the simplest possible cost function, `OneMinusFidelity`, by using the L-BFGS optimizer from scipy.

# In[16]:


import datetime
from scipy.optimize import OptimizeResult, minimize

from qiskit_addon_aqc_tensor.objective import OneMinusFidelity

objective = OneMinusFidelity(aqc_target_mps, aqc_ansatz, simulator_settings)

stopping_point = 1.0 - aqc_stopping_fidelity


def callback(intermediate_result: OptimizeResult):
    fidelity = 1 - intermediate_result.fun
    print(f"{datetime.datetime.now()} Intermediate result: Fidelity {fidelity:.8f}")
    if intermediate_result.fun < stopping_point:
        # Good enough for now
        raise StopIteration


result = minimize(
    objective,
    aqc_initial_parameters,
    method="L-BFGS-B",
    jac=True,
    options={"maxiter": aqc_max_iterations},
    callback=callback,
)
if result.status not in (
    0,
    1,
    99,
):  # 0 => success; 1 => max iterations reached; 99 => early termination via StopIteration
    raise RuntimeError(
        f"Optimization failed: {result.message} (status={result.status})"
    )

print(f"Done after {result.nit} iterations.")
output["num_iterations"] = result.nit
aqc_final_parameters = result.x


# In[17]:


output["aqc_final_parameters"] = list(aqc_final_parameters)


# ### Construct optimized circuit for initial portion of time evolution
#
# At this point, it is only necessary to find the final parameters to the ansatz circuit.

# In[18]:


aqc_final_circuit = aqc_ansatz.assign_parameters(aqc_final_parameters)


# ### Calculate fidelity after optimization

# In[19]:


aqc_final_mps = tensornetwork_from_circuit(aqc_final_circuit, simulator_settings)
aqc_fidelity = abs(compute_overlap(aqc_final_mps, aqc_target_mps)) ** 2
print("Fidelity of AQC portion:", aqc_fidelity)
output["aqc_fidelity"] = aqc_fidelity


# ### Construct final circuit, with remainder of time evolution

# In[20]:


final_circuit = aqc_final_circuit.copy()
if remainder_evolution_time:
    remainder_circuit = generate_time_evolution_circuit(
        hamiltonian,
        synthesis=SuzukiTrotter(reps=remainder_num_trotter_steps),
        time=remainder_evolution_time,
    )
    final_circuit.compose(remainder_circuit, inplace=True)


# ## Step 2: Transpile circuits into ISA Circuits

# #### Transpile PUBs (circuits and observables) to match the backend ISA (Instruction Set Architecture)
# By selecting `optimization_level=3`, the transpiler will choose a 1D chain of qubits which minimizes the noise affecting our circuit. Once we have converted our circuits into the format that the backend is prepared to accept, we will apply a complimentary transformation to our observables as well.

# In[21]:


from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

service = QiskitRuntimeService()
backend = service.backend(backend_name)

# Transpile pubs (circuits and observables) to match ISA
pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=3)
isa_circuit = pass_manager.run(final_circuit)
isa_observable = observable.apply_layout(isa_circuit.layout)


# In[22]:


isa_2qubit_depth = isa_circuit.depth(lambda x: x.operation.num_qubits == 2)
print("ISA circuit two-qubit depth:", isa_2qubit_depth)
output["twoqubit_depth"] = isa_2qubit_depth


# In[23]:


if dry_run:
    import sys

    print("Aborting before hardware execution since `dry_run` is True.")
    if is_running_in_serverless():
        save_result(output)
    sys.exit(0)


# ## Step 3: Execute quantum experiments on backend

# #### Execute experiments / load previous results from disk
# Here is where we would initiate our experiments through runtime, however, for the purposes of this demo, we will instead be loading previously run results from disk.

# In[24]:


from pathlib import Path
import dill
from qiskit_ibm_runtime import EstimatorV2 as Estimator


perform_hw_expt = False
hw_results_filename = "hw_results_aqc.pkl"

if perform_hw_expt or is_running_in_serverless():
    estimator = Estimator(backend, options=estimator_options)

    # Submit job
    job = estimator.run([(isa_circuit, isa_observable)])
    print("Job ID:", job.job_id())
    output["job_id"] = job.job_id()

    # Wait until job is complete
    hw_results = job.result()
    hw_results_dicts = [pub_result.data.__dict__ for pub_result in hw_results]

    # Save results to disk
    Path(hw_results_filename).parent.mkdir(parents=True, exist_ok=True)
    with open(hw_results_filename, "wb") as f:
        dill.dump([hw_results_dicts, estimator_options], f)


# In[25]:


# Load results from disk
with open(hw_results_filename, "rb") as f:
    hw_results_dicts, estimator_options = dill.load(f)

# Save hardware results to serverless
output["hw_results"] = hw_results_dicts

# Re-organize expectation values
hw_expvals = [pub_result_data["evs"].tolist() for pub_result_data in hw_results_dicts]

# Save expectation values to serverless
print("Hardware expectation values", hw_expvals)
output["hw_expvals"] = hw_expvals[0]


# ## Step 4: Report expectation value
#
# Now we can compare the expectation value with its exact result for the parameters if running this notebook directly.

# In[26]:


if not is_running_in_serverless():
    # This comes from a tensor network calculation,
    ref_expval = -0.5887
    print(f"Exact:\t\t{ref_expval:.4f}")
    print(f"AQC:\t{hw_expvals[0]:.4f}, |∆| = {np.abs(ref_expval - hw_expvals[0]):.4f}")


# Or, if it's a serverless program, save the result.

# In[27]:


if is_running_in_serverless():
    save_result(output)
