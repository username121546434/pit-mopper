"""Has all classes related to the menubar"""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from typing import Iterable, TYPE_CHECKING
from .types import MenubarItem, MenubarSeperator, MenubarCommand

if TYPE_CHECKING:
    from typing_extensions import Unpack

TABWIDTH = len('\t'.expandtabs())


def pad_with_tabs(s,maxlen):
    # https://stackoverflow.com/a/1746241/19581763
    return s + "\t" * int((maxlen-len(s)-1)/TABWIDTH+1)


class SubMenu:
    """Acts as a submenu for the `CustomMenuBar` class"""
    def __init__(self):
        self._popup = None
        self._menubutton: list[MenubarItem] = []
        self.label: tk.Label | None = None
        self.parent: CustomMenuBar | None = None
        self._open = False
        self.bg = 'white'
        self.fg = 'black'
        self.active_bg = 'blue'
        self.active_fg = self.fg

    def on_popup(self, *_):
        """Called to show the menubar"""
        assert self.parent and self.label
        for label in self.parent._lb_list:
            if label.menu._open:
                if label.menu is self:
                    self.destroy()
                    return
                else:
                    label.menu.destroy()
        if not self._open:
            x, y, height = self.label.winfo_rootx(), self.label.winfo_rooty(), self.label.winfo_height()

            self._popup = tk.Toplevel(self.label.master, bg=self.label.cget('bg'))
            self._popup.overrideredirect(True)
            self._popup.geometry(f'+{x}+{y + height}')
            self._popup.bind('<Button-1>', self._on_command)
            self._popup.config(bg=self.bg, padx=1, pady=1)

            biggest_label = 0
            for kwargs in self._menubutton:
                if len(kwargs.get('label', 'None')) > biggest_label:
                    biggest_label = len(kwargs.get('label', 'None'))
            self.max_len = biggest_label + (8 - biggest_label % 8)

            self.num = 0
            for kwargs in self._menubutton:
                if kwargs.get(tk.SEPARATOR, False):
                    self._add_separator()
                else:
                    self._add_command(kwargs) # type: ignore
                self.num += 1
            del self.num
            self._popup.bind('<Leave>', self._leave)
            self._popup.bind('<FocusOut>', self.destroy)
            self._open = True
        
    def add_checkbutton(self, **kwargs: Unpack[MenubarCommand]):
        """Add a checkbutton, accepts same arguments as `add_command` but `variable` is a required argument now"""
        kwargs[tk.CHECKBUTTON] = True
        self._menubutton.append(kwargs)

    def add_command(self, **kwargs: Unpack[MenubarCommand]):
        """
        Add a command to the menubar.

        Parameters
        ----------
        `label`: The label of this item
        `command`: The command that is executed when button is clicked
        `accelerator`: The accelerator for this item

        Any other parameters will be added to the `MenuButton` instance
        """
        self._menubutton.append(kwargs)
    
    def _add_separator(self):
        ttk.Separator(self._popup, orient='horizontal').grid(row=self.num, sticky=tk.NSEW, column=0)
    
    def add_separator(self):
        """Add a seperator"""
        self._menubutton.append(MenubarSeperator(separator=True))

    def _add_command(self, kwargs: MenubarCommand):
        command = kwargs.get('command', None)
        checkbutton = kwargs.get(tk.CHECKBUTTON, False)
        var = kwargs.get('variable', None)
        accelerator = kwargs.get('accelerator', None)
        label = kwargs.get('label')

        mb = tk.Menubutton(self._popup, text=label,
                           bg=self.bg,
                           fg=self.fg,
                           activebackground=self.active_bg,
                           activeforeground=self.active_fg,
                           borderwidth=0,
                           anchor='w',
                        )
        mb.config(text=f'{pad_with_tabs(label, self.max_len)}  {accelerator if accelerator is not None else ""}')
        
        mb._command = command # type: ignore
        if checkbutton:
            mb._var = var # type: ignore
            if var.get(): # type: ignore
                mb.config(text=f'✔ {mb.cget("text")}')
            mb.bind('<Button-1>', lambda e: self._on_command(e, True))
        else:
            mb.bind('<Button-1>', self._on_command)
        mb.grid(sticky=tk.NSEW, row=self.num, column=0)

    def _on_command(self, event: tk.Event, checkbutton: bool=False):
        assert self._popup
        w = event.widget
        if isinstance(w, ttk.Separator):
            return

        if w._command is not None:
            self._popup.master.after(1, w._command)
        if checkbutton:
            w._var.set(not w._var.get())
        
        self.destroy()
    
    def _leave(self, event: tk.Event):
        assert self._popup

        _, height_xy = self._popup.winfo_geometry().split('x')
        _, x, y = height_xy[1:].split('+')
        x, y = int(x), int(y)
        if event.widget is self._popup and \
        (event.x < x or event.x > self._popup.winfo_width() or
        event.y < y or event.y > self._popup.winfo_height()):
            self.destroy()
    
    def destroy(self, _=None):
        """Close the submenu, if it is open"""
        if not self._open:
            return
        assert self._popup
        self._popup.destroy()
        self._popup = None
        self._open = False
    
    def _pop(self, index: int | None=None):
        if index is None:
            self._menubutton.pop()
        else:
            self._menubutton.pop(index)
    
    def pop(self, index: int | None | Iterable[int | None]):
        """Pop one element from self at `index`.

        If `index` is `None`, then remove the last element.

        If `index` is an iterable, then it will remove all elements in the iterable"""
        if isinstance(index, int) or index is None:
            self._pop(index)
        else:
            for i in index:
                self._pop(i)
    
    @property
    def is_open(self):
        """Whether the menu window is open or not"""
        return self._open

    @property
    def window(self):
        """The `TopLevel` that this menu is associated with, if it is open"""
        return self._popup


