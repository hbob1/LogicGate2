import tkinter as tk
from tkinter import ttk, messagebox
import os

GATE_INPUTS = {
    "AND": 2,
    "OR": 2,
    "XOR": 2,
    "NOT": 1,
}

class Component:
    def __init__(self, cid, ctype, x, y, num_inputs=2):
        self.id = cid
        self.type = ctype
        self.x = x
        self.y = y
        self.width = 60
        self.num_inputs = num_inputs
        self.height = max(30, 20 * self.num_inputs)

class CircuitVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Circuit Builder with Visualization")

        self.canvas = tk.Canvas(root, width=1200, height=800, bg="white")
        self.canvas.grid(row=0, column=1, rowspan=20)

        self.components = []
        self.inputs = []  # (name, index, value)
        self.connections = []  # (from_id, findex, to_id, tindex)
        self.output = None
        self.component_map = {}  # id -> Component
        self.input_map = {}  # (component_id, index) -> value

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
        ttk.Combobox(frm, textvariable=self.ctype, values=list(GATE_INPUTS.keys()), width=5).grid(row=2, column=1)
        ttk.Entry(frm, textvariable=self.cx, width=4).grid(row=3, column=0)
        ttk.Entry(frm, textvariable=self.cy, width=4).grid(row=3, column=1)
        ttk.Button(frm, text="Add", command=self.add_component).grid(row=2, column=2, rowspan=2)

        ttk.Label(frm, text="Add Input").grid(row=4, column=0, columnspan=2, pady=(10, 0))
        self.in_name = tk.StringVar()
        self.in_index = tk.StringVar()
        self.in_value = tk.BooleanVar()
        ttk.Entry(frm, textvariable=self.in_name, width=6).grid(row=5, column=0)
        ttk.Entry(frm, textvariable=self.in_index, width=4).grid(row=5, column=1)
        ttk.Checkbutton(frm, text="Value", variable=self.in_value).grid(row=5, column=2)
        ttk.Button(frm, text="Add Input", command=self.add_input).grid(row=5, column=3)

        ttk.Label(frm, text="Add Connection").grid(row=6, column=0, columnspan=2, pady=(10, 0))
        self.from_id = tk.StringVar()
        self.findex = tk.StringVar()
        self.to_id = tk.StringVar()
        self.tindex = tk.StringVar()
        ttk.Entry(frm, textvariable=self.from_id, width=6).grid(row=7, column=0)
        ttk.Entry(frm, textvariable=self.findex, width=4).grid(row=7, column=1)
        ttk.Entry(frm, textvariable=self.to_id, width=6).grid(row=8, column=0)
        ttk.Entry(frm, textvariable=self.tindex, width=4).grid(row=8, column=1)
        ttk.Button(frm, text="Connect", command=self.add_connection).grid(row=7, column=2, rowspan=2)

        ttk.Label(frm, text="Set Output").grid(row=9, column=0, pady=(10, 0))
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

            # Draw inputs
            for i in range(comp.num_inputs):
                cx = x - 10
                cy = y + h / (comp.num_inputs + 1) * (i + 1)
                color = "gray"
                val = self.input_map.get((comp.id, i))
                if val is not None:
                    color = "green" if val else "red"
                self.canvas.create_oval(cx - 5, cy - 5, cx + 5, cy + 5, fill=color, outline="black")

            # Draw output port
            self.canvas.create_oval(x + w, y + h // 2 - 5, x + w + 10, y + h // 2 + 5, fill="black")

        # Draw connections
        for conn in self.connections:
            from_id, _, to_id, _ = conn
            if from_id in self.component_map and to_id in self.component_map:
                f = self.component_map[from_id]
                t = self.component_map[to_id]
                fx, fy = f.x + f.width + 5, f.y + f.height // 2
                tx, ty = t.x - 5, t.y + t.height // 2
                self.canvas.create_line(fx, fy, tx, ty, arrow=tk.LAST)

    def get_inputs_from_file(self, filename):
        max_index = -1
        try:
            with open(filename, "r") as f:
                for line in f:
                    if line.startswith("input"):
                        parts = line.strip().split()
                        for p in parts:
                            if p.startswith("index="):
                                idx = int(p.split("=")[1])
                                max_index = max(max_index, idx)
            return max_index + 1 if max_index >= 0 else 2  # default fallback
        except Exception as e:
            print(f"Failed to read file: {filename}, {e}")
            return 2

    def add_component(self):
        try:
            cid = self.cid.get().strip()
            ctype = self.ctype.get().strip()
            x = int(self.cx.get())
            y = int(self.cy.get())

            # Determine number of inputs based on type
            if ctype in GATE_INPUTS:
                num_inputs = GATE_INPUTS[ctype]
            else:
                # Try to load subcomponent from file
                filename = f"components/{ctype}.txt"
                if os.path.exists(filename):
                    num_inputs = self.get_inputs_from_file(filename)
                else:
                    messagebox.showerror("Error", f"Unknown gate or missing file: {ctype}")
                    return

            comp = Component(cid, ctype, x, y, num_inputs)
            self.components.append(comp)
            self.component_map[cid] = comp
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Invalid position values")

    def add_input(self):
        try:
            name = self.in_name.get().strip()
            index = int(self.in_index.get())
            value = self.in_value.get()
            self.inputs.append((name, index, value))
            self.input_map[(name, index)] = value
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Invalid input values")

    def add_connection(self):
        try:
            from_id = self.from_id.get().strip()
            findex = int(self.findex.get())
            to_id = self.to_id.get().strip()
            tindex = int(self.tindex.get())
            self.connections.append((from_id, findex, to_id, tindex))
            self.draw_components()
        except ValueError:
            messagebox.showerror("Error", "Invalid connection indices")

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
