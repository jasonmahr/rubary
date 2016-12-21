"""TkInter GUI.

Jason Mahr
"""


from algorithm import solve
from constants import *
from cube import Cube
from random import random
from selectors import Geometric, Rank
import Tkinter as tk
from validate import is_solved, is_valid


def normal(scale=1):
    """Generates a font and font size tuple based on the given scale."""
    return (FONT, int(scale * BASE_SIZE))


def bold(scale=1):
    """Generates a bold font and size tuple based on the given scale."""
    return (FONT, int(scale * BASE_SIZE), 'bold')


class Rows:
    """For use with grid. When called, outputs the relative row."""
    def __init__(self):
        self.row = 1
    def __call__(self, relative_increment):
        """There is a clear behavior for this class."""
        self.row += relative_increment
        return self.row


class Error:
    """Error message for the cube net."""
    def __init__(self, master, row, column):
        # Sets up a label at the specified coordinate with a StringVar.
        self.text = tk.StringVar()
        self.label = tk.Label(master, textvariable=self.text, fg=ERROR,
                              font=normal())
        self.label.grid(row=row, column=column, sticky=tk.W)
        self.off()

    def off(self):
        self.text.set('')

    def invalid(self):
        self.text.set(TAB + TAB + 'Invalid cube! Verify your colors.')

    def solved(self):
        self.text.set(TAB + TAB + 'Nothing to do! Try using Scramble.')

    def destroy(self):
        self.label.destroy()
        

class Net:
    """A cube net. This is what the user uses to input their Rubik's
    Cube. In popular usage, a cube net is a 2D shape that folds into a
    cube.
    """
    def __init__(self, master, row, column, columnspan, center_colors, error):
        # The selected color will replace clicked tiles
        self.center_colors = center_colors
        self.selected_color = L
        self.cube = Cube()

        self.master = master
        self.row = row
        self.column = column
        self.cs = columnspan

        # Holds a pointer to the error to be able to dismiss messages
        self.error = error
        self.canvas = None
        self.refresh()

    def refresh(self):
        """Creates a new canvas to reflect an updated cube."""
        self.destroy()
        self.new()
        self.draw()

    def destroy(self):
        if self.canvas:
            self.canvas.destroy()
    
    def new(self):
        self.canvas = tk.Canvas(self.master, width=WIDTH, height=HEIGHT)
        self.canvas.bind('<Button-1>', self.update)
        self.canvas.grid(row=self.row, column=self.column, columnspan=self.cs)

    def draw(self):
        """Draws all tiles, including center and panel tiles."""
        for side in range(6):
            
            # Get the color associated with the side
            c = self.center_colors[side]

            # Draw the center tile
            ((x1, x2), (y1, y2)) = CENTERS[side]
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline=BKGD)
            
            # Draw this side's tile in the panel
            ((x1, x2), (y1, y2)) = PANEL[side]
            line = EMPH if self.selected_color == side else BKGD
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline=line)

            # Draw this side's label
            (x, y) = LABEL_XY[side]
            font = normal(1.8) if self.selected_color == side else normal(1.8)
            self.canvas.create_text(x, y, text=LABEL[side], fill=c, font=font)

            # Draw this side's tiles around the center tile
            for index in range(8):
                ((x1, x2), (y1, y2)) = TILES[side][index]
                c = self.center_colors[self.cube.get((side, index))]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=c,
                                             outline=BKGD)

    def update(self, event):
        """Handles a mouse click and edits the cube as appropriate."""

        # Turn off errors, if they exist, after the user interacts
        self.error.off()
        for side in range(6):
            
            # If a panel tile was clicked, update `self.selected_color`
            ((x1, x2), (y1, y2)) = PANEL[side]
            if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                self.selected_color = side
                return self.refresh()

            # If a tile was clicked, update its color
            for index in range(8):
                ((x1, x2), (y1, y2)) = TILES[side][index]
                if x1 <= event.x <= x2 and y1 <= event.y <= y2:
                    self.cube.set((side, index), self.selected_color)
                    return self.refresh()

    def reset(self):
        """Reset functionality."""
        self.error.off()
        self.cube.reset()
        self.refresh()

    def scramble(self):
        """Scramble functionality."""
        self.error.off()
        self.cube.scramble()
        self.refresh()

    def get_cube(self):
        """If cube is ready, output for solving and destroy canvas."""
        if not is_valid(self.cube):
            return self.error.invalid()
        if is_solved(self.cube):
            return self.error.solved()
        self.error.destroy()
        self.destroy()
        return self.cube


class Application(tk.Frame):
    """This is the Tk application."""
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.master.minsize(width=MINWIDTH, height=MINHEIGHT)
        self.grid()
        self.rows = Rows()

        """Initialize selector here."""
        self.selector = Geometric() if GEOMETRIC_SELECTION else Rank()
        self.create_widgets()


    def destroy_widgets(self, widgets):
        """Helper function for destroying several widgets at once."""
        for widget in widgets:
            widget.destroy()


    def create_widgets(self):
        """Creates the initial widgets of the application."""

        # Welcome
        title = 'Welcome to Rubary.'
        self.title = tk.Label(self, text=title, font=bold(1.6))
        self.title.grid(row=self.rows(0), column=0, sticky=tk.W)

        intro = "Rubary evolves Rubik's Cube solutions."
        self.intro = tk.Label(self, text=intro, font=bold(1.2))
        self.intro.grid(row=self.rows(1), column=0, sticky=tk.W)

        # Step 1
        self.step1 = tk.Label(self, text='1. Select Colors', font=bold(1.4))
        self.step1.grid(row=self.rows(1), column=0, sticky=tk.W)

        # Note 1
        n1 = (TAB + "A face's color is the color of its center, which cannot "
              + "move. Each side must have\n" + TAB + "a different color.")
        self.n1 = tk.Label(self, text=n1, font=normal(1.2), justify=tk.LEFT)
        self.n1.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)

        # Frame

        self.f1 = tk.Frame(self)
        self.f1.grid(row=self.rows(1), column=0)

        # Side Labels

        self.f1.left = tk.Label(self.f1, text='Left', font=normal())
        self.f1.left.grid(row=self.rows(0), column=0, sticky=tk.W)

        self.f1.right = tk.Label(self.f1, text='Right', font=normal())
        self.f1.right.grid(row=self.rows(1),column=0, sticky=tk.W)

        self.f1.front = tk.Label(self.f1, text='Front', font=normal())
        self.f1.front.grid(row=self.rows(1), column=0, sticky=tk.W)

        self.f1.back = tk.Label(self.f1, text='Back', font=normal())
        self.f1.back.grid(row=self.rows(1),column=0, sticky=tk.W)

        self.f1.up = tk.Label(self.f1, text='Top', font=normal())
        self.f1.up.grid(row=self.rows(1), column=0, sticky=tk.W)

        self.f1.down = tk.Label(self.f1, text='Bottom', font=normal())
        self.f1.down.grid(row=self.rows(1),column=0, sticky=tk.W)

        # Input fields

        self.left_color = tk.StringVar()
        self.f1.lc = apply(tk.OptionMenu, (self.f1, self.left_color) + COLORS)
        self.f1.lc.grid(row=self.rows(-5), column=1, sticky=tk.W)
        self.f1.lc.config(width=DROPDOWN_WIDTH)

        self.right_color = tk.StringVar()
        self.f1.rc = apply(tk.OptionMenu, (self.f1, self.right_color) + COLORS)
        self.f1.rc.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.f1.rc.config(width=DROPDOWN_WIDTH)

        self.front_color = tk.StringVar()
        self.f1.fc = apply(tk.OptionMenu, (self.f1, self.front_color) + COLORS)
        self.f1.fc.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.f1.fc.config(width=DROPDOWN_WIDTH)

        self.back_color = tk.StringVar()
        self.f1.bc = apply(tk.OptionMenu, (self.f1, self.back_color) + COLORS)
        self.f1.bc.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.f1.bc.config(width=DROPDOWN_WIDTH)

        self.up_color = tk.StringVar()
        self.f1.uc = apply(tk.OptionMenu, (self.f1, self.up_color) + COLORS)
        self.f1.uc.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.f1.uc.config(width=DROPDOWN_WIDTH)

        self.down_color = tk.StringVar()
        self.f1.dc = apply(tk.OptionMenu, (self.f1, self.down_color) + COLORS)
        self.f1.dc.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.f1.dc.config(width=DROPDOWN_WIDTH)

        # Buttons

        self.cont = tk.Button(self, text='Continue', command=self.s2, bg='red')
        self.cont.grid(row=self.rows(1), column=11)

        self.cancel = tk.Button(self, text='Cancel', command=self.quit)
        self.cancel.grid(row=self.rows(0), column=12)

        # Steps 2 and 3

        self.step2 = tk.Label(self, text='2. Input Cube', font=bold(1.4))
        self.step2.grid(row=self.rows(1), column=0, sticky=tk.W)

        self.step3 = tk.Label(self, text="3. Solve Cube", font=bold(1.4))
        self.step3.grid(row=self.rows(1), column=0, sticky=tk.W)


    def s2(self):
        """Moves the GUI to Step 2."""

        # Collect information
        selected_colors = [self.left_color.get(), self.right_color.get(),
                           self.front_color.get(), self.back_color.get(),
                           self.up_color.get(), self.down_color.get()]
        if (len(set([color for color in selected_colors if color])) != 6):
            return
        
        # Save information
        for i in range(6):
            if selected_colors[i] == 'White':
                selected_colors[i] = 'White Smoke'
            elif selected_colors[i] == 'Silver':
                selected_colors[i] = 'Light Gray'
            elif selected_colors[i] == 'Gray':
                selected_colors[i] = 'Dark Gray'
            elif selected_colors[i] == 'Black':
                selected_colors[i] = 'Gray25'

        # Destroy Step 1 widgets
        self.destroy_widgets([self.n1, self.f1, self.cont, self.cancel,
                              self.step3])

        # Note 2
        n2 = (TAB + 'Click to paste the selected color. Centers are '
              + 'fixed, Scramble first resets, and\n' + TAB
              + 'Solve is disabled for invalid cube states.')
        self.n2 = tk.Label(self, text=n2, font=normal(1.2), justify=tk.LEFT)
        self.n2.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)

        # Initialize error and canvas
        error = Error(self, self.rows(2), 0)
        net = Net(self, self.rows(-1), 0, FULL, selected_colors, error)

        # Buttons

        self.scramble = tk.Button(self, text='Scramble', command=net.scramble)
        self.scramble.grid(row=self.rows(1), column=1, sticky=tk.W)

        self.reset = tk.Button(self, text='Reset', command=net.reset)
        self.reset.grid(row=self.rows(0), column=2, sticky=tk.W)
        
        self.solv = tk.Button(self, text='Solve', command=lambda: self.s3(net))
        self.solv.grid(row=self.rows(0), column=3, sticky=tk.W)

        self.cancel = tk.Button(self, text='Cancel', command=self.quit)
        self.cancel.grid(row=self.rows(0), column=4, sticky=tk.W)

        # Step 3 Label and update

        self.step3 = tk.Label(self, text="3. Solve Cube", font=bold(1.4))
        self.step3.grid(row=self.rows(1), column=0, sticky=tk.W)

        self.master.update()


    def s3(self, net):
        """Moves the GUI to Step 3 if cube is valid and not solved."""

        # Get the cube. If cube is invalid or solved, return.
        cube = net.get_cube()
        if not cube:
            return
        
        # Destroy Step 2 widgets
        self.destroy_widgets([self.n2, self.scramble, self.reset, self.solv,
                              self.cancel])
        
        # Note 3
        n3 = tk.StringVar()
        n3.set(TAB + 'Initializing solve . . .')
        self.n3 = tk.Label(self, textvariable=n3, font=normal(1.2))
        self.n3.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)

        self.master.update()

        # Mailbox for updating algorithm status
        def mailbox(generations, phase, fitness, time):
            status = (('Generation {}: We are on phase {} of 7 with fitness '
                       + 'of {}. Time: {} s.').format(generations, phase,
                       fitness, round(time, 1)))
            n3.set(TAB + status)
            self.master.update()
        
        # Solve cube
        solution = solve(cube, self.selector, mailbox)

        # Print status
        solution_len = len(solution[2])
        first = int(solution_len * 0.38)
        second = int(solution_len * 0.7)
        status = (('A solution was found in {} generations! It took {} '
                   + 'seconds and contains {} moves:').format(
                   solution[1], round(solution[0], 1), solution_len))
        n3.set(TAB + status)


        """End of Thistlethwaite is all half turns, which take up two
        characters each, so divide the string unevenly.
        """
        moves1 = TAB + TAB + ' '.join(solution[2][:first])
        moves2 = TAB + TAB + ' '.join(solution[2][first:second])
        moves3 = TAB + TAB + ' '.join(solution[2][second:])

        self.m1 = tk.Label(self, text=moves1, font=normal(1.2))
        self.m1.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)

        self.m2 = tk.Label(self, text=moves2, font=normal(1.2))
        self.m2.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)
        
        self.m3 = tk.Label(self, text=moves3, font=normal(1.2))
        self.m3.grid(row=self.rows(1), column=0, columnspan=FULL, sticky=tk.W)
      
        # Exit button
        self.exit_btn = tk.Button(self, text='Exit', command=self.quit)
        self.exit_btn.grid(row=self.rows(1), column=1, sticky=tk.W)
        self.master.update()


# Run app
app = Application()
app.master.title('RUBARY')
app.mainloop()
