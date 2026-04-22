# This code is part of Qiskit.
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

"""Tests for QiskitServerless class."""

from unittest import TestCase, mock
import pytest

from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_serverless.core.job_event import JobEvent
from qiskit_ibm_catalog import QiskitServerless


class TestServerless(TestCase):
    """TestServerless."""

    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_authentication(self, _verify_mock):
        """Tests authentication of serverless client."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )

        # pylint: disable=protected-access
        assert serverless._client.token == "token"
        assert serverless._client.instance == "instance"
        assert serverless._client.host == "http://host"
        # pylint: enable=protected-access

    @mock.patch.object(
        IBMServerlessClient,
        "functions",
        return_value=[QiskitFunction("the-ultimate-answer")],
    )
    @mock.patch.object(
        IBMServerlessClient, "jobs", return_value=[Job("42", mock.MagicMock())]
    )
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_basic_functions(self, _verify_mock, jobs_mock, functions_list_mock):
        """Tests basic function of serverless client."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )

        # pylint: disable=protected-access
        assert serverless._client.token == "token"
        assert serverless._client.instance == "instance"
        assert serverless._client.host == "http://host"
        # pylint: enable=protected-access

        jobs = serverless.jobs(limit=10)
        functions = serverless.list()

        jobs_mock.assert_called()
        called_kwargs = jobs_mock.call_args.kwargs
        assert called_kwargs["filter"] == "serverless"
        assert called_kwargs["limit"] == 10
        functions_list_mock.assert_called_with(**{"filter": "serverless"})

        assert len(jobs) == 1
        assert len(functions) == 1

    @mock.patch.object(
        IBMServerlessClient, "jobs", return_value=[Job("42", mock.MagicMock())]
    )
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_jobs_with_function_filter(self, _verify_mock, jobs_mock):
        """Tests that 'function' is forwarded and 'serverless' filter is enforced."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )

        my_function = QiskitFunction("my-func")

        # Call jobs with both function and an additional kwarg
        jobs = serverless.jobs(function=my_function, limit=7)

        jobs_mock.assert_called()
        called_args = jobs_mock.call_args.args
        called_kwargs = jobs_mock.call_args.kwargs

        # Positional args should be empty because we pass by keyword
        assert called_args == ()

        # Ensure 'function' got forwarded and 'filter' remained enforced
        assert called_kwargs["function"] is my_function
        assert called_kwargs["filter"] == "serverless"
        assert called_kwargs["limit"] == 7

        assert len(jobs) == 1
        assert isinstance(jobs[0], Job)
        assert jobs[0].job_id == "42"

    @mock.patch.object(IBMServerlessClient, "upload")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_upload_method(self, _verify_mock, upload_mock):
        """Tests that upload() forwards function parameter correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        test_function = QiskitFunction("test-function")
        mock_uploaded_function = mock.MagicMock()
        upload_mock.return_value = mock_uploaded_function

        result = serverless.upload(function=test_function)

        upload_mock.assert_called_once_with(test_function)
        assert result == mock_uploaded_function

    @mock.patch.object(IBMServerlessClient, "function")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_load_method(self, _verify_mock, function_mock):
        """Tests that load() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_function = mock.MagicMock()
        function_mock.return_value = mock_function

        result = serverless.load(title="test-function", provider="test-provider")

        function_mock.assert_called_once_with(
            title="test-function", provider="test-provider"
        )
        assert result == mock_function

    @mock.patch.object(IBMServerlessClient, "job")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_job_method(self, _verify_mock, job_mock):
        """Tests that job() forwards job_id correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_job = Job("test-job-id", mock.MagicMock())
        job_mock.return_value = mock_job

        result = serverless.job(job_id="test-job-id")

        job_mock.assert_called_once_with(job_id="test-job-id")
        assert result == mock_job

    @mock.patch.object(IBMServerlessClient, "job")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_get_job_by_id_deprecation_warning(self, _verify_mock, job_mock):
        """Tests that get_job_by_id() shows deprecation warning."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_job = Job("test-job-id", mock.MagicMock())
        job_mock.return_value = mock_job

        with pytest.warns(DeprecationWarning) as warning_info:
            result = serverless.get_job_by_id(job_id="test-job-id")

        # Verify the warning message
        warning_message = str(warning_info[0].message)
        assert "get_job_by_id" in warning_message
        assert "deprecated" in warning_message
        assert "job" in warning_message

        # Verify it still works
        job_mock.assert_called_once_with(job_id="test-job-id")
        assert result == mock_job

    @mock.patch.object(IBMServerlessClient, "runtime_jobs")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_runtime_jobs_method(self, _verify_mock, runtime_jobs_mock):
        """Tests that runtime_jobs() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_job_ids = ["job1", "job2", "job3"]
        runtime_jobs_mock.return_value = mock_job_ids

        result = serverless.runtime_jobs(
            job_id="test-job-id", runtime_session="test-session"
        )

        runtime_jobs_mock.assert_called_once_with("test-job-id", "test-session")
        assert result == mock_job_ids

    @mock.patch.object(IBMServerlessClient, "runtime_sessions")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_runtime_sessions_method(self, _verify_mock, runtime_sessions_mock):
        """Tests that runtime_sessions() forwards job_id correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_session_ids = ["session1", "session2"]
        runtime_sessions_mock.return_value = mock_session_ids

        result = serverless.runtime_sessions(job_id="test-job-id")

        runtime_sessions_mock.assert_called_once_with("test-job-id")
        assert result == mock_session_ids

    @mock.patch.object(IBMServerlessClient, "events")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_events_method(self, _verify_mock, events_mock):
        """Tests that events() forwards job_id and kwargs correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_events = [
            JobEvent(
                event_type="STATUS_CHANGE",
                origin="API",
                context="SET_SUB_STATUS",
                created="2024-01-01T00:00:00Z",
                data={"status": "RUNNING"},
            )
        ]
        events_mock.return_value = mock_events

        result = serverless.events(job_id="test-job-id", event_type="STATUS_CHANGE")

        events_mock.assert_called_once_with("test-job-id", event_type="STATUS_CHANGE")
        assert result == mock_events

    @mock.patch.object(IBMServerlessClient, "provider_jobs")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_provider_jobs_method(self, _verify_mock, provider_jobs_mock):
        """Tests that provider_jobs() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_jobs = [Job("job1", mock.MagicMock()), Job("job2", mock.MagicMock())]
        provider_jobs_mock.return_value = mock_jobs
        test_function = QiskitFunction("test-function")

        result = serverless.provider_jobs(function=test_function, limit=5, offset=10)

        provider_jobs_mock.assert_called_once_with(test_function, limit=5, offset=10)
        assert result == mock_jobs

    @mock.patch.object(IBMServerlessClient, "files")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_files_method(self, _verify_mock, files_mock):
        """Tests that files() forwards function parameter correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_files = ["file1.txt", "file2.py", "file3.json"]
        files_mock.return_value = mock_files
        test_function = QiskitFunction("test-function")

        result = serverless.files(function=test_function)

        files_mock.assert_called_once_with(test_function)
        assert result == mock_files

    @mock.patch.object(IBMServerlessClient, "provider_files")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_provider_files_method(self, _verify_mock, provider_files_mock):
        """Tests that provider_files() forwards function parameter correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        mock_files = ["provider_file1.txt", "provider_file2.py"]
        provider_files_mock.return_value = mock_files
        test_function = QiskitFunction("test-function")

        result = serverless.provider_files(function=test_function)

        provider_files_mock.assert_called_once_with(test_function)
        assert result == mock_files

    @mock.patch.object(IBMServerlessClient, "file_download")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_file_download_method(self, _verify_mock, file_download_mock):
        """Tests that file_download() forwards all parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        file_download_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.file_download(
            file="test.txt",
            function=test_function,
            target_name="downloaded.txt",
            download_location="/tmp/",
        )

        file_download_mock.assert_called_once_with(
            "test.txt", test_function, "downloaded.txt", "/tmp/"
        )
        assert result is None

    @mock.patch.object(IBMServerlessClient, "provider_file_download")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_provider_file_download_method(
        self, _verify_mock, provider_file_download_mock
    ):
        """Tests that provider_file_download() forwards all parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        provider_file_download_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.provider_file_download(
            file="provider_test.txt",
            function=test_function,
            target_name="provider_downloaded.txt",
            download_location="/tmp/provider/",
        )

        provider_file_download_mock.assert_called_once_with(
            "provider_test.txt",
            test_function,
            "provider_downloaded.txt",
            "/tmp/provider/",
        )
        assert result is None

    @mock.patch.object(IBMServerlessClient, "file_upload")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_file_upload_method(self, _verify_mock, file_upload_mock):
        """Tests that file_upload() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        file_upload_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.file_upload(file="upload.txt", function=test_function)

        file_upload_mock.assert_called_once_with("upload.txt", test_function)
        assert result is None

    @mock.patch.object(IBMServerlessClient, "provider_file_upload")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_provider_file_upload_method(self, _verify_mock, provider_file_upload_mock):
        """Tests that provider_file_upload() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        provider_file_upload_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.provider_file_upload(
            file="provider_upload.txt", function=test_function
        )

        provider_file_upload_mock.assert_called_once_with(
            "provider_upload.txt", test_function
        )
        assert result is None

    @mock.patch.object(IBMServerlessClient, "file_delete")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_file_delete_method(self, _verify_mock, file_delete_mock):
        """Tests that file_delete() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        file_delete_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.file_delete(file="delete.txt", function=test_function)

        file_delete_mock.assert_called_once_with("delete.txt", test_function)
        assert result is None

    @mock.patch.object(IBMServerlessClient, "provider_file_delete")
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_provider_file_delete_method(self, _verify_mock, provider_file_delete_mock):
        """Tests that provider_file_delete() forwards parameters correctly."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )
        provider_file_delete_mock.return_value = None
        test_function = QiskitFunction("test-function")

        result = serverless.provider_file_delete(
            file="provider_delete.txt", function=test_function
        )

        provider_file_delete_mock.assert_called_once_with(
            "provider_delete.txt", test_function
        )
        assert result is None

    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_repr_method(self, _verify_mock):
        """Tests that __repr__() returns correct string representation."""
        serverless = QiskitServerless(
            token="token", instance="instance", host="http://host"
        )

        result = repr(serverless)

        assert result == "<QiskitServerless>"

    @mock.patch.object(IBMServerlessClient, "save_account")
    def test_save_account_static_method(self, save_account_mock):
        """Tests that save_account() forwards all parameters correctly."""
        save_account_mock.return_value = None

        QiskitServerless.save_account(
            token="test-token",
            channel="test-channel",
            instance="test-instance",
            name="test-name",
            overwrite=True,
        )

        save_account_mock.assert_called_once_with(
            channel="test-channel",
            token="test-token",
            instance="test-instance",
            name="test-name",
            overwrite=True,
        )
