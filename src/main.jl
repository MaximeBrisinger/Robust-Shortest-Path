
include("branch_and_cut_integer.jl")
include("cutting_planes2.jl")
include("duality.jl")
include("data.jl")


using ArgParse, CSV, DataFrames

using .BranchAndCut, .CuttingPlanes, .Duality, .dataUtils

function main(mode, verbose, path_to_data, CPU_time_limit)
    input_graph = dataUtils.readData(path_to_data)

    if mode == "Duality"
        dict_row = Dict{String, Any}()
        dict_row["path"] = path_to_data
        dict_row = Duality.solve_dual(input_graph, dict_row, verbose, CPU_time_limit)

        if isfile("saves/benchmark_dual.csv")
            df = DataFrame(CSV.File("saves/benchmark_dual.csv"))
            append!(df, DataFrame(dict_row))
        else
            df = DataFrame(dict_row)
        end
        CSV.write("saves/benchmark_dual.csv", df)

    elseif mode == "BranchAndCut"
        dict_row = Dict{String, Any}()
        dict_row["path"] = path_to_data
        dict_row = BranchAndCut.branch_and_cut_integer(input_graph, dict_row, verbose, CPU_time_limit)

        if isfile("saves/benchmark_BC.csv")
            df = DataFrame(CSV.File("saves/benchmark_BC.csv"))
            append!(df, DataFrame(dict_row))
        else
            df = DataFrame(dict_row)
        end
    
        CSV.write("saves/benchmark_BC.csv", df)

    elseif mode == "CuttingPlanes"
        dict_row = Dict{String, Any}()
        dict_row["path"] = path_to_data
        dict_row = CuttingPlanes.cutting_planes(input_graph, dict_row, verbose, CPU_time_limit)

        if isfile("saves/benchmark_CP.csv")
            df = DataFrame(CSV.File("saves/benchmark_CP.csv"))
            append!(df, DataFrame(dict_row))
        else
            df = DataFrame(dict_row)
        end

        CSV.write("saves/benchmark_CP.csv", df)
    end
end

function parse_commandline(args)
    s = ArgParseSettings()
    @add_arg_table s begin
        "--mode"
            help = "mode de modélisation : Duality;
                                            DualityVanilla;
                                            CuttingPlanes;
                                            BranchAndCut"
            # arg_type = String
            default = "Duality"
        "--verbose"
            help = "indique si les logs doivent être affichés"
            arg_type = Bool
            default = false
        "--data"
            help = "path to data"
            # arg_type = String
            default = "data/20_USA-road-d.NY.gr"
        "--CPU_time_limit"
            help = "CPU time limit"
            arg_type = Float64
            default = 2.0 * 60.0

    end

    pa = parse_args(args, s)
    mode = pa["mode"]
    verbose = pa["verbose"]
    data = pa["data"]
    # save_file = pa["save_file"]
    CPU_time_limit = pa["CPU_time_limit"]

    main(mode, verbose, data, CPU_time_limit)

end

parse_commandline(ARGS)