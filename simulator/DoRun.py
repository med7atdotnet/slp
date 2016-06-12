#!/usr/bin/env python
from __future__ import print_function

import copy
import importlib
import sys

import simulator.Configuration as Configuration

module = sys.argv[1]

Arguments = importlib.import_module("{}.Arguments".format(module))

a = Arguments.Arguments()
a.parse(sys.argv[2:])

configuration = Configuration.create(a.args.configuration, a.args)

if a.args.mode == "GUI":
    from simulator.TosVis import GuiSimulation as Simulation
else:
    from simulator.Simulation import Simulation

with Simulation(module, configuration, a.args) as sim:

    # Create a copy of the provided attacker model
    attacker = copy.deepcopy(a.args.attacker_model)

    # Setup each attacker model
    attacker.setup(sim, configuration.sink_id, 0)

    sim.add_attacker(attacker)

    try:
        sim.run()
    except (KeyboardInterrupt, SystemExit, RuntimeError) as ex:
        import traceback
        print("Killing run due to {}".format(ex), file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        sys.exit(3)
    else:
        sim.metrics.print_results()

sys.exit(0)
