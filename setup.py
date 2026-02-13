"""Setup script for OpenClaw Skills Hub."""

from setuptools import setup, find_packages


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="openclaw-skills-hub",
    version="1.0.0",
    author="OpenClaw Community",
    author_email="community@openclaw.ai",
    description="A production-grade Python application that compiles all OpenClaw community skills into a single unified catalog",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/openclaw/skills-hub",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openclaw-skills-hub=openclaw_skills_hub.cli.main:main",
            "openclaw-skills-api=openclaw_skills_hub.api.server:run_server",
        ],
    },
    include_package_data=True,
    package_data={
        "openclaw_skills_hub": ["data/**/*"],
    },
)
