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


def arc_pen_width(weight, max_weight):
    return 0.5 + 3 * (math.log(1 + weight) / math.log(1 + max_weight))


def print_arcs(arcs):
    max_weight = max([arc["weight"] for arc in arcs])
    for arc in arcs:
        pen_width = arc_pen_width(arc["weight"], max_weight)
        print(f'{arc["src"]} -> {arc["dest"]} [penwidth={pen_width}]')


def is_boundary_node(partition):
    return partition in [3, 4, 5]


def partition_shape(partition):
    if partition == 1:
        return 'ellipse'
    elif partition == 2:
        return 'box'
    elif is_boundary_node(partition):
        return 'hexagon'
    else:
        raise Exception("unexpected partition")


def node_label(name, bio_mass, partition):
    if is_boundary_node(partition):
        return name
    else:
        return f'{name}\\n({bio_mass:.2f} gC.m²)'


def node_font_size(bio_mass, max_bio_mass, partition):
    if is_boundary_node(partition):
        return 21
    else:
        return 14 * (1 + (math.log(1 + bio_mass) / math.log(1 + max_bio_mass)))


def node_colour(partition):
    if is_boundary_node(partition):
        return "white"
    else:
        return "0.482, 0.3, 0.9"


def node_width(bio_mass, max_bio_mass, partition):
    if is_boundary_node(partition):
        return 3
    else:
        return 3 * (1 + (math.log(1 + bio_mass) / math.log(1 + max_bio_mass)))


def node_height(bio_mass, max_bio_mass, partition):
    if is_boundary_node(partition):
        return 0.5
    else:
        return 0.6 * (1 + (math.log(1 + bio_mass) / math.log(1 + max_bio_mass)))


def print_nodes(nodes, partitions, bio_masses):
    max_bio_mass = max(bio_masses)
    for node_num in range(len(nodes)):
        bio_mass = bio_masses[node_num]
        partition = partitions[node_num]
        shape = partition_shape(partition)
        colour = node_colour(partition)
        font_size = node_font_size(bio_mass, max_bio_mass, partition)
        width = node_width(bio_mass, max_bio_mass, partition)
        height = node_height(bio_mass, max_bio_mass, partition)
        label = node_label(nodes[node_num], bio_mass, partition)
        if is_boundary_node(partition):
            print(
                f'{node_num + 1} [label="{label}" shape="{shape}" style=filled fillcolor="{colour}" fontsize={font_size} ]'
            )
        else:
            print(
                f'{node_num + 1} [label="{label}" shape="{shape}" style=filled fillcolor="{colour}" fontsize={font_size} '
                f'fixedsize=true height={height} width={width}]'
            )


generate_dotty(*process_lines(trim_lines(ignore_comments(sys.stdin.readlines()))))
