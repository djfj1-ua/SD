import argparse
from EC_S import Sensor

PROG_NAME = "Sensor"
PROG_DESC = "Aplicación que iniciará el sensor del Taxi."

def parse_args():
    parser = argparse.ArgumentParser(prog=PROG_NAME, description=PROG_DESC)

    parser.add_argument("--engine-ip", type=str, required=True)
    parser.add_argument("--engine-port", type=int, required=True)

    return parser.parse_args()

def main(args):
    servidor = Sensor(args)
    servidor.serve()

if __name__ == "__main__":
    args = parse_args()
    main(args)