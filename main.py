import argparse
from src.old.utils import save_results_csv
from src.old.antcolony import AntColony


def main(args):
    file = args.input
    time_limit = args.time_limit
    nb_ants = args.nb_ants
    t_max = args.t_max

    data_folder = "src/data/"

    ac = AntColony(input_folder=data_folder,
                   input_file=file,
                   nb_ants=nb_ants,
                   t_max=t_max,
                   time_limit=time_limit)

    path, cost, initial_path, initial_cost, total_time, time_for_best_value = ac.main()

    print(f"\nBest cost is {cost}, with path {path}")
    print(f"\nInitial best cost was {initial_cost}, with path {initial_path}")
    print(f"\nExecution time : {total_time}s")
    print(f"\nTime to reach best value : {time_for_best_value}s")

    save_results_csv(obj=cost,
                     time=total_time,
                     time_best=time_for_best_value,
                     instance=file,
                     nb_ants=ac.m,
                     t_max=ac.t_max,
                     improve_init=bool(cost < initial_cost),
                     termination_status=(not ac.interrupted)
                     )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('--input', default='20_USA-road-d.BAY.gr', type=str,
                        help='File name of the instance to solve')
    parser.add_argument('--nb_ants', default=30, help='Number of ants in the colony', type=int)
    parser.add_argument('--t_max', default=13, help='Maximum number of iterations', type=int)
    parser.add_argument('--time_limit', default=60, type=int)
    args = parser.parse_args()
    main(args)
