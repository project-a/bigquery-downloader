
def MARA_CONFIG_MODULES():
    from bigquery_downloader import config
    return [config]

def MARA_CLICK_COMMANDS():
    from bigquery_downloader import cli
    return [cli.download_data]
