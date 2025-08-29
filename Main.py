# Overengineered Calculator

import tkinter as tk
import time, random, sys, platform, traceback, pathlib
from typing import Dict, Tuple, Optional

# theme
PALETTE: Dict[str, str] = {
    "bg": "#0a0b10",
    "card": "#101421",
    "shadow": "#06070c",
    "display_bg": "#0b0e19",
    "display_fg": "#f8fbff",
    "muted": "#a4b0d3",
}

# fonts and spacing
FONT_DISPLAY: Tuple[str, int, str] = ("Consolas", 36, "bold")
FONT_BTN: Tuple[str, int, str]     = ("Inter", 22, "bold")
FONT_TOP: Tuple[str, int, str]     = ("Inter", 12, "bold")
PADDING = 16

# symbols
SYMBOLS = {"×": "*", "÷": "/"}

def safe_randint(lo: int, hi: int) -> int:
    lo, hi = int(lo), int(hi)
    if hi < lo:
        lo, hi = hi, lo
    return lo if hi == lo else random.randint(lo, hi)

def safe_randrange(n: int) -> int:
    n = int(n)
    return 0 if n <= 1 else random.randrange(n)

def safe_choice(seq):
    return random.choice(seq) if seq else None

def clamp_channel(c: int) -> int:
    return max(0, min(255, c))

def parse_hex(c: str) -> Tuple[int,int,int]:
    c = c.lstrip("#")
    return int(c[0:2],16), int(c[2:4],16), int(c[4:6],16)

def to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"

def mix(c1: str, c2: str, t: float) -> str:
    r1,g1,b1 = parse_hex(c1); r2,g2,b2 = parse_hex(c2)
    r = int(r1 + (r2-r1)*t); g = int(g1 + (g2-g1)*t); b = int(b1 + (b2-b1)*t)
    return to_hex(r,g,b)

def jitter_color(c: str, amt: int=24) -> str:
    r,g,b = parse_hex(c)
    r += random.randint(-amt,amt); g += random.randint(-amt,amt); b += random.randint(-amt,amt)
    return to_hex(clamp_channel(r), clamp_channel(g), clamp_channel(b))

def ensure_contrast(bg: str, fg: str) -> str:
    br,bg_,bb = parse_hex(bg); fr,fg_,fb = parse_hex(fg)
    def lum(r,g,b):
        return 0.2126*(r/255)**2.2 + 0.7152*(g/255)**2.2 + 0.0722*(b/255)**2.2
    L1 = lum(br,bg_,bb); L2 = lum(fr,fg_,fb)
    if abs(L1-L2) < 0.25:
        if L1 > 0.5: return "#0a0b10"
        else: return "#f8fbff"
    return fg

def neon_styles(key: str) -> Tuple[str,str,str,str,str]:
    palette = {
        "AC":  ("#ff4d6d", "#ff6b88", "#ff2347", "#140006", "#ffb1bd"),
        "⌫":   ("#ff9e4d", "#ffb979", "#ff7f29", "#180e03", "#ffd1b3"),
        "(":   ("#6df2ff", "#90f6ff", "#47ecff", "#001519", "#c6fbff"),
        ")":   ("#6df2ff", "#90f6ff", "#47ecff", "#001519", "#c6fbff"),
        "7":   ("#6d9fff", "#90b6ff", "#4782ff", "#040a18", "#c6dbff"),
        "8":   ("#5df0ff", "#85f5ff", "#2aeaff", "#001418", "#bffaff"),
        "9":   ("#ffb84d", "#ffc879", "#ffa829", "#1b1100", "#ffe0b3"),
        "÷":   ("#ff4141", "#ff6b6b", "#ff2424", "#140303", "#ff9f9f"),
        "4":   ("#90ff4d", "#aaff7a", "#79ff1f", "#0e1806", "#d6ff3b"),
        "5":   ("#ff6df8", "#ff90fb", "#ff47f5", "#170a17", "#ffc6fd"),
        "6":   ("#4dffda", "#7affe5", "#1fffd3", "#001713", "#b3fff1"),
        "×":   ("#ff4141", "#ff6b6b", "#ff2424", "#140303", "#ff9f9f"),
        "1":   ("#ffd24d", "#ffde7a", "#ffc829", "#191200", "#ffe9b3"),
        "2":   ("#6eff4d", "#8aff7a", "#49ff1f", "#0c1607", "#caffb3"),
        "3":   ("#4dbbff", "#79ccff", "#29aaff", "#041218", "#b3e2ff"),
        "-":   ("#ff4141", "#ff6b6b", "#ff2424", "#140303", "#ff9f9f"),
        "0":   ("#ff9e4d", "#ffb979", "#ff7f29", "#180e03", "#ffd1b3"),
        ".":   ("#ff7ab3", "#ff9ac7", "#ff5aa1", "#180a11", "#ffc3df"),
        "=":   ("#00f0a8", "#2df5bd", "#00d895", "#00130e", "#94fbe0"),
        "+":   ("#ff4141", "#ff6b6b", "#ff2424", "#140303", "#ff9f9f"),
    }
    return palette.get(key, ("#2b2f3a", "#353b49", "#1f2430", "#e8ecf4", "#48516a"))

