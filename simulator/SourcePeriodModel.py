from collections import OrderedDict

import math, numbers

from data.restricted_eval import restricted_eval

class PeriodModel(object):
    def __init__(self, times):
        self.period_times = times

        self._validate_times()

    def _validate_times(self):
        pass

    def fastest(self):
        """Returns the smallest period possible with this model"""
        raise NotImplemented()

    def build_arguments(self):
        build_arguments = {}

        def to_tinyos_format(time):
            return int(time * 1000)

        periods = [
            "{{{}U, {}U}}".format(to_tinyos_format(end), to_tinyos_format(period))
            for ((start, end), period)
            in self.period_times.items()
            if not math.isinf(end)
        ]

        end_period = [
            to_tinyos_format(period)
            for ((start, end), period)
            in self.period_times.items()
            if math.isinf(end)
        ][0]

        build_arguments["PERIOD_TIMES_MS"] = "{ " + ", ".join(periods) + " }"
        build_arguments["PERIOD_ELSE_TIME_MS"] = "{}U".format(end_period)

        return build_arguments

class FixedPeriodModel(PeriodModel):
    def __init__(self, period):

        self.period = float(period)

        times = OrderedDict()
        times[(0, float('inf'))] = self.period

        super(FixedPeriodModel, self).__init__(times)

    def fastest(self):
        return self.period

    def __repr__(self):
        return "FixedPeriodModel(period={})".format(self.period)

class FactoringPeriodModel(PeriodModel):
    def __init__(self, starting_period, max_period, duration, factor):

        self.starting_period = float(starting_period)
        self.max_period = float(max_period)
        self.duration = float(duration)
        self.factor = float(factor)

        if self.factor <= 1:
            raise RuntimeError("The factor ({}) must be greater than 1".format(self.factor))

        times = OrderedDict()

        period = float(starting_period)
        current_time = 0.0

        while period <= max_period:

            end_time = current_time + duration if period * factor <= max_period else float('inf')

            times[(current_time, end_time)] = period

            current_time = end_time
            period *= factor

        super(FactoringPeriodModel, self).__init__(times)

    def fastest(self):
        return self.starting_period

    def __repr__(self):
        return "FactoringPeriodModel(starting_period={}, max_period={}, duration={}, factor={})".format(
            self.starting_period, self.max_period, self.duration, self.factor)

def models():
    """A list of the names of the available period models."""
    return [cls for cls in PeriodModel.__subclasses__()]

def eval_input(source):
    result = restricted_eval(source, models())

    if isinstance(result, numbers.Number):
        return FixedPeriodModel(result)
    elif isinstance(result, PeriodModel):
        return result
    else:
        raise RuntimeError("The source ({}) is not valid.".format(source))