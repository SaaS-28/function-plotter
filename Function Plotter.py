import sympy as sp
import tkinter as tk
import re
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.patches as patches

class FunctionPlotterApp:

    valid_characters = [
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', 
        '(', ')', '+', '-', '*', '/', 'π', 'e', 'e²', 'e³', 'x', 
        'x²', 'x³', '^', 'sin(', 'cos(', 'tan(', '√(', 'ln(',
        'Backspace', 'Shift', 'Control', 'Delete'
    ]

    # Check if input is valid
    def is_valid_char(self, char):
        return char in self.valid_characters or char in ('\x08', 'Shift', 'Control', '\x7f')
    
    # Prevent the insertion of unvalid char
    def on_key_press(self, event):
        char = event.char

        # Handles input like Backspace, Shift, Ctrl, Canc
        if char == '\x08':  # Backspace
            return None
        elif event.keysym in ('Shift_R', 'Shift_L', 'Control_R', 'Control_L'):  # Shift and Ctrl
            return None
        elif char == '\x7f':  # Delete
            return None
        elif not self.is_valid_char(char):
            return "break"  # Blocks unvalid char

        return None  # Allows char

    # Initializes the Tkinter window
    def __init__(self, root):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # If the user closes the app, a function is called
        self.root.title("Function Plotter")

        self.initialize_plot()
        self.create_gui()

    # Initializes the canvas and figure (axes)
    def initialize_plot(self):
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Function used to process the math expression given by the user and plot it using SymPy
    def plot_function(self):
        expression = self.expr_entry.get()

        try:
            expr_graph_text = expression

            # Add the multiplication symbol between numbers and variables
            # Pattern to find numbers followed by x or e (for example, 2x, 3e, etc.)
            expression = re.sub(r'(\d)([xeπ])', r'\1*\2', expression)

            # Prepare the expression
            expression = expression.replace('²', '**2').replace('³', '**3').replace('√', 'sqrt')

            x = sp.symbols('x') # Defines x
            expr_sympy = sp.sympify(expression, locals={'π': sp.pi, 'e': sp.E}) # Converts the expression given by the user in SymPy expression

            # Calculates the values
            x_values = [sp.Rational(i, 10) for i in range(-100, 101)]
            y_values = [expr_sympy.subs(x, xi) for xi in x_values]

            # Convert to real numbers
            x_values = [float(xi) for xi in x_values]
            y_values = [float(yi) if yi.is_real else None for yi in y_values]

            # Plot the expression
            self.ax.clear()
            self.ax.axhline(0, color='black', linewidth=2)
            self.ax.axvline(0, color='black', linewidth=2)
            self.ax.grid(True)
            self.ax.plot(x_values, y_values, label=expr_graph_text, color='blue')
            self.ax.legend(loc='upper right')
            self.ax.set_xlim(-10, 10)
            self.ax.set_ylim(-10, 10)

            # Draws correctly the axes
            arrow_x = patches.FancyArrowPatch((-10, 0), (10, 0), arrowstyle='->', mutation_scale=20)
            arrow_y = patches.FancyArrowPatch((0, -10), (0, 10), arrowstyle='->', mutation_scale=20)
            self.ax.add_patch(arrow_x)
            self.ax.add_patch(arrow_y)

            self.canvas.draw()

        except Exception as e:
            print(f"Error during graph creation: {e}")

    # Creates the GUI with the virtual keyboard and expression label
    def create_gui(self):

        # Setting a style for the widgets
        style = ttk.Style(self.root)
        
        # Configuring style for the buttons
        style.configure('TButton',
                        font=('Arial', 12),
                        padding=10,
                        relief="flat",
                        background="#4CAF50",
                        foreground="black")
        
        style.map('TButton', 
                background=[('active', '#45a049')])
        
        # Configuring style for the input box
        style.configure('TEntry',
                        font=('Arial', 12),
                        padding=10,
                        relief="solid",
                        borderwidth=2,
                        foreground="black",
                        background="#f2f2f2")

        # Configuring style for the labels
        style.configure('TLabel',
                        font=('Arial', 14, 'bold'),
                        background="#f2f2f2",
                        foreground="#333333")

        # Creating frame for the keyboard
        keyboard_frame = ttk.Frame(self.root)
        keyboard_frame.pack(side=tk.BOTTOM, pady=15)

        buttons = [
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
            '(', ')', '+', '-', '*', '/', 'π', 'e', 'e²', 'e³', 'x',
            'x²', 'x³', '^', 'sin(', 'cos(', 'tan(', '√(', 'ln('
        ]

        # Formatting the list
        rows = [buttons[i:i+6] for i in range(0, len(buttons), 6)]

        for row_index, row in enumerate(rows):
            for col_index, button_text in enumerate(row):
                ttk.Button(
                    keyboard_frame, text=button_text,
                    command=lambda t=button_text: self.add_symbol(t),
                    width=4, style="TButton"  # Applichiamo lo stile al pulsante
                ).grid(row=row_index, column=col_index, padx=5, pady=5)

        # Label for the expression
        self.expr_label = ttk.Label(self.root, text="Write your expression here:", style="TLabel")
        self.expr_label.pack(pady=5)

        # Input box
        self.expr_entry = ttk.Entry(self.root, width=20, style="TEntry")
        self.expr_entry.pack(pady=5)

        # Binding the keypress event to the entry box
        self.expr_entry.bind("<KeyPress>", self.on_key_press)

        # Binding Enter and C keys to their respective functions
        self.root.bind("<Return>", lambda event: self.plot_function())  # Bind Enter to Plot Graph
        self.root.bind("<c>", lambda event: self.expr_entry.delete(0, tk.END))  # Bind C to Clear

        # "Plot Graph" Button
        ttk.Button(self.root, text="Plot Graph", command=self.plot_function, width=15, style="TButton").pack(pady=5)
        
        # "Clear" Button
        ttk.Button(self.root, text="Clear", command=lambda: self.expr_entry.delete(0, tk.END), width=15, style="TButton").pack(pady=5)

    # Adds a symbol to the expression text field
    def add_symbol(self, symbol):
        replacements = {'x²': 'x²', 'x³': 'x³', 'π': 'π', '√': '√('}
        self.expr_entry.insert(tk.END, replacements.get(symbol, symbol))

    # Handles window close event
    def on_closing(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    FunctionPlotterApp(root)
    root.mainloop()
