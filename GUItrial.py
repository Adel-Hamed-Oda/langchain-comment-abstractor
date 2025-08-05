import tkinter as tk
from tkinter import filedialog
import csv

def choose_file():
    filepath = filedialog.askopenfilename(
        title="Select a CSV File",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    
    if filepath:
        with open(filepath, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                print(row)

root = tk.Tk()
root.title("CSV File Picker")

button = tk.Button(root, text="Choose CSV File", command=choose_file)
button.pack(pady=10)

root.mainloop()