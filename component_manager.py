import tkinter as tk
from tkinter import ttk, messagebox
import os

class Component:
    def __init__(self, cid, ctype, x, y):
        self.id = cid
        self.type = ctype
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30

class CircuitVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Builder with Visualization")

        self.canvas = tk.Canvas(root, width=600, height=400, bg="white")
        self.canvas.grid(row=0, column=1, rowspan=20)

        self.components = []
        self.inputs = []
        self.connections = []
        self.output = None

        self.component_positions = {}  # id -> Component

        self.name_var = tk.StringVar(value="XOR")

        self.build_gui()

    def build_gui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="n")

        ttk.Label(frm, text="Circuit Name").grid(row=0, column=0)
        ttk.Entry(frm, textvariable=self.name_var).grid(row=0, column=1)

        ttk.Label(frm, text="Add Component").grid(row=1, column=0, columnspan=2, pady=(10, 0))
        self.cid = tk.StringVar()
        self.ctype = tk.StringVar()
        self.cx = tk.StringVar()
        self.cy = tk.StringVar()
        ttk.Entry(frm, textvariable=self.cid, width=8).grid(row=2, column=0)
        ttk.Combobox(frm, textvariable=self.ctype, values=["AND", "OR", "NOT"], width=5).grid(row=2, column=1)
        ttk.Entry(frm, textvariable=self.cx, width=4).grid(row=3, column=0)
        ttk.Entry(frm, textvariable=self.cy, width=4).grid(row=3, column=1)
        ttk.Button(frm, text="Add", command=self.add_component).grid(row=2, column=2, rowspan=2)

        ttk.Label(frm, text="Input").grid(row=4, column=0, columnspan=2, pady=(10, 0))
        self.in_index = tk.StringVar()
        self.in_value = tk.BooleanVar()
        ttk.Entry(frm, textvariable=self.in_index, width=4).grid(row=5, column=0)
        ttk.Checkbutton(frm, text="Value", variable=self.in_value).grid(row=5, column=1)
        ttk.Button(frm, text="Add Input", command=self.add_input).grid(row=5, column=2)

        ttk.Label(frm, text="Connection").grid(row=6, column=0, columnspan=2, pady=(10, 0))
        self.from_id = tk.StringVar()
        self.findex = tk.StringVar()
        self.to_id = tk.StringVar()
        self.tindex = tk.StringVar()
        ttk.Entry(frm, textvariable=self.from_id, width=6).grid(row=7, column=0)
        ttk.Entry(frm, textvariable=self.findex, width=4).grid(row=7, column=1)
        ttk.Entry(frm, textvariable=self.to_id, width=6).grid(row=8, column=0)
        ttk.Entry(frm, textvariable=self.tindex, width=4).grid(row=8, column=1)
        ttk.Button(frm, text="Connect", command=self.add_connection).grid(row=7, column=2, rowspan=2)

        ttk.Label(frm, text="Output").grid(row=9, column=0, pady=(10, 0))
        self.out_id = tk.StringVar()
        self.out_index = tk.StringVar()
        ttk.Entry(frm, textvariable=self.out_id, width=6).grid(row=10, column=0)
        ttk.Entry(frm, textvariable=self.out_index, width=4).grid(row=10, column=1)
        ttk.Button(frm, text="Set", command=self.set_output).grid(row=10, column=2)

        ttk.Button(frm, text="Export", command=self.export).grid(row=11, column=0, columnspan=3, pady=10)

    def draw_components(self):
        self.canvas.delete("all")
        for comp in self.components:
            x, y, w, h = comp.x, comp.y, comp.width, comp.height
            self.canvas.create_rectangle(x, y, x + w, y + h, fill="lightblue")
            self.canvas.create_text(x + w / 2, y + h / 2, text=f"{comp.id}\n{comp.type}")
            self.canvas.create_oval(x + w, y + h // 2 - 5, x + w + 10, y + h // 2 + 5, fill="green", outline="black")
            self.canvas.create_oval(x - 10, y + h // 2 - 5, x, y + h // 2 + 5, fill="red", outline="black")

        for conn in self.connections:
            from_id, _, to_id, _ = conn
            if from_id in self.component_positions and to_id in self.component_positions:
                f = self.component_positions[from_id]
                t = self.component_positions[to_id]
                fx, fy = f.x + f.width + 5, f.y + f.height // 2
                tx, ty = t.x - 5, t.y + t.height // 2
                self.canvas.create_line(fx, fy, tx, ty, arrow=tk.LAST)

    def add_component(self):
        try:
            cid = self.cid.get().strip()
            ctype = self.ctype.get().strip()
            x = int(self.cx.get())
            y = int(self.cy.get())

            comp = Component(cid, ctype, x, y)
            self.components.append(comp)
            self.component_positions[cid] = comp
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Invalid position values")

    def add_input(self):
        try:
            index = int(self.in_index.get())
            value = self.in_value.get()
            self.inputs.append(("XOR", index, value))
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Index must be integer")

    def add_connection(self):
        try:
            from_id = self.from_id.get().strip()
            findex = int(self.findex.get())
            to_id = self.to_id.get().strip()
            tindex = int(self.tindex.get())
            self.connections.append((from_id, findex, to_id, tindex))
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Invalid indices")

    def set_output(self):
        try:
            self.output = (self.out_id.get().strip(), int(self.out_index.get().strip()))
        except ValueError:
            messagebox.showerror("Error", "Invalid output index")

    def export(self):
        os.makedirs("components", exist_ok=True)
        name = self.name_var.get().strip()
        with open(f"components/{name}.txt", "w") as f:
            for comp in self.components:
                f.write(f"comp id={comp.id} type={comp.type}\n")
            for name, index, value in self.inputs:
                f.write(f"input name={name} index={index} value={int(value)}\n")
            for from_id, findex, to_id, tindex in self.connections:
                f.write(f"connect from={from_id} findex={findex} to={to_id} tindex={tindex}\n")
            if self.output:
                f.write(f"Out put={self.output[0]} kndex={self.output[1]}\n")
        messagebox.showinfo("Exported", f"Saved to components/{name}.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = CircuitVisualizer(root)
    root.mainloop()
