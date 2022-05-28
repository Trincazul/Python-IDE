# -------------------------- # imports # -------------------------- #
import tkinter as tk
import tkinter.font as tkFont
import tkinter.filedialog as tkFileDialog
import threading
import glob
import math
import platform
import subprocess
import os
import tempfile
import functools

# -------------------------- # window setup # -------------------------- #
window = tk.Tk()
window.tk.call('tk', 'scaling', 2.0)
window.geometry(f'{window.winfo_screenwidth()}x{window.winfo_screenheight()}')
window.title('Python IDE')

# -------------------------- # config_vars # -------------------------- #
OPEN_FILE = '_main.py'

TOOLBAR_HEIGHT = 40
TOOLBAR_ITEM_WIDTH = 1 
TOOLBAR_COLOR = '#0e1525'
TOOLBAR_TEXT_COLOR = '#FFFFFF'
TOOLBAR_FONT_SIZE = '7'
TOOLBAR_FONT = tkFont.Font(family='Terminal', size=TOOLBAR_FONT_SIZE)
TOOLBAR_DROPDOWN_COLOR = '#3f495f'

EDITOR_BG_COLOR = '#1c2333'
EDITOR_FONT_SIZE = '8'
EDITOR_FONT = tkFont.Font(family='Terminal', size=EDITOR_FONT_SIZE)
EDITOR_FONT_COLOR = '#FFFFFF'
EDITOR_CURSOR_COLOR = '#0079f2'
EDITOR_SCROLLBAR_COLOR = '#3c445c'
EDITOR_LINEDISPLAY_WIDTH = 3
EDITOR_LINEDISPLAY_FG = '#ffffff'
EDITOR_HIGHLIGHT_COLOR = '#004182'
EDITOR_SIDE = 'left'

OUTPUT_BG_COLOR = '#1c2333'
OUTPUT_FONT = tkFont.Font(family='Terminal', size=EDITOR_FONT_SIZE)
OUTPUT_FONT_COLOR = '#FFFFFF'
OUTPUT_SCROLLBAR_COLOR = '#3c445c'
OUTPUT_HIGHLIGHT_COLOR = '#004182'
OUTPUT_SIDE = 'top'

SYNTAX_KEYWORDS_COLOR = '#0079f2'
SYNTAX_FUNCTIONS_COLOR = '#c9c236'
SYNTAX_OPERATIONS_COLOR = '#9fc2e5'
SYNTAX_CLASS_COLOR = '#ff3154'
SYNTAX_SELF_COLOR = '#ff004c'
SYNTAX_DUNDER_METHOD_COLOR = '#4437a6'
SYNTAX_TYPE_COLOR = '#845692'
SYNTAX_COMMENT_COLOR = '#0c6324'
SYNTAX_BOOL_COLOR = '#9fc2e5'
SYNTAX_STRING_COLOR = '#dea670'

MISC_DIVIDER_THICKNESS = 10
MISC_TAB_WIDTH = 2
MISC_FULLSCREEN = True
MISC_AUTOINDENT = True

UPDATE_LINE_FREQ = 100#ms
UPDATE_SYNTAX_HIGHLIGHTING_FREQ = 50#ms

HIDDEN_FILES = ['poetry.lock','replit.nix','pyproject.toml']

