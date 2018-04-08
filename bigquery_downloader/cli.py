"""Command line interface for BigQuery downloader"""

import datetime
import pathlib

import click
from bigquery_downloader import config, downloader


@click.command()
@click.option('--query_file_path', help='The path for the sql file to run.', type=click.Path(exists=True))
@click.option('--json_credentials_path', help='The path to a google cloud credentials json file.',
              type=click.Path(exists=True))
@click.option('--data_dir', help='The path where to store results.', type=click.Path(exists=True))
@click.option('--output_file_name', help='The filename of each output file, e.g. "subfolder/data.csv.gz".',
              type=click.STRING)
@click.option('--use_legacy_sql', help='When true, then the bigquery "legacy sql" is used, default: False.',
              type=click.BOOL)
@click.option('--first_date', help='The first day for which to download data, e.g. "2010-01-01"', type=click.STRING)
def download_data(**kwargs):
    """
    Downloads a list of data sets from bigquery.

    When no option is specified, the defaults from the config module are used instead
    """
    if any(kwargs.values()):
        if kwargs['first_date']:
            kwargs['first_date'] = datetime.datetime.strptime(kwargs['first_date'], "%Y-%m-%d").date()
        for arg in ['query_file_path', 'json_credentials_path', 'data_dir']:
            if kwargs[arg]:
                kwargs[arg] = pathlib.Path(kwargs[arg])

        config.data_sets = lambda: [config.DataSet(**kwargs)]

    downloader.download_data()
