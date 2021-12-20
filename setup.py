from setuptools import find_packages, setup

with open("README.rst") as file:
    readme = file.read()

with open("LICENSE") as file:
    license = file.read()

setup(
    name="deposition",
    version="1.0.0-alpha",
    description="Molecular dynamics wrapper for deposition simulations",
    long_description=readme,
    author="M. J. Cyster",
    author_email="martincyster@fastmail.com",
    url="https://github.com/mmtn/deposition",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
    python_requires=">=3.7",
    install_requires=[
        "click>=7.1.2",
        "numpy>=1.20.2",
        "pandas>=1.2.4",
        "pymatgen>=2022.0.8",
        "PyYAML>=5.4.1",
        "schema>=0.7.4",
        "Sphinx>=4.2.0",
    ],
)
