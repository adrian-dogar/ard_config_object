from setuptools import setup, find_packages
import pathlib

CWD = pathlib.Path(__file__).parent

README = (CWD / "README.md").read_text()

setup(
    name='ard-config-object',
    version='0.2.2',
    url='https://github.com/adrian-dogar/ard_config_object',
    author='Adrian Ruben Dogar',
    author_email='adrian.dogar@gmail.com',
    description='Manage configuration objects with secrets',
    long_description=README,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[
        "pyyaml",
        "python-dotenv",
    ],
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)