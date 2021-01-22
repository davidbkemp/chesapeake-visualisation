import sys


def ignore_comments(lines):
    return filter(lambda line: not line.startswith("%"), lines)


def trim_lines(lines):
    return [line.strip() for line in lines]


def extract_partitions(line_num, lines):
    line_num = line_num + 1
    if not lines[line_num].startswith("*vertices"):
        raise Exception("Partition missing vertices")
    num_vertices = int(lines[line_num][len("*vertices"):])
    partitions = [int(line) for line in lines[line_num + 1: line_num + num_vertices + 1]]
    return line_num + num_vertices, partitions


def extract_vertex_name(vertex):
    return vertex[vertex.find('"') + 1: -1]


def extract_vertex_names(vertices):
    return [extract_vertex_name(vertex) for vertex in vertices]


def extract_nodes(line_num, lines):
    line_num = line_num + 1
    if not lines[line_num].startswith("*vertices"):
        raise Exception("Partition missing vertices")
    num_vertices = int(lines[line_num][len("*vertices"):])
    vertices = extract_vertex_names(lines[line_num + 1: line_num + num_vertices + 1])
    return line_num + num_vertices + 1, vertices


def extract_arcs(line_num, lines):
    line_num = line_num + 1
    arcs = []
    while line_num < len(lines):
        arc_components = lines[line_num].split()
        if len(arc_components) != 3:
            break
        weight = float(arc_components[2])
        arcs.append({"src": arc_components[0], "dest": arc_components[1], "weight": weight})
        line_num = line_num + 1
    return line_num, arcs


def process_lines(lines):
    partitions = []
    nodes = []
    arcs = []
    line_num = 0
    while line_num < len(lines):
        if lines[line_num].startswith("*partition"):
            (line_num, partitions) = extract_partitions(line_num, lines)
        if lines[line_num].startswith("*network"):
            (line_num, nodes) = extract_nodes(line_num, lines)
        if lines[line_num].startswith("*arcs"):
            (line_num, arcs) = extract_arcs(line_num, lines)
        line_num = line_num + 1
    return partitions, nodes, arcs


def generate_dotty(partitions, nodes, arcs):
    print('digraph chesapeake {')
    print_nodes(nodes, partitions)
    print_arcs(arcs)
    print('}')


def print_arcs(arcs):
    for arc in arcs:
        print(f'{arc["src"]} -> {arc["dest"]}')


def partition_shape(partition):
    if partition == 1:
        return 'ellipse'
    elif partition == 2:
        return 'box'
    elif partition == 3:
        return 'pentagon'
    elif partition == 4:
        return 'Mdiamond'
    elif partition == 5:
        return 'doubleoctagon'
    else:
        raise Exception("unexpected partition")

def print_nodes(nodes, partitions):
    for node_num in range(len(nodes)):
        shape = partition_shape(partitions[node_num])
        print(f'{node_num + 1} [label="{nodes[node_num]}" shape="{shape}"]')


generate_dotty(*process_lines(trim_lines(ignore_comments(sys.stdin.readlines()))))
