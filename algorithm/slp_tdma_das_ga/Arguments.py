
import os.path

from simulator.ArgumentsCommon import ArgumentsCommon
import simulator.Configuration
import simulator.SourcePeriodModel
import simulator.MobilityModel

algorithm_module = __import__(__package__, globals(), locals(), ['object'])

class Arguments(ArgumentsCommon):
    def __init__(self):
        super(Arguments, self).__init__("SLP TDMA DAS GA", has_safety_period=True)

        self.add_argument("--source-period",
                          type=simulator.SourcePeriodModel.eval_input, required=True)
        self.add_argument("-sp", "--slot-period", type=float, required=True, help="Time of a single slot")
        self.add_argument("-dp", "--dissem-period", type=float, required=True, help="Time of the beacon period")
        # self.add_argument("-ts", "--tdma-num-slots", type=int, required=True, help="Total number of slots available")
        self.add_argument("-gh", "--genetic-header", type=str, required=True, help="The name of the header file generated by the GA")
        self.add_argument("--source-mobility",
                          type=simulator.MobilityModel.eval_input,
                          default=simulator.MobilityModel.StationaryMobilityModel())

    def virtual_arguments(self):
        params = algorithm_module.get_parameters_in_header(self.args.genetic_header)

        # source_period = self.args.dissem_period + self.args.slot_period * params["GA_TOTAL_SLOTS"]
        # source_period = simulator.SourcePeriodModel.eval_input(str(source_period))

        return {
            "tdma_num_slots": params["GA_TOTAL_SLOTS"],
            # "fitness_function": params["GA_FITNESS_FUNCTION"],
            # "source_period": source_period,
        }

    def build_arguments(self):
        result = super(Arguments, self).build_arguments()

        result["TDMA_NUM_SLOTS"] = self.args.tdma_num_slots
        result["SLOT_PERIOD_MS"] = int(self.args.slot_period * 1000)
        result["DISSEM_PERIOD_MS"] = int(self.args.dissem_period * 1000)
        result["GENETIC_HEADER"] = self.args.genetic_header

        return result
