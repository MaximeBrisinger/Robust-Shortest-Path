# include("data.jl")

module CuttingPlanesInt

export cutting_planes

ENV["CPLEX_STUDIO_BINARIES"] = "/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/"


include("data.jl")
using .dataUtils
using JuMP, CPLEX



function SP1(arcs, input_graph)
    """
    modelizes the problem as a fractionnary-backpack problem
    arcs : list of tuples representing arcs ij with x_ij=1 in the current solution
    input_graph : instance of InputGraph
    """
    sort!(arcs, by= a->a[3] , rev=true)

    i=1
    quantity=0
    contin=true
    sol_sp1 = []
    val_sp1 = 0
    while i <= length(arcs) && contin
        if quantity + arcs[i][4] <= input_graph.d1
            quantity += arcs[i][4]
            val_sp1 += arcs[i][3] * arcs[i][4]
            push!(sol_sp1, (arcs[i][1], arcs[i][2], arcs[i][3], arcs[i][4]))
        else
            push!(sol_sp1, (arcs[i][1], arcs[i][2], arcs[i][3], input_graph.d1 - quantity))
            val_sp1 += arcs[i][3] * (input_graph.d1 - quantity)
            contin= false
        end
        i += 1
    end

    return sol_sp1, sum(a[3] for a in arcs) + val_sp1
end

function SP2(vertexes, input_graph)
    """
    modelizes the problem as a fractionnary-backpack problem
    x : list representing vetexes et i with x_i=1 in the current solution
    input_graph : instance of InputGraph
    """
    sort!(vertexes, by= x->x[3], rev=true)

    i=1
    quantity=0
    contin=true
    sol_sp2 = []
    val_sp2 = 0
    while i <= length(vertexes) && contin
        if quantity + 2 <= input_graph.d2
            quantity += 2
            val_sp2 +=  2 * vertexes[i][3]
            push!(sol_sp2, (vertexes[i][1], vertexes[i][2], vertexes[i][3], 2))
        else
            push!(sol_sp2, (vertexes[i][1], vertexes[i][2], vertexes[i][3], input_graph.d2 - quantity))
            val_sp2 += (input_graph.d2 - quantity) * vertexes[i][3]
            contin= false
        end
        i += 1
    end

    return sol_sp2, sum(v[2] for v in vertexes) + val_sp2
end

function init_master_Problem(input_graph, U1, U2)
    """
    input_graph : instance of the class InputGraph of data.jl
    U1 : lists of matrixes of size n x n. Each elements of U1 is a admissible realisation of (delta_ij^1)_ij
    U2 : lists of lists of size n. Each elements of U1 is a admissible realisation of p_i^2
    """

    model = Model(CPLEX.Optimizer)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, y[1:input_graph.n], binary=true)
    @variable(model, z, lower_bound=0)

    #OBJECTIVE
    @objective(model, Min, z)

    #SETTING Z
    #@constraint(model, set_z[s=1:length(U1)], z >= sum(U1[s][a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs))

    #FLOWS
    @expression(model, inflow[i=1:input_graph.n; i!=input_graph.s], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[2] == i))
    @expression(model, outflow[i=1:input_graph.n; i!=input_graph.t], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[1] == i))

    @constraint(model, flow[i=1:input_graph.n; i!=input_graph.s && i!=input_graph.t], inflow[i] - outflow[i] == 0)
    @constraint(model, flow_s, outflow[input_graph.s] == 1)
    @constraint(model, flow_t, inflow[input_graph.t] == 1)

    #SETTING Y VALUES
    @constraint(model, set_y[i=1:input_graph.n; i!=input_graph.t], outflow[i] - y[i] == 0)
    @constraint(model, set_yt, inflow[input_graph.t] - y[input_graph.t] == 0)
    
    #CAPACITY
    #@constraint(model, set_capas[s=1:length(U2)], sum(U2[s][i] * y[i] for i in 1:input_graph.n) <= input_graph.S)

    return model
end

