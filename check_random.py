import argparse
import math
import random
import sys
import traceback


def excepthook(type, value, tb):
    traceback.print_exception(type, value, tb)
    sys.exit(3)


def magic(x):
    return '' if x is None else x


sys.excepthook = excepthook

argparser = argparse.ArgumentParser()

argparser.add_argument('-l', '--limit', type=int, required=True)
argparser.add_argument('-w', '--warning', type=int)
argparser.add_argument('-c', '--critical', type=int)
argparser.add_argument('-u', '--unknown', type=int)

try:
    args = argparser.parse_args()
except SystemExit:
    sys.exit(3)

random.seed()
x = random.randrange(0, args.limit)

for (threshold, code, status) in (
        (args.unknown, 3, 'UNKNOWN'),
        (args.critical, 2, 'CRITICAL'),
        (args.warning, 1, 'WARNING'),
        (-math.inf, 0, 'OK')
):
    if threshold is not None and x > threshold:
        print(f'RANDOM {status}: {x} |x={x};{magic(args.warning)};{magic(args.critical)};0;{args.limit}')
        sys.exit(code)
