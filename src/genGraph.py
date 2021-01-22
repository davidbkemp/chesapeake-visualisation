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
    partition = lines[line_num + 1: line_num + num_vertices + 1]
    return line_num + num_vertices, partition


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


def extract_arcs(line_num, lines, nodes):
    line_num = line_num + 1
    arcs = []
    while line_num < len(lines):
        arc_components = lines[line_num].split()
        if len(arc_components) != 3:
            break
        src = nodes[int(arc_components[0]) - 1]
        dest = nodes[int(arc_components[1]) - 1]
        weight = float(arc_components[2])
        arcs.append({"src": src, "dest": dest, "weight": weight})
        line_num = line_num + 1
    return line_num, arcs


def process_lines(lines):
    partition = []
    nodes = []
    arcs = []
    line_num = 0
    while line_num < len(lines):
        if lines[line_num].startswith("*partition"):
            (line_num, partition) = extract_partitions(line_num, lines)
        if lines[line_num].startswith("*network"):
            (line_num, nodes) = extract_nodes(line_num, lines)
        if lines[line_num].startswith("*arcs"):
            (line_num, arcs) = extract_arcs(line_num, lines, nodes)
        line_num = line_num + 1
    return partition, nodes, arcs


def generate_dotty(partition, nodes, arcs):
    print('digraph chesapeake {')
    for arc in arcs:
        print(f'"{arc["src"]}" -> "{arc["dest"]}"')
    print('}')


generate_dotty(*process_lines(trim_lines(ignore_comments(sys.stdin.readlines()))))
