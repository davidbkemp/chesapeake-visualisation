import sys
import math


def ignore_comments(lines):
    return filter(lambda line: not line.startswith("%"), lines)


def trim_lines(lines):
    return [line.strip() for line in lines]


def extract_vertices_section(line_num, lines):
    line_num = line_num + 1
    if not lines[line_num].startswith("*vertices"):
        raise Exception("Vertex section missing vertices")
    num_vertices = int(lines[line_num][len("*vertices"):])
    partitions = lines[line_num + 1: line_num + num_vertices + 1]
    return line_num + num_vertices + 1, partitions


def extract_partitions(line_num, lines):
    new_line_num, vertex_data = extract_vertices_section(line_num, lines)
    return new_line_num, [int(vertex_item) for vertex_item in vertex_data]


def extract_vertex_name(vertex):
    return vertex[vertex.find('"') + 1: -1]


def extract_nodes(line_num, lines):
    new_line_num, vertex_data = extract_vertices_section(line_num, lines)
    return new_line_num, [extract_vertex_name(vertex_item) for vertex_item in vertex_data]


def extract_bio_masses(line_num, lines):
    new_line_num, vertex_data = extract_vertices_section(line_num, lines)
    return new_line_num, [float(vertex_item) for vertex_item in vertex_data]


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
    bio_masses = []
    line_num = 0
    while line_num < len(lines):
        if lines[line_num].startswith("*partition"):
            (line_num, partitions) = extract_partitions(line_num, lines)
        if lines[line_num].startswith("*network"):
            (line_num, nodes) = extract_nodes(line_num, lines)
        if lines[line_num].startswith("*arcs"):
            (line_num, arcs) = extract_arcs(line_num, lines)
        if lines[line_num].startswith("*vector bio-masses"):
            (line_num, bio_masses) = extract_bio_masses(line_num, lines)
        line_num = line_num + 1
    return partitions, nodes, arcs, bio_masses


def generate_dotty(partitions, nodes, arcs, bio_masses):
    print('digraph chesapeake {')
    print_nodes(nodes, partitions, bio_masses)
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


def node_colour(bio_mass, max_bio_mass):
    hue = 0.482
    saturation = 0.714
    density = colour_density(bio_mass, max_bio_mass)
    return f'{hue}, {saturation}, {density}'


def colour_density(bio_mass, max_bio_mass):
    return 1 - (math.log(1 + bio_mass) / (3 * math.log(1 + max_bio_mass)))


def print_nodes(nodes, partitions, bio_masses):
    max_bio_mass = max(bio_masses)
    for node_num in range(len(nodes)):
        bio_mass = bio_masses[node_num]
        shape = partition_shape(partitions[node_num])
        colour = node_colour(bio_mass, max_bio_mass)
        label = f'{nodes[node_num]}\\n({bio_mass}'
        print(
            f'{node_num + 1} [label="{label})" shape="{shape}" style=filled, fillcolor="{colour}"]'
        )


generate_dotty(*process_lines(trim_lines(ignore_comments(sys.stdin.readlines()))))
