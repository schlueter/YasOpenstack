import sys

def log(*msgs):
    print(*msgs, file=sys.stderr)
