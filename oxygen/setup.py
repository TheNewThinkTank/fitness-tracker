
from setuptools import setup, find_packages

setup(
    name="oxygen",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "click",
    ],
    entry_points={
        "console_scripts": [
            "oxygen=oxygen.cli:main",
        ],
    },
)
