include("data.jl")

ENV["CPLEX_STUDIO_BINARIES"] = "/opt/ibm/ILOG/CPLEX_Studio201/cplex/bin/x86-64_linux/"
import .dataUtils
using JuMP, CPLEX



function SP1()

end


function SP2()

end

function init_master_Problem(input_graph, U1, U2)
    """
    input_graph : instance of the class InputGraph of data.jl
    U1 : lists of matrixes of size n x n. Each elements of U1 is a admissible realisation of (delta_ij^1)_ij
    U2 : lists of lists of size n. Each elements of U1 is a admissible realisation of p_i^2
    """

    model = Model(CPLEX.Optimizer)
    MOI.set(model, MOI.NumberOfThreads(), 1)

    @variable(model, x[a=[(arc[1], arc[2]) for arc in input_graph.arcs]], binary=true)
    @variable(model, y[1:input_graph.n], binary=true)
    @variable(model, z, lower_bound=0)

    #OBJECTIVE
    @objective(model, Min, z)

    #SETTING Z
    @constraint(model, set_z[s=1:length(U1)], z >= sum(U1[s][a[1], a[2]] * x[(a[1], a[2])] for a in input_graph.arcs))

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
    @constraint(model, set_capas=1:length(U2), sum(U2[s][i] * y[i] for i in 1:input_graph.n) <= input_graph.S)

    return model
end

function callback_add_constraints(cb_data::CPLEX.CallbackContext, context_id::Clong)
    """
    cb_data : 
    context_id :
    """
    if isIntegerPoint(cb_data, context_id)

        CPLEX.load_callback_variable_primal(cb_data, context_id)

        x_val = callback_value(cb_data, x)


        # SP1
        

        # SP2



        MOI.submit(m, MOI.LazyConstraint(cb_data), cstr)
        println("Add constraint x <= 1")
    end
end





function cutting_planes(input_graph)
    U1 = []
    U2 = []

    model = init_master_Problem(input_graph, U1, U2)


    

end