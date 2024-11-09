# This code is a Qiskit project.
#
# (C) Copyright IBM 2024.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

import json
import os
import subprocess
import sys
import pytest

from qiskit.quantum_info import SparsePauliOp


@pytest.fixture
def hamsim_script(tmpdir, scope="module") -> str:
    """Create script from notebook."""
    from nbconvert.exporters import ScriptExporter

    notebook_filename = os.path.join(os.path.dirname(__file__), "hamsim_template.ipynb")
    script, script_info = ScriptExporter().from_filename(notebook_filename)
    script_name = script_info["metadata"]["name"]
    script_file = tmpdir / (script_name + script_info["output_extension"])
    with script_file.open("w", encoding="utf-8") as f:
        f.write(script)
    return str(script_file)


def run_program(program, arguments, tmpdir):
    """Run a serverless program in a mock environment."""
    from qiskit_serverless.serializers.program_serializers import QiskitObjectsEncoder

    with open(tmpdir / "arguments.serverless", "w", encoding="utf-8") as f:
        json.dump(arguments, f, cls=QiskitObjectsEncoder)
    cp = subprocess.run(
        [sys.executable, program],
        env={"ENV_JOB_ID_GATEWAY": "something-anything", **os.environ},
        cwd=str(tmpdir),
        stdout=sys.stdout,
        stderr=subprocess.STDOUT,
        check=True,
    )


def run_hamsim(hamsim_script, tmpdir, **kwargs):
    run_program(hamsim_script, {"dry_run": True, **kwargs}, tmpdir)


def test_invalid_stopping_fidelity(hamsim_script, tmpdir):
    with pytest.raises(subprocess.CalledProcessError):
        run_hamsim(hamsim_script, tmpdir, aqc_stopping_fidelity=1.1)


def test_dry_run(hamsim_script, tmpdir):
    with pytest.raises(subprocess.CalledProcessError):
        # FIXME: This is in a pytest.raises block because the program fails
        # when it is about to transpile to hardware.  It'd be nice to fix this
        # somehow.
        hamiltonian = SparsePauliOp.from_sparse_list(
            [("XX", (i, i + 1), 1.0) for i in range(3)], num_qubits=4
        ) + SparsePauliOp.from_sparse_list(
            [("YY", (i, i + 1), 1.0) for i in range(3)], num_qubits=4
        )
        observable = SparsePauliOp.from_sparse_list([("ZZ", (1, 2), 1.0)], num_qubits=4)
        run_hamsim(
            hamsim_script,
            tmpdir,
            dry_run=True,
            hamiltonian=hamiltonian,
            observable=observable,
            backend_name="no_device",
            aqc_evolution_time=0.2,
            aqc_ansatz_num_trotter_steps=1,
            aqc_target_num_trotter_steps=8,
            remainder_evolution_time=0.1,
            remainder_num_trotter_steps=2,
            aqc_max_iterations=300,
        )
