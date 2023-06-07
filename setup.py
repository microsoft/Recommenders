# Copyright (c) Recommenders contributors.
# Licensed under the MIT License.

import site
import sys
import time
from os import environ
from pathlib import Path

from setuptools import find_packages, setup

site.ENABLE_USER_SITE = "--user" in sys.argv[1:]

# Version
here = Path(__file__).absolute().parent
version_data = {}
with open(here.joinpath("recommenders", "__init__.py"), "r") as f:
    exec(f.read(), version_data)
version = version_data.get("__version__", "0.0")

# Get the long description from the README file
with open(here.joinpath("recommenders", "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()

HASH = environ.get("HASH", None)
if HASH is not None:
    version += ".post" + str(int(time.time()))

install_requires = [
    "pandas>1.5.2,<2.1",  # requires numpy
    "tqdm>=4.65.0,<5",
    "matplotlib>=3.6.0,<4",
    "scikit-learn>=1.1.3,<2",  # 1.0.2 may not support Python 3.10.  requires scipy
    "numba>=0.57.0,<1",
    "lightfm>=1.17,<2",
    "lightgbm>=3.3.2,<4",
    "memory_profiler>=0.61.0,<1",
    "nltk>=3.8.1,<4",
    "seaborn>=0.12.0,<1",
    "transformers>=4.26.0,<5",  # requires pyyaml
    "bottleneck>=1.3.7,<2",
    "category_encoders>=2.6.0,<3",
    "jinja2>=3.1.0,<3.2",
    "cornac>=1.15.2,<2",
    "retrying>=1.3.4",
    "pandera[strategies]>=0.15.0",  # For generating fake datasets
    "scikit-surprise>=1.1.3",
    "scrapbook>=0.5.0,<1.0.0",
]

# shared dependencies
extras_require = {
    "examples": [
        "azure-mgmt-cosmosdb>=9.0.0,<10",
        "hyperopt>=0.2.7,<1",
        "ipykernel>=6.20.1,<7",
        "notebook>=6.5.4,<8",
        "locust>=2.15.1,<3",
        "papermill>=2.4.0,<3",
    ],
    "gpu": [
        "nvidia-ml-py3>=11.510.69",
        # TensorFlow compiled with CUDA 11.2, cudnn 8.1
        "tensorflow~=2.6.1;python_version=='3.6'",
        "tensorflow~=2.7.0;python_version>='3.7'",
        "tf-slim>=1.1.0",
        "torch>=2.0.1",
        "fastai>=2.7.11,<3",
    ],
    "spark": [
        "databricks_cli>=0.17.7,<1",
        "pyarrow>=10.0.1",
        "pyspark>=3.0.1,<=3.4.0",
    ],
    "dev": [
        "black>=23.3.0,<24",
        "pytest>=7.2.1",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.10.0",  # for access to mock fixtures in pytest
        "pytest-rerunfailures>=11.1.2",  # to mark flaky tests
    ],
}
# For the brave of heart
extras_require["all"] = list(set(sum([*extras_require.values()], [])))

# The following dependencies need additional testing
extras_require["experimental"] = [
    # xlearn requires cmake to be pre-installed
    "xlearn==0.40a1",
    # VW C++ binary needs to be installed manually for some code to work
    "vowpalwabbit>=8.9.0,<9",
    # nni needs to be upgraded
    "nni==1.5",
    "pymanopt>=0.2.5",
]

# The following dependency can be installed as below, however PyPI does not allow direct URLs.
# Temporary fix for pymanopt, only this commit works with TF2
# "pymanopt@https://github.com/pymanopt/pymanopt/archive/fb36a272cdeecb21992cfd9271eb82baafeb316d.zip",

setup(
    name="recommenders",
    version=version,
    description="Recommenders - Python utilities for building recommendation systems",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/recommenders-team/recommenders",
    project_urls={
        "Documentation": "https://microsoft-recommenders.readthedocs.io/en/stable/",
        "Wiki": "https://github.com/recommenders-team/recommenders/wiki",
    },
    author="Recommenders contributors",
    author_email="recommenders-technical-discuss@lists.lfaidata.foundation",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    extras_require=extras_require,
    keywords="recommendations recommendation recommenders recommender system engine "
    "machine learning python spark gpu",
    install_requires=install_requires,
    package_dir={"recommenders": "recommenders"},
    python_requires=">=3.8, <3.12",
    packages=find_packages(
        where=".",
        exclude=["contrib", "docs", "examples", "scenarios", "tests", "tools"],
    ),
    setup_requires=["numpy>=1.15"],
)
