module dataUtils

import Unicode

export IntputGraph, readData
 
mutable struct InputGraph
    n::Int64
    s::Int64
    t::Int64
    S::Float64
    d1::Float64
    d2::Float64
    weights::Array{Float64}
    weights_uncert::Array{Float64}
    arcs
    traveltime_matrix::Array{Float64,2}
    ceil_uncert_traveltime::Array{Float64,2}
 end


 
function readData(data_path)
    """
    charge les donees
    """
    str = Unicode.normalize(read(data_path, String); stripcc=true)
    breaks_in = [' '; '='; ';'; ','; '\n'; '['; ']']
    aux = split(str, breaks_in; limit=0, keepempty=false)
     
    n = 0
    s = 0
    t = 0
    S = 0
    d1 = 0
    d2 = 0
    weights = []
    weights_uncert = []
    traveltime_matrix = nothing #zeros(Float64, n, n)
    ceil_uncert_traveltime = nothing
    arcs = []

    for i in 1:length(aux)
        if contains(aux[i], "n")
            n = parse(Int64, aux[i+1])
            traveltime_matrix = zeros(Float64, n, n)
            ceil_uncert_traveltime = zeros(Float64, n, n)
        elseif aux[i] == "ph"
            weights_uncert = []
            for j in 1:n
                push!(weights_uncert, parse(Float64, aux[i+j]))
            end
        elseif isequal(aux[i], "Mat")
            j=0
            while i + 4 * j + 4 <= length(aux)
                x = parse(Int64, aux[i + 4*j + 1])
                y = parse(Int64, aux[i + 4*j + 2])
                traveltime_matrix[x, y] = parse(Float64, aux[i + 4 * j + 3])
                ceil_uncert_traveltime[x, y] = parse(Float64, aux[i + 4 * j + 4])  
                push!(arcs, (x, y))
                j += 1
            end
        elseif contains(aux[i], "s")
            s = parse(Int64, aux[i+1])  # the method parse() convert the string to Int64
        elseif contains(aux[i], "t")
            t = parse(Int64, aux[i+1])
        elseif contains(aux[i], "S")
            S = parse(Float64, aux[i+1])
        elseif contains(aux[i], "d1")
            d1 = parse(Float64, aux[i+1])
        elseif contains(aux[i], "d2")
            d2 = parse(Float64, aux[i+1])
        elseif contains(aux[i], "p")
            for j in 1:n
                push!(weights, parse(Float64, aux[i+j]))
            end
        end
    end
    #println(n, s, t, S, d1, d2, weights, weights_uncert, edges, traveltime_matrix, ceil_uncert_traveltime)
    return InputGraph(n, s, t, S, d1, d2, weights, weights_uncert, arcs, traveltime_matrix, ceil_uncert_traveltime)

end

end

