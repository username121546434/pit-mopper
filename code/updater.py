import os
import sys
import requests
from pkg_resources import parse_version
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from zipfile import ZipFile


def check_for_updates(current_version: str, download_zip: bool, master: Tk | Toplevel):
    response = requests.get('https://api.github.com/repos/username121546434/minesweeper-python/releases')
    response.raise_for_status()
    latest_version = response.json()[0]["tag_name"][1:]
    is_beta = response.json()[0]["prerelease"]
    choice = messagebox.askyesno(title='Update Available',
                            message=f'You have version {current_version} but {latest_version} is available. Do you want to update?\nIs Beta: {is_beta}')

    if parse_version(latest_version) > parse_version(current_version) and choice:
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
        download_url = asset['browser_download_url']
        filename = asset['name']
        download = requests.get(download_url, stream=True)
        window = Toplevel(master)
        window.title('Updater')
        progress = Progressbar(window, mode='determinate', length=200)
        progress.pack()
        total_size = int(download.headers.get('content-length'))
        increment = (1 / total_size) * 100
        with open(os.path.expanduser(f'~\\Downloads\\{filename}'), 'wb') as f:
            for data in download.iter_content(chunk_size=1000):
                progress['value'] += increment * len(data)
                f.write(data)
                window.update()
        window.destroy()
        if download_zip:
            with ZipFile(os.path.expanduser(f'~\\Downloads\\{filename}')) as zip_file:
                dir = filename[:-3]
                dir = os.path.expanduser(f'~\\Downloads\\{dir}')
                zip_file.extractall(dir)
            messagebox.showinfo(title='Update', message=f'''The update has completed, you can find it in {dir}. You can delete the previous update or keep it in case you get issues with the new one.''')
        else:
            master.destroy()
            os.startfile(os.path.expanduser(f'~\\Downloads\\{filename}'))
            sys.exit()
    else:
        if not choice:
            messagebox.showinfo(title='Update', message='There are no updates available')
