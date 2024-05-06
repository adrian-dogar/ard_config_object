from setuptools import setup, find_packages

setup(
    name='ard_config_object',
    version='0.1.0',
    url='https://github.com/adi-do/ard_config_object',
    author='Adrian Ruben Dogar',
    author_email='adrian.dogar@gmail.com',
    description='Manage configuration objects with secrets',
    packages=find_packages(),
    install_requires=['python-dotenv', 'json'],
)