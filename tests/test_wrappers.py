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

"""Tests for wrappers."""

from unittest import TestCase, mock

from qiskit_serverless import IBMServerlessClient
from qiskit_serverless.core import Job, QiskitFunction
from qiskit_ibm_catalog import QiskitServerless, QiskitFunctionsCatalog


class TestCatalog(TestCase):
    """TestCatalog."""

    @mock.patch.object(
        IBMServerlessClient,
        "functions",
        return_value=[QiskitFunction("the-ultimate-answer")],
    )
    @mock.patch.object(
        IBMServerlessClient, "jobs", return_value=[Job("42", mock.MagicMock())]
    )
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_token"
    )
    def test_basic_functions(self, _token_mock, jobs_mock, functions_list_mock):
        """Tests basic function of catalog."""
        catalog = QiskitFunctionsCatalog("token")
        jobs = catalog.jobs(limit=10)
        functions = catalog.list()

        jobs_mock.assert_called_with(**{"filter": "catalog", "limit": 10})
        functions_list_mock.assert_called_with(**{"filter": "catalog"})

        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(functions), 1)


class TestServerless(TestCase):
    """TestServerless."""

    @mock.patch.object(
        IBMServerlessClient,
        "functions",
        return_value=[QiskitFunction("the-ultimate-answer")],
    )
    @mock.patch.object(
        IBMServerlessClient, "jobs", return_value=[Job("42", mock.MagicMock())]
    )
    @mock.patch(
        "qiskit_serverless.core.clients.serverless_client.ServerlessClient._verify_token"
    )
    def test_basic_functions(self, _token_mock, jobs_mock, functions_list_mock):
        """Tests basic function of serverless client."""
        serverless = QiskitServerless("token")
        jobs = serverless.jobs(limit=10)
        functions = serverless.list()

        jobs_mock.assert_called_with(**{"filter": "serverless", "limit": 10})
        functions_list_mock.assert_called_with(**{"filter": "serverless"})

        self.assertEqual(len(jobs), 1)
        self.assertEqual(len(functions), 1)
