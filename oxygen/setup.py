
from setuptools import setup, find_packages

setup(
    name="oxygen",
    version="0.0.1",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "click>=8.1.8,<9",
        "fitness-tracker>=0.1.0",
    ],
    entry_points={
        "console_scripts": [
            "oxygen=oxygen.cli:cli",
        ],
    },
)
