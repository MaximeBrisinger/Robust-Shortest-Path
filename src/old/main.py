import argparse
from pathlib import Path
import src.with_dual


def main(args):
    getattr(src.with_dual, args.method)(args.input, args.time_limit)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--method', choices=['duality'], default="duality", type=str)
    parser.add_argument('--input', default='20_USA-road-d.BAY.gr', type=str,
                        help='File name of the instance to solve')
    parser.add_argument('--time_limit', default=10)
    args = parser.parse_args()
    main(args)
