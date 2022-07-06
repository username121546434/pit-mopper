import requests
import os
import subprocess
from tkinter import messagebox
from tkinter import *
from zipfile import ZipFile
from tkinter.ttk import Progressbar
import sys

if os.path.exists('unins000.exe'):
    download_zip = False
    subprocess.run(['unins000.exe', '/SILENT'])
else:
    download_zip = True

response = requests.get('https://api.github.com/repos/username121546434/minesweeper-python/releases')
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
progress_window = Tk()
progress_window.title('Updater')
download = requests.get(download_url, stream=True)
progress = Progressbar(progress_window, mode='determinate', length=200)
progress.pack()
total_size = int(download.headers.get('content-length'))
increment = (1 / total_size) * 100
with open(os.path.expanduser(f'~\\Downloads\\{filename}'), 'wb') as f:
    for data in download.iter_content(chunk_size=1000):
        progress['value'] += increment * len(data)
        f.write(data)
        progress_window.update()
progress_window.destroy()
if download_zip:
    with ZipFile(os.path.expanduser(f'~\\Downloads\\{filename}')) as zip_file:
        dir = filename[:-3]
        dir = os.path.expanduser(f'~\\Downloads\\{dir}')
        zip_file.extractall(dir)
    messagebox.showinfo(title='Update', message=f'''The update has completed, you can find it in {dir}. You can delete the previous update or keep it in case you get issues with the new one.''')
else:
    os.startfile(os.path.expanduser(f'~\\Downloads\\{filename}'))
    sys.exit()