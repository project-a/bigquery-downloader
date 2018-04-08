# BigQuery Downloader

A Python script for incrementally downloading BigQuery data sets that are organized by day to local csv files. 

## Example 

[There exists](https://mail.python.org/pipermail/distutils-sig/2016-May/028986.html) a public BigQuery data set of [PyPI](https://pypi.python.org) package downloads at [https://bigquery.cloud.google.com/dataset/the-psf:pypi](https://bigquery.cloud.google.com/dataset/the-psf:pypi) (Google login required). It contains for each day since late 2016 data about (almost) each individual package download. 

A query that aggregates download counts per project and a few other attributes could look like this:

```sql
SELECT
  DAY_ID                                               AS day_id,
  CAST(timestamp AS DATE)                              AS date,
  file.project                                         AS project_name,
  file.version                                         AS project_version,
  count(*)                                             AS number_of_downloads,
  REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)") AS python_version,
  details.installer.name                               AS installer_name
FROM `the-psf.pypi.downloadsDAY_ID`
GROUP BY day_id, date, project_name, project_version, python_version, installer_name;
```

Given such a query (e.g. as `pypi-downloads.sql`) and a credentials file (see below), the script incrementally runs the query for each day from a given start date until yesterday (UTC) and stores the result to .csv.gz files. Note the string `DAY_ID` in the `FROM` clause above. It will be replaced by a `'%Y%m%d'` formatted date for each date in the time range.

```bash
download-bigquery-data \
   --first_date='2017-01-01' \
   --query_file_path=pypi-downloads.sql \
   --json_credentials_path=bigquery-credentials.json \
   --output_file_name=pypi/downloads-v1.csv.gz \
   --data_dir=/tmp
```

Output (on Apr 7th 2018 UTC):

```
Initializing BigQuery client
Next file: /tmp/2018/04/06/pypi/downloads-v1.csv.gz
----------------------------
SELECT
  20180406                                              AS day_id,
  CAST(timestamp AS DATE)                              AS date,
  file.project                                         AS project_name,
  file.version                                         AS project_version,
  count(*)                                             AS number_of_downloads,
  REGEXP_EXTRACT(details.python, r"^([^\.]+\.[^\.]+)") AS python_version,
  details.installer.name                               AS installer_name
FROM `the-psf.pypi.downloads20180406`
GROUP BY day_id, date, project_name, project_version, python_version, installer_name;
----------------------------
Waiting for result .........
Downloading 987681 rows
Writing /tmp/2018/04/06/pypi/downloads-v1.csv.gz
Skipping /tmp/2018/04/05/pypi/downloads-v1.csv.gz, already exists
Skipping /tmp/2018/04/04/pypi/downloads-v1.csv.gz, already exists
...
```

Output files that already have been downloaded are not downloaded again. When the query changes, it is recommended to change the output file name to a different name, e.g. `pypi/downloads-v2.csv.gz`.

&nbsp;


## Obtaining BigQuery Credentials

*(Adapted from [https://github.com/ofek/pypinfo](https://github.com/ofek/pypinfo))*

1. Signup or login at [https://bigquery.cloud.google.com](https://bigquery.cloud.google.com). The first TB of queried data each month is for free, then it costs some money (unlikely to be reached by the example).

2. Create a new project at [https://console.developers.google.com/cloud-resource-manager](https://console.developers.google.com/cloud-resource-manager). Any name is fine, e.g. `mara-example-project-bigquery`.
 
3. Enable the BigQuery API at [https://console.cloud.google.com/apis/api/bigquery-json.googleapis.com/overview](https://console.cloud.google.com/apis/api/bigquery-json.googleapis.com/overview). Make sure the correct project is chosen using the drop-down on top. 

4. Follow the instructions at [https://cloud.google.com/storage/docs/authentication#generating-a-private-key](https://cloud.google.com/storage/docs/authentication#generating-a-private-key) to create credentials in JSON format. During creation, choose ``BigQuery User`` as role. Move the file wherever you want (e.g. `bigquery-credentials.json` in the example above). 

&nbsp;

## Installation

(Requires Python 3.6 or later)

Via pip:

```pip install --git+https://github.com/mara/bigquery-downloader.git```


Or: clone the repository, then:

```bash
cd bigquery-downloader
python3 -m venv .venv
.venv/bin/pip install .
```

the script is now available at `.venv/bin/download-bigquery-data`.

&nbsp;


## Usage

```
download-bigquery-data --help
Usage: download-bigquery-data [OPTIONS]

  Downloads a list of data sets from bigquery.

  When no option is specified, the defaults from the config module are used
  instead

Options:
  --query_file_path PATH        The path for the sql file to run.
  --json_credentials_path PATH  The path to a google cloud credentials json
                                file.
  --data_dir PATH               The path where to store results.
  --output_file_name TEXT       The filename of each output file, e.g.
                                "subfolder/data.csv.gz".
  --use_legacy_sql BOOLEAN      When true, then the bigquery "legacy sql" is
                                used, default: False.
  --first_date TEXT             The first day for which to download data, e.g.
                                "2010-01-01"
  --help                        Show this message and exit.
```


