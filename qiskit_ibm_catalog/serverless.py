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

from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_serverless.core.function import RunnableQiskitFunction


class QiskitServerless:
    """
    A client for connecting to the Qiskit serverless.

    Credentials can be saved to disk by calling the `save_account()` method::

        from qiskit_ibm_catalog import QiskitServerless
        QiskitServerless.save_account(token=<INSERT_IBM_QUANTUM_TOKEN>, instance=<INSERT_CRN>)

    Once the credentials are saved, you can simply instantiate the serverless with no
    constructor args, as shown below.

        from qiskit_ibm_catalog import QiskitServerless
        serverless = QiskitServerless()

    You can also enable an account just for the current session by instantiating the
    serverless with the API token and CRN::

        from qiskit_ibm_catalog import QiskitServerless
        serverless = QiskitServerless(token=<INSERT_IBM_QUANTUM_TOKEN>, instance=<INSERT_CRN>)
    """

    PRE_FILTER_KEYWORD: str = "serverless"

    # pylint: disable=too-many-arguments
    def __init__(
        self,
        token: Optional[str] = None,
        channel: Optional[str] = None,
        instance: Optional[str] = None,
        name: Optional[str] = None,
        *,
        host: Optional[str] = None,
    ) -> None:
        """
        Initialize qiskit serverless client.

        If a ``token`` is used to initialize an instance, the ``name`` argument
        will be ignored.

        If only a ``name`` is provided, the token for the named account will
        be retrieved from the user's local IBM Quantum account config file.

        Args:
            channel: identifies the method to use to authenticate the user
            token: IBM quantum token or IBM Cloud Api Key
            instance: IBM Cloud CRN
            name: Name of the account to load
        """
        self._client = IBMServerlessClient(
            channel=channel, token=token, instance=instance, name=name, host=host
        )

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

    def list(
        self,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        **kwargs,
    ) -> List[QiskitFunction]:
        """Returns list of functions uploaded by user.

        Args:
            limit: Maximum number of functions to return.
            offset: Number of functions to skip for pagination.
            **kwargs: Additional query parameters for advanced filtering.

        Returns:
            List[QiskitFunction]: List of functions uploaded by the user.

        Example::

            # Get all user functions:

            serverless = QiskitServerless()
            functions = serverless.list()

            # Get first 10 functions:

            functions = serverless.list(limit=10)

            # Get next page of functions:

            functions = serverless.list(limit=10, offset=10)
        """
        params = {**kwargs, "filter": self.PRE_FILTER_KEYWORD}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        return self._client.functions(**params)

    def jobs(
        self,
        function: Optional[QiskitFunction] = None,
        *,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        created_after: Optional[str] = None,
        **kwargs,
    ) -> List[Job]:
        """Returns list of jobs from serverless.

        Args:
            function: Filter jobs by the function that created them.
            limit: Maximum number of jobs to return. Default: 10.
            offset: Number of jobs to skip for pagination. Default: 0.
            status: Filter by job status. Valid values:
                - "QUEUED": Job is waiting to run
                - "RUNNING": Job is currently executing
                - "DONE": Job completed successfully
                - "ERROR": Job failed with an error
                - "CANCELLED": Job was cancelled
            created_after: Filter jobs created after this timestamp.
                Format: ISO 8601 (e.g., "2024-01-01T00:00:00Z")
            **kwargs: Additional query parameters for advanced filtering.

        Returns:
            List[Job]: List of Job objects matching the specified criteria.

        Example::

            # Get the 5 most recent jobs:

            serverless = QiskitServerless()
            jobs = serverless.jobs(limit=5)

            # Get completed jobs:

            jobs = serverless.jobs(status="DONE", limit=10)

            # Get jobs from a specific function:

            my_function = serverless.load("my-function")
            jobs = serverless.jobs(function=my_function, limit=20)

            # Get jobs created after a specific date:

            jobs = serverless.jobs(
                created_after="2024-01-01T00:00:00Z",
                status="DONE"
            )

        Note:
            The 'filter' parameter is automatically set to "serverless" to ensure
            only serverless jobs are returned. This cannot be overridden.
        """
        params = {
            **kwargs,
            "limit": limit,
            "offset": offset,
            "filter": self.PRE_FILTER_KEYWORD,
        }
        if status is not None:
            params["status"] = status
        if created_after is not None:
            params["created_after"] = created_after
        return self._client.jobs(function=function, **params)

    def provider_jobs(
        self,
        function: QiskitFunction,
        *,
        limit: int = 10,
        offset: int = 0,
        status: Optional[str] = None,
        created_after: Optional[str] = None,
        **kwargs,
    ) -> List[Job]:
        """List of jobs created by the provider for this function.

        Args:
            function: Function object to filter jobs by.
            limit: Maximum number of jobs to return. Default: 10.
            offset: Number of jobs to skip for pagination. Default: 0.
            status: Filter by job status. Valid values:
                - "QUEUED": Job is waiting to run
                - "RUNNING": Job is currently executing
                - "DONE": Job completed successfully
                - "ERROR": Job failed with an error
                - "CANCELLED": Job was cancelled
            created_after: Filter jobs created after this timestamp.
                Format: ISO 8601 (e.g., "2024-01-01T00:00:00Z")
            **kwargs: Additional query parameters for advanced filtering.

        Returns:
            List[Job]: List of Job objects for the specified provider and function.

        Raises:
            QiskitServerlessException: If the function doesn't have an associated provider.

        Example::

            # Get provider jobs for a function:

            serverless = QiskitServerless()
            my_function = serverless.load("my-function")
            jobs = serverless.provider_jobs(my_function, limit=10)

            # Get completed provider jobs:

            jobs = serverless.provider_jobs(
                my_function,
                status="DONE",
                limit=20
            )
        """
        params = {
            **kwargs,
            "limit": limit,
            "offset": offset,
        }
        if status is not None:
            params["status"] = status
        if created_after is not None:
            params["created_after"] = created_after
        return self._client.provider_jobs(function, **params)

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

    def runtime_jobs(
        self, job_id: str, runtime_session: Optional[str] = None
    ) -> List[str]:
        """Returns list of qiskit runtime job ids associated to the serverless job id
        and optionally filtered by session.

        Returns:
            List[str]: job ids
        """
        return self._client.runtime_jobs(job_id, runtime_session)

    def runtime_sessions(self, job_id: str):
        """Returns list of qiskit runtime session ids associated to the serverless job id.

        Returns:
            List[str]: session ids
        """
        return self._client.runtime_sessions(job_id)

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
        return "<QiskitServerless>"

    @staticmethod
    def save_account(
        token: Optional[str] = None,
        channel: Optional[str] = None,
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

        IBMServerlessClient.save_account(
            channel=channel,
            token=token,
            instance=instance,
            name=name,
            overwrite=overwrite,
        )
