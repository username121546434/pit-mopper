from tkinter import Toplevel, Label
import os
from tkinter.ttk import Progressbar
from typing import Iterable, Sized, TypeVar, Sequence
from .functions import change_theme_of_window

T = TypeVar('T', Sized, Sequence)


def progress_bar_window(iterable: Iterable[T], total_size: int, text_format: str='Loading... {}', title: str='Loading...') -> Iterable[T]:
    """Creates a new tkinter `Toplevel` and creates a progress bar for a task

    Args:
        `iterable`: An iterable to use as a task
        `total_size`: The total length of the iterable
        `text_format`: A format string that will be used for the label
        `title`: The title to be used for the window

    Returns: An iterator that will automatically update the progress in the loopp
    """
    progress_window = Toplevel()
    progress_window.config(padx=20, pady=20)
    progress_window.title(title)
    if os.name == 'nt':
        progress_window.master.attributes('-disabled', True) # type: ignore
        progress_window.attributes('-disabled', True)

    label = Label(progress_window, text=text_format.format('0%'))
    label.pack()
    progress = Progressbar(progress_window, mode='determinate', length=200)
    progress.pack()

    increment = (1 / total_size) * 100
    percent = 0.0

    change_theme_of_window(progress_window)

    for data in iterable:
        progress['value'] += increment * len(data)
        percent += len(data) / total_size
        label.config(text=text_format.format(f'{percent:.2%}'))
        progress_window.update()
        yield data

    progress_window.destroy()
