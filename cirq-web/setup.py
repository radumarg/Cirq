# Copyright 2021 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import runpy

from setuptools import find_packages, setup

# This reads the __version__ variable from cirq_web/_version.py
__version__ = runpy.run_path('cirq_web/_version.py')['__version__']
assert __version__, 'Version string cannot be empty'

name = 'cirq-web'

description = 'Web-based 3D visualization tools for Cirq.'

# README file as long_description.
long_description = open('README.md', encoding='utf-8').read()

# Read in requirements
requirements = open('requirements.txt').readlines()
requirements = [r.strip() for r in requirements]
requirements += [f'cirq-core=={__version__}']

packs = ['cirq_web'] + ['cirq_web.' + package for package in find_packages(where='cirq_web')]

setup(
    name=name,
    version=__version__,
    url='http://github.com/quantumlib/cirq',
    author='The Cirq Developers',
    author_email='cirq-dev@googlegroups.com',
    maintainer="Google Quantum AI open-source maintainers",
    maintainer_email="quantum-oss-maintainers@google.com",
    # TODO: #6648 - update when internal docs build supports python3.11
    python_requires='>=3.10.0',
    install_requires=requirements,
    license='Apache 2',
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=packs,
    package_data={'cirq_web': ['dist/*.bundle.js']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Quantum Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Typing :: Typed",
    ],
    keywords=[
        "algorithms",
        "api",
        "cirq",
        "google",
        "google quantum",
        "nisq",
        "python",
        "quantum",
        "quantum algorithms",
        "quantum circuit",
        "quantum circuit simulator",
        "quantum computer simulator",
        "quantum computing",
        "quantum development kit",
        "quantum information",
        "quantum programming",
        "quantum programming language",
        "quantum simulation",
        "sdk",
        "simulation",
    ],
)
