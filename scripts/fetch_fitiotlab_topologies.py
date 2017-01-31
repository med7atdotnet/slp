#!/usr/bin/env python
from __future__ import print_function

import json
import os
from pprint import pprint
import subprocess

from data.util import create_dirtree, touch

platform_mapping = {
    "wsn430v13": "wsn430:cc1101",
    "wsn430v14": "wsn430:cc2420",
}

archi_mapping = {
    "wsn430:cc1101": "wsn430v13",
    "wsn430:cc2420": "wsn430v14",
}

supported_platforms = platform_mapping.keys()
supported_hardware = platform_mapping.values()

output_directory = "data/testbed/info/fitiotlab/"

create_dirtree(output_directory)
touch("data/testbed/info/__init__.py")
touch(os.path.join(output_directory, "__init__.py"))

site_names = ["euratech", "grenoble", "rennes", "strasbourg"]

class NodeDetails:


    @staticmethod
    def parse(obj, name, converter=lambda x: x):
        value = obj[name]
        if value == " ":
            return None
        else:
            return converter(value)

    def __init__(self, obj):
        self.archi = NodeDetails.parse(obj, "archi")
        self.uid = NodeDetails.parse(obj, "uid")
        self.mobile = NodeDetails.parse(obj, "mobile", bool)
        self.network_address = NodeDetails.parse(obj, "network_address")
        self.site = NodeDetails.parse(obj, "site")
        self.mobility_type = NodeDetails.parse(obj, "mobility_type")
        self.state = NodeDetails.parse(obj, "state")

        self.nid = int(self.network_address.split(".", 1)[0].split("-", 1)[1])

        try:
            self.coords = (float(obj["x"]), float(obj["y"]), float(obj["z"]))
        except ValueError:
            self.coords = None

    def __repr__(self):
        return "arch: {} | uid: {} | nid: {} | mobile: {} | addr: {} | site: {} | mobility: {} | state: {} | coords: {}".format(
            self.archi, self.uid, self.nid, self.mobile, self.network_address, self.site, self.mobility_type, self.state, self.coords)


def create_node_objects(obj):
    if "archi" in obj:
        return NodeDetails(obj)
    else:
        return obj

for site in site_names:
    print("Fetching topology for {}".format(site))

    path = os.path.join(output_directory, site + ".json")
    pypath = os.path.join(output_directory, site + ".py")

    with open(path, "w") as out_file:
       subprocess.check_call("experiment-cli info --site {} -l".format(site), stdout=out_file, shell=True)

    with open(path, "r") as out_file:
        nodes = json.load(out_file, object_hook=create_node_objects)["items"]

    nodes = [node for node in nodes if node.archi in supported_hardware and node.state == "Alive" and not node.mobile]

    platforms = {archi_mapping[node.archi] for node in nodes}

    if len(platforms) != 1:
        raise RuntimeError("Each testbed topology must consist of only 1 platform")

    pprint(nodes)

    with open(pypath, "w") as out_file:
        print('import numpy as np', file=out_file)
        print('', file=out_file)
        print('from simulator.Topology import Topology', file=out_file)
        print('', file=out_file)
        print('class {}(Topology):'.format(site.title()), file=out_file)
        print('    """The layout of nodes on the Grenbole testbed, see: https://www.iot-lab.info/testbed/maps.php?site={}"""'.format(site), file=out_file)
        print('    def __init__(self):', file=out_file)
        print('        super({}, self).__init__()'.format(site.title()), file=out_file)
        print('        ', file=out_file)
        print('        self.platform = "{}"'.format(next(iter(platforms))), file=out_file)
        print('        ', file=out_file)

        for node in nodes:
            print('        self.nodes[{}] = np.array({}, dtype=np.float64)'.format(node.nid, node.coords), file=out_file)

        print('            ', file=out_file)
        print('        self._process_node_id_order("topology")', file=out_file)
        print('        ', file=out_file)
        print('    def __str__(self):', file=out_file)
        print('        return "{}<>"'.format(site.title()), file=out_file)
