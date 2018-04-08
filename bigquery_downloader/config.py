"""Configuration of queries against big query data sets"""

import datetime
import pathlib


class DataSet:
    def __init__(self, query_file_path: pathlib.Path = None, json_credentials_path: pathlib.Path = None,
                 data_dir: pathlib.Path = None, output_file_name: str = None, replacements: {str: str} = None,
                 use_legacy_sql: bool = None, first_date: datetime.date = None):
        """
        A query to download to local files for a range of dates.

        The files for each date be form:
            `{data_dir}/year/month/day/{output_file_name}`

        Args:
            query_file_path: The path for the sql file to run.
            json_credentials_path: The path to a google cloud credentials json file
            data_dir: The path where to store results
            output_file_name: The filename of each output file
            replacements: A dictionary of string replacements {replace: with}
            use_legacy_sql: When true, then the bigquery "legacy sql" is used
            first_date: The first day for which to download data
        """
        self.query_file_path = query_file_path or pathlib.Path('/path/to/query.sql')
        self.json_credentials_path = json_credentials_path or pathlib.Path('/path/to/big-query-credentials.json')
        self.output_file_name = output_file_name or 'exported.csv.gz'
        self.replacements = replacements or {}
        self.use_legacy_sql = use_legacy_sql or False
        self.first_date = first_date or datetime.date(2010, 1, 1)
        self.data_dir = data_dir or pathlib.Path('/tmp/bigquery/')

    def __repr__(self) -> str:
        return '{' + ',\n  '.join([f'{key}={value}' for key, value in self.__dict__.items()]) + '}'


def data_sets() -> [DataSet]:
    """A list of data sets to download from BigQuery"""
    return [DataSet()]
