import os
import sys
import requests
from packaging.version import Version
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from zipfile import ZipFile
from markdown import Markdown
from io import StringIO


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

def check_for_updates(current_version: str, download_zip: bool, master: Tk | Toplevel):
    try:
        response = requests.get('https://api.github.com/repos/username121546434/minesweeper-python/releases')
    except requests.exceptions.ConnectionError as error:
        messagebox.showerror(title='Failed to Check for Updates', message=f'''This is most likely because you do not have an internet connection.
If you do have an internet connection, then here are details so you can report a bug:

{error}''')
        return None
    response.raise_for_status()
    latest_version = response.json()[0]["tag_name"]
    body = md_to_text(response.json()[0]['body'])

    if Version(latest_version) > Version(current_version):
        window = Toplevel(master)
        window.title('Update Available')
        choice = BooleanVar(window)

        text = Text(window, height=len(body.splitlines()), width=max(len(line) for line in [line.strip() for line in body.splitlines()]))
        text.focus()
        text.insert('end', f'You have version {current_version} but {latest_version} is available. Do you want to update?\nPatch notes are below.\n\n{body}')
        text.pack()

        Checkbutton(window, onvalue=True, offvalue=False, variable=choice, text='Update?').pack()

        Button(window, text='Continue', command=window.destroy).pack()
        master.wait_window(window)

    if Version(latest_version) > Version(current_version) and choice.get():
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
        progress_window = Toplevel(master)
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
            master.destroy()
            os.startfile(os.path.expanduser(f'~\\Downloads\\{filename}'))
            sys.exit()
    else:
        try:
            _ = choice
        except NameError:
            messagebox.showinfo(title='Update', message='There are no updates available')
        else:
            messagebox.showinfo(title='Update Rejected', message='You have rejected the update')
