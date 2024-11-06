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
from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_serverless.core.function import RunnableQiskitFunction


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

    def upload(self, function: QiskitFunction) -> RunnableQiskitFunction:
        """Uploads qiskit function.

        Args:
            function (QiskitFunction): function to upload

        Returns:
            QiskitFunction: uploaded qiskit function
        """
        return self._client.upload(function)

    def load(
        self, title: str, provider: Optional[str] = None
    ) -> Optional[RunnableQiskitFunction]:
        """Loads qiskit function by title.

        Args:
            title (str): title of function.
            provider (Optional[str], optional): Provider of function. Defaults to None.

        Returns:
            Optional[QiskitFunction]: qiskit function
        """
        return self._client.function(title=title, provider=provider)

    def list(self, **kwargs) -> List[QiskitFunction]:
        """Returns list of functions uploaded by user.

        Returns:
            List[QiskitFunction]: list of functions.
        """
        return self._client.functions(
            **{**kwargs, **{"filter": self.PRE_FILTER_KEYWORD}}
        )

    def jobs(self, **kwargs) -> List[Job]:
        """Returns list of jobs.

        Returns:
            List[Job]: jobs
        """
        return self._client.jobs(**{**kwargs, **{"filter": self.PRE_FILTER_KEYWORD}})

    def job(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: Job
        """
        return self._client.job(job_id=job_id)

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

    def files(self, provider: Optional[str] = None) -> List[str]:
        """Returns list of available files produced by programs to download."""
        return self._client.files(provider)

    def file_download(
        self,
        file: str,
        target_name: Optional[str] = None,
        download_location: str = "./",
        provider: Optional[str] = None,
    ):
        """Download file."""
        return self._client.file_download(
            file, target_name, download_location, provider
        )

    def file_delete(self, file: str, provider: Optional[str] = None):
        """Deletes file uploaded or produced by the programs,"""
        return self._client.file_delete(file, provider)

    def file_upload(self, file: str, provider: Optional[str] = None):
        """Upload file."""
        return self._client.file_upload(file, provider)

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
