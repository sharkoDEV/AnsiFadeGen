# gradient.py
from math import floor

PRESETS = {
    "red": (255, 0, 0),
    "yellow": (255, 255, 0),
    "green": (37, 196, 104),
    "lime": (0, 255, 0),
    "blue": (0, 0, 255),
    "cyan": (0, 255, 255),
    "grey": (186, 191, 188),
    "gray": (186, 191, 188),
    "white": (255, 255, 255),
    "pink": (255, 0, 230),
    "purple": (162, 0, 255),
}

# === ANSI constants (ESC real) ===
ESC = "\033"          # ASCII 27 (escape)
RESET = f"{ESC}[0m"

def ansi_truecolor(r: int, g: int, b: int, ch: str) -> str:
    return f"{ESC}[38;2;{r};{g};{b}m{ch}"

def parse_color(s: str):
    s = s.lower()
    if s in PRESETS:
        return PRESETS[s]
    try:
        r, g, b = map(int, s.split(","))
        return (r, g, b)
    except Exception:
        raise ValueError(f"Invalid color: {s}")

def lerp(a: int, b: int, t: float) -> int:
    return int(a + (b - a) * t)

def generate_gradient_text(lines, color_list, direction="diagonal"):
    """
    Apply a multi-stop gradient to ASCII lines.
    direction: "horizontal" | "vertical" | "diagonal"
    color_list: e.g. ["red","blue"] or ["255,0,0","0,0,255", "255,255,0"]
    """
    colors = [parse_color(c) for c in color_list]
    if len(colors) < 2:
        raise ValueError("At least two colors required for gradient.")

    n = len(colors) - 1
    h = len(lines)
    w = max((len(l) for l in lines), default=0)

    out_lines = []
    for y, line in enumerate(lines):
        # keep trailing spaces (don’t rstrip), but drop only the newline
        line_no_nl = line[:-1] if line.endswith("\n") else line
        buf = []
        for x, ch in enumerate(line_no_nl):
            if direction == "horizontal":
                t = x / max(1, w - 1)
            elif direction == "vertical":
                t = y / max(1, h - 1)
            else:  # diagonal
                t = ((x / max(1, w - 1)) + (y / max(1, h - 1))) / 2

            seg = min(floor(t * n), n - 1)
            local_t = (t * n) - seg

            c1, c2 = colors[seg], colors[seg + 1]
            r = lerp(c1[0], c2[0], local_t)
            g = lerp(c1[1], c2[1], local_t)
            b = lerp(c1[2], c2[2], local_t)

            buf.append(ansi_truecolor(r, g, b, ch))

        out_lines.append("".join(buf) + RESET)
    return "\n".join(out_lines)
