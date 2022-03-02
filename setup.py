import setuptools
from setuptools import find_namespace_packages

with open('README.md', encoding="utf8") as file:
    long_description = file.read()

setuptools.setup(
    name='analytics_adobe_azure',
    version='0.0.3',
    author='AlexZ',
    author_email='alexdataanalyst@gmail.com',
    description='Automate Adobe Analytics Reports API v2 requests to export to Azure Blob Storage programmatically.',
    url='https://github.com/alexcargfs/Adobe-Azure-Analytics-report-api-v2.0',
    download_url = 'https://github.com/alexcargfs/Adobe-Azure-Analytics-report-api-v2.0/archive/refs/tags/v0.0.3.tar.gz',    
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