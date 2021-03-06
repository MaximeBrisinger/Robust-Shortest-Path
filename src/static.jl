

module Static

export solve_static

ENV["CPLEX_STUDIO_BINARIES"] = "/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/"

include("data.jl")
using .dataUtils

using JuMP, CPLEX

#devenue inutile

function solve_static(input_graph, dict_row, verbose, CPU_time_limit)

    model = Model(CPLEX.Optimizer)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, y[1:input_graph.n], binary=true)

    #OBJECTIVE
    @objective(model, Min, sum(input_graph.traveltime_matrix[a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs))

    #FLOWS
    @expression(model, inflow[i=1:input_graph.n], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[2] == i))
    @expression(model, outflow[i=1:input_graph.n], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[1] == i))

    @constraint(model, flow[i=1:input_graph.n; i!=input_graph.s && i!=input_graph.t], inflow[i] - outflow[i] == 0)
    @constraint(model, flow_s1, outflow[input_graph.s] == 1)
    @constraint(model, flow_s2, inflow[input_graph.s] == 0)
    @constraint(model, flow_t1, inflow[input_graph.t] == 1)
    @constraint(model, flow_t2, outflow[input_graph.t] == 0)


    #SET Y VALUES
    @constraint(model, set_y[i=1:input_graph.n; i!=input_graph.t], outflow[i] - y[i] == 0)
    @constraint(model, set_yt, inflow[input_graph.t] - y[input_graph.t] == 0)

    #CAPACITY
    @constraint(model, capa, sum([y[i] * input_graph.weights[i] for i in 1:input_graph.n]) <= input_graph.S)
    

    set_time_limit_sec(model, CPU_time_limit)

    optimize!(model)

    if verbose
        println("SOLUTION :")
        println("VALEUR ", objective_value(model))
        x_val = value.(x)
        eps = 10^(-5)
        for a in input_graph.arcs
            if x_val[a] > 1-eps
                println(a[1], "->", a[2], " ", input_graph.traveltime_matrix[a[1], a[2]], " ", input_graph.ceil_uncert_traveltime[a[1], a[2]])
            end
        end
        println()
        for i in 1:input_graph.n
            if y_val[i] > 1-eps
                println(i, " ", input_graph.weights[i], " ", input_graph.weights_uncert[i])
            end
        end
    end

    push!(dict_row, "Nombre de variables" => numvar(model))
    push!(dict_row, "Time (s)" => solve_time(model))
    push!(dict_row, "Time limit (s)" => CPU_time_limit)
    push!(dict_row, "Nombre de noeuds" => node_count(model))
    push!(dict_row, "termination status" => (termination_status(model) == MOI.OPTIMAL))
    push!(dict_row, "has_value" => has_values(model))
    push!(dict_row, "is_feasible" => (primal_status(model) == MOI.FEASIBLE_POINT))

    if has_values(model)
        push!(dict_row, "Objective value" => objective_value(model))
        push!(dict_row, "objective bound" => objective_bound(model))
        push!(dict_row, "Gap" => MOI.get(model, MOI.RelativeGap()))
    else
        push!(dict_row, "Objective value" => missing)
        push!(dict_row, "Gap" => missing)
        push!(dict_row, "objective bound" => missing)
    end
    return dict_row
end

# time_limit = 60
# input_graph = dataUtils.readData("data/20_USA-road-d.NY.gr")
# solve_dual(input_graph, time_limit)
end 