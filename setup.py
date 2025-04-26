from setuptools import setup, find_packages

setup(
    name="investment_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    description="Property Investment Analysis App with AI Agents",
    author="Property Investment Team",
    install_requires=[
        # Dependencies are specified in requirements.txt and pyproject.toml
    ],
    extras_require={
        "dev": [
            "pytest==7.4.3",
            "pytest-cov==4.1.0",
            "black==23.10.1",
            "isort==5.12.0",
            "mypy==1.6.1",
            "ruff==0.1.3",
        ]
    },
    entry_points={
        "console_scripts": [
            "investment_agent=investment_agent.main:main",
        ],
    },
)