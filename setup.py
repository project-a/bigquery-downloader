from setuptools import setup, find_packages

setup(
    name='bigquery-downloader',
    version='3.0.0',

    description="A script for downloading BigQuery data sets that are organized by day",

    install_requires=[
        'google-cloud-bigquery>=1.24.0',
        'click>=6.0'
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
