import argparse
from EC_Customer import Customer

PROG_NAME = "Cliente"
PROG_DESC = "Aplicación que iniciará a un cliente."

def parse_args():
    parser = argparse.ArgumentParser(prog=PROG_NAME, description=PROG_DESC)

    parser.add_argument("--broker-ip", type=str, required=True)
    parser.add_argument("--broker-port", type=int, required=True)
    parser.add_argument("--customer-id", type=int, required=True)

    return parser.parse_args()

def main(args):
    cliente = Customer(args)
    cliente.serve()

if __name__ == "__main__":
    args = parse_args()
    main(args)