function cutting_planes(input_graph, dict_row, verbose, CPU_time_limit)
    U1 = []
    U2 = [input_graph.weights]
    
    # MODEL DEFINITION 
    model = Model(CPLEX.Optimizer)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, y[1:input_graph.n], binary=true)
    @variable(model, z, lower_bound=0)

    #OBJECTIVE
    @objective(model, Min, z)

    #SETTING Z
    @constraint(model, set_z[s=1:length(U1)], z >= sum(U1[s][a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs))

    #FLOWS
    @expression(model, inflow[i=1:input_graph.n], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[2] == i))
    @expression(model, outflow[i=1:input_graph.n], sum(x[(a[1], a[2])] for a in input_graph.arcs if a[1] == i))

    @constraint(model, flow[i=1:input_graph.n; i!=input_graph.s && i!=input_graph.t], inflow[i] - outflow[i] == 0)
    @constraint(model, flow_s1, outflow[input_graph.s] == 1)
    @constraint(model, flow_s2, inflow[input_graph.s] == 0)
    @constraint(model, flow_t1, inflow[input_graph.t] == 1)
    @constraint(model, flow_t2, outflow[input_graph.t] == 0)


    #SETTING Y VALUES
    @constraint(model, set_y[i=1:input_graph.n; i!=input_graph.t], outflow[i] - y[i] == 0)
    @constraint(model, set_yt, inflow[input_graph.t] - y[input_graph.t] == 0)
    
    #CAPACITY
    @constraint(model, set_capas[s=1:length(U2)], sum(U2[s][i] * y[i] for i in 1:input_graph.n) <= input_graph.S)


    MOI.set(model, MOI.NumberOfThreads(), 1)

    contin = true
    optim = false
    start = time()
    eps = 10 ^ (-5)
    n_solve = 0
    set_optimizer_attribute(model, "CPX_PARAM_SCRIND", 0)
    while contin
        set_time_limit_sec(model, CPU_time_limit - (time()-start))
        optimize!(model)
        n_solve += 1
        x_val = value.(x)
        y_val = value.(y)
        z_val = value.(z)


               
        arcs = [(a[1], a[2], input_graph.traveltime_matrix[a[1], a[2]], input_graph.ceil_uncert_traveltime[a[1], a[2]]) for a in input_graph.arcs if x_val[(a[1], a[2])] >= eps] #TOD0: transformer en 1-eps
        sol_sp1, val_sp1 = SP1(arcs, input_graph)

        # SP2
        vertexes = [(i, input_graph.weights[i], input_graph.weights_uncert[i]) for i in 1:input_graph.n if y_val[i] >= 1-eps]
        sol_sp2, val_sp2 = SP2(vertexes, input_graph)

        if !(CPU_time_limit - (time()-start) > eps)
            contin = false
        end

        if !(abs(z_val - val_sp1) < eps && input_graph.S >= val_sp2) #solution non optimale
            if contin
                @constraint(model, z >= sum(a[3] * a[4] * x[(a[1], a[2])] for a in sol_sp1) + sum(x[(a[1], a[2])] * input_graph.traveltime_matrix[a[1], a[2]] for a in input_graph.arcs))
                @constraint(model, sum(y[v[1]] * input_graph.weights[v] for v in 1:input_graph.n) + sum(y[v[1]] * v[3] * v[4] for v in sol_sp2) <= input_graph.S)
            end
        else 
            contin = false #ca marche
            optim = true
        end
    end


    if verbose
        println("SOLUTION :")
        println("OPTIMALE ? ", optim)
        println("VALEUR ", objective_value(model))
        x_val = value.(x)
        y_val = value.(y)
        out_flow_val = value.(outflow)
        eps = 10^(-5)
        for a in input_graph.arcs
            if x_val[a] > eps
                println(a[1], "->", a[2], " ", input_graph.traveltime_matrix[a[1], a[2]], " ", input_graph.ceil_uncert_traveltime[a[1], a[2]], " ", x_val[a])
            end
        end
        println()
        println("Y")
        for i in 1:input_graph.n
            if y_val[i] > 1-eps
                println(i, " ", input_graph.weights[i], " ", input_graph.weights_uncert[i])
            end
        end
        println()
        println("INFLOW")
        for i in 1:input_graph.n
            println(i, " ", out_flow_val[i])
        end
        println()
        println("OUTFLOW")
        for i in 1:input_graph.n
            println(i, " ", out_flow_val[i])
        end

        println()
        vertexes = [(i, input_graph.weights[i], input_graph.weights_uncert[i]) for i in 1:input_graph.n if y_val[i] >= 1-eps]
        sol_sp2, val_sp2 = SP2(vertexes, input_graph)
        println("POIDS ", sum(y_val[i] * input_graph.weights[i] for i in 1:input_graph.n), " ", val_sp2, " ", input_graph.S)
    end


    push!(dict_row, "Nombre de variables" => numvar(model))
    push!(dict_row, "Time (s)" => time() - start)#solve_time(model))
    push!(dict_row, "Time limit (s)" => CPU_time_limit)
    #push!(dict_row, "Nombre de noeuds" => node_count(model))
    push!(dict_row, "termination status" => optim)
    #push!(dict_row, "has_value" => has_values(model))
    #push!(dict_row, "is_feasible" => (primal_status(model) == MOI.FEASIBLE_POINT))
    push!(dict_row, "n_solves" => n_solve)

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
# model = cutting_planes(dataUtils.readData("data/20_USA-road-d.NY.gr"), time_limit)

end