class _LabelTypeHint(tk.Label):
    """Label used for type-hinting in IDE's"""
    menu: SubMenu


class CustomMenuBar(tk.Frame):
    """
    Used as the menubar for Pit Mopper, taken from https://stackoverflow.com/a/63208829/19581763
    """
    def __init__(self, master=None, cnf={}, **kw):
        """Arguments are: `foreground` and overbackground"""
        kw = tk._cnfmerge((cnf, kw)) # type: ignore
        kw['relief'] = kw.get('relief', 'raised')
        self._fg = kw.pop('fg', kw.pop('foreground', 'black'))
        self._over_bg = kw.pop('overbackground', 'blue')
        super().__init__(master=master, **kw)
        self._lb_list: list[_LabelTypeHint] = []
        self.config(highlightthickness=0)
    
    def _on_press(self, label, command=None):
        """Internal function.\n
        This is called when a user clicks on a menubar."""
        label.menu.on_popup()
        if command: command()  # Calls the function passed to `add_menu` method.
    
    def _on_hover(self, event: tk.Event):
        """Internal function.
        
        This is called when a label is being hovered on"""
        if not isinstance(event.widget, tk.Label):
            return
        event.widget.config(bg=self._over_bg)
        
        for label in self._lb_list:
            if label.menu._open and label.menu is not event.widget:
                label.menu.destroy() # Remove the currently open menubar
                event.widget.menu.on_popup() # type: ignore
                break
    
    def _on_leave(self, event: tk.Event):
        """Internal function.
        
        This is called when a label stops being hovered on"""
        event.widget.config(bg=self['bg'])
    
    def add_menu(self, title, menu: SubMenu, command=None):
        """Add menu labels."""
        l = tk.Label(self, text=title, fg=self._fg, bg=self['bg'], padx=2, pady=2)
        l.pack(side='left')
        l.bind('<Enter>', self._on_hover)
        l.bind('<Leave>', self._on_leave)
        l.menu = menu  # type: ignore
                       # Easy to access menu with the instance 
                       #   of the label saved in the `self._lb_list`
        menu.label = l
        menu.parent = self
        l.bind('<1>', lambda e: self._on_press(l, command))
        self._lb_list.append(l) # type: ignore
    
    def remove_menu(self, menu: SubMenu):
        new_list = []
        for label in self._lb_list:
            if label.menu is menu:
                label.destroy()
            else:
                new_list.append(label)
        self._lb_list = new_list
    
    def change_bg_fg(self, bg=None, fg=None, sub_bg='white', sub_fg='black', sub_overbg='blue'):
        """Changes the background/foreground of the menu"""
        if not bg == None:
            self.config(bg=bg)
        if not fg == None:
            self._fg = fg
        for l in self._lb_list:
            l.config(bg=self['bg'], fg=self._fg)
            menu: SubMenu = l.menu
            menu.bg = sub_bg
            menu.fg = sub_fg
            menu.active_bg = sub_overbg
    
    def iter_children(self):
        for label in self._lb_list:
            yield label.menu


def demo():
    root = tk.Tk()
    root.geometry('200x200')
    mb = CustomMenuBar(root)
    mb.pack(side='top', expand=1, fill='x', anchor='n')
    theme = tk.BooleanVar(root)

    filemenu = SubMenu()
    filemenu.add_command(label='New', accelerator='Ctrl-N')
    filemenu.add_command(label='Open', accelerator='Ctrl-O')
    filemenu.add_separator()
    filemenu.add_command(label='Export')
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=root.quit, accelerator='Ctrl-Q')

    editmenu = SubMenu()
    editmenu.add_command(label='Copy', accelerator='Ctrl-C')
    editmenu.add_command(label='Paste', accelerator='Ctrl-V')
    editmenu.add_separator()
    editmenu.add_checkbutton(label='Change Theme', accelerator='Ctrl-D', variable=theme, command=lambda: (mb.change_bg_fg('red', 'white', 'black', 'white'), print(theme.get())))

    mb.add_menu('File', filemenu)
    mb.add_menu('Edit', editmenu)

    root.mainloop()

if __name__ == "__main__":
    demo()