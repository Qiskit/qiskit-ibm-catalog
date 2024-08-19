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

"""
.. currentmodule:: qiskit_ibm_catalog

.. autosummary::
    :toctree: ../stubs/

    QiskitFunctionsCatalog
    QiskitServerless
    QiskitFunction
"""
# pylint: disable=W0404
from importlib_metadata import version as metadata_version, PackageNotFoundError

from qiskit_serverless import QiskitFunction

from .catalog import QiskitFunctionsCatalog
from .serverless import QiskitServerless


try:
    __version__ = metadata_version("qiskit_ibm_catalog")
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass
