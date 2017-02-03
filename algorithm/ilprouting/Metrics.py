from __future__ import print_function, division

from simulator.MetricsCommon import MetricsCommon

class Metrics(MetricsCommon):
    def __init__(self, sim, configuration):
        super(Metrics, self).__init__(sim, configuration)

    @staticmethod
    def items():
        d = MetricsCommon.items()

        d["AwaySent"]               = lambda x: x.number_sent("Away")
        d["BeaconSent"]             = lambda x: x.number_sent("Beacon")
        d["PollSent"]               = lambda x: x.number_sent("Poll")

        # 13 is ERROR_RTX_FAILED_TRYING_OTHER
        d["FailedAvoidSink"]        = lambda x: x.errors[13] / x.num_normal_sent_if_finished()

        return d
