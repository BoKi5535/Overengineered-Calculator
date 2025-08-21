
# Overengineered Calculator

import tkinter as tk
import time, random, sys, platform
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

# per-button colors
FUNKY: Dict[str, Tuple[str, str, str, str, str]] = {
    "AC":  ("#ff4775", "#ff6990", "#ff2d5f", "#16040a", "#ff9bb2"),
    "←":   ("#a96bff", "#b88bff", "#9a4dff", "#0d0616", "#d7baff"),
    "(":   ("#ff80df", "#ffa2ea", "#ff66d6", "#1a0b16", "#ffc6f1"),
    ")":   ("#7dff7a", "#9aff97", "#63ff60", "#061306", "#c6ffc5"),
    "7":   ("#ffe34d", "#ffe97a", "#ffd81f", "#1b1600", "#fff2a6"),
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

# color utils
def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    r = max(0,min(255,r)); g=max(0,min(255,g)); b=max(0,min(255,b))
    return f"#{r:02x}{g:02x}{b:02x}"

def mix(a: str, b: str, t: float) -> str:
    r1,g1,b1 = hex_to_rgb(a); r2,g2,b2 = hex_to_rgb(b)
    r = int(r1 + (r2-r1)*t); g = int(g1 + (g2-g1)*t); b = int(b1 + (b2-b1)*t)
    return rgb_to_hex(r,g,b)

def jitter_color(base: str, amt: int = 24) -> str:
    r,g,b = hex_to_rgb(base)
    r += random.randint(-amt,amt); g += random.randint(-amt,amt); b += random.randint(-amt,amt)
    return rgb_to_hex(r,g,b)

def luminance(col: str) -> float:
    r,g,b = hex_to_rgb(col)
    return 0.2126*(r/255) + 0.7152*(g/255) + 0.0722*(b/255)

def ensure_contrast(bg: str, fg: str, min_diff: float = 0.35) -> str:
    if abs(luminance(bg)-luminance(fg)) < min_diff:
        return "#ffffff" if luminance(bg) < 0.5 else "#000000"
    return fg

def neon_styles(label: str) -> Tuple[str, str, str, str, str]:
    return FUNKY.get(label, ("#2a3152", "#35406b", "#1e2642", "#e6ecff", "#6f7db0"))

# platform
def is_windows() -> bool:
    return platform.system().lower().startswith("win")

def to_python_ops(expr: str) -> str:
    return expr.replace("×","*").replace("÷","/")

def sanitize_expression(expr: str) -> str:
    expr = to_python_ops(expr)
    for ch in expr:
        if ch not in "0123456789.+-*/() ":
            raise ValueError("bad char")
    return expr

# widgets
class FunkyButton(tk.Button):
    def __init__(self, master, text, command):
        bg, hov, prs, fg, outline = neon_styles(text)
        fg = ensure_contrast(bg, fg)
        super().__init__(
            master, text=text, command=command, font=FONT_BTN,
            relief="flat", bd=0, padx=18, pady=18, fg=fg, bg=bg,
            activeforeground=fg, activebackground=prs, cursor="hand2",
            highlightthickness=2, highlightbackground=outline, highlightcolor=outline
        )
        self._bg, self._hov, self._prs, self._outline = bg, hov, prs, outline
        self.bind("<Enter>", lambda e: self.config(bg=self._hov, highlightbackground=self._outline))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg,  highlightbackground=self._outline))
        self.bind("<ButtonPress-1>", lambda e: self.config(bg=self._prs))
        self.bind("<ButtonRelease-1>", lambda e: self.config(bg=self._hov))

