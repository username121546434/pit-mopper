import os
import sys
import requests
from packaging.version import Version
from tkinter import *
from tkinter import messagebox
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
        os.startfile('updater.exe')
        sys.exit()
    else:
        try:
            _ = choice
        except NameError:
            messagebox.showinfo(title='Update', message='There are no updates available')
        else:
            messagebox.showinfo(title='Update Rejected', message='You have rejected the update')
