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
.. currentmodule:: qiskit_ibm_catalog.serverless

.. autosummary::
    :toctree: ../stubs/

    QiskitServerless
"""
# pylint: disable=duplicate-code
from __future__ import annotations

from typing import Optional, List
import warnings

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_serverless.core.client import IBMServerlessClient
from qiskit_serverless.core.function import QiskitFunction
from qiskit_serverless.core.job import Job


class QiskitServerless:
    """
    A client for connecting to the Qiskit serverless.

    Credentials can be saved to disk by calling the `save_account()` method::

        from qiskit_ibm_catalog import QiskitServerless
        QiskitServerless.save_account(token=<INSERT_IBM_QUANTUM_TOKEN>)

    Once the credentials are saved, you can simply instantiate the serverless with no
    constructor args, as shown below.

        from qiskit_ibm_catalog import QiskitServerless
        serverless = QiskitServerless()

    You can also enable an account just for the current session by instantiating the
    serverless with the API token::

        from qiskit_ibm_catalog import QiskitServerless
        serverless = QiskitServerless(token=<INSERT_IBM_QUANTUM_TOKEN>)
    """

    PRE_FILTER_KEYWORD: str = "serverless"

    def __init__(self, token: Optional[str] = None, name: Optional[str] = None) -> None:
        """
        Initialize qiskit serverless client.

        If a ``token`` is used to initialize an instance, the ``name`` argument
        will be ignored.

        If only a ``name`` is provided, the token for the named account will
        be retrieved from the user's local IBM Quantum account config file.

        Args:
            token: IBM quantum token
            name: Name of the account to load
        """
        self._client = IBMServerlessClient(token=token, name=name)

    def upload(self, function: QiskitFunction) -> QiskitFunction:
        """Uploads qiskit function.

        Args:
            function (QiskitFunction): function to upload

        Returns:
            QiskitFunction: uploaded qiskit function
        """
        title = self._client.upload(function)
        return QiskitFunction(
            title,
            job_client=self._client._job_client,  # pylint: disable=protected-access
        )

    def load(
        self, title: str, provider: Optional[str] = None
    ) -> Optional[QiskitFunction]:
        """Loads qiskit function by title.

        Args:
            title (str): title of function.
            provider (Optional[str], optional): Provider of function. Defaults to None.

        Returns:
            Optional[QiskitFunction]: qiskit function
        """
        return self._client.get(title=title, provider=provider)

    def list(self, **kwargs) -> List[QiskitFunction]:
        """Returns list of functions uploaded by user.

        Returns:
            List[QiskitFunction]: list of functions.
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

    def job(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: Job
        """
        return self._client.get_job_by_id(job_id=job_id)

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: Job
        """
        warnings.warn(
            "`get_job_by_id` method has been deprecated. "
            "And will be removed in future releases. "
            "Please, use `job` instead.",
            DeprecationWarning,
        )
        return self.job(job_id=job_id)

    def __repr__(self) -> str:
        return "<QiskitServerless>"

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
