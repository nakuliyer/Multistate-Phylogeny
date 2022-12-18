from argparse import ArgumentParser
import os

from implementation import *

two_state_dir = "sample_two_state_runs"
three_state_dir = "sample_three_state_runs"

parser = ArgumentParser()

parser.add_argument("-d", "--draw", dest="draw",
                    help="draw matrices on success", action='store_true')
parser.add_argument("-a", "--all", dest="runall",
                    help="run all test matrices", action='store_true')
parser.add_argument("-f", "--file", dest="filename",
                    help="file representing the input matrix")
parser.add_argument("-n", "--numstates", dest="numstates", type=int,
                    choices=[2, 3], default=3, 
                    help="don't print status messages to stdout")

args = parser.parse_args()

if not args.runall and not args.filename or args.runall and args.filename:
    raise Exception("Must either pass a test matrix file with \"-f\" or specify all testing matrices to be run with \"-a\"")

def run_from_file(fname: str, states: int):
    M = np.loadtxt(fname)
    if states == 2:
        T = two_state_phylo(M, draw=args.draw)
    elif states == 3:
        T = three_state_phylo(M, draw=args.draw)
    if T:
        print(f"Matrix \"{fname}\" has a perfect phylogeny")
    else:
        print(f"Matrix \"{fname}\" does not have a perfect phylogeny")

if args.runall:
    for fname in os.listdir(two_state_dir):
        f = os.path.join(two_state_dir, fname)
        run_from_file(f, 2)
    for fname in os.listdir(three_state_dir):
        f = os.path.join(three_state_dir, fname)
        run_from_file(f, 3)
else:
    run_from_file(args.filename, args.numstates)