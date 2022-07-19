# https://stackoverflow.com/a/63208829
import tkinter as tk


class CustomMenuBar(tk.Frame):
    def __init__(self, master=None, cnf={}, **kw):
        kw = tk._cnfmerge((cnf, kw))
        kw['relief'] = kw.get('relief', 'raised')
        self._fg = kw.pop('fg', kw.pop('foreground', 'black'))
        self._over_bg = kw.pop('overbackground', 'blue')
        super().__init__(master=master, **kw)
        self._lb_list:list[tk.Label] = []
        self.config(highlightthickness=0)
    
    def _on_press(self, label, command=None):
        """Internal function.\n
        This is called when a user clicks on a menubar."""
        label.menu.post(label.winfo_rootx(), 
            label.winfo_rooty() + label.winfo_height() + 5) # 5 padding (set accordingly)
        if command: command()  # Calls the function passed to `add_menu` method.
    
    def add_menu(self, title, menu, command=None):
        """Add menu labels."""
        l = tk.Label(self, text=title, fg=self._fg, bg=self['bg'], padx=2, pady=2)
        l.pack(side='left')
        l.bind('<Enter>', lambda e: l.config(bg=self._over_bg))
        l.bind('<Leave>', lambda e: l.config(bg=self['bg']))
        l.menu = menu  # Easy to access menu with the instance 
                       #   of the label saved in the `self._lb_list`
        l.bind('<1>', lambda e: self._on_press(l, command))
        self._lb_list.append(l)
    
    def change_bg_fg(self, bg=None, fg=None):
        """Changes the background/foreground of the menu"""
        if not bg == None:
            self.config(bg=bg)
        if not fg == None:
            self._fg = fg
        for l in self._lb_list:
            l.config(bg=self['bg'], fg=self._fg)


def demo():
    root = tk.Tk()
    root.geometry('200x200')
    mb = CustomMenuBar(root)
    mb.pack(side='top', expand=1, fill='x', anchor='n')

    filemenu = tk.Menu(mb)
    filemenu.add_command(label='New')
    filemenu.add_command(label='Open')
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=root.quit)

    editmenu = tk.Menu(mb)
    editmenu.add_command(label='Copy')
    editmenu.add_command(label='Paste')

    mb.add_menu('File', filemenu)
    mb.add_menu('Edit', editmenu)

    root.mainloop()

if __name__ == "__main__":
    demo()   