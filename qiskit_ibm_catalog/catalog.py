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
import warnings

from qiskit_ibm_runtime import QiskitRuntimeService
from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_serverless.core.enums import Channel
from qiskit_serverless.core.function import RunnableQiskitFunction
from qiskit_serverless.exception import QiskitServerlessException


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

    def __init__(
        self,
        token: Optional[str] = None,
        channel: str = Channel.IBM_QUANTUM.value,
        instance: Optional[str] = None,
        name: Optional[str] = None,
    ) -> None:
        """
        Initialize qiskit functions catalog.

        If a ``token`` is used to initialize an instance, the ``name`` argument
        will be ignored.

        If only a ``name`` is provided, the token for the named account will
        be retrieved from the user's local IBM Quantum account config file.

        Args:
            channel: identifies the method to use to authenticate the user
            token: IBM quantum token
            instance: IBM Cloud CRN
            name: Name of the account to load
        """
        self._client = IBMServerlessClient(
            channel=channel, token=token, instance=instance, name=name
        )

    def load(
        self, title: str, provider: Optional[str] = None
    ) -> Optional[RunnableQiskitFunction]:
        """Loads Qiskit function by title

        Args:
            title (str): title of function
            provider (Optional[str], optional): provider of function. Defaults to None.

        Returns:
            Optional[QiskitFunction]: qiskit function
        """
        return self._client.function(title=title, provider=provider)

    def list(self, **kwargs) -> List[QiskitFunction]:
        """Returns a list of available qiskit functions in catalog.

        Returns:
            List[QiskitFunction]: list of qiskit functions
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

    def provider_jobs(self, function: QiskitFunction, **kwargs) -> List[Job]:
        """List of jobs created in this provider and function.

        Args:
            function: QiskitFunction
            **kwargs: additional parameters for the request

        Raises:
            QiskitServerlessException: validation exception

        Returns:
            [Job] : list of jobs
        """
        return self._client.provider_jobs(function, **kwargs)

    def job(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: job
        """
        return self._client.job(job_id=job_id)

    def get_job_by_id(self, job_id: str) -> Optional[Job]:
        """Returns job by id.

        Args:
            job_id (str): job id

        Returns:
            Job: job
        """
        warnings.warn(
            "`get_job_by_id` method has been deprecated. "
            "And will be removed in future releases. "
            "Please, use `job` instead.",
            DeprecationWarning,
        )
        return self.job(job_id=job_id)

    def files(self, function: QiskitFunction) -> List[str]:
        """Returns the list of files available for the user in the Qiskit Function folder."""
        return self._client.files(function)

    def provider_files(self, function: QiskitFunction) -> List[str]:
        """Returns the list of files available for the provider in the Qiskit Function folder."""
        return self._client.provider_files(function)

    def file_download(
        self,
        file: str,
        function: QiskitFunction,
        target_name: Optional[str] = None,
        download_location: str = "./",
    ):
        """Download a file available to the user for the specific Qiskit Function."""
        return self._client.file_download(
            file, function, target_name, download_location
        )

    def provider_file_download(
        self,
        file: str,
        function: QiskitFunction,
        target_name: Optional[str] = None,
        download_location: str = "./",
    ):
        """Download a file available to the provider for the specific Qiskit Function."""
        return self._client.provider_file_download(
            file,
            function,
            target_name,
            download_location,
        )

    def file_delete(self, file: str, function: QiskitFunction):
        """Deletes a file available to the user for the specific Qiskit Function."""
        return self._client.file_delete(file, function)

    def provider_file_delete(self, file: str, function: QiskitFunction):
        """Deletes a file available to the provider for the specific Qiskit Function."""
        return self._client.provider_file_delete(file, function)

    def file_upload(self, file: str, function: QiskitFunction):
        """Uploads a file in the specific user's Qiskit Function folder."""
        return self._client.file_upload(file, function)

    def provider_file_upload(self, file: str, function: QiskitFunction):
        """Uploads a file in the specific provider's Qiskit Function folder."""
        return self._client.provider_file_upload(file, function)

    def __repr__(self) -> str:
        return "<QiskitFunctionsCatalog>"

    @staticmethod
    def save_account(
        token: Optional[str] = None,
        channel: str = Channel.IBM_QUANTUM.value,
        instance: Optional[str] = None,
        name: Optional[str] = None,
        overwrite: Optional[bool] = False,
    ) -> None:
        """
        Save the account to disk for future use.

        Args:
            token: IBM Quantum API token
            channel: identifies the method to use to authenticate the user
            instance: IBM Cloud CRN
            name: Name of the account to save
            overwrite: ``True`` if the existing account is to be overwritten
        """
        try:
            channel_enum = Channel(channel)
        except ValueError as error:
            raise QiskitServerlessException(
                "Your channel value is not correct. Use one of the available channels: "
                f"{Channel.LOCAL.value}, {Channel.IBM_QUANTUM.value}, {Channel.IBM_CLOUD.value}"
            ) from error

        QiskitRuntimeService.save_account(
            channel=channel_enum.value,
            token=token,
            instance=instance,
            name=name,
            overwrite=overwrite,
        )
