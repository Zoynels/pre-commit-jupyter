# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

setup(
    name="zs-jupyter-notebook-cleanup",
    version="2.0.0",
    description="Automagically remove notebook outputs and another block for better security and less git diff",
    author="Zoynels",
    url="https://github.com/Zoynels/pre-commit-jupyter",
    packages=find_packages(),
    python_requires=">=3",
    install_requires=[],
    entry_points={"console_scripts": ["zs-jupyter-notebook-cleanup=zs_jupyter_notebook_cleanup.cli:main"]},
)
