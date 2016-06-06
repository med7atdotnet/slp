import argparse
from simulator.ArgumentsCommon import ArgumentsCommon
import simulator.SourcePeriodModel
import simulator.MobilityModel
import simulator.Configuration as Configuration

class Arguments(ArgumentsCommon):
    def __init__(self):
        parser = argparse.ArgumentParser(description="SLP Phantom", add_help=True)
        super(Arguments, self).__init__(parser, has_safety_period=True)

        parser.add_argument("--source-period",
            type=simulator.SourcePeriodModel.eval_input, required=True)
        parser.add_argument("--source-mobility",
            type=simulator.MobilityModel.eval_input,
            default=simulator.MobilityModel.StationaryMobilityModel())

        parser.add_argument("--walk-length", type=int, required=True)

        parser.add_argument("--landmark-node", default="sink_id")

    def build_arguments(self):
        result = super(Arguments, self).build_arguments()

        result["RANDOM_WALK_HOPS"] = int(self.args.walk_length)

        result["LANDMARK_NODE_ID"] = self._get_landmark_node_id()

        configuration = Configuration.create(self.args.configuration, self.args)

        result["BOTTOM_LEFT_NODE_ID"] = configuration.topology.bottom_left

        result["BOTTOM_RIGHT_NODE_ID"] = configuration.topology.bottom_right

        result["TOP_RIGHT_NODE_ID"] = configuration.topology.top_right

        return result

    def _get_landmark_node_id(self):
        landmark = self.args.landmark_node
        configuration = Configuration.create(self.args.configuration, self.args)

        try:
            landmark = int(landmark)

            max_id = len(configuration.topology.nodes)
            if landmark < 0 or landmark >= max_id:
                raise RuntimeError("The landmark node id is not in the range of [0,{})".format(max_id))

            return landmark

        except ValueError:
            attr_sources = [configuration, configuration.topology]
            for attr_source in attr_sources:
                if hasattr(attr_source, landmark):
                    return int(getattr(attr_source, landmark))
            else:
                raise RuntimeError("No way to work out landmark node from {}.".format(landmark))
