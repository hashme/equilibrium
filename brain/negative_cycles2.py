import networkx, heapq, random, os
from math import log, exp

import CoinsEMarketData, CryptsyMarketData, BterMarketData

def create_graph(data):
    graph = networkx.DiGraph()
    for key in data:
        for currency in data[key]:
            if '_' in currency:# and 'WDC' not in currency and 'DEM' not in currency:
                graph.add_edge(key, currency, weight = -log(data[key][currency][0]))
            else:
                graph.add_edge(currency, key, weight = 0.0)#!!!
                graph.add_edge(key, currency, weight = 0.0)#data[key][currency])
    graph.remove_node('WDC_coins-e')
    graph.remove_node('DEM_coins-e')
    return graph

def find_negative_cycle(graph):
    fake_node = "???"
    distance_matrix = {}
    parents = {}
    for node in graph.nodes():
        graph.add_edge(fake_node, node, weight = 0)
    for node in graph.nodes():
        distance_matrix[node] = 999999e10
    distance_matrix[fake_node] = 0
    parents[fake_node] = None
    edges = graph.edges(data = True)
    random.shuffle(edges)
    for i in xrange(len(graph) - 1):
        for node_from,node_to,weight in edges:
            weight = weight['weight']
            if (weight + distance_matrix[node_from]) < distance_matrix[node_to]:
                distance_matrix[node_to] = weight + distance_matrix[node_from]
                parents[node_to] = node_from
    for node_from,node_to,weight in edges:
        weight = weight['weight']
        if (weight + distance_matrix[node_from]) < distance_matrix[node_to]:
            distance_matrix[node_to] = weight + distance_matrix[node_from]
            parents[node_to] = node_from
            graph.remove_node(fake_node)
            path = []
            current_node = node_to
            while current_node not in path:
                path.append(current_node)
                if current_node in parents.keys():
                    current_node = parents[current_node]
                else:
                    break
            path.append(current_node)
            return path[path.index(path[-1]):]
    graph.remove_node(fake_node)
    return None

def get_data():
    coinse_data = CoinsEMarketData.getMarketPrices()
    cryptsy_data = CryptsyMarketData.getMarketPrices()
    bter_data = {}#BterMarketData.getMarketPrices()
    data = dict(coinse_data.items()+cryptsy_data.items()+bter_data.items())
    return data

def get_path(data):
    graph = create_graph(data)
    exchange_nodes = []
    wallet_nodes = []
    for node in graph.nodes():
        if '_' in node:
            exchange_nodes.append(node)
        else:
            wallet_nodes.append(node)
    for node in exchange_nodes:
        graph.add_edge(node, node.split('_')[0], weight = 0.0)
        graph.add_edge(node.split('_')[0], node, weight = 0.0)
    path = find_negative_cycle(graph)
    if path:
        print path
        print 'Found negative edge cycle!'
        current_weight = 1.0
        for i in range(len(path)-1):
            if '_' not in path[i+1]:
                print path[i],path[i+2]
            elif '_' not in path[i]:
                pass
            else:
                current_weight /= data[path[i]][path[i+1]][0]
                print path[i],path[i+1],data[path[i]][path[i+1]]
        if current_weight < 1.0:
            current_weight = 1.0
            print 'Cycle seemed reversed; trying other way round.'
            path.reverse()
            for i in range(len(path)-1):
                if '_' not in path[i+1]:
                    print path[i],path[i+2]
                elif '_' not in path[i]:
                    pass
                else:
                    current_weight /= data[path[i]][path[i+1]][0]
                    print path[i],path[i+1],data[path[i]][path[i+1]]
        print 'Return on cycle:',current_weight
    else:
        print 'No negative edge cycle found on this run'
    return filter(lambda x:'_' in x, path), current_weight

def get_volume(path, data, return_on_cycle):
    max_flow = 99999999e100
    for i in range(len(path)-1):
        if path[i].split('_')[1]!=path[i+1].split('_')[1]:
            continue
        if max_flow > data[path[i]][path[i+1]][1]:
            max_flow = data[path[i]][path[i+1]][1]
        max_flow /= data[path[i]][path[i+1]][0]
    return max_flow/return_on_cycle

while True:
    data = get_data()
    ##print data['BTC_poloniex']['LTC_poloniex'][0]
    ##print 1.0/data['LTC_poloniex']['BTC_poloniex'][0]
    
    path, return_on_cycle = get_path(data)
    volume = get_volume(path, data, return_on_cycle)
    print '-::EXECUTE TRADE::-'
    print path
    print ' using '+str(volume)+' of '+path[0]
    print '\n\n\n\n'
