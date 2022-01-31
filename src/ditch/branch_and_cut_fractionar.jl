include("data.jl")

ENV["CPLEX_STUDIO_BINARIES"] = "/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/"
import .dataUtils
using JuMP, CPLEX



function SP1(arcs, input_graph)
    """
    modelizes the problem as a fractionnary-backpack problem
    arcs : list of tuples representing arcs ij with x_ij=1 in the current solution
    input_graph : instance of InputGraph
    """
    sort!(arcs, by= a-> a[3]* a[5], rev=true)

    i=1
    quantity=0
    contin=true
    sol_sp1 = []
    val_sp1 = 0
    while i <= length(arcs) && contin
        if quantity + arcs[i][4] <= input_graph.d1
            quantity += arcs[i][4]
            val_sp1 += arcs[i][3] * arcs[i][5] * arcs[i][4]
            push!(sol_sp1, (arcs[i][1], arcs[i][2], arcs[i][3], arcs[i][4]))
        else
            push!(sol_sp1, (arcs[i][1], arcs[i][2], arcs[i][3], input_graph.d1 - quantity))
            val_sp1 += arcs[i][3] * arcs[i][5] * (input_graph.d1 - quantity)
            contin= false
        end
        i += 1
    end

    return sol_sp1, sum(a[3] * a[5] for a in arcs) + val_sp1
end

function SP2(vertexes, input_graph)
    """
    modelizes the problem as a fractionnary-backpack problem
    x : list representing vetexes et i with x_i=1 in the current solution
    input_graph : instance of InputGraph
    """
    sort!(vertexes, by= x -> x[3] * x[4], rev=true)

    i = 1
    quantity = 0
    contin = true
    sol_sp2 = []
    val_sp2 = 0
    while i <= length(vertexes) && contin
        if quantity + 2 <= input_graph.d2
            quantity += 2
            val_sp2 +=  2 * vertexes[i][3] * vertexes[i][4]
            push!(sol_sp2, (vertexes[i][1], vertexes[i][2], vertexes[i][3], 2))
        else
            push!(sol_sp2, (vertexes[i][1], vertexes[i][2], vertexes[i][3], input_graph.d2 - quantity))
            val_sp2 += (input_graph.d2 - quantity) * vertexes[i][3] * vertexes[i][4]
            contin= false
        end
        i += 1
    end

    return sol_sp2, sum(v[2] * v[4] for v in vertexes) + val_sp2
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

function branch_and_cut_fractionnar(input_graph, CPU_time_limit)
    U1 = []
    U2 = []

    function isIntegerPoint(cb_data::CPLEX.CallbackContext, context_id::Clong)

        if context_id != CPX_CALLBACKCONTEXT_CANDIDATE
            return false
        end
        ispoint_p = Ref{Cint}()
        ret = CPXcallbackcandidateispoint(cb_data, ispoint_p)

        if ret != 0 || ispoint_p[] == 0
            return false
        else
            return true
        end
    end


    function callback_add_constraints(cb_data)#::CPLEX.CallbackContext, context_id::Clong)
        """
        cb_data : 
        context_id :
        """
        #println("A ")#, context_id, " ", CPX_CALLBACKCONTEXT_RELAXATION)

        status = callback_node_status(cb_data, model)
        println("A", status, MOI.CALLBACK_NODE_STATUS_FRACTIONAL, MOI.CALLBACK_NODE_STATUS_INTEGER)
        if status !=  MOI.CALLBACK_NODE_STATUS_FRACTIONAL && status !=  MOI.CALLBACK_NODE_STATUS_INTEGER#CPX_CALLBACKCONTEXT_RELAXATION && !(isIntegerPoint(cb_data, context_id))
            return
        else
            #println("B")
            #CPLEX.load_callback_variable_primal(cb_data, context_id)
            #x_val = callback_value(cb_data, x)
            #println("C")
            x_val = callback_value.(Ref(cb_data), x)
            y_val = callback_value.(Ref(cb_data), y)
            z_val = callback_value.(Ref(cb_data), z)

            # SP1
            eps = 10 ^ (-5)
            arcs = [(a[1], a[2], input_graph.traveltime_matrix[a[1], a[2]], input_graph.ceil_uncert_traveltime[a[1], a[2]], x_val[(a[1], a[2])]) for a in input_graph.arcs if x_val[(a[1], a[2])] >= eps]
            sol_sp1, val_sp1 = SP1(arcs, input_graph)


            # SP2
            vertexes = [(i, input_graph.weights[i], input_graph.weights_uncert[i], y_val[i]) for i in 1:input_graph.n if y_val[i] >= eps]
            sol_sp2, val_sp2 = SP2(vertexes, input_graph)
            println("D")
            if !(abs(z_val - val_sp1) < eps && input_graph.S >= val_sp2) #solution non optimale
                cstr1 = @build_constraint(z >= sum(a[3] * (1 + a[4]) * x[(a[1], a[2])] for a in sol_sp1))
                println("A1")
                MOI.submit(model, MOI.LazyConstraint(cb_data), cstr1)
                println("A2")
                cstr2 = @build_constraint(sum(y[v[1]] * (v[2] + v[3] * v[4]) for v in sol_sp2) <= input_graph.S)
                MOI.submit(model, MOI.LazyConstraint(cb_data), cstr2)
            end
        end
    end
    
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
    set_time_limit_sec(model, CPU_time_limit)
    #MOI.set(model, CPLEX.CallbackFunction(), callback_add_constraints)
    MOI.set(model, MOI.LazyConstraintCallback(), callback_add_constraints)
    
    optimize!(model)
    
    println("----- SOLUTION ----")
    println()
    println("VALUE ", objective_value(model))
    x_val = value.(x)
    y_val = value.(y)
    eps = 10^(-5)
    for a in input_graph.arcs
        if x_val[a] > 1-eps
            println("PATH ", a[1], "->", a[2], " ", input_graph.traveltime_matrix[a[1], a[2]], " ", input_graph.ceil_uncert_traveltime[a[1], a[2]])
        end
    end
    println()
    for i in 1:input_graph.n
        if y_val[i] > 1-eps
            println("NODE ", i, " ", input_graph.weights[i], " ", input_graph.weights_uncert[i])
        end
    end
end

time_limit = 60
model = branch_and_cut_fractionnar(dataUtils.readData("data/20_USA-road-d.NY.gr"), time_limit)
