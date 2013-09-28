#!/usr/bin/env python

from setuptools import setup, find_packages

from employ import __version__

setup(
    name="employ",
    version=__version__,
    author="Brett Langdon",
    author_email="brett@blangdon.com",
    packages=find_packages(),
    namespace_packages=[
        "employ.commands",
        "employ.managers",
    ],
    install_requires=[
        "docopt>=0.6.0",
        "boto>=2.13.0",
        "paramiko>=1.11.0",
        "straight.plugin>=1.4.0",
    ],
    scripts=[
        "bin/employ",
    ],
    setup_requires=[],
    description="A distributed command execution framework.",
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
