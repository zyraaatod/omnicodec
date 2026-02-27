from __future__ import annotations

from dataclasses import dataclass
import shutil
import sys


@dataclass(frozen=True)
class Color:
    reset: str = "\033[0m"
    bold: str = "\033[1m"
    dim: str = "\033[2m"
    black: str = "\033[30m"
    red: str = "\033[91m"
    green: str = "\033[92m"
    yellow: str = "\033[93m"
    blue: str = "\033[94m"
    magenta: str = "\033[95m"
    cyan: str = "\033[96m"
    white: str = "\033[97m"
    magenta_bg: str = "\033[45m"
    gray: str = "\033[90m"


C = Color()

# ANSI escape codes
CLEAR_SCREEN = "\033[2J\033[H"
CLEAR_LINE = "\033[2K"
CURSOR_UP = "\033[A"


def clear_screen() -> None:
    """Clear terminal screen and move cursor to home position."""
    print(CLEAR_SCREEN, end="")
    sys.stdout.flush()


def _term_width(default: int = 100) -> int:
    return shutil.get_terminal_size((default, 24)).columns


def _box(title: str, lines: list[str], color: str = C.cyan, width: int | None = None) -> str:
    """Create a bordered box with title."""
    w = width or min(max(_term_width(), 80), 120)
    inner = w - 4  # Account for borders and padding
    encoding = (sys.stdout.encoding or "").lower()
    unicode_ok = "utf" in encoding or sys.platform != "win32"

    if unicode_ok:
        h, v, tl, tr, bl, br, jt, jb = "═", "║", "╔", "╗", "╚", "╝", "╠", "╣"
    else:
        h, v, tl, tr, bl, br, jt, jb = "-", "|", "+", "+", "+", "+", "+", "+"

    top = f"{color}{tl}{h * (w - 2)}{tr}{C.reset}"
    head = f"{color}{v}{C.bold}  {title[: w - 6]:^{w - 6}}  {C.reset}{color}{v}{C.reset}"
    sep = f"{color}{jt}{h * (w - 2)}{jb}{C.reset}"
    body = []
    for line in lines:
        # Wrap long lines
        wrapped = []
        for i in range(0, max(len(line), 1), inner):
            wrapped.append(line[i:i + inner])
        for wline in wrapped:
            body.append(f"{color}{v}{C.reset}  {wline[:inner]:<{inner}}  {color}{v}{C.reset}")
    bottom = f"{color}{bl}{h * (w - 2)}{br}{C.reset}"
    return "\n".join([top, head, sep, *body, bottom])


def banner() -> str:
    """Create the OMNICODEC banner."""
    lines = [
        "",
        f"{C.cyan}{C.bold}  ██████╗ ███╗   ███╗███╗   ██╗██╗ ██████╗ ██████╗ ██████╗ ███████╗ ██████╗{C.reset}",
        f"{C.blue}{C.bold} ██╔═══██╗████╗ ████║████╗  ██║██║██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔════╝{C.reset}",
        f"{C.magenta}{C.bold} ██║   ██║██╔████╔██║██╔██╗ ██║██║██║     ██║   ██║██║  ██║█████╗  ██║     {C.reset}",
        f"{C.yellow}{C.bold} ╚██████╔╝██║╚██╔╝██║██║╚██╗██║██║╚██████╗╚██████╔╝██████╔╝███████╗╚██████╗{C.reset}",
        f"{C.dim}{C.gray}  Universal Encode/Decode Toolkit - Termux • Linux • macOS{C.reset}",
        "",
    ]
    return "\n".join(lines)


def home_panel(total_methods: int, total_categories: int, uptime: str, last_action: str) -> str:
    """Create the home panel with stats and menu."""
    lines = [
        "",
        f"{C.yellow}{C.bold}Statistics:{C.reset}",
        f"  Methods:    {C.cyan}{total_methods}{C.reset}",
        f"  Categories: {C.cyan}{total_categories}{C.reset}",
        f"  Uptime:     {C.cyan}{uptime}{C.reset}",
        f"  Last:       {C.cyan}{last_action or 'None'}{C.reset}",
        "",
        f"{C.yellow}{C.bold}Main Menu:{C.reset}",
        f"  {C.cyan}[1, e]{C.reset} ENC       - Encode data dengan 1 method",
        f"  {C.cyan}[2, d]{C.reset} DEC       - Decode data back to original",
        f"  {C.cyan}[3, l]{C.reset} LIST      - List all available methods",
        f"  {C.cyan}[s]{C.reset} SPESIAL   - 🔥 SPESIAL: 1 file → 1 file (all enc) ⭐",
        f"  {C.cyan}[a]{C.reset} ENC ALL   - Encode 1 file dengan SEMUA method!",
        f"  {C.cyan}[c]{C.reset} CLEAR     - Refresh and clear the screen",
        f"  {C.cyan}[h]{C.reset} HELP      - Show help information",
        f"  {C.cyan}[q]{C.reset} EXIT      - Exit application",
        "",
        f"{C.red}{C.bold}  [x] ALL IN ONE  - Process 1 file: ENC+DEC semua method! 🔥{C.reset}",
        "",
        f"{C.dim}  Shortcuts: clear/cls | help/? | 1/enc | 2/dec | 3/list | s/spesial | a/enc-all | x/all-in-one | q/quit{C.reset}",
        "",
    ]
    return _box("MAIN CONTROL", lines, color=C.cyan)


def methods_panel(category: str, rows: list[str]) -> str:
    return _box(f"METHODS - {category}", rows, color=C.magenta)


def print_success(msg: str) -> None:
    """Print success message with green checkmark."""
    symbol = "✓" if sys.stdout.encoding and "utf" in sys.stdout.encoding.lower() else "[+]"
    print(f"{C.green}{C.bold}{symbol}{C.reset} {C.green}{msg}{C.reset}")


def print_error(msg: str) -> None:
    """Print error message with red X."""
    symbol = "✗" if sys.stdout.encoding and "utf" in sys.stdout.encoding.lower() else "[!]"
    print(f"{C.red}{C.bold}{symbol}{C.reset} {C.red}{msg}{C.reset}")


def print_info(msg: str) -> None:
    """Print info message with blue i."""
    symbol = "ℹ" if sys.stdout.encoding and "utf" in sys.stdout.encoding.lower() else "[i]"
    print(f"{C.cyan}{C.bold}{symbol}{C.reset} {C.cyan}{msg}{C.reset}")


def print_warning(msg: str) -> None:
    """Print warning message with yellow exclamation."""
    symbol = "⚠" if sys.stdout.encoding and "utf" in sys.stdout.encoding.lower() else "[!]"
    print(f"{C.yellow}{C.bold}{symbol}{C.reset} {C.yellow}{msg}{C.reset}")


def prompt() -> str:
    return f"\n{C.magenta_bg}{C.black}{C.bold} omnicodec > {C.reset} "


def separator() -> str:
    """Return a visual separator line."""
    width = _term_width()
    return f"{C.dim}{'─' * width}{C.reset}"
