from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    readme = f.read()

setup(
    name='ard-config-object',
    version='0.3.1',
    url='https://github.com/adrian-dogar/ard_config_object',
    author='Adrian Ruben Dogar',
    author_email='adrian.dogar@gmail.com',
    description='Manage configuration objects with secrets',
    long_description=readme,
    long_description_content_type="text/markdown",
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