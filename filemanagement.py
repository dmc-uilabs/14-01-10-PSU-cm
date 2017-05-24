import urllib.request
import zipfile
import os

def download_tdp_data(url):
        urllib.request.urlretrieve(url, "TDPdata.zip")
        print("TDP Data Downloaded")

def unzip_directories():

    directory = os.fsencode('./')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".zip"):
            zip_ref = zipfile.ZipFile(filename, 'r')
            if filename.startswith("TDP"):
                zip_ref.extractall('./TDPdata')
            else:
                zip_ref.extractall('./')
            zip_ref.close()
            continue
        else:
            continue

def upload_report():
    import time
    timestamp = int(time.time())

    with open('credentials.json') as json_data:
        d = json.load(json_data)
        access_key = d['accessKeyId']
        secret_key = d['secretAccessKey']

    from boto.s3.connection import S3Connection
    conn = S3Connection(access_key, secret_key)

    bucket = conn.get_bucket('psubucket01')

    from boto.s3.key import Key
    k = Key(bucket)
    file_name = str(timestamp)+'report.pdf'
    k.key = file_name
    k.set_contents_from_filename('./report.pdf')

    return file_name