include("data.jl")

#ENV["CPLEX_STUDIO_BINARIES"] = "C:/Program Files/IBM/ILOG/CPLEX_Studio1210/cplex/bin/x64_win64/"
ENV["CPLEX_STUDIO_BINARIES"] = "/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/"
import .dataUtils
using JuMP, CPLEX

function build_dual(input_graph)

    model = Model(CPLEX.Optimizer)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, t1, lower_bound=0)
    @variable(model, t2, lower_bound=0)
    @variable(model, z[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], lower_bound=0)
    @variable(model, z_prime[1:input_graph.n], lower_bound=0)
    @variable(model, y[1:input_graph.n], binary=true)

    #OBJECTIVE
    @objective(model, Min, sum(input_graph.traveltime_matrix[a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs)
                        + t1 * input_graph.d1
                        + sum(input_graph.ceil_uncert_traveltime[a[1], a[2]] * z[(a[1], a[2])] for a in input_graph.arcs)
    )

    #FLOWS
    @expression(model, inflow[i=1:input_graph.n; i!=input_graph.s], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[2] == i))
    @expression(model, outflow[i=1:input_graph.n; i!=input_graph.t], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[1] == i))

    @constraint(model, flow[i=1:input_graph.n; i!=input_graph.s && i!=input_graph.t], inflow[i] - outflow[i] == 0)
    @constraint(model, flow_s, outflow[input_graph.s] == 1)
    @constraint(model, flow_t, inflow[input_graph.t] == 1)

    #SET Y VALUES
    @constraint(model, set_y[i=1:input_graph.n; i!=input_graph.t], outflow[i] - y[i] == 0)
    @constraint(model, set_yt, inflow[input_graph.t] - y[input_graph.t] == 0)

    #CAPACITY
    @constraint(model, capa, sum([y[i] * input_graph.weights[i] + 2 * z_prime[i] for i in 1:input_graph.n]) + t2 * input_graph.d2 <= input_graph.S)

    #SETTING THE VALUES OF T1 AND T2
    @constraint(model, set_t1[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], t1 + z[a] >= input_graph.traveltime_matrix[a[1], a[2]] * x[a])
    @constraint(model, set_t2[i=1:input_graph.n], t2 + z_prime[i] >= input_graph.weights_uncert[i] * y[i])

    return model
end

function solve_dual(input_graph, CPU_time_limit)

    model = Model(CPLEX.Optimizer)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, t1, lower_bound=0)
    @variable(model, t2, lower_bound=0)
    @variable(model, z[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], lower_bound=0)
    @variable(model, z_prime[1:input_graph.n], lower_bound=0)
    @variable(model, y[1:input_graph.n], binary=true)

    #OBJECTIVE
    @objective(model, Min, sum(input_graph.traveltime_matrix[a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs)
                        + t1 * input_graph.d1
                        + sum(input_graph.ceil_uncert_traveltime[a[1], a[2]] * z[(a[1], a[2])] for a in input_graph.arcs)
    )

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
    @constraint(model, capa, sum([y[i] * input_graph.weights[i] + 2 * z_prime[i] for i in 1:input_graph.n]) + t2 * input_graph.d2 <= input_graph.S)

    #SETTING THE VALUES OF T1 AND T2
    @constraint(model, set_t1[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], t1 + z[a] >= input_graph.traveltime_matrix[a[1], a[2]] * x[a])
    @constraint(model, set_t2[i=1:input_graph.n], t2 + z_prime[i] >= input_graph.weights_uncert[i] * y[i])


    println("")
    println("---------- Resolution ----------")
    set_time_limit_sec(model, CPU_time_limit)
    optimize!(model)
    println(objective_value(model))

    x_val = value.(x)
    eps = 10^(-5)
    for a in input_graph.arcs
        if x_val[a] > 1-eps
            println(a[1], "->", a[2], " ", input_graph.traveltime_matrix[a[1], a[2]], " ", input_graph.ceil_uncert_traveltime[a[1], a[2]])
        end
    end
        
end

time_limit = 60
input_graph = dataUtils.readData("data/20_USA-road-d.BAY.gr")
solve_dual(input_graph, time_limit)