PYTHON_SYNTAX = {
  ('int','str','list','set','dict','tuple','bool','float','bytes',
   'memoryview','bytearray','object'): SYNTAX_TYPE_COLOR,
  ('and', 'exec', 'not', 'assert', 'finally',
   'or', 'break', 'for', 'pass', 'from', 'in',
   'print', 'continue', 'global', 'raise', 'def',
   'if', 'return', 'del', 'import', 'try', 'is', 
   'match','case','async','while'): SYNTAX_KEYWORDS_COLOR, 
  ("abs","aiter","all","any","anext","ascii",
   "breakpoint","bin","callable","chr","classmethod",
   "compile","complex","delattr","dir","divmod","enumerate","eval",
   "exec","exit","filter","format","frozenset","getattr","globals",
   "hasattr","hash","help","hex","id","input","isinstance",
   "issubclass","iter","len","locals","map","max",
   "min","next","oct","open","ord","pow","print","property",
   "range","repr","reversed","round","setattr","slice","sorted",
   "staticmethod","sum","super","type","vars","zip"): SYNTAX_FUNCTIONS_COLOR,
  ('=','+','-','/','//','%','*','**','>','<','!=','&','^','|'): SYNTAX_OPERATIONS_COLOR,
  ('#',): SYNTAX_COMMENT_COLOR,
  ('True','False','None','NotImplemented'): SYNTAX_BOOL_COLOR,
  ('class',): SYNTAX_CLASS_COLOR, 
  ('self',):SYNTAX_SELF_COLOR,
  ("__abs__", "__add__", "__and__", "__call__", "__class__", "__cmp__",
   "__coerce__", "__complex__", "__contains__", "__del__", "__delattr__",
   "__delete__", "__delitem__", "__delslice__", "__dict__", "__div__",
   "__divmod__", "__eq__", "__float__", "__floordiv__", "__ge__", "__get__",
   "__getattr__", "__getattribute__", "__getitem__", "__getslice__", "__gt__",
   "__hash__", "__hex__", "__iadd__", "__iand__", "__idiv__", "__ifloordiv__",
   "__ilshift__", "__imod__", "__imul__", "__index__", "__init__",
   "__instancecheck__", "__int__", "__invert__", "__ior__", "__ipow__",
   "__irshift__", "__isub__", "__iter__", "__itruediv__", "__ixor__", "__le__",
   "__len__", "__long__", "__lshift__", "__lt__", "__metaclass__", "__mod__",
   "__mro__", "__mul__", "__ne__", "__neg__", "__new__", "__nonzero__",
   "__oct__", "__or__", "__pos__", "__pow__", "__radd__", "__rand__", "__rcmp__",
   "__rdiv__", "__rdivmod__", "__repr__", "__reversed__", "__rfloordiv__", "__rlshift__",
   "__rmod__", "__rmul__", "__ror__", "__rpow__", "__rrshift__", "__rshift__", "__rsub__",
   "__rtruediv__", "__rxor__", "__set__", "__setattr__", "__setitem__",
   "__setslice__", "__slots__", "__str__", "__sub__", "__subclasscheck__", "__truediv__", 
   "__unicode__", "__weakref__", "__xor__"): SYNTAX_DUNDER_METHOD_COLOR,
  ('Exception','StopIteration','SystemExit','StandardError','ArithmeticError',
   'OverflowError','FloatingPointError','ZeroDivisionError','AssertionError',
   'AttributeError','EOFError','ImportError','KeyboardInterrupt','LookupError',
   'IndexError','KeyError','NameError','UnboundLocalError','EnvironmentError',
   'IOError','OSError','SyntaxError','IndentationError','SystemError','SystemExit','TypeError',
   'ValueError','RuntimeError','NotImplementedError'):'#ffffff',
  ('"',"'"):SYNTAX_STRING_COLOR
}

# -------------------------- # functions # -------------------------- #
def find_all(data, substr):
  matches = []
  if substr.__class__ is not tuple:
    substr = (substr,)
  r = 0
  for i,v in enumerate(substr):
    while str(v) in data:
      c = data.index(v)
      matches.append((c+r,c+len(v)+r))
      data = data.replace(v, '', 1)
      r += len(v)
  return matches if matches else None

def open_file():
  global OPEN_FILE
  save()
  f = tkFileDialog.askopenfile()
  OPEN_FILE = f.name
  editor.delete('1.0','end')
  load()

def open_sidebar_file(event):
  global OPEN_FILE
  save()
  OPEN_FILE = event.widget.get(event.widget.curselection()[0])
  editor.delete('1.0','end')
  load()

def run():
  save()
  with open(OPEN_FILE, 'r') as file:
    with tempfile.TemporaryFile() as tempf:
        proc = subprocess.Popen(['python3', OPEN_FILE], stdout=tempf)
        proc.wait()
        tempf.seek(0)
        terminal_output = tempf.read().decode('utf-8')
    output.config(state='normal')
    output.delete('1.0', 'end')
    output.insert('1.0', str(terminal_output))
    output.config(state='disabled')

def load():
  try: file = open(OPEN_FILE,'r')
  except: file = open(OPEN_FILE,'w')
  finally: file.close()
  with open(OPEN_FILE) as file:
    editor.insert('1.0', file.read())

def save():
  with open(OPEN_FILE,'w') as file:
    file.write(editor.get('1.0', 'end'))
    
def save_and_close():
  save()
  window.after_cancel(syntax_highlighter__process)
  window.destroy()
window.protocol("WM_DELETE_WINDOW", save_and_close) #if closed normally

def save_as():
  with tkFileDialog.asksaveasfile(mode='w', defaultextension=".py") as file:
    if file is None:
        return
    file.write(str(editor.get(1.0, 'end')))
    file.close()
# -------------------------- # toolbar # -------------------------- #
toolbar = tk.Menu(master=window, bg=TOOLBAR_COLOR, bd=0, fg=TOOLBAR_TEXT_COLOR, font=TOOLBAR_FONT)

