"""Setup script for Ultron"""

from setuptools import setup, find_packages

setup(
    name="ultron",
    version="0.1.0",
    description="Intent-Based Task Automation System",
    author="Ultron Team",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "sentencepiece>=0.1.99",
        "python-telegram-bot>=20.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "ultron=ultron.main:main",
        ],
    },
)