# app
class OverengineeredCalculator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Overengineered Calculator")
        self.root.configure(bg=PALETTE["bg"])
        self.root.geometry("600x980")
        self.root.resizable(False, False)
        self.root.bind_all("<Key>", lambda e: "break")

        # toggles
        self.enable_sounds = True
        self.enable_wiggle = True
        self.enable_random_dots = True
        self.enable_bursts_on_click = True
        self.enable_display_rainbow = True
        self.enable_button_jiggle = True
        self.enable_confetti_on_equals = True
        self.enable_glow_pulse = True
        self.enable_button_glow = True
        self.enable_operator_flash = True
        self.enable_title_wave = True

        # shadow
        self.shadow = tk.Frame(root, bg=PALETTE["shadow"])
        self.shadow.place(x=PADDING+4, y=PADDING+6, relwidth=1, width=-(PADDING*2), height=920)
        self.card = tk.Frame(root, bg=PALETTE["card"])
        self.card.place(x=PADDING, y=PADDING, relwidth=1, width=-(PADDING*2), height=920)

        # top
        top = tk.Frame(self.card, bg=PALETTE["card"])
        top.pack(fill="x", padx=PADDING, pady=(PADDING, 8))
        self.title_lbl = tk.Label(top, text="Overengineered Calculator", bg=PALETTE["card"], fg=PALETTE["muted"], font=FONT_TOP)
        self.title_lbl.pack(side="left")
        self.clock_lbl = tk.Label(top, text="", bg=PALETTE["card"], fg=PALETTE["muted"], font=FONT_TOP)
        self.clock_lbl.pack(side="right")
        self._tick_clock()

        # display wrapper
        self.disp_wrap = tk.Frame(self.card, bg=PALETTE["card"], height=104)
        self.disp_base_x = PADDING
        self.disp_wrap.place(x=self.disp_base_x, y=PADDING+34, relwidth=1, width=-(PADDING*2), height=104)

        # display
        self.display_var = tk.StringVar(value="0")
        self.entry = tk.Entry(
            self.disp_wrap, textvariable=self.display_var, font=FONT_DISPLAY, justify="right",
            state="disabled", disabledbackground=PALETTE["display_bg"], disabledforeground=PALETTE["display_fg"],
            relief="flat", bd=0, insertbackground=PALETTE["display_fg"]
        )
        self.entry.configure(cursor="arrow")
        self.entry.bind("<Button-1>", lambda e: "break")
        self.entry.pack(fill="both", expand=True)

        # divider
        tk.Frame(self.card, bg=PALETTE["shadow"], height=2).place(x=PADDING, y=PADDING+148, relwidth=1, width=-(PADDING*2))

        # grid
        self.grid_frame = tk.Frame(self.card, bg=PALETTE["card"])
        self.grid_frame.place(x=PADDING, y=PADDING+162, relwidth=1, width=-(PADDING*2), height=610)

        rows = [
            [("AC", None), ("←", None), ("(", None), (")", None)],
            [("7", None),  ("8", None),  ("9", None),  ("÷", None)],
            [("4", None),  ("5", None),  ("6", None),  ("×", None)],
            [("1", None),  ("2", None),  ("3", None),  ("-", None)],
            [("0", None),  (".", None),  ("=", None),  ("+", None)],
        ]
        for r in range(len(rows)): self.grid_frame.rowconfigure(r, weight=1, uniform="row")
        for c in range(4): self.grid_frame.columnconfigure(c, weight=1, uniform="col")

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

        # title pulsing
        self._pulse_tick = 0
        self._pulse_title_glow()

        # button glow loop
        self._btn_glow_phase = 0
        self._pulse_buttons_glow()

        # title wave
        self._wave_phase = 0
        self._title_wave_tick()

        # AC press timestamps
        self._ac_press_times = []

    # sounds
    def _click_sound(self, tone=880, dur=40):
        if not self.enable_sounds: return
        try:
            if is_windows():
                import winsound
                winsound.Beep(int(tone), int(dur))
            else:
                self.root.bell()
        except Exception:
            pass

    # clock
    def _tick_clock(self):
        self.clock_lbl.config(text=time.strftime("%H:%M:%S"))
        self.root.after(1000, self._tick_clock)

    # display 
    def _set_display(self, text):
        s = str(text)
        self.entry.config(state="normal")
        self.entry.delete(0, tk.END)
        self.entry.insert(0, s)
        self.entry.config(state="disabled")
        self.display_var.set(s)

    def _get_display(self):
        return self.display_var.get()

    # logic
    def press(self, label: str):
        if label == "AC":
            self._record_ac_press()
            self._set_display("0"); return
        if label == "←":
            cur = self._get_display()
            cur = cur[:-1] if cur else "0"
            if not cur: cur = "0"
            self._set_display(cur); return
        if label == "=":
            self.equals(); return
        self.insert(label)

    def insert(self, s: str):
        cur = self._get_display()
        if cur == "0":
            if s.isdigit(): cur = s
            elif s == ".": cur = "0."
            elif s in ("+", "-", "×", "÷", "("): cur = "0"+s
            elif s == ")": cur = "0"
            else: cur = s
        else:
            cur += s
        self._set_display(cur)

    def equals(self):
        expr = self._get_display()
        try:
            safe = sanitize_expression(expr)
            result = eval(safe, {"__builtins__": None}, {})
            if isinstance(result, float) and result.is_integer(): result = int(result)
            self._flash_equals()
            if self.enable_confetti_on_equals: self._confetti_burst_center()
            self._click_sound(520, 90)
            self._set_display(result)
        except Exception:
            self._click_sound(300, 120)
            self._set_display("Overengineered Error")

    # button handler
    def _on_button(self, label: str):
        tone = 640 if label in {"+","-","×","÷"} else 900 if label=="=" else 760 if label.isdigit() else 700
        self._click_sound(tone, 40 if label != "=" else 70)
        if self.enable_bursts_on_click: self._spawn_dot_near_button(label)
        if self.enable_wiggle: self._wiggle_display()
        if self.enable_button_jiggle: self._jiggle_button(label)
        if self.enable_operator_flash and label in {"+","-","×","÷"}: self._flash_operator(label)
        self.press(label)

    # flash equals
    def _flash_equals(self):
        b = self.buttons.get("=")
        if not b: return
        orig = b.cget("highlightbackground")
        b.config(highlightbackground="#9affd7")
        self.root.after(180, lambda: b.config(highlightbackground=orig))

    # flash operator
    def _flash_operator(self, label: str):
        b = self.buttons.get(label)
        if not b: return
        orig = b.cget("bg")
        b.config(bg=jitter_color(orig, 60))
        self.root.after(120, lambda: self._reset_button_bg(b, orig))

    def _reset_button_bg(self, btn: tk.Button, color: str):
        try: btn.config(bg=color)
        except: pass

    # wiggle display
    def _wiggle_display(self):
        seq = [0, 6, -6, 4, -4, 2, -2, 0]
        def step(i=0):
            if i >= len(seq): return
            self.disp_wrap.place_configure(x=self.disp_base_x + seq[i])
            self.root.after(18, lambda: step(i+1))
        step()

    # button jiggle
    def _jiggle_button(self, label: str):
        btn = self.buttons.get(label)
        if not btn: return
        seq = [0,2,-2,1,-1,0]
        orig_padx = 18; orig_pady = 18
        def s(i=0):
            if i>=len(seq):
                try: btn.config(padx=orig_padx, pady=orig_pady)
                except: pass
                return
            try: btn.config(padx=orig_padx+seq[i], pady=orig_pady+seq[i])
            except: pass
            self.root.after(14, lambda: s(i+1))
        s()

    # dots auto
    def _auto_pop(self):
        if self.enable_random_dots: self._spawn_dot()
        self.root.after(random.randint(120, 320), self._auto_pop)

    # spawn dot
    def _spawn_dot(self, at: Optional[Tuple[int,int]] = None):
        self.card.update_idletasks()
        w, h = self.card.winfo_width(), self.card.winfo_height()
        if at is None:
            x = random.randint(PADDING+8, w-PADDING-8)
            y = random.randint(PADDING+162, h-40)
        else:
            x, y = at
        size = random.randint(6, 16)
        color = random.choice(self.pop_colors)
        dot = tk.Canvas(self.card, width=size, height=size, bg=PALETTE["card"], highlightthickness=0, bd=0)
        dot.place(x=x, y=y)
        oid = dot.create_oval(0, 0, size, size, fill=color, outline="")
        self._animate_dot(dot, oid, size, 0)

    def _animate_dot(self, dot: tk.Canvas, oid: int, max_size: int, k: int):
        if k < 5:
            s = int(max_size * (1 + k*0.25))
            dot.config(width=s, height=s); dot.coords(oid, 0, 0, s, s)
            self.root.after(30, lambda: self._animate_dot(dot, oid, max_size, k+1))
        else:
            def shrink(i=5):
                if i<=0:
                    try: dot.destroy()
                    except: pass
                    return
                s2 = int(max_size * (1 + i*0.2))
                dot.config(width=s2, height=s2); dot.coords(oid, 0, 0, s2, s2)
                self.root.after(30, lambda: shrink(i-1))
            shrink()

    def _spawn_dot_near_button(self, label: str):
        btn = self.buttons.get(label)
        if not btn: return
        bx = btn.winfo_rootx() - self.card.winfo_rootx()
        by = btn.winfo_rooty() - self.card.winfo_rooty()
        bw, bh = btn.winfo_width(), btn.winfo_height()
        px = bx + random.randint(10, max(12, bw-12))
        py = by + random.randint(10, max(12, bh-12))
        for _ in range(random.randint(2,5)):
            jx = random.randint(-8,8); jy = random.randint(-8,8)
            self._spawn_dot((px + jx, py + jy))

    # marquee
    def _start_marquee(self):
        self.card.update_idletasks()
        self.marquee_x = -self.marquee.winfo_reqwidth()
        self.marquee.place(x=self.marquee_x, rely=1.0, y=-8, anchor="sw")
        self._marquee_step()

    def _marquee_step(self):
        width = self.card.winfo_width()
        self.marquee_x += 3
        if self.marquee_x > width:
            self.marquee_x = -self.marquee.winfo_reqwidth()
        self.marquee.place(x=self.marquee_x, rely=1.0, y=-8, anchor="sw")
        self.root.after(18, self._marquee_step)

    # display rainbow loop
    def _display_rainbow_loop(self):
        if self.enable_display_rainbow:
            base = PALETTE["display_fg"]
            t = (self._rainbow_step % 60) / 60.0
            col = mix(base, jitter_color("#6ef9ff", 32), t)
            try: self.entry.config(disabledforeground=col, insertbackground=col)
            except: pass
            self._rainbow_step += 1
        self.root.after(50, self._display_rainbow_loop)

    # title glow
    def _pulse_title_glow(self):
        if self.enable_glow_pulse:
            t = (self._pulse_tick % 40)/40.0
            c1, c2 = "#8fa8ff", "#a4b0d3"
            fg = mix(c1, c2, abs(2*t-1))
            try: self.title_lbl.config(fg=fg)
            except: pass
            self._pulse_tick += 1
        self.root.after(60, self._pulse_title_glow)

    # buttons glow pulse
    def _pulse_buttons_glow(self):
        if self.enable_button_glow:
            phase = (self._btn_glow_phase % 40)/40.0
            for label, btn in self.buttons.items():
                bg, hov, prs, fg, outline = neon_styles(label)
                oc = mix(outline, jitter_color(outline, 40), abs(2*phase-1))
                try: btn.config(highlightbackground=oc, highlightcolor=oc)
                except: pass
            self._btn_glow_phase += 1
        self.root.after(70, self._pulse_buttons_glow)

    # title wave 
    def _title_wave_tick(self):
        if not self.enable_title_wave:
            self.root.after(120, self._title_wave_tick)
            return
        text = "Overengineered Calculator"
        phase = self._wave_phase
        styled = []
        for i,ch in enumerate(text):
            t = (phase + i) % 10
            col = mix("#a4b0d3", "#bcd2ff", t/10)
            styled.append((ch, col))
        
        avg_col = mix("#a4b0d3", "#bcd2ff", ((phase%10)/10))
        try: self.title_lbl.config(fg=avg_col)
        except: pass
        self._wave_phase += 1
        self.root.after(120, self._title_wave_tick)

    # confetti
    def _confetti_burst_center(self):
        cx = self.card.winfo_width()//2
        cy = PADDING+162 + 300
        for _ in range(14):
            self._confetti_piece((cx + random.randint(-40,40), cy + random.randint(-30,30)))

    def _confetti_piece(self, at: Tuple[int,int]):
        x,y = at
        size = random.randint(6,12)
        color = random.choice(self.pop_colors)
        canvas = tk.Canvas(self.card, width=size*2, height=size*2, bg=PALETTE["card"], highlightthickness=0, bd=0)
        canvas.place(x=x, y=y)
        pts = [0,size*2, size,size*0, size*2,size*2]
        poly = canvas.create_polygon(pts, fill=color, outline="")
        self._animate_confetti(canvas, poly, x, y, size)

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
            self.root.after(24, lambda: step(i+1, x, y))
        step()

    # AC easter egg
    def _record_ac_press(self):
        t = time.time()
        self._ac_press_times = [tt for tt in self._ac_press_times if t-tt < 1.2]
        self._ac_press_times.append(t)
        if len(self._ac_press_times) >= 5:
            self._party_mode()

    def _party_mode(self):
        keys = list(self.buttons.values())
        def strobe(k=0):
            if k>=10:
                for b in keys: self._reset_button_colors(b)
                return
            for b in keys: self._randomize_button_colors(b)
            self.root.after(80, lambda: strobe(k+1))
        strobe()

    def _reset_button_colors(self, btn: tk.Button):
        txt = btn.cget("text")
        bg, hov, prs, fg, outline = neon_styles(txt)
        fg = ensure_contrast(bg, fg)
        try:
            btn.config(bg=bg, fg=fg, activeforeground=fg, activebackground=prs, highlightbackground=outline, highlightcolor=outline)
        except: pass

    def _randomize_button_colors(self, btn: tk.Button):
        txt = btn.cget("text")
        bg, hov, prs, fg, outline = neon_styles(txt)
        bg2 = jitter_color(bg, 40); hov2 = jitter_color(hov, 40); prs2 = jitter_color(prs, 40); fg2 = ensure_contrast(bg2, jitter_color(fg, 40)); out2 = jitter_color(outline, 40)
        try:
            btn.config(bg=bg2, fg=fg2, activeforeground=fg2, activebackground=prs2, highlightbackground=out2, highlightcolor=out2)
        except: pass

# run
def create_overengineered_calculator() -> OverengineeredCalculator:
    root = tk.Tk()
    return OverengineeredCalculator(root)

def run_overengineered_calculator():
    app = create_overengineered_calculator()
    app.root.mainloop()

# main
if __name__ == "__main__":
    run_overengineered_calculator()
