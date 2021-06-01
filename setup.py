# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from setuptools import find_packages, setup

with open("README.md", "r", encoding='utf_8') as fh:
    long_description = fh.read()

install_requires=[
    'pystopwatch2',
    'hyperopt',
    'tensorwatch>=0.9.1', 'tensorboard',
    'pretrainedmodels', 'tqdm', 'sklearn', 'matplotlib', 'psutil',
    'requests', 'seaborn', 'h5py', 'rarfile',
    'gorilla', 'pyyaml', 'overrides', 'runstats', 'psutil', 'statopt',
    'pyunpack', 'patool', 'ray>=1.0.0', 'Send2Trash',
    'transformers', 'pytorch_lightning', 'tokenizers', 'datasets',
    # nvidia transformer-xl
    'dllogger @ git+https://github.com/NVIDIA/dllogger.git',
    'pytorch-transformers', 'sacremoses', 'pynvml'
]

setup(
    name="archai",
    version="0.6.4",
    description="Research platform for Neural Architecture Search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Shital Shah, Debadeepta Dey",
    author_email="shitals@microsoft.com, dedey@microsoft.com",
    url="https://github.com/microsoft/archai",
	license="MIT",
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
