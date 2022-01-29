import Unicode


mutable struct Vertex
    id_vertex::Int
    pos_x::Float64
    pos_y::Float64
    demand::Float64
 end
 
 mutable struct InputGraph
    n::Int64
    s::Int64
    t::Int64
    S::Int64
    weights::Array{Float64}
    weights_incert::Array{Float64}
    edges::Array{Float64}
    traveltime_matrix::Array{Float64,2}
    ceil_incert_traveltime::Array{Float64,2}
 end

function readData(data_path)
    """
    charge les donees
    """
    str = Unicode.normalize(read(data_path, String); stripcc=true)
    breaks_in = [' '; '='; ';'; '\n', '[', ']']
    aux = split(str, breaks_in; limit=0, keepempty=false)
 
    println(aux)
    #G = InputGraph([],[],Dict())
    weights = []
    weights_incert = []

    #data = DataCVRP(G′, 0, 0, false, !app["noround"])
     
    dim = 0
    for i in 1:length(aux)
        if contains(aux[i], "n")
            n = parse(Int, aux[i+1])
        elseif contains(aux[i], "s")
            s = parse(Float64, aux[i+1])  # the method parse() convert the string to Int64
        elseif contains(aux[i], "t")
            t = parse(Float64, aux[i+1])
        elseif contains(aux[i], "S")
            S = parse(Float64, aux[i+1])
        elseif contains(aux[i], "d1")
            d1 = parse(Float64, aux[i+1])
        elseif contains(aux[i], "d2")
            d2 = parse(Float64, aux[i2])
        elseif contains(aux[i], "p")
            weights = []
            for j in 1:n
                push!(weights, parse(Float64, aux[i+j]))
            end
        elseif contains(aux[i], "ph")
            weights_incert = []
            for j in 1:n
                push!(weights_incert, parse(Float64, aux[i+j]))
            end
        elseif contains(aux[i], "Mat")
            traveltime_matrix = zeros(Float64, n, n)
            ceil_incert_traveltime = zeros(Float64, n, n)
            for j in 0:(n-1)
                traveltime_matrix[i + 4j]
                

                
            end
        
        
        
        
        
        
        
        
        
        
        
        data.coord = true
          j = i+1
          while aux[j] != "DEMAND_SECTION" 
             v = Vertex(0, 0, 0, 0)
             v.id_vertex = parse(Int, aux[j])-1 # depot is forced to be 0, fisrt customer to be 1, and so on
             v.pos_x = parse(Float64, aux[j+1])
             v.pos_y = parse(Float64, aux[j+2])
             push!(G′.V′, v) # add v in the vertex array
             j+=3
          end
       elseif contains(aux[i], "DEMAND_SECTION")
          j = i+1
          while aux[j] != "DEPOT_SECTION"
             pos = parse(Int, aux[j])
             G′.V′[pos].demand = parse(Float64, aux[j+1])
             j += 2
          end
          data.depot_id = 0
          break
        end
    end
end
readData("data/20_USA-road-d.NY.gr")