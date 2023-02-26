import glob
import os
import subprocess
import sys
import webbrowser
import requests
from packaging.version import Version
from tkinter import Toplevel, BooleanVar, Checkbutton, Button
from markdown import markdown
from tkinterweb.htmlwidgets import HtmlFrame
import tkinter.messagebox as messagebox

from .prog_bar_tk import progress_bar_window
from .constants import VERSION
from .network import check_internet
import tempfile
import shutil
from .functions import change_theme_of_window


def is_new_update_available() -> tuple[bool, dict]:
    """
    Checks if an update is available

    Returns: A tuple where the first element is whether there is and update available, and the second is the version info
    """
    response = requests.get('https://api.github.com/repos/username121546434/pit-mopper/releases/latest')
    response.raise_for_status()
    latest_version_info = response.json()
    latest_version = latest_version_info["tag_name"]

    return (Version(latest_version) > Version(VERSION), latest_version_info)


def download(download_url: str, extension: str | None=None) -> str:
    """
    Downloads a file from `download_url` and saves it as a temporary file

    Args:
        `download_url`: The url to download the file from
        `extension`: The file extension of the file

    Returns: The path to the file where it was written
    """
    download = requests.get(download_url, stream=True)
    header = download.headers.get('content-length')
    assert header
    total_size = int(header)

    filename = tempfile.mkstemp(suffix=extension)
    f = os.fdopen(filename[0], 'wb')

    try:
        for data in progress_bar_window(download.iter_content(chunk_size=1_000), total_size, 'Downloading... {}'):
            f.write(data)
    finally:
        f.close()
    return filename[1]


def update_windows(app_quit, assets: list):
    messagebox.showinfo(title='Update', message='Press "Ok" to update Pit Mopper')
    download_zip = not os.path.exists('unins0000.exe')

    if download_zip:
        asset = [
            asset
            for asset in assets
            if asset['content_type'] == 'application/x-zip-compressed' # *.zip file
        ][0]
    else:
        asset = [
            asset
            for asset in assets
            if asset['content_type'] == 'application/x-msdownload' # *.exe file
        ][0]
    download_url: str = asset['browser_download_url']
    filename: str = asset['name']
    file_extension = '.' + filename.split('.')[-1]

    installer_or_zip_file = download(download_url, file_extension)

    bat_file = os.path.join(os.getenv('TEMP'), 'Pit Mopper Update.bat') # type: ignore
    if download_zip:
        extract_dir = tempfile.mkdtemp()
        shutil.unpack_archive(installer_or_zip_file, extract_dir, 'zip')
        with open(bat_file, 'w') as bat:
            bat.write(f'''
@echo off
timeout 3 /NOBREAK
del /q "{installer_or_zip_file}"
robocopy /MOV /MIR {extract_dir} "{os.getcwd()}"
rmdir {extract_dir} /S /Q
start "Pit Mopper" "{os.path.join(os.path.split(sys.executable)[0], 'Pit Mopper.exe')}"
(goto) 2>nul & del "%~f0"
''')
    else:
        with open(bat_file, 'w') as bat:
            bat.write(f'''
@echo off
timeout 3 /NOBREAK
"{installer_or_zip_file}" /SILENT /SUPPRESSMSGBOXES /NOCANCEL /FORCECLOSEAPPLICATIONS
del /q "{installer_or_zip_file}"
start "Pit Mopper" "{os.path.join(os.path.split(sys.executable)[0], 'Pit Mopper.exe')}"
(goto) 2>nul & del "%~f0"
''')
    subprocess.Popen(['cmd', '/C', bat_file], creationflags=subprocess.CREATE_NO_WINDOW,
                start_new_session=True)
    app_quit()


def update_ubuntu(app_quit, assets: list):
    messagebox.showinfo(title='Update', message='Press "Ok" to update Pit Mopper')

    asset = [
        asset
        for asset in assets
        if asset['name'].endswith('.tar.gz') and 'Ubuntu' in asset['name']
    ][0]
    download_url: str = asset['browser_download_url']

    file = download(download_url, '.tar.gz')
    curr_dir = os.getcwd()
    tmp_dir = tempfile.mkdtemp()
    extract_dir = os.path.join(tmp_dir, os.path.basename(curr_dir))
    os.mkdir(extract_dir)

    shutil.unpack_archive(file, extract_dir, 'gztar')
    os.remove(file)
    shutil.rmtree(curr_dir)
    shutil.move(extract_dir, os.path.split(curr_dir)[0])
    shutil.rmtree(tmp_dir)

    app_quit()


def check_for_updates(app_quit):
    if not check_internet():
        messagebox.showerror('No internet', 'You can only check for updates with an internet connection')
        return
    update_available, latest_version_info = is_new_update_available()
    body = latest_version_info['body']
    title = latest_version_info['name']

    if update_available:
        window = Toplevel()
        window.title('Update Available')
        choice = BooleanVar(window)

        frame = HtmlFrame(window, messages_enabled=False)

        m_html = f'<center><h1>{title}</h1></center>' + markdown(body,)
        frame.load_html(m_html)
        frame.on_link_click(webbrowser.open)
        frame.pack(fill="both", expand=True)

        Checkbutton(window, onvalue=True, offvalue=False, variable=choice, text='Update?', font=('Arial', 15, 'bold')).pack()

        Button(window, text='Continue', command=window.destroy, font=('Arial', 15)).pack()
        change_theme_of_window(window)
        window.master.wait_window(window)
    else:
        messagebox.showinfo(title='Update', message='There are no updates available')
        return
    
    if os.name == 'posix' and choice.get():
        update_ubuntu(app_quit, latest_version_info['assets'])
    elif os.name == 'nt' and choice.get():
        update_windows(app_quit, latest_version_info['assets'])
    else:
        messagebox.showinfo('Update Rejected', 'You have rejected the update')
        return
