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

from qiskit.providers import Backend
from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_serverless.core.function import RunnableQiskitFunction
from qiskit_serverless.core.job_event import JobEvent
from qiskit_serverless.core.compute_profile import ComputeProfile, ComputeProfileList


class QiskitServerless:  # pylint: disable=too-many-public-methods
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

    def dependencies_versions(self) -> List[str]:
        """Discover the dependencies (and versions) baked into the runtime image.

        Read-only discovery: this reports what the runtime image already ships, so
        you know what you do not need to bring yourself.

        Returns:
            List[str]: dependency requirement strings, e.g. ``["numpy==2.1.0", ...]``.
        """
        return self._client.dependencies_versions()

    def dependency_report(self, requirements: List[str]):
        """Diff your requirements against what the runtime image already ships.

        For each requirement this reports whether it is already baked into the
        image (so you should not bring it), needs to be brought as a wheel, or
        clashes with a different baked version. It is a client-side diff over
        :meth:`dependencies_versions`; it uploads nothing. The result prints as an
        aligned table.

        Args:
            requirements: requirement strings, e.g. ``["numpy>=2", "mypkg", "jax<0.5"]``.

        Returns:
            A report (a list of entries) that prints as a table.
        """
        return self._client.dependency_report(requirements)

    def compute_profiles(self) -> ComputeProfileList:
        """List the compute profiles registered on this deployment.

        These are the profiles a Fleets function's ``sizes_map`` can name. The
        catalog is deployment-specific, so discover the profiles here rather than
        hard-coding identifiers. The returned list prints as an aligned table.

        Returns:
            ComputeProfileList: the registered profiles (a list that prints as a table).
        """
        return self._client.compute_profiles()

    def compute_profile(
        self,
        compute_profile_id: Optional[str] = None,
        *,
        cpu: Optional[int | str] = None,
        memory: Optional[int | str] = None,
        gpu: Optional[str] = None,
    ) -> ComputeProfile:
        """Get a single registered compute profile, by id or by exact resources.

        Call it one of two ways:

        - by id: ``serverless.compute_profile("24x120")``
        - by resources: ``serverless.compute_profile(cpu=24, memory=120[, gpu="1l40s"])``
          -- ``cpu`` and ``memory`` are required, ``gpu`` is optional (omitted means
          CPU-only). Every value given must match a single registered profile exactly.

        Args:
            compute_profile_id: the profile id to look up. Mutually exclusive with the
                resource arguments.
            cpu: required when looking up by resources.
            memory: required when looking up by resources.
            gpu: optional GPU specifier when looking up by resources.

        Returns:
            ComputeProfile: the matching registered profile.
        """
        return self._client.compute_profile(
            compute_profile_id, cpu=cpu, memory=memory, gpu=gpu
        )

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

    def events(self, job_id: str, **kwargs) -> List[JobEvent]:
        """Returns events of the job.

        Args:
            job_id (str): job id
            **kwargs: Additional query parameters for filtering.

        Returns:
            List[JobEvent]: list of job events
        """
        return self._client.events(job_id, **kwargs)

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

    def add_wheels(self, function: QiskitFunction, patterns: List[str]) -> List[str]:
        """Upload locally-built wheels to a function's file area.

        Each pattern is a local path or glob (e.g. ``"dist/mypkg-1.0-*.whl"``);
        every match must be a ``.whl`` file. The wheels are uploaded into the
        function's ``wheels`` sub-directory so they are available at runtime.
        Install them from your entrypoint with ``install_uploaded_wheels()``, which
        reads that same directory. Use :meth:`list_wheels` and :meth:`remove_wheels`
        to see and remove what has been uploaded.

        Args:
            function: the function whose file area the wheels are uploaded to.
            patterns: local paths or globs matching the wheel files to upload.

        Returns:
            List[str]: the uploaded wheel file names, in upload order.
        """
        return self._client.add_wheels(function, patterns)

    def list_wheels(self, function: QiskitFunction) -> List[str]:
        """List the wheels currently uploaded to a function (via :meth:`add_wheels`).

        Returns:
            List[str]: the wheel file names in the function's ``wheels`` sub-directory.
        """
        return self._client.list_wheels(function)

    def remove_wheels(self, function: QiskitFunction, names: List[str]) -> None:
        """Remove previously uploaded wheels from a function.

        To update a wheel, remove the old one and :meth:`add_wheels` the new build.

        Args:
            function: the function to remove wheels from.
            names: wheel file names to remove, as returned by :meth:`list_wheels`.
        """
        return self._client.remove_wheels(function, names)

    def backends(self, **kwargs) -> List[Backend]:
        """Returns the backends accessible through the active instance.

        Args:
            **kwargs: Filtering options forwarded to the client (e.g. ``name``,
                ``min_num_qubits``, ``filters``, ``refresh_cache``).

        Returns:
            List[Backend]: Backends matching the given criteria.
        """
        return self._client.backends(**kwargs)

    def backend(self, name: str, **kwargs) -> Backend:
        """Returns a single backend by name.

        Args:
            name: Name of the backend to retrieve.
            **kwargs: Additional options forwarded to the client.

        Returns:
            Backend: The requested backend.
        """
        return self._client.backend(name, **kwargs)

    def least_busy(self, **kwargs) -> Backend:
        """Returns the backend with the fewest pending jobs.

        Args:
            **kwargs: Filtering options forwarded to the client (e.g.
                ``min_num_qubits``, ``filters``).

        Returns:
            Backend: The least busy backend matching the given criteria.
        """
        return self._client.least_busy(**kwargs)

    def usage(self) -> dict:
        """Returns runtime usage information for the active instance.

        Returns:
            dict: Usage details for the active instance.
        """
        return self._client.usage()

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


#: Alias for :class:`QiskitServerless`.
#:
#: Introduced as the forward-looking name for the managed-workflow client.
#: ``QiskitServerless`` remains available for backwards compatibility and refers
#: to the same class.
ManagedWorkflowClient = QiskitServerless
