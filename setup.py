from setuptools import setup, find_packages

setup(
    name="email2md",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pytz",
    ],
    entry_points={
        "console_scripts": [
            "email2md=email2md.cli:main",
        ],
    },
)
