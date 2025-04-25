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
        # Dependencies are specified in requirements.txt
    ],
    entry_points={
        "console_scripts": [
            "investment_agent=investment_agent.main:main",
        ],
    },
)