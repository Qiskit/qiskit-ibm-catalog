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

"""Tests for QiskitFunctionsCatalog class."""

from unittest import TestCase, mock

from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_ibm_catalog import QiskitFunctionsCatalog


class TestCatalog(TestCase):
    """TestCatalog."""

    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_credentials"
    )
    def test_authentication(self, _verify_mock):
        """Tests authentication of serverless client."""
        catalog = QiskitFunctionsCatalog(token="token", instance="instance")

        # pylint: disable=protected-access
        self.assertEqual(catalog._client.token, "token")
        self.assertEqual(catalog._client.instance, "instance")
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
        """Tests basic function of catalog."""
        catalog = QiskitFunctionsCatalog(token="token", instance="instance")

        jobs = catalog.jobs(limit=10)
        functions = catalog.list()

        jobs_mock.assert_called()
        called_kwargs = jobs_mock.call_args.kwargs
        assert called_kwargs["filter"] == "catalog"
        assert called_kwargs["limit"] == 10
        functions_list_mock.assert_called_with(**{"filter": "catalog"})

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
        catalog = QiskitFunctionsCatalog(token="token", instance="instance")

        my_function = QiskitFunction("my-func")

        # Call jobs with both function and an additional kwarg
        jobs = catalog.jobs(function=my_function, limit=7)

        jobs_mock.assert_called()
        called_args = jobs_mock.call_args.args
        called_kwargs = jobs_mock.call_args.kwargs

        # Positional args should be empty because we pass by keyword
        assert called_args == ()

        # Ensure 'function' got forwarded and 'filter' remained enforced
        assert called_kwargs["function"] is my_function
        assert called_kwargs["filter"] == "catalog"
        assert called_kwargs["limit"] == 7

        self.assertEqual(len(jobs), 1)
        self.assertIsInstance(jobs[0], Job)
        self.assertEqual(jobs[0].job_id, "42")
