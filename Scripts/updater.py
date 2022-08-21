import os
from random import randint
import webbrowser
import requests
from packaging.version import Version
from tkinter import *
from tkinter.ttk import Progressbar
from zipfile import ZipFile
from tkinter import messagebox
from markdown import Markdown
from io import StringIO

from Scripts.constants import VERSION
from .network import check_internet


def unmark_element(element, stream=None):
    if stream is None:
        stream = StringIO()
    if element.text:
        stream.write(element.text)
    for sub in element:
        unmark_element(sub, stream)
    if element.tail:
        stream.write(element.tail)
    return stream.getvalue()


# patching Markdown
Markdown.output_formats["plain"] = unmark_element
__md = Markdown(output_format="plain")
__md.stripTopLevelTags = False


def md_to_text(text):
    return __md.convert(text)

def check_for_updates(app_quit):
    if not check_internet():
        messagebox.showerror('No internet', 'You can only check for updates with an internet connection')
        return
    response = requests.get('https://api.github.com/repos/username121546434/pit-mopper/releases')
    response.raise_for_status()
    latest_version = response.json()[0]["tag_name"]
    body = md_to_text(response.json()[0]['body'])

    if Version(latest_version) > Version(VERSION):
        window = Toplevel()
        window.title('Update Available')
        choice = BooleanVar(window)

        text = Text(window, height=len(body.splitlines()), width=max(len(line) for line in [line.strip() for line in body.splitlines()]))
        text.focus()
        text.insert('end', f'You have version {VERSION} but {latest_version} is available. Do you want to update?\nPatch notes are below.\n\n{body}')
        text.config(state='disabled')
        text.pack()

        Checkbutton(window, onvalue=True, offvalue=False, variable=choice, text='Update?').pack()

        Button(window, text='Continue', command=window.destroy).pack()
        window.master.wait_window(window)
    else:
        messagebox.showinfo(title='Update', message='There are no updates available')
        return
    
    if os.name == 'posix' and choice.get():
        messagebox.showinfo('Update', 'Automatic updates are not supported on Linux, but you will be taken to the download link')
        webbrowser.open('https://github.com/username121546434/pit-mopper/releases/latest')

    elif os.name == 'nt' and choice.get():
        messagebox.showinfo(title='Update', message='Press "Ok" to update Pit Mopper')
        if os.path.exists('unins000.exe'):
            download_zip = False
        else:
            download_zip = True

        response = requests.get('https://api.github.com/repos/username121546434/pit-mopper/releases')
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
        file = os.path.expanduser(f'~\\Downloads\\{filename}')
        total_size = int(download.headers.get('content-length'))
        increment = (1 / total_size) * 100
        with open(file, 'wb') as f:
            for data in download.iter_content(chunk_size=1000):
                progress['value'] += increment * len(data)
                f.write(data)
                progress_window.update()
        progress_window.destroy()
        bat_file = os.path.join(os.getenv('TEMP'), 'Pit Mopper Update.bat')
        if download_zip:
            with ZipFile(file) as zip_file:
                dir = filename[:-3]
                dir = os.path.expanduser(f'~\\Downloads\\{dir}')
                zip_file.extractall(dir)
            os.remove(file)
            with open(bat_file, 'w') as bat:
                bat.write(f'''@echo off
timeout 3
robocopy /MOV /MIR {dir} "{os.getcwd()}"
rmdir {dir} /S /Q
(goto) 2>nul & del "%~f0"''')
        else:
            tempfile = os.path.join(os.getenv('TEMP'), f'{randint(34856485, 34534345345445)}.txt')
            _, tempfile_name = os.path.split(tempfile)
            with open(tempfile, 'w') as _:
                pass
            with open(bat_file, 'w') as bat:
                bat.write(f'''@echo off
timeout 3
"{os.path.abspath('./unins000.exe')}" /SILENT /SUPPRESSMSGBOXES
copy {tempfile} {os.getcwd()}
if %errorlevel% == 1 (
    {file} /DIR="{os.getcwd()}" /SILENT /SUPPRESSMSGBOXES /NOCANCEL /FORCECLOSEAPPLICATIONS /ALLUSERS
) else (
    del /q {os.path.join(os.getcwd(), tempfile_name)}
    {file} /DIR="{os.getcwd()}" /SILENT /SUPPRESSMSGBOXES /NOCANCEL /FORCECLOSEAPPLICATIONS /CURRENTUSER
)
del /q {file}
del /q {tempfile}
(goto) 2>nul & del "%~f0"''')
        os.startfile(bat_file)
        app_quit()
    else:
        messagebox.showinfo(title='Update Rejected', message='You have rejected the update')
