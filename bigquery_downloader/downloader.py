import datetime
import gzip
import sys
import time

from bigquery_downloader import config


def download_data():
    """Downloads all configured data sets"""
    import bigquery

    for data_set in config.data_sets():
        print('Initializing BigQuery client')
        bigquery_client = bigquery.get_client(json_key_file=data_set.json_credentials_path,
                                              readonly=True, num_retries=3)

        first_date = data_set.first_date
        last_date = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)

        # load query and apply pattern substitutions
        query = open(data_set.query_file_path, 'r', encoding="utf-8").read().strip()
        for replace, _with in data_set.replacements.items():
            query.replace(replace, _with)

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
            job_id, _ = bigquery_client.query(day_query, use_legacy_sql=data_set.use_legacy_sql)
            while True:
                is_complete, row_count = bigquery_client.check_job(job_id)
                if is_complete:
                    break
                else:
                    sys.stdout.write('.')
                time.sleep(1)

            print(f'\nDownloading {row_count} rows')
            rows = bigquery_client.get_query_rows(job_id)

            print(f'Writing {path}')
            with gzip.open(path, "wt", encoding='utf-8') as file:
                if row_count:
                    file.write('\t'.join(rows[0].keys()) + '\n')
                    for row in rows:
                        file.write('\t'.join(
                            [str(col).replace('\t', '\\t') if col != None else '' for col in row.values()]) + '\n')