toolbar_file_button = tk.Menu(toolbar, tearoff=0,bg=TOOLBAR_DROPDOWN_COLOR,bd=0,font=TOOLBAR_FONT)
toolbar_file_button.add_command(label="New", command=None)
toolbar_file_button.add_command(label="Open", command=open_file)
toolbar_file_button.add_command(label="Save", command=save)
toolbar_file_button.add_command(label="Save as...", command=save_as)
toolbar_file_button.add_command(label="Close", command=None)
toolbar_file_button.add_separator()
toolbar_file_button.add_command(label="Exit", command=save_and_close)
toolbar.add_cascade(label="File", menu=toolbar_file_button)

toolbar_edit_button = tk.Menu(toolbar, tearoff=0,bg=TOOLBAR_DROPDOWN_COLOR,bd=0,font=TOOLBAR_FONT)
toolbar.add_cascade(label="Edit", menu=toolbar_edit_button)

toolbar_run_button = tk.Menu(toolbar, tearoff=0,bg=TOOLBAR_DROPDOWN_COLOR,bd=0,font=TOOLBAR_FONT)
toolbar_run_button.add_separator()
toolbar_run_button.add_command(label="Run Program", command=run)
toolbar.add_cascade(label="Run", menu=toolbar_run_button)

window.config(menu=toolbar)

# -------------------------- cont master ---------------------------#
edit_and_out_master = tk.LabelFrame(width=1,bg=EDITOR_BG_COLOR,highlightthickness=0,bd=0)
edit_and_out_master.pack(side='right',expand=True, fill='both')

# -------------------------- # editor # -------------------------- #
editor_container = tk.LabelFrame(width=1, height=1,master=edit_and_out_master, bg=EDITOR_BG_COLOR,highlightthickness=0,bd=0)
editor_container.pack(side='top',fill='both',expand=True)
lines_container = tk.Text(master=editor_container, font=EDITOR_FONT,
    fg=EDITOR_LINEDISPLAY_FG, bg=EDITOR_BG_COLOR,highlightthickness=0,bd=0,
    width=EDITOR_LINEDISPLAY_WIDTH,height=1, relief='flat')
lines_container.pack(side='left',fill='y', expand=False)
lines_container.configure(state="disabled")
scrollbar = tk.Scrollbar(master=editor_container,bd=0, borderwidth=0,
    troughcolor=EDITOR_BG_COLOR,highlightthickness=0,
    bg=EDITOR_SCROLLBAR_COLOR, relief='flat')
scrollbar.pack(side='right',fill='y')
editor = tk.Text(width=1, height=1,master=editor_container,bg=EDITOR_BG_COLOR,highlightthickness=0,bd=0,
    font=EDITOR_FONT, fg=EDITOR_FONT_COLOR,insertbackground=EDITOR_CURSOR_COLOR, 
    tabs=(EDITOR_FONT.measure(' ' * MISC_TAB_WIDTH),), yscrollcommand=scrollbar.set,
    selectbackground=EDITOR_HIGHLIGHT_COLOR,selectforeground=EDITOR_FONT_COLOR)
scrollbar.config(command=editor.yview)
editor.pack(side=EDITOR_SIDE, expand=True, fill='both')

# -------------------------- # dir sidebar # -------------------------- #
current_working_dir = glob.glob(f'{os.getcwd()}')[0]
current_working_dir_contents = glob.glob(f'{os.getcwd()}/*')
current_working_dir_contents = [v.replace(current_working_dir+('/' if os.path.isfile(v) else ''), '') for i, v in enumerate(current_working_dir_contents)]
for i, v in enumerate(current_working_dir_contents):
  if os.path.isdir(current_working_dir+v):
    current_working_dir_contents.remove(v)
  if v.strip().lower() in HIDDEN_FILES:
    current_working_dir_contents.remove(v.strip().lower())
directory_container = tk.LabelFrame(bg=OUTPUT_BG_COLOR,highlightthickness=0,bd=0)
directory_container.pack(side='left',fill='both')

dir_box = tk.Listbox(master=directory_container, font=EDITOR_FONT,
    fg=EDITOR_LINEDISPLAY_FG, bg=EDITOR_BG_COLOR,highlightthickness=0,bd=0, relief='flat')
for i,v in enumerate(current_working_dir_contents):
  dir_box.insert(0,v)
