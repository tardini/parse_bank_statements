from tkinter.ttk import Style

frc = '#b0d0b0'  # Frame, Notebook, Checkbutton
tbc = '#eaeaea'  # Toolbar, Button
figc = '#70a0c0' # Figure

sty = Style()
#sty.theme_use('classic')
sty.theme_use('alt')
sty.configure('TNotebook.Tab', background=frc, width=12)
sty.configure('TFrame', background=frc)
sty.configure('TCheckbutton', background=frc)
sty.configure('TButton', background=tbc, width=12)
sty.configure('TLabel', background=frc, width=12)
sty.configure('TEntry', background=frc)

