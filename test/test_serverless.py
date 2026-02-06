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

from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
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
        self.assertEqual(serverless._client.token, "token")
        self.assertEqual(serverless._client.instance, "instance")
        self.assertEqual(serverless._client.host, "http://host")
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
        self.assertEqual(serverless._client.token, "token")
        self.assertEqual(serverless._client.instance, "instance")
        self.assertEqual(serverless._client.host, "http://host")
        # pylint: enable=protected-access

        jobs = serverless.jobs(limit=10)
        functions = serverless.list()

        jobs_mock.assert_called()
        called_kwargs = jobs_mock.call_args.kwargs
        assert called_kwargs["filter"] == "serverless"
        assert called_kwargs["limit"] == 10
        functions_list_mock.assert_called_with(**{"filter": "serverless"})

        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(functions), 1)

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

        self.assertEqual(len(jobs), 1)
        self.assertIsInstance(jobs[0], Job)
        self.assertEqual(jobs[0].job_id, "42")
