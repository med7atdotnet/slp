#!/usr/bin/env python
from __future__ import print_function, division

import os
import subprocess
import sys

from data import submodule_loader
import data.cycle_accurate

import simulator.VersionDetection as VersionDetection

def main(module, a):
    try:
        avrora_path = os.environ["AVRORA_JAR_PATH"]
    except KeyError:
        raise RuntimeError("Unable to find the environment variable AVRORA_JAR_PATH so cannot run avrora.")

    # Build the binaries
    from data.run.driver.cycle_accurate_builder import Runner as Builder

    from simulator import Configuration

    # Only check dependencies on non-cluster runs
    # Cluster runs will have the dependencies checked in create.py
    from simulator import dependency
    dependency.check_all()

    target = module.replace(".", "/") + ".txt"

    cycle_accurate = submodule_loader.load(data.cycle_accurate, a.args.simulator)

    builder = Builder(cycle_accurate)
    builder.total_job_size = 1
    a, module, module_path, target_directory = builder.add_job((module, a), target)

    configuration = Configuration.create(a.args.configuration, a.args)

    from datetime import datetime

    # Print out the versions of slp-algorithms-tinyos and tinyos being used
    print("@version:java={}".format(VersionDetection.java_version()))
    print("@version:python={}".format(VersionDetection.python_version()))
    print("@version:numpy={}".format(VersionDetection.numpy_version()))

    print("@version:slp-algorithms={}".format(VersionDetection.slp_algorithms_version()))
    print("@version:tinyos={}".format(VersionDetection.tinyos_version()))

    print("@version:avrora={}".format(VersionDetection.avrora_version()))

    # Print other potentially useful meta data
    print("@date:{}".format(str(datetime.now())))
    print("@host:{}".format(os.uname()))

    # Print out the argument settings
    for (k, v) in vars(a.args).items():
        if k not in a.arguments_to_hide:
            print("{}={}".format(k, v))

    # Make sure this header has been written
    sys.stdout.flush()

    # See: http://compilers.cs.ucla.edu/avrora/help/sensor-network.html
    options = {
        "platform": builder.platform,
        "simulation": "sensor-network",
        "seconds": "30",
        "monitors": "energy",
        "radio-range": a.args.distance + 0.25,
        "nodecount": str(configuration.size()),
        "topology": "static",
        "topology-file": os.path.join(target_directory, "topology.txt"),
        "random-seed": a.args.seed,
    }

    target_file = os.path.join(target_directory, "main.elf")

    options_string = " ".join("-{}={}".format(k,v) for (k,v) in options.items())

    # Give a niceness to allow system to continue to respond
    command = "nice -n 15 java -jar {} {} {}".format(avrora_path, options_string, target_file)

    print("@command:{}".format(command))

    subprocess.check_call(command, shell=True)