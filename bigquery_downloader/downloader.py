import datetime
import gzip
import sys

from bigquery_downloader import config


def download_data():
    """Downloads all configured data sets"""
    from google.cloud import bigquery
    from google.api_core import retry
    from google.api_core.exceptions import ClientError

    for data_set in config.data_sets():
        print('Initializing BigQuery client')

        bigquery_client = bigquery.Client.from_service_account_json(
            json_credentials_path=data_set.json_credentials_path)

        first_date = data_set.first_date
        last_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)

        # load query and apply pattern substitutions
        query = open(data_set.query_file_path, 'r', encoding="utf-8").read().strip()
        for replace, _with in data_set.replacements.items():
            query = query.replace(replace, _with)

        # iterate all days in reverse order
        for day in [last_date - datetime.timedelta(x) for x in range((last_date - first_date).days + 1)]:
            path = data_set.data_dir / day.strftime('%Y/%m/%d') / data_set.output_file_name
            if path.exists():
                print(f'Skipping {path}, already exists')
                continue

            if not path.parent.exists():
                path.parent.mkdir(parents=True)

            print(f'Next file: {path}')

            day_query = query.replace('DAY_ID', f'{day:%Y%m%d}')
            print(f'----------------------------\n{day_query}\n----------------------------')
            sys.stdout.write('Waiting for result ')
            try:
                query_options = bigquery.job.QueryJobConfig(use_legacy_sql=data_set.use_legacy_sql)
                # API request
                job = bigquery_client.query(day_query, job_config=query_options, retry=retry.Retry(deadline=60))

                # get all the rows in the results. The iterator automatically handles pagination
                results = job.result()

                print(f'\nDownloading {results.total_rows} rows')

                print(f'Writing {path}')
                fields = [field.name for field in results.schema]
                with gzip.open(path, "wt", encoding='utf-8') as file:
                    if results:
                        file.write('\t'.join(fields) + '\n')
                        for row in results:
                            file.write('\t'.join(
                                [str(col).replace('\t', '\\t') if col is not None else '' for col in
                                 row.values()]) + '\n')

            except ClientError as e:
                response_status_code = int(e.code)
                if response_status_code == 404 and data_set.ignore_404s:
                    for error in e.errors:
                        sys.stderr.write('ERROR: {}'.format(error['message']))
                else:
                    raise e
