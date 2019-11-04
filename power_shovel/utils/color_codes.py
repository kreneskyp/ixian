BOLD_WHITE = "\033[1m"
RED = "\033[91m"
OK_GREEN = "\033[92m"
ENDC = "\033[0m"
YELLOW = "\033[93m"
GRAY = "\033[90m"


def format(txt, color):
    return "{color}{txt}{end}".format(color=color, txt=txt, end=ENDC)


def red(txt):
    return format(txt, RED)


def green(txt):
    return format(txt, OK_GREEN)


def yellow(txt):
    return format(txt, YELLOW)


def gray(txt):
    return format(txt, GRAY)


def bold_white(txt):
    return format(txt, BOLD_WHITE)
