import sys
import io
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from gradient import PRESETS, parse_color, lerp

# === Force UTF-8 everywhere ===
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class GradientGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎨 ANSI Gradient Generator (Live Colors)")
        self.geometry("850x700")
        self.configure(bg="#1e1e1e")

        # === Input section ===
        frm_input = tk.Frame(self, bg="#1e1e1e")
        frm_input.pack(padx=10, pady=10, fill="x")

        tk.Label(frm_input, text="Text:", fg="white", bg="#1e1e1e").grid(row=0, column=0, sticky="w")
        self.txt_input = ScrolledText(
            frm_input, height=5, wrap="word",
            bg="#252526", fg="white", insertbackground="white",
            font=("Consolas", 11)
        )
        self.txt_input.grid(row=1, column=0, columnspan=5, sticky="nsew", pady=5)

        # === Colors ===
        tk.Label(frm_input, text="Colors (e.g. red,0,255,0,blue):", fg="white", bg="#1e1e1e").grid(row=2, column=0, sticky="w")
        self.ent_colors = tk.Entry(frm_input, bg="#252526", fg="white", insertbackground="white", font=("Consolas", 10))
        self.ent_colors.insert(0, "red,blue")
        self.ent_colors.grid(row=3, column=0, columnspan=3, sticky="we", pady=5)

        # === Direction ===
        tk.Label(frm_input, text="Direction:", fg="white", bg="#1e1e1e").grid(row=2, column=3, sticky="w")
        self.cmb_direction = ttk.Combobox(frm_input, values=["horizontal", "vertical", "diagonal"])
        self.cmb_direction.current(2)
        self.cmb_direction.grid(row=3, column=3, sticky="we", padx=5)

        # === Buttons ===
        btn_generate = ttk.Button(frm_input, text="Generate", command=self.generate)
        btn_generate.grid(row=3, column=4, padx=5, sticky="e")

        btn_export = ttk.Button(frm_input, text="Export ANSI", command=self.export)
        btn_export.grid(row=3, column=5, padx=5, sticky="e")

        # === Output section ===
        tk.Label(self, text="Result (colored preview):", fg="white", bg="#1e1e1e").pack(anchor="w", padx=10)
        self.txt_output = ScrolledText(
            self, height=25, bg="#000", fg="white",
            insertbackground="white", font=("Consolas", 11)
        )
        self.txt_output.pack(padx=10, pady=5, fill="both", expand=True)

        # === Footer hint ===
        tk.Label(
            self,
            text=f"Available colors: {', '.join(PRESETS.keys())} — or use R,G,B values",
            fg="#888", bg="#1e1e1e", font=("Consolas", 9)
        ).pack(anchor="w", padx=10, pady=(0, 5))

    # === Gradient generation and display ===
    def generate(self):
        raw_text = self.txt_input.get("1.0", "end").rstrip("\n")
        if not raw_text.strip():
            messagebox.showwarning("Warning", "Text is empty.")
            return

        colors = self._parse_colors()
        if not colors:
            return

        lines = raw_text.splitlines()
        h = len(lines)
        w = max((len(l) for l in lines), default=0)
        direction = self.cmb_direction.get()

        self.txt_output.delete("1.0", "end")

        # Draw text line by line with colored tags
        for y, line in enumerate(lines):
            for x, ch in enumerate(line):
                if direction == "horizontal":
                    t = x / max(1, w - 1)
                elif direction == "vertical":
                    t = y / max(1, h - 1)
                else:
                    t = ((x / max(1, w - 1)) + (y / max(1, h - 1))) / 2

                seg = int(t * (len(colors) - 1))
                seg = min(seg, len(colors) - 2)
                local_t = (t * (len(colors) - 1)) - seg

                c1, c2 = colors[seg], colors[seg + 1]
                r = lerp(c1[0], c2[0], local_t)
                g = lerp(c1[1], c2[1], local_t)
                b = lerp(c1[2], c2[2], local_t)
                color_hex = f"#{r:02x}{g:02x}{b:02x}"

                tag_name = f"c_{r}_{g}_{b}"
                if not tag_name in self.txt_output.tag_names():
                    self.txt_output.tag_configure(tag_name, foreground=color_hex)
                self.txt_output.insert("end", ch, tag_name)

            self.txt_output.insert("end", "\n")

    # === Parse color list (names + RGB) ===
    def _parse_colors(self):
        color_tokens = []
        temp = ""
        nums = 0
        for part in self.ent_colors.get().split(","):
            part = part.strip()
            if not part:
                continue
            if part.isdigit():
                temp += part + ","
                nums += 1
                if nums == 3:
                    color_tokens.append(temp.rstrip(","))
                    temp, nums = "", 0
            else:
                if temp:
                    temp, nums = "", 0
                color_tokens.append(part)

        if temp:
            messagebox.showerror("Error", "Incomplete RGB color (expected R,G,B).")
            return None

        try:
            return [parse_color(c) for c in color_tokens]
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return None

    # === Export ANSI text ===
    def export(self):
        from gradient import generate_gradient_text
        raw_text = self.txt_input.get("1.0", "end").rstrip("\n")
        if not raw_text.strip():
            messagebox.showwarning("Warning", "Text is empty.")
            return

        colors = [c.strip() for c in self.ent_colors.get().split(",") if c.strip()]
        direction = self.cmb_direction.get()

        from gradient import generate_gradient_text
        try:
            lines = raw_text.splitlines()
            ansi_text = generate_gradient_text(lines, colors, direction)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export ANSI text"
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(ansi_text)
            messagebox.showinfo("Success", f"Exported successfully to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")


if __name__ == "__main__":
    app = GradientGUI()
    app.mainloop()
