#!/usr/bin/env python

from setuptools import setup, find_packages

from employ import __version__

setup(
    name="employ",
    version=__version__,
    author="Brett Langdon",
    author_email="brett@blangdon.com",
    packages=find_packages(),
    install_requires=[
        "docopt>=0.6.0",
        "boto>=2.13.0",
    ],
    setup_requires=[],
    description="Distributed one time command execution and aggregation tool",
    license="MIT",
    url='https://github.com/brettlangdon/employ',
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
    ],
)
