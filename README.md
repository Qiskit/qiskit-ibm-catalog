![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-informational)
[![Python](https://img.shields.io/badge/Python-3.8%20%7C%203.9%20%7C%203.10-informational)](https://www.python.org/)
[![Qiskit](https://img.shields.io/badge/Qiskit-%E2%89%A5%201.0.0-6133BD)](https://github.com/Qiskit/qiskit)
[![License](https://img.shields.io/github/license/qiskit-community/quantum-prototype-template?label=License)](https://github.com/qiskit-community/quantum-prototype-template/blob/main/LICENSE.txt)
[![Code style: Black](https://img.shields.io/badge/Code%20style-Black-000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/qiskit-community/quantum-prototype-template/actions/workflows/test_latest_versions.yml/badge.svg)](https://github.com/qiskit-community/quantum-prototype-template/actions/workflows/test_latest_versions.yml)
[![Coverage](https://coveralls.io/repos/github/qiskit-community/quantum-prototype-template/badge.svg?branch=main)](https://coveralls.io/github/qiskit-community/quantum-prototype-template?branch=main)

# Qiskit IBM catalog client

...

### Table of Contents

##### For Users

1.  [Installation](#installation)
2.  [Quickstart Guide](#quickstart-guide)
3.  [Tutorials](docs/tutorials/example_tutorial.ipynb)
4.  [File Glossary](docs/file-map-and-description.md)
5.  [How to Give Feedback](#how-to-give-feedback)
6.  [Contribution Guidelines](#contribution-guidelines)
7. [References and Acknowledgements](#references-and-acknowledgements)
8. [License](#license)

##### For Developers/Contributors

1. [Contribution Guide](CONTRIBUTING.md)
2. [Technical Docs](docs/technical_docs.md)

----------------------------------------------------------------------------------------------------

### Installation

```shell
pip install qiskit-ibm-catalog
```


### Quickstart guide

```python
from qiskit_ibm_catalog import QiskitFunctionsCatalog

catalog = QiskitFunctionsCatalog(token=...)

catalog.list()
# [<QiskitFunction("ibm/...")>, ...]

function = catalog.load("ibm/...")

job = function.run(circuit=...)

job.logs()

job.result()
```

----------------------------------------------------------------------------------------------------

### How to Give Feedback

We encourage your feedback! You can share your thoughts with us by:
- [Opening an issue](https://github.com/Qiskit/qiskit-ibm-catalog/issues) in the repository


----------------------------------------------------------------------------------------------------

### Contribution Guidelines

For information on how to contribute to this project, please take a look at our [contribution guidelines](CONTRIBUTING.md).


----------------------------------------------------------------------------------------------------

## References and Acknowledgements
[1] Qiskit SDK \
    https://github.com/Qiskit/qiskit


----------------------------------------------------------------------------------------------------

### License
[Apache License 2.0](LICENSE.txt)
