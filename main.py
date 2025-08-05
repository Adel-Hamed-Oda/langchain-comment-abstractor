import OpenAIAgent
import tkinter as tk
from tkinter import filedialog
import csv

API_KEY = "..."

MAIN_FONT = ("Arial", 16)

root = tk.Tk()
root.title("ah shi, here we go again")
root.geometry("800x600")

headers = []
chosen_header = ""
filepath = ""

def main():
    ask_for_file_button = tk.Button(text="Please choose a csv file", font=MAIN_FONT, command=ask_for_file_button_on_click)
    ask_for_file_button.pack()

    root.mainloop()

def ask_for_file_button_on_click():
    global filepath
    filepath = filedialog.askopenfilename(
        title="Please select a CSV File",
        filetypes=[("CSV", "*.csv"), ("All", "*.*")]
    )

    if (filepath):
        with open(filepath, mode='r', newline='') as file:
            reader = list(csv.DictReader(file))
            global headers
            headers = list(reader[0].keys()) if reader else []

        setup_header_buttons()

def setup_header_buttons():
    label = tk.Label(text="Please choose header to abstract", font=MAIN_FONT)
    label.pack()
    
    buttons = []
    last_y = 100
    
    for i in range(len(headers)):
        def set_header(i=i):
            global chosen_header
            chosen_header = headers[i]

        buttons.append(tk.Button(text=headers[i], font=("Arial", 12), command=set_header))
        buttons[i].place(x = 50, y = 100 + 40 * i)
        last_y = 100 + 40 * i
    
    apply_button = tk.Button(text="Run Abstraction", font=MAIN_FONT, command=run_abstractor)
    apply_button.place(x = 325, y = last_y + 40)

def run_abstractor():
    if not chosen_header:
        error_label = tk.Label(text="Please choose a header", font=("Arial", 16, ), fg="red")
        error_label.place(x=20, y=0)
        return

    global filepath
    with open(filepath, mode='r', newline='') as file:
        reader = list(csv.DictReader(file))

        comments = str([row.get(chosen_header, "").strip() for row in reader])

        model = OpenAIAgent.Model(key = API_KEY)

        system_msg = str(
            "You will receive a list of strings corresponding to comments. " +
            "Your task is to convert each comment into a short abstraction (1-5 words). " +
            "Return the same number of items, maintaining order. " +
            "Do not add extra text or change the format." +
            "Please don't mess this up"
        )

        model.send(system_msg, "system")
        model.send(comments, "human")
        model.process()
        result = model.receive()
        model.clear()

        system_msg = str(
            "You will receive a list of strings corresponding to some abstractions about some comments. " +
            "You will also receive a list containing all the comments themselves. " +
            "Your job is to look at each comment in the 2nd list, and replace it with the appropriate abstraction from the first list. " +
            "make sure you try doing this for every comment and that the result is the same length as the original list of comments. " +
            "Do not add extra text or change the format." +
            "Please don't mess this up"
        )

        model.send(system_msg, "system")
        model.send(result, "human")
        model.send(comments, "human")
        model.process()

        result = read_result_into_list(model.receive())

        if len(result) != len(reader):
            print("=== headers === " + str(headers))
            print("=== chosen header === " + str(chosen_header))
            print("=== result === " + str(result))
            print("=== result length === " + str(len(result)))
            print("=== original length === " + str(len(reader)))
            print("=== comments === " + comments)
            return

        for i, row in enumerate(reader):
            row[chosen_header] = result[i].strip().replace('[', '').replace(']', '').replace("'", "")

        with open('data.csv', mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(reader)

        model.clear()
        root.quit()
        print("Mission Successful")

def read_result_into_list(result):
    if isinstance(result, list):
        return [item.strip() for item in result]
    elif isinstance(result, str):
        return [item.strip() for item in result.split(",")]
    else:
        raise TypeError("Please make sure the results are in a valid format")

if __name__ == "__main__":
    main()