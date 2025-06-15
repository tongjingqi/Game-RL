# spider.pyw

#!/usr/bin/python3
# spider.pyw

'''
Spider solitaire.  
'''

from model import Model, Stats, SummaryStats
from view import View, StatsDialog
import tkinter as tk
from tkinter.messagebox import showerror, showinfo, askokcancel
from datetime import datetime
import sys, os
from utils import ScrolledList

FMT  = '%Y_%m_%d_%H_%M_%S'      # format strings for datetime objects
FMT2 = '%x %X'

helpText = '''
OBJECTIVE
Spider is played with eight decks of 13 spade cards each, totaling 104 unique cards with multiple copies. The objective is to arrange each of the ten waste piles in sequence from the King down to the Ace. When a suit is arranged in sequence, it may be removed to a foundation pile. If all suits are moved to the foundations, the game is won.

SETUP
There are ten waste piles. The leftmost four initially have six cards each, and the remaining six initially have five cards each. The remaining 104 cards are placed in the stock. There are also eight foundation piles. All the interesting action takes place in the waste piles. 

MOVING CARDS
Any card may be placed on top of another card that is one higher in rank. For example, a 7 may be moved on top of an 8, or a Queen on top of a King; suits and colors don't matter for this purpose. A run of cards in the same suit in descending sequence is available for play, but you don't have to move all of them. For example, if the top three cards of some pile are the 3, 4, and 5 of Spades, you can move the 3 on top of a 4, the 3 and 4 on top of a 5, or all three on top of a 6. 

If you have an empty waste pile, you can move any available cards for play onto the empty pile.  

If a move leaves a face-down card showing on the top of a pile, that card is turned face up.

COMPLETE SUITS
Once you have arranged a complete suit in order from the King down to the Ace, it can be removed to a foundation pile, but you needn't do so immediately. This allows you to use it to help organize other piles in the waste piles.

DEALING
When there are no more moves you care to make, you can deal another row. You deal by clicking the stock. This deals one card face up on each of the waste piles. You may not deal if there is an empty waste pile.

STRATEGY
- Turn as many cards as possible face up.
- Form runs of the same suit in descending order.
- Utilize empty waste piles (spaces) strategically.
- Prioritize moves involving higher-ranked cards to unlock more possibilities.

VARIANTS 
In circular spider solitaire, a King may be placed on top of an Ace and a run may have a King on top of an Ace, allowing for extended sequences.
'''

class FileList(ScrolledList):
    def __init__(self, parent, dataDir, **kwargs):
        super().__init__(parent, [], **kwargs)
        files = (f[:-4] for f in os.listdir(dataDir) if f.endswith('.spi'))
        dates = [datetime.strptime(f, FMT) for f in files]
        dates.sort()
        dates = [d.strftime(FMT2) for d in dates]
        self.listbox.insert(0, *dates)
        self.listbox.see(tk.END)
        self.listbox.selection_set(tk.END)
        
    def runCommand(self, selection):
        # LoadFileDialog will handle it
        pass
            
class LoadFileDialog:
    # Modified slightly from SimpleDialog in tkinter/simpledialog.py
    # The kwargs will be passed to the listbox
    def __init__(self, master, dataDir, **kwargs):
        self.root = tk.Toplevel(master)
        self.answer = None         # the file name
        buttons = ('Okay', 'Cancel')
        okay = 0
        cancel = 1
        title = 'Load Game'
        self.root.title(title)
        self.root.iconname(title)
        frame = tk.Frame(self.root)
        frame.pack()        
        self.listbox = FileList(frame, dataDir, **kwargs)
        self.listbox.pack(expand=1, fill=tk.BOTH)
        self.cancel = cancel
        self.okay = okay
        for num in range(len(buttons)):
            s = buttons[num]
            b = tk.Button(frame, text=s,
                       command=(lambda self=self, num=num: self.done(num)))
            b.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.root.protocol('WM_DELETE_WINDOW', self.wm_delete_window)
        self._set_transient(master)
    
    def _set_transient(self, master, relx=0.5, rely=0.3):
        widget = self.root
        widget.withdraw() # Remain invisible while we figure out the geometry
        widget.transient(master)
        widget.update_idletasks() # Actualize geometry information
        if master.winfo_ismapped():
            m_width = master.winfo_width()
            m_height = master.winfo_height()
            m_x = master.winfo_rootx()
            m_y = master.winfo_rooty()
        else:
            m_width = master.winfo_screenwidth()
            m_height = master.winfo_screenheight()
            m_x = m_y = 0
        w_width = widget.winfo_reqwidth()
        w_height = widget.winfo_reqheight()
        x = m_x + (m_width - w_width) * relx
        y = m_y + (m_height - w_height) * rely
        if x + w_width > master.winfo_screenwidth():
            x = master.winfo_screenwidth() - w_width
        elif x < 0:
            x = 0
        if y + w_height > master.winfo_screenheight():
            y = master.winfo_screenheight() - w_height
        elif y < 0:
            y = 0
        widget.geometry("+%d+%d" % (x, y))
        widget.deiconify() # Become visible at the desired location
    
    def go(self):
        self.root.wait_visibility()
        self.root.grab_set()
        self.root.mainloop()
        self.root.destroy()
        return self.answer
    
    def wm_delete_window(self):
        self.done(self.cancel)
    
    def done(self, num):
        if num == self.okay:
            item = self.listbox.get(tk.ACTIVE)
            self.answer = datetime.strptime(item, FMT2).strftime(FMT) + '.spi'
        self.root.quit()
      
