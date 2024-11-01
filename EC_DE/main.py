import argparse
import threading
from EC_DE import Engine

PROG_NAME = "Engine"
PROG_DESC = "Aplicación que iniciará el Engine del Taxi."

def parse_args():
    parser = argparse.ArgumentParser(prog=PROG_NAME, description=PROG_DESC)

    parser.add_argument("--central-ip", type=str, required=True)
    parser.add_argument("--central-port", type=int, required=True)
    parser.add_argument("--broker-ip", type=str, required=True)
    parser.add_argument("--broker-port", type=int, required=True)
    parser.add_argument("--taxi-id", type=int, required=True)

    return parser.parse_args()

def main(args):
    servidor = Engine(args)
    servidor.serve()

if __name__ == "__main__":
    args = parse_args()
    main(args)