class FunkyButton(tk.Button):
    def __init__(self, master, label: str, cmd, **kw):
        bg, hov, prs, fg, outline = neon_styles(label)
        super().__init__(
            master,
            text=label,
            command=cmd,
            font=FONT_BTN,
            bg=bg,
            fg=ensure_contrast(bg, fg),
            activebackground=prs,
            activeforeground=ensure_contrast(bg, fg),
            relief="flat",
            bd=0,
            highlightbackground=outline,
            highlightcolor=outline,
            padx=14, pady=10,
            **kw
        )
        self._base_bg = bg
        self._hov_bg = hov
        self._prs_bg = prs
        self._fg = ensure_contrast(bg, fg)
        self._outline = outline
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, _):
        try: self.config(bg=self._hov_bg)
        except: pass
    def _on_leave(self, _):
        try: self.config(bg=self._base_bg)
        except: pass
    def _on_press(self, _):
        try: self.config(bg=self._prs_bg)
        except: pass
    def _on_release(self, _):
        try: self.config(bg=self._hov_bg)
        except: pass

class OverengineeredCalculator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Overengineered Calculator")
        self.root.configure(bg=PALETTE["bg"])
        self.root.geometry("360x540")
        self.root.resizable(False, False)
        self.root.bind_all("<Key>", lambda e: "break")

        # toggles
        self.enable_sounds = True
        self.enable_wiggle = True
        self.enable_random_dots = True
        self.enable_bursts_on_click = True
        self.enable_display_rainbow = True
        self.enable_glow_pulse = True

        # card
        self.card = tk.Frame(self.root, bg=PALETTE["card"], bd=0, highlightthickness=0)
        self.card.place(relx=0.5, rely=0.5, anchor="c", width=560, height=920)

        # title
        self.title_lbl = tk.Label(
            self.card, text="Overengineered", bg=PALETTE["card"], fg=PALETTE["muted"], font=("Inter", 16, "bold")
        )
        self.title_lbl.place(x=PADDING, y=PADDING)

        # display wrapper
        self.disp_wrap = tk.Frame(self.card, bg=PALETTE["display_bg"])
        self.disp_wrap.place(x=PADDING, y=64, width=560-2*PADDING, height=120)
        self.disp_base_x = self.disp_wrap.winfo_x()

        # display entry
        self.entry = tk.Entry(
            self.disp_wrap,
            bd=0,
            relief="flat",
            font=FONT_DISPLAY,
            bg=PALETTE["display_bg"],
            fg=PALETTE["display_fg"],
            insertbackground=PALETTE["display_fg"],
            disabledforeground=PALETTE["display_fg"],
            highlightthickness=0,
            justify="right"
        )
        self.entry.place(relx=1.0, rely=0.5, anchor="e", relwidth=1.0, x=-12)
        self.entry.insert(0, "0")
        self.entry.config(state="disabled")

        # grid
        self.grid_frame = tk.Frame(self.card, bg=PALETTE["card"])
        self.grid_frame.place(x=PADDING, y=220, width=560-2*PADDING, height=620)
        for r in range(5):
            self.grid_frame.grid_rowconfigure(r, weight=1)
        for c in range(4):
            self.grid_frame.grid_columnconfigure(c, weight=1)

        rows = [
            [("AC", None), ("(", None), (")", None), ("⌫", None)],
            [("7", None), ("8", None), ("9", None), ("÷", None)],
            [("4", None), ("5", None), ("6", None), ("×", None)],
            [("1", None), ("2", None), ("3", None), ("-", None)],
            [(".", None), ("0", None), ("=", None), ("+", None)],
        ]

        self.buttons: Dict[str, tk.Button] = {}
        for r, row in enumerate(rows):
            for c, (label, _) in enumerate(row):
                btn = FunkyButton(self.grid_frame, label, lambda t=label: self._on_button(t))
                btn.grid(row=r, column=c, sticky="nsew", padx=8, pady=8)
                self.buttons[label] = btn

        # marquee
        self.marquee_text = "  Overengineered  Overengineered  Overengineered  "
        self.marquee = tk.Label(self.card, text=self.marquee_text, bg=PALETTE["card"], fg=PALETTE["muted"], font=("Inter", 13, "bold"))
        self.marquee_x = -1000
        self._start_marquee()

        # colors for dots
        self.pop_colors = [
            "#ff4d6d","#ffd166","#06d6a0","#00f5d4","#80ffdb",
            "#48bfe3","#c77dff","#ff9e00","#ff70a6","#90f1ef",
            "#f4c2c2","#caffbf","#9bf6ff","#bdb2ff","#ffc6ff"
        ]

        # loops
        self._auto_pop()

        # rainbow state
        self._rainbow_step = 0
        self._display_rainbow_loop()

        # pulse
        self._pulse_tick = 0
        self._pulse_title_glow()

        # click confetti
        if self.enable_bursts_on_click:
            self.card.bind("<Button-1>", self._click_burst)

        # init entry state
        self._set_display("0")

    def _start_marquee(self):
        self.marquee.place(x=self.marquee_x, rely=1.0, y=-8, anchor="sw")
        self._marquee_step()

    def _set_display(self, txt: str):
        try:
            self.entry.config(state="normal")
            self.entry.delete(0, "end")
            self.entry.insert(0, txt)
            self.entry.config(state="disabled")
        except:
            pass

    def _get_display(self) -> str:
        try:
            self.entry.config(state="normal")
            v = self.entry.get()
            self.entry.config(state="disabled")
            return v
        except:
            return "0"

    def _on_button(self, label: str):
        if label == "AC":
            self._set_display("0")
            self._jiggle_button(label)
            self._randomize_button_colors(self.buttons.get(label))
            return
        if label == "⌫":
            cur = self._get_display()
            cur = cur[:-1] if len(cur) > 1 else "0"
            self._set_display(cur)
            self._jiggle_button(label)
            self._randomize_button_colors(self.buttons.get(label))
            return
        if label == "=":
            self._compute()
            self._jiggle_button(label)
            self._randomize_button_colors(self.buttons.get(label))
            return

        if label in SYMBOLS:
            ch = SYMBOLS[label]
        else:
            ch = label

        cur = self._get_display()
        if cur == "0" and ch not in (".", "(", ")"):
            cur = ""
        cur += ch
        self._set_display(cur)
        self._jiggle_button(label)
        self._randomize_button_colors(self.buttons.get(label))

    def _compute(self):
        cur = self._get_display()
        try:
            safe = {"__builtins__": None}
            safe.update({
                "abs": abs, "round": round, "min": min, "max": max,
                "pow": pow, "time": time.time,
            })
            cur = cur.replace("×", "*").replace("÷", "/")
            val = eval(cur, safe, {})
            self._set_display(str(val))
        except:
            self._set_display("Error")

    def _wiggle_display(self):
        seq = [0, 6, -6, 4, -4, 2, -2, 0]
        def step(i=0):
            if i >= len(seq): return
            self.disp_wrap.place_configure(x=self.disp_base_x + seq[i])
            self.root.after(18, lambda: step(i+1))
        step()

    def _jiggle_button(self, label: str):
        btn = self.buttons.get(label)
        if not btn: return
        seq = [0, 1, 2, 1, 0]
        orig_padx = int(btn.cget("padx")); orig_pady = int(btn.cget("pady"))
        def s(i=0):
            if i >= len(seq):
                try: btn.config(padx=orig_padx, pady=orig_pady)
                except: pass
                return
            try: btn.config(padx=orig_padx+seq[i], pady=orig_pady+seq[i])
            except: pass
            self.root.after(14, lambda: s(i+1))
        s()

    def _auto_pop(self):
        if self.enable_random_dots: self._spawn_dot()
        self.root.after(random.randint(120, 320), self._auto_pop)

    def _spawn_dot(self, at: Optional[Tuple[int,int]] = None):
        self.card.update_idletasks()
        w = self.card.winfo_width() or self.card.winfo_reqwidth()
        h = self.card.winfo_height() or self.card.winfo_reqheight()
        if at is None:
            x = safe_randint(PADDING+8, max(PADDING+8, w-PADDING-8))
            y = safe_randint(PADDING+162, max(PADDING+162, h-40))
        else:
            x, y = at
        size = random.randint(6, 16)
        color = safe_choice(self.pop_colors) or "#ffffff"
        dot = tk.Canvas(self.card, width=size, height=size, bg=PALETTE["card"], highlightthickness=0, bd=0)
        dot.place(x=x, y=y)
        oid = dot.create_oval(0, 0, size, size, fill=color, outline="")
        self._animate_dot(dot, oid, size, 0)

    def _animate_dot(self, dot: tk.Canvas, oid: int, max_size: int, k: int):
        if k < 5:
            s = int(max_size * (1 + k*0.25))
            dot.config(width=s, height=s); dot.coords(oid, 0, 0, s, s)
            self.root.after(16, lambda: self._animate_dot(dot, oid, max_size, k+1))
        else:
            self._fade_and_destroy(dot, oid)

    def _fade_and_destroy(self, dot: tk.Canvas, oid: int):
        def step(i=0):
            if i>8:
                try: dot.destroy()
                except: pass
                return
            try: dot.itemconfig(oid, stipple=f"gray{i*12}")
            except: pass
            self.root.after(16, lambda: step(i+1))
        step()

    def _click_burst(self, ev):
        bx, by = ev.x, ev.y
        btn = None
        for b in self.buttons.values():
            try:
                bx0 = b.winfo_rootx() - self.card.winfo_rootx()
                by0 = b.winfo_rooty() - self.card.winfo_rooty()
                bw = b.winfo_width()
                bh = b.winfo_height()
                if bx0 <= bx <= bx0+bw and by0 <= by <= by0+bh:
                    btn = b; break
            except:
                pass

        if btn is not None:
            try:
                br = btn.winfo_rootx() - self.card.winfo_rootx()
                by_ = btn.winfo_rooty() - self.card.winfo_rooty()
                bw = btn.winfo_width(); bh = btn.winfo_height()
                px = br + random.randint(10, max(12, bw-12))
                py = by_ + random.randint(10, max(12, bh-12))
                for _ in range(random.randint(2,5)):
                    jx = random.randint(-8,8); jy = random.randint(-8,8)
                    self._confetti_piece((px+jx, py+jy))
            except:
                pass
        else:
            self._confetti_piece((bx, by))

    def _marquee_step(self):
        width = self.card.winfo_width()
        self.marquee_x += 3
        if self.marquee_x > width:
            self.marquee_x = -self.marquee.winfo_reqwidth()
        self.marquee.place(x=self.marquee_x, rely=1.0, y=-8, anchor="sw")
        self.root.after(18, self._marquee_step)

    def _display_rainbow_loop(self):
        if self.enable_display_rainbow:
            base = PALETTE["display_fg"]
            t = (self._rainbow_step % 60) / 60.0
            col = mix(base, jitter_color("#6ef9ff", 32), t)
            try: self.entry.config(disabledforeground=col, insertbackground=col)
            except: pass
            self._rainbow_step += 1
        self.root.after(50, self._display_rainbow_loop)

    def _pulse_title_glow(self):
        if self.enable_glow_pulse:
            t = (self._pulse_tick % 40)/40.0
            c1, c2 = "#8fa8ff", "#a4b0d3"
            fg = mix(c1, c2, abs(2*t-1))
            try: self.title_lbl.config(fg=fg)
            except: pass
            self._pulse_tick += 1
        self.root.after(60, self._pulse_title_glow)

    def _confetti_piece(self, at: Tuple[int,int]):
        cx, cy = at
        size = random.randint(6,12)
        color = safe_choice(self.pop_colors) or "#ffffff"
        canvas = tk.Canvas(self.card, width=size*2, height=size*2, bg=PALETTE["card"], highlightthickness=0, bd=0)
        canvas.place(x=cx, y=cy)
        pts = [0,size*2, size,size*0, size*2,size*2]
        poly = canvas.create_polygon(pts, fill=color, outline="")
        self._animate_confetti(canvas, poly, cx, cy, size)

    def _animate_confetti(self, canvas: tk.Canvas, poly: int, x0: int, y0: int, size: int):
        dx = random.choice([-2,-1,1,2])
        dy = random.randint(3,6)
        frames = random.randint(16,28)
        def step(i=0, x=x0, y=y0):
            if i>=frames:
                try: canvas.destroy()
                except: pass
                return
            x += dx; y += dy
            try: canvas.place_configure(x=x, y=y)
            except: pass
            try:
                t = i/frames
                s = int(size*(1-t*0.7))
                canvas.config(width=max(2,s*2), height=max(2,s*2))
                canvas.coords(poly, 0,s*2, s,0, s*2,s*2)
            except: pass
            self.root.after(16, lambda: step(i+1, x, y))
        step()

    def _randomize_button_colors(self, btn: tk.Button):
        if not btn: return
        txt = btn.cget("text")
        bg, hov, prs, fg, outline = neon_styles(txt)
        bg2 = jitter_color(bg, 40); hov2 = jitter_color(hov, 40); prs2 = jitter_color(prs, 40)
        fg2 = ensure_contrast(bg2, jitter_color(fg, 40)); out2 = jitter_color(outline, 40)
        try:
            btn.config(bg=bg2, fg=fg2, activeforeground=fg2, activebackground=prs2, highlightbackground=out2, highlightcolor=out2)
        except: pass

def create_overengineered_calculator() -> OverengineeredCalculator:
    root = tk.Tk()
    return OverengineeredCalculator(root)

def run_overengineered_calculator():
    app = create_overengineered_calculator()
    app.root.mainloop()

# main
if __name__ == "__main__":
    try:
        run_overengineered_calculator()
    except Exception:
        log = pathlib.Path(sys.executable).with_name("error.log")
        log.write_text(traceback.format_exc(), encoding="utf-8")
        raise
