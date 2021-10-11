from setuptools import setup, find_packages

with open('README.rst') as file:
    readme = file.read()

with open('LICENSE') as file:
    license = file.read()

setup(
    name='deposition',
    version='1.0.0-alpha',
    description='Molecular dynamics wrapper for deposition simulations',
    long_description=readme,
    author='M. J. Cyster',
    author_email='martincyster@fastmail.com',
    url='https://github.com/mmtn/deposition',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
