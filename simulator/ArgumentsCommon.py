import multiprocessing

from simulator.Simulation import Simulation
import simulator.Attacker as Attacker
import simulator.Configuration as Configuration
import simulator.SourcePeriodModel as SourcePeriodModel

class ArgumentsCommon(object):
    def __init__(self, parser, has_safety_period=False):
        parser.add_argument("--mode", type=str, choices=["GUI", "SINGLE", "PARALLEL", "CLUSTER", "TESTBED"], required=True)

        parser.add_argument("--seed", type=int)

        parser.add_argument("-cm", "--communication-model", type=str, choices=Simulation.available_communication_models(), required=True)
        parser.add_argument("-nm", "--noise-model", type=str, choices=Simulation.available_noise_models(), required=True)

        parser.add_argument("-ns", "--network-size", type=int, required=True)
        parser.add_argument("-d", "--distance", type=float, default=4.5)
        parser.add_argument("-c", "--configuration", type=str, required=True, choices=Configuration.names())

        parser.add_argument("-am", "--attacker-model", type=Attacker.eval_input, required=True)

        parser.add_argument("-st", "--latest-node-start-time", type=float, required=False, default=1.0, help="Used to specify the latest possible start time. Start times will be chosen in the inclusive random range [0, x] where x is the value specified.")

        if has_safety_period:
            parser.add_argument("-safety", "--safety-period", type=float, required=True)

        parser.add_argument("--job-size", type=int, default=1)
        parser.add_argument("--thread-count", type=int, default=multiprocessing.cpu_count())

        parser.add_argument("--job-id", type=int, default=None, help="Used to pass the array id when this job has been submitted as a job array to the cluster.")

        parser.add_argument("-v", "--verbose", action="store_true")

        parser.add_argument("--gui-node-label", type=str, required=False, default=None)
        parser.add_argument("--gui-scale", type=int, required=False, default=6)

        self.parser = parser

        # Haven't parsed anything yet
        self.args = None

        self.arguments_to_hide = {"job_id", "verbose", "gui_node_label", "gui_scale"}

    def parse(self, argv):
        self.args = self.parser.parse_args(argv)

        if hasattr(self.args, 'source_mobility'):
            configuration = Configuration.create(self.args.configuration, self.args)
            self.args.source_mobility.setup(configuration)
        
        return self.args

    def build_arguments(self):
        result = {}

        if self.args.verbose:
            result["SLP_VERBOSE_DEBUG"] = 1

        # Source period could either be a float or a class derived from PeriodModel
        if hasattr(self.args, 'source_period'):
            if isinstance(self.args.source_period, float):
                if float(self.args.source_period) <= 0:
                    raise RuntimeError("The source_period ({}) needs to be greater than 0".format(self.args.source_period))

                result["SOURCE_PERIOD_MS"] = int(self.args.source_period * 1000)
            elif isinstance(self.args.source_period, SourcePeriodModel.PeriodModel):
                result.update(self.args.source_period.build_arguments())
            else:
                raise RuntimeError("The source_period ({}) either needs to be a float or an instance of SourcePeriodModel.PeriodModel".format(self.args.source_period))

        if hasattr(self.args, 'source_mobility'):
            result.update(self.args.source_mobility.build_arguments())
        else:
            # If there are no mobility models provided, then the only source specified
            # by the configuration can be used instead.
            # This is mainly for legacy algorithm support, StationaryMobilityModels
            # are a better choice for new algorithms.

            configuration = Configuration.create(self.args.configuration, self.args)

            if len(configuration.source_ids) != 1:
                raise RuntimeError("Invalid number of source ids in configuration {}, there must be exactly one.".format(configuration))

            (source_id,) = configuration.source_ids

            result["SOURCE_NODE_ID"] = source_id

        return result