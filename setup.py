import setuptools
from setuptools import find_namespace_packages

with open('README.md', encoding="utf8") as file:
    long_description = file.read()

setuptools.setup(
    name='adobe_analytic_API_V2.0-azure',
    version='0.0.2',
    author='AlexZ',
    author_email='alexdataanalyst@gmail.com',
    description='Automate Adobe Analytics Reports API v2 requests to export to Azure Blob Storage programmatically.',
    url='https://github.com/alexcargf/adobe_analytic-azure',
    download_url = 'https://github.com/alexcargf/adobe_analytic-azure/archive/refs/tags/0.0.2.tar.gz',    
    package_dir={'': 'src'},
    packages=find_namespace_packages(where='src'),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'pandas',
        'requests',
        'PyJWT',
        'azure.storage.blob',
        'DateTime',
        'requests-mock',
        'pytest-mock'
    ],
    python_requires='>=3.6',
)