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
.. currentmodule:: qiskit_ibm_catalog.catalog

.. autosummary::
    :toctree: ../stubs/

    QiskitFunctionsCatalog
"""
from __future__ import annotations

from typing import Optional, List

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_serverless.core.client import IBMServerlessClient
from qiskit_serverless.core.function import QiskitFunction
from qiskit_serverless.core.job import Job


class QiskitFunctionsCatalog:
    """
    A client for connecting to the Qiskit functions catalog.

    Credentials can be saved to disk by calling the `save_account()` method::

        from qiskit_ibm_catalog import QiskitFunctionsCatalog
        QiskitFunctionsCatalog.save_account(token=<INSERT_IBM_QUANTUM_TOKEN>)

    Once the credentials are saved, you can simply instantiate the catalog with no
    constructor args, as shown below.

        from qiskit_ibm_catalog import QiskitFunctionsCatalog
        catalog = QiskitFunctionsCatalog()

    You can also enable an account just for the current session by instantiating the
    provider with the API token::

        from qiskit_ibm_catalog import QiskitFunctionsCatalog
        catalog = QiskitFunctionsCatalog(token=<INSERT_IBM_QUANTUM_TOKEN>)
    """

    PRE_FILTER_KEYWORD: str = "catalog"

    def __init__(self, token: Optional[str] = None, name: Optional[str] = None) -> None:
        """
        Initialize qiskit functions catalog.

        If a ``token`` is used to initialize an instance, the ``name`` argument
        will be ignored.

        If only a ``name`` is provided, the token for the named account will
        be retrieved from the user's local IBM Quantum account config file.

        Args:
            token: IBM quantum token
            name: Name of the account to load
        """
        self._client = IBMServerlessClient(token=token, name=name)

    def load(
        self, title: str, provider: Optional[str] = None
    ) -> Optional[QiskitFunction]:
        """Loads Qiskit function by title

        Args:
            title (str): title of function
            provider (Optional[str], optional): provider of function. Defaults to None.

        Returns:
            Optional[QiskitFunction]: qiskit function
        """
        return self._client.get(title=title, provider=provider)

    def list(self, **kwargs) -> List[QiskitFunction]:
        """Returns a list of available qiskit functions in catalog.

        Returns:
            List[QiskitFunction]: list of qiskit functions
        """
        return self._client.list(**{**kwargs, **{"filter": self.PRE_FILTER_KEYWORD}})

    def jobs(self, **kwargs) -> List[Job]:
        """Returns list of jobs.

        Returns:
            List[Job]: jobs
        """
        return self._client.get_jobs(
            **{**kwargs, **{"filter": self.PRE_FILTER_KEYWORD}}
        )

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: job
        """
        return self._client.get_job_by_id(job_id=job_id)

    def __repr__(self) -> str:
        return "<QiskitFunctionsCatalog>"

    @staticmethod
    def save_account(
        token: Optional[str] = None,
        name: Optional[str] = None,
        overwrite: Optional[bool] = False,
    ) -> None:
        """
        Save the account to disk for future use.

        Args:
            token: IBM Quantum API token
            name: Name of the account to save
            overwrite: ``True`` if the existing account is to be overwritten
        """
        QiskitRuntimeService.save_account(token=token, name=name, overwrite=overwrite)
