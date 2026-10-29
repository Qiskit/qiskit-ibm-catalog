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

"""Tests for the backwards-compatible class name aliases."""

from unittest import TestCase

import qiskit_ibm_catalog
from qiskit_ibm_catalog import (
    FunctionsCatalog,
    ManagedWorkflow,
    ManagedWorkflowClient,
    QiskitFunction,
    QiskitFunctionsCatalog,
    QiskitServerless,
)


class TestAliases(TestCase):
    """The new names must be importable and identical to the legacy names."""

    def test_functions_catalog_alias(self):
        """FunctionsCatalog aliases QiskitFunctionsCatalog."""
        self.assertIs(FunctionsCatalog, QiskitFunctionsCatalog)

    def test_managed_workflow_client_alias(self):
        """ManagedWorkflowClient aliases QiskitServerless."""
        self.assertIs(ManagedWorkflowClient, QiskitServerless)

    def test_managed_workflow_alias(self):
        """ManagedWorkflow aliases the qiskit_serverless QiskitFunction."""
        self.assertIs(ManagedWorkflow, QiskitFunction)

    def test_new_names_exported(self):
        """Each new name is reachable as a package attribute."""
        for name in ("FunctionsCatalog", "ManagedWorkflowClient", "ManagedWorkflow"):
            self.assertTrue(hasattr(qiskit_ibm_catalog, name))
