import os
import sys
import requests
from pkg_resources import parse_version
from tkinter import messagebox
from tqdm.gui import tqdm
from zipfile import ZipFile


def download(url, filename):
    download = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        with tqdm(total=int(download.headers.get('content-length'))/1000000) as progress:
            for data in download.iter_content(chunk_size=1000000):
                f.write(data)
                progress.update(len(data)/1000000)
            progress.close()


def check_for_updates(current_version: str, download_zip: bool):
    response = requests.get(
        'https://api.github.com/repos/username121546434/minesweeper-python/releases')
    response.raise_for_status()
    latest_version = response.json()[0]["tag_name"][1:]
    is_beta = response.json()[0]["prerelease"]

    if parse_version(latest_version) > parse_version(current_version) and \
        messagebox.askyesno(title='Update Available',
                            message=f'You have version {current_version} but {latest_version} is available. Do you want to update?\nIs Beta: {is_beta}'):
        messagebox.showinfo(title='Update', message='Press "Ok" to update Minesweeper')
        if download_zip:
            asset = [
                asset
                for asset in response.json()[0]['assets']
                if asset['content_type'] == 'application/x-zip-compressed'
            ][0]
        else:
            asset = [
                asset
                for asset in response.json()[0]['assets']
                if asset['content_type'] == 'application/x-msdownload'
            ][0]
            asset['name'] = os.path.expanduser(r'~\AppData\Local\Temp' + '\\' + asset['name'])
        download_url = asset['browser_download_url']
        filename = asset['name']
        download(download_url, os.path.expanduser(f'~\\Downloads\\{filename}'))
        if download_zip:
            with ZipFile(filename) as zip_file:
                dir = filename[:-3]
                dir = os.path.expanduser(f'~\\Downloads\\{dir}')
                zip_file.extractall(dir)
            messagebox.showinfo(title='Update', message='The update has completed, ')
        else:
            os.system(filename)
            sys.exit()
    else:
        messagebox.showinfo(title='Update', message='There are no updates available')
