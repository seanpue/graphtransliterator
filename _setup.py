#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open("README.rst") as readme_file:
    readme = readme_file.read()

requirements = ["Click", "marshmallow", "pyyaml"]

setup_requirements = ["pytest-runner"]

test_requirements = ["pytest"]

setup(
    author="A. Sean Pue",
    author_email="pue@msu.edu",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    description="A graph-based transliteration tool",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    keywords="graphtransliterator",
    name="graphtransliterator",
    packages=find_packages(include=["graphtransliterator"]),
    package_data={
        # include yaml and json files, e.g. in bundled transliterators
        "": ["*.yaml", "*.json"]
    },
    entry_points={
        "console_scripts": ["graphtransliterator=graphtransliterator.cli:main",],
    },
    python_requires=">=3.9",
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/seanpue/graphtransliterator",
    version="1.2.3",
    zip_safe=False,
)