class Spider:
    def __init__(self):
        self.model = Model()
        self.view = View(self, self.quit, width=950, height=1000, scrollregion=(0, 0, 950, 3000))
        self.makeHelp()
        self.circular = tk.BooleanVar()
        self.open = tk.BooleanVar() 
        self.circular.set(False)
        self.open.set(False)
        self.circular.trace('w', self.optionChanged)
        self.open.trace('w', self.optionChanged)
        self.makeMenu()
        self.view.start()      #  start the event loop
        
    def deal(self):
        model = self.model
        self.saveStats()
        model.deal(self.circular.get(), self.open.get())
        self.view.show()
        
    def makeHelp(self):
        top = self.helpText = tk.Toplevel()
        top.transient(self.view.root)
        top.protocol("WM_DELETE_WINDOW", top.withdraw)
        top.withdraw()
        top.resizable(False, True)
        top.title("Spider Help")
        f = tk.Frame(top)
        self.helpText.text = text = tk.Text(f, height=30, width=80, wrap=tk.WORD)
        text['font'] = ('Helvetica', 12, 'normal')
        text['bg'] = '#ffef85'
        text['fg'] = '#8e773f'
        scrollY = tk.Scrollbar(f, orient=tk.VERTICAL, command=text.yview)
        text['yscrollcommand'] = scrollY.set
        text.grid(row=0, column=0, sticky='NS')
        f.rowconfigure(0, weight=1)
        scrollY.grid(row=0, column=1, sticky='NS')
        tk.Button(f, text='Dismiss', command=top.withdraw).grid(row=1, column=0)
        f.grid(sticky='NS')
        top.rowconfigure(0, weight=1)
        text.insert(tk.INSERT, helpText)
        
    def makeMenu(self):
        top = self.view.menu
        
        game = tk.Menu(top, tearoff=False)
        game.add_command(label='New', command=self.deal)
        game.add_command(label='Save', command=self.save)
        game.add_command(label='Open', command=self.load)
        game.add_command(label='Quit', command=self.quit)
        top.add_cascade(label='Game', menu=game)
           
        options = tk.Menu(top, tearoff=False)
        options.add_checkbutton(label='Circular', variable=self.circular)
        options.add_checkbutton(label='Open',  variable=self.open)
        top.add_cascade(label='Options', menu=options)
    
        stats = tk.Menu(top, tearoff=False)
        stats.add_command(label='Display Stats', command=self.showStats)
        stats.add_command(label='Clear Stats', command=self.clearStats)
        top.add_cascade(label='Stats',   menu=stats)
           
        top.add_command(label='Help', command=self.showHelp)  
         
    def notdone(self):
        showerror('Not implemented', 'Not yet available') 
          
    def save(self):
        model = self.model
        now = datetime.today().strftime(FMT)
        dataDir = os.path.join(os.path.dirname(sys.argv[0]), 'data')
        if not os.path.exists(dataDir):
            os.mkdir(dataDir)
        saveFile = os.path.join(dataDir, now + '.spi')
        model.save(saveFile)
        
    def load(self):
        try:
            dataDir = os.path.join(os.path.dirname(sys.argv[0]), 'data')
            filename = LoadFileDialog(self.view.root, dataDir, bg='lemonChiffon').go()
            if filename:
                self.model.load(os.path.join(dataDir, filename))
                self.view.show()
        except FileNotFoundError:
            showerror('No Files to Open', f'Directory\n{dataDir}\ndoes not exist')      
          
    def showHelp(self):
        self.helpText.deiconify()
        self.helpText.text.see('1.0')  
    
    def optionChanged(self, *args):
        if self.model.undoStack or self.model.redoStack:
            showinfo("Option Changed", "Changes Will Take Effect Next Game")
        else:
            self.model.reset(self.circular.get(), self.open.get())
            self.model.adjustOpen(self.open.get())
            self.view.show()
        
    def saveStats(self):
        model = self.model
        if model.stock:             # not all cards dealt means game abandoned
            return                     
        if model.statsSaved:    # don't save stats for same game twice
            return
        model.statsSaved = True
        stats = model.stats()
        with open(os.path.join(os.path.dirname(sys.argv[0]), 'stats.txt'), 'a') as fout:
            fout.write(f'{stats.variant} {stats.win} {stats.moves} {stats.up} {stats.up1} {stats.date}\n')  
          
    def loadStats(self):
        '''
        Returns None if no stats file found, or [] for empty stats file.
        Returns a list containing summary stats.
        '''
        try:
            with open(os.path.join(os.path.dirname(sys.argv[0]), 'stats.txt')) as fin:
                stats = [Stats(*s.strip().split()) for s in fin.readlines()]
            std = [stat for stat in stats if stat.variant == 'Standard']
            circ = [stat for stat in stats if stat.variant == 'Circular']
            show = [stat for stat in stats if stat.variant == 'Open']
            both = [stat for stat in stats if stat.variant == 'Both']
            stats = []
            for s in (std, circ, show, both):
                if s:
                    stats.append(self.summary(s)) 
            return stats
        except IOError:
            return None
        
    def summary(self, stats):
        '''
        Pre: stats is not empty
        '''
        variant = stats[0].variant 
        games = len(stats)
        wins = len([s for s in stats if s.win == 'True'])
        moves = sum(int(s.moves) for s in stats) // games
        up = sum(int(s.up) for s in stats) // games
        up1 = sum(int(s.up1) for s in stats) // games
        return SummaryStats(variant, games, wins, moves, up, up1)
      
    def showStats(self):
        stats = self.loadStats()
        self.view.showStats(stats)
        
    def clearStats(self):
        if askokcancel("Confirm Clear Stats", "Do you really want to erase all stats to date?"): 
            open(os.path.join(os.path.dirname(sys.argv[0]), 'stats.txt'), 'w').close()
    
    def quit(self):
        self.saveStats()
        self.view.root.quit()
          
if __name__ == "__main__":
  Spider()