dir_box.pack()
dir_box.bind("<<ListboxSelect>>", functools.partial(open_sidebar_file))
dragbar1 = tk.Frame(bg=TOOLBAR_COLOR,highlightthickness=0,bd=0,width=MISC_DIVIDER_THICKNESS)
dragbar1.pack(fill='both',side='right')
# -------------------------- # editor linecounter # -------------------------- #
last = int(editor.index('end-1c').split('.')[0]) 
def update_line_counter():
  global last
  if int(editor.index('end-1c').split('.')[0]) != last:
    last = int(editor.index('end-1c').split('.')[0]) 
    lines_container.configure(state="normal")
    lines_container.delete('1.0','end')
    for i in range(last):
      lines_container.insert('1.0',str(last-i)+'\n')
    lines_container.configure(state="disabled")
  window.after(UPDATE_LINE_FREQ,update_line_counter)
window.after(UPDATE_LINE_FREQ,update_line_counter)

# -------------------------- # output # -------------------------- #
output_container = tk.LabelFrame(master=edit_and_out_master, bg=OUTPUT_BG_COLOR,highlightthickness=0,bd=0)
output_scrollbar = tk.Scrollbar(master=output_container,bd=0, borderwidth=0,
    troughcolor=OUTPUT_BG_COLOR,highlightthickness=0,
    bg=OUTPUT_SCROLLBAR_COLOR, relief='flat')
output_scrollbar.pack(side='right',fill='y')
dragbar = tk.Frame(master=edit_and_out_master,bg=TOOLBAR_COLOR,highlightthickness=0,bd=0,height=MISC_DIVIDER_THICKNESS)
dragbar.pack(fill='both')
output = tk.Text(width=1, height=1,master=output_container,bg=OUTPUT_BG_COLOR,highlightthickness=0,bd=0,
    font=OUTPUT_FONT, fg=OUTPUT_FONT_COLOR,selectbackground=OUTPUT_HIGHLIGHT_COLOR,
    selectforeground=OUTPUT_FONT_COLOR)
output.pack(side=OUTPUT_SIDE,fill='both')
output_container.pack(side='bottom',fill='both',expand=True)
output_scrollbar.config(command=output.yview)
output.configure(state="disabled")

# -------------------------- # syntax highlighting # -------------------------- #
SYNTAX_HIGHLIGHTING = {}
for i,v in enumerate(PYTHON_SYNTAX.keys()):
  for i,c in enumerate(v):
    SYNTAX_HIGHLIGHTING.update({c:PYTHON_SYNTAX[v]})

def syntax_highlight():
  for i,v in enumerate(SYNTAX_HIGHLIGHTING.keys()):
    if v.__class__ is tuple:
      for i,c in enumerate(v):
        try: editor.tag_remove(c, '1.0', 'end')
        except: pass
    else:
      try:editor.tag_remove(v, '1.0', 'end')
      except:pass
  data = [(find_all(editor.get("1.0",'end-1c'),v),SYNTAX_HIGHLIGHTING[v],v) for i,v in enumerate(SYNTAX_HIGHLIGHTING.keys())]
  text = editor.get("1.0",'end-1c')
  for i,v in enumerate(data):
    if v[0] is not None:
      if '#' not in v[2] and "'" not in v[2] and '"' not in v[2]:
        for r,c in enumerate(v[0]):
            editor.tag_add(v[2], f'1.0 + {str(c[0])}c', f'1.0 + {str(c[1])}c')            
        editor.tag_configure(v[2], foreground=v[1])
      elif '#' in v[2]:
        for r,c in enumerate(v[0]):
          editor.tag_add(v[2], f'1.0 + {str(c[0])}c', f'1.0 + {str(c[0])}c lineend')    
        editor.tag_configure(v[2], foreground=v[1]) 
      elif "'" in v[2] or '"' in v[2]:
        str_count = 0
        for r,c in enumerate(v[0]):
          str_count += 1
          if str_count % 2 == 1:
            try:
              comp = f'1.0 + {str(v[0][r+1][1])}c'
            except IndexError:
              comp = 'end'
            editor.tag_add(v[2], f'1.0 + {str(c[0])}c', f'{comp}')    
        editor.tag_configure(v[2], foreground=v[1]) 
  return window.after(UPDATE_SYNTAX_HIGHLIGHTING_FREQ,syntax_highlight)
syntax_highlighter__process = window.after(UPDATE_SYNTAX_HIGHLIGHTING_FREQ,syntax_highlight)

def error_highlighter():
  editor.tag_config("error", bgstipple="@squiggly.xbm", background='red')
  
# -------------------------- # mainloop # -------------------------- #
if MISC_FULLSCREEN:
  window.wm_attributes('-fullscreen', True)  
load()
window.mainloop()






