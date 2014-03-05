import networkx, heapq, random, os
from math import log, exp

import CryptsyTrader, CoinsETrader
import CoinsEMarketData, CryptsyMarketData, BterMarketData, PoloniexMarketData

def create_graph(data):
    graph = networkx.DiGraph()
    for key in data:
        for currency in data[key]:
            if '_' in currency:#  not:
                graph.add_edge(key, currency, weight = -log(data[key][currency][0]))
            else:
                graph.add_edge(currency, key, weight = 0.0)#!!!
                graph.add_edge(key, currency, weight = 0.0)#data[key][currency])
    ##graph.remove_node('WDC_coins-e')
    ##graph.remove_node('DEM_coins-e')
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
    print '(.) Scraping Coins-E API.'
    ##coinse_data = CoinsEMarketData.getMarketPrices()
    print '(.) Scraping Cryptsy API.'
    cryptsy_data = CryptsyMarketData.getMarketPrices()
    try:
        print '(.) Scraping Bter API.'
        bter_data = {}
        time.sleep(1.5)
    except:
        print '(!) Bter API scrape failed.'
    try:
        print '(.) Scraping Poloniex API.'
        poloniex_data = PoloniexMarketData.getMarketPrices()
    except:
        print '(!) Poloniex API scrape failed.'
        poloniex_data = {}
##coinse_data.items()
    data = dict(cryptsy_data.items()+bter_data.items()+poloniex_data.items())
    return data

def get_path(data):
    print '(.) Creating graph.'
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
            path.reverse()
            for i in range(len(path)-1):
                if '_' not in path[i+1]:
                    print path[i],path[i+2]
                elif '_' not in path[i]:
                    pass
                else:
                    current_weight /= data[path[i]][path[i+1]][0]
                    print path[i],path[i+1],data[path[i]][path[i+1]]
            if current_weight< 1.0:
                path = None
    else:
        print '(!) No negative edge cycles found on graph.'
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

def executeOnce():
    forbidden_currencies = []
    forbidden_exchanges = ['coins-e','poloniex']
    data = get_data()
    path, return_on_cycle = get_path(data)
    for k in range(50):
        path, return_on_cycle = get_path(data)
        if return_on_cycle > 1.06:
            for item in path:
                if item.split('_')[1] in forbidden_exchanges:
                    print '(!) Forbidden exchange. Finding another path.'
                    continue
                if item.split('_')[0] in forbidden_currencies:
                    print '(!) Forbidden currency. Finding another path.'
                    continue
            for i in range(len(path)-1):
                if path[i].split('_')[1]!=path[i+1].split('_')[1]:
                    print '(!) Currently no support for transferring between those two exchanges.'
                    continue
        else:
            print '(!) Bad return on cycle. Finding another path.'
            continue
    volume = get_volume(path, data, return_on_cycle)
    print '(@) Found cycle worth trading.'
    print path
    print '(@) Max flow of '+str(volume)+'. Return Rate of ' + str(return_on_cycle)
    print '(.) Beginning trade path...'
    exchange = path[0].split('_')[1]
    executor = None
    if exchange == 'coins-e':executor=CoinsETrader.execute
    if exchange == 'cryptsy':executor=CryptsyTrader.execute
    print '(.) Starting with '+str(volume)+' of '+path[0].split('_')[0]+'.'
    for i in range(len(path)-1):
        frm = path[i].split('_')[0]
        to = path[i+1].split('_')[0]
        price = float(data[path[i].split('_')[0]][path[i+1].split('_')[0]][0])
        print '(.) Trading '+str(volume)+' of '+frm+' for '+to+' at '+str(price)+'.'
        executor(frm,to,volume,price)
        volume /= price
        print '(@) Successful trade! Now have '+str(volume)+' of '+to+'.'
    print '(@) Ended with '+str(volume)+' of '+path[0].split('_')[0]+'!!!'


while True:
    try:
        executeOnce()
    except Exception,e:
        print str(e)
