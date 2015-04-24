import os, itertools

from collections import OrderedDict

from data.run.common import RunSimulationsCommon

class RunSimulations(RunSimulationsCommon):
    def __init__(self, driver, results_directory, skip_completed_simulations=True):
        super(RunSimulations, self).__init__(driver, results_directory, skip_completed_simulations)

    def run(self, exe_path, distance, sizes, source_periods, configurations, attacker_models, repeats):
        if self.skip_completed_simulations:
            self._check_existing_results(['network_size', 'source_period', 'configuration', 'attacker_model'])
        
        if not os.path.exists(exe_path):
            raise RuntimeError("The file {} doesn't exist".format(exe_path))

        for (size, source_period, configuration, attacker_model) in itertools.product(sizes, source_periods, configurations, attacker_models):
            if not self._already_processed(repeats, size, source_period, configuration):

                executable = 'python {} {}'.format(
                    self.optimisations,
                    exe_path)

                opts = OrderedDict()
                opts["--mode"] = self.driver.mode()
                opts["--network-size"] = size
                opts["--configuration"] = configuration
                opts["--source-period"] = source_period
                opts["--distance"] = distance
                opts["--job-size"] = repeats
                opts["--attacker-model"] = attacker_model

                optItems = ["{} {}".format(k, v) for (k,v) in opts.items()]

                options = 'algorithm.protectionless ' + " ".join(optItems)

                filenameItems = (
                    size,
                    source_period,
                    configuration,
                    attacker_model,
                    distance
                )

                filename = os.path.join(
                    self.results_directory,
                    '-'.join(map(str, filenameItems)).replace(".", "_") + ".txt"
                )

                self.driver.add_job(executable, options, filename)
