from setuptools import setup, find_packages

setup(
    name='bigquery-downloader',
    version='1.0.1',

    description="A script for downloading BigQuery data sets that are organized by day",

    install_requires=[
        'bigquery-python>=1.14.0',
        'click>=6.0',
        'pyOpenSSL>=17.5.0'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
        'console_scripts': [
            'download-bigquery-data=bigquery_downloader.cli:download_data'
        ]
    },
    python_requires='>=3.6'
)
