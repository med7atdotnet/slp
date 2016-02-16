from __future__ import division

from simulator.Simulator import OutputCatcher
from simulator.MetricsCommon import MetricsCommon

class Metrics(MetricsCommon):
    def __init__(self, sim, configuration):
        super(Metrics, self).__init__(sim, configuration)

        self.register('Metric-PATH-END', self.process_PATH_END)

        self._paths_reached_end = []

    def process_PATH_END(self, line):
        (time, node_id, proximate_source_id, ultimate_source_id, sequence_number, hop_count) = line.split(',')

        self._paths_reached_end.append((ultimate_source_id, sequence_number))

    def paths_reached_end(self):
        return len(self._paths_reached_end) / len(self.normal_sent_time)

    @staticmethod
    def items():
        d = MetricsCommon.items()
        d["AwaySent"]               = lambda x: x.number_sent("Away")
        d["BeaconSent"]             = lambda x: x.number_sent("Beacon")
        d["PathsReachedEnd"]        = lambda x: x.paths_reached_end()

        return d
