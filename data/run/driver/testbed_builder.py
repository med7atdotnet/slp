from __future__ import print_function, division

import glob
import importlib
import os
import shlex
import shutil
import time

import data.util
from data.progress import Progress

from simulator import Builder
from simulator import Configuration

def choose_platform(provided, available):
    if provided is None:
        if isinstance(available, str):
            return available
        else:
            raise RuntimeError("Unable to choose between the available platforms {}".format(available))
    else:
        if provided in available:
            return provided
        else:
            raise RuntimeError("The provided platform {} is not in the available platforms {}".format(provided, available))


class Runner(object):
    def __init__(self, testbed, platform=None):
        self._progress = Progress("building file")
        self.total_job_size = None
        self._jobs_executed = 0

        self.testbed = testbed
        self.platform = choose_platform(platform, self.testbed.platform())

    def add_job(self, options, name, estimated_time=None):
        print(name)

        if not self._progress.has_started():
            self._progress.start(self.total_job_size)

        # Create the target directory
        target_directory = name[:-len(".txt")]

        data.util.create_dirtree(target_directory)

        # Get the job arguments
        options = shlex.split(options)
        module, argv = options[0], options[1:]
        module_path = module.replace(".", "/")

        a = self.parse_arguments(module, argv)

        # Build the binary

        # These are the arguments that will be passed to the compiler
        build_args = self.build_arguments(a)
        build_args["TESTBED"] = self.testbed.name()
        build_args["TESTBED_" + self.testbed.name().upper()] = 1

        log_mode = self.testbed.log_mode()
        if log_mode == "printf":
            build_args["USE_SERIAL_PRINTF"] = 1
            build_args["SERIAL_PRINTF_BUFFERED"] = 1
        elif log_mode == "unbuffered_printf":
            build_args["USE_SERIAL_PRINTF"] = 1
            build_args["SERIAL_PRINTF_UNBUFFERED"] = 1
        elif log_mode == "serial":
            build_args["USE_SERIAL_MESSAGES"] = 1
        else:
            raise RuntimeError("Unknown testbed log mode {}".format(log_mode))

        print("Building for {}".format(build_args))

        build_result = Builder.build_actual(module_path, self.platform, **build_args)

        print("Build finished with result {}, waiting for a bit...".format(build_result))

        # For some reason, we seemed to be copying files before
        # they had finished being written. So wait a  bit here.
        time.sleep(1)

        print("Copying files to {}...".format(target_directory))

        files_to_copy = (
            "app.c",
            "ident_flags.txt",
            "main.exe",
            "main.ihex",
            "main.srec",
            "tos_image.xml",
            "wiring-check.xml",
        )
        for name in files_to_copy:
            try:
                shutil.copy(os.path.join(module_path, "build", self.platform, name), target_directory)
            except IOError as ex:
                # Ignore expected fails
                if name not in {"main.srec", "wiring-check.xml"}:
                    print("Not copying {} due to {}".format(name, ex))

        # Copy any generated class files
        for file in glob.glob(os.path.join(module_path, "*.class")):
            shutil.copy(file, target_directory)

        print("All Done!")

        self._progress.print_progress(self._jobs_executed + 1)

        self._jobs_executed += 1

        return a, module, module_path, target_directory

    def mode(self):
        return "TESTBED"

    @staticmethod
    def parse_arguments(module, argv):
        arguments_module = importlib.import_module("{}.Arguments".format(module))

        a = arguments_module.Arguments()
        a.parse(argv)

        return a

    @staticmethod
    def build_arguments(a):
        build_args = a.build_arguments()

        configuration = Configuration.create(a.args.configuration, a.args)

        build_args.update(configuration.build_arguments())

        return build_args
