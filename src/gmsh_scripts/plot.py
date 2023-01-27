import argparse
from pathlib import Path

from pyvis.network import Network

from gmsh_scripts.factory import FACTORY as FACTORY
from gmsh_scripts.run import init_walk
from gmsh_scripts.load import load


def plot_action(a, output=None, height='600px', width='600px', title="",
                options=False, no_hierarchy=False,
                background='white', font='black'):
    output = 'output.html' if output is None else output
    n = Network(height=height, width=width, heading=title,
                directed=True, bgcolor=background, font_color=font)

    def get_class(action):
        cls = action.__class__
        return cls.__module__ + '.' + cls.__qualname__

    def make_title(action):
        title = f"""
        class: {get_class(action)}<br>
        zone: {action.volume_zone}<br>"""
        return title

    graph = a.make_tree()
    nodes, edges, groups = set(), set(), {}
    node2index = {}
    for p, cs in graph.items():
        if p not in nodes:
            n.add_node(node2index.setdefault(p, len(nodes)),
                       label=p.volume_zone,
                       group=groups.setdefault(p.volume_zone, len(groups)),
                       title=make_title(p)
                       )
            nodes.add(p)
        for c in cs:
            if c not in nodes:
                n.add_node(node2index.setdefault(c, len(nodes)),
                           label=c.volume_zone,
                           group=groups.setdefault(c.volume_zone, len(groups)),
                           title=make_title(c)
                           )
                nodes.add(c)
            if (p, c) not in edges:
                n.add_edge(node2index[p], node2index[c])
                edges.add((p, c))
    if options:
        n.show_buttons()
    else:
        if not no_hierarchy:
            n.set_options("""
            var options = {
              "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "LR"
                    }
                }
            }
            """)
    n.write_html(str(Path(output)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='input')
    parser.add_argument('-o', '--output', help='output', default=None)
    parser.add_argument('--height', help='height', default='100%')
    parser.add_argument('--width', help='width', default='100%')
    parser.add_argument('--title', help='title', default='')
    parser.add_argument('--background', help='background color', default='white')
    parser.add_argument('--font', help='font color', default='black')
    parser.add_argument('--options', help='show options', action='store_true')
    parser.add_argument('--no_hierarchy', help='non hierarchical layout', action='store_true')
    args = vars(parser.parse_known_args()[0])  # arguments dictionary
    p = Path(args['input'])
    d = load(p)
    d.setdefault('metadata', {})
    d.setdefault('data', {})
    top_kwargs = d['data']
    init_walk(top_kwargs)
    top_block = FACTORY(top_kwargs)
    args['output'] = p.with_suffix('.html') if args['output'] is None else args['output']
    args.pop('input')
    plot_action(top_block, **args)


if __name__ == '__main__':
    main()
