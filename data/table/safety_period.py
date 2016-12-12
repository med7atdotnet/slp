# Author: Matthew Bradbury

from __future__ import print_function

import itertools

from simulator.Configuration import configuration_rank

from data import latex, results

class TableGenerator:

    def __init__(self, result_file, time_after_first_normal_to_safety_period, fmt=None):
        self._result_names = ('received ratio',
                              'normal latency', 'ssd', 'captured',
                              'time after first normal')

        self._results = results.Results(
            result_file,
            parameters=tuple(),
            results=self._result_names
        )

        self.time_after_first_normal_to_safety_period = time_after_first_normal_to_safety_period

        self.fmt = fmt
        if fmt is None:
            from data_formatter import TableDataFormatter
            self.fmt = TableDataFormatter()

    def write_tables(self, stream, param_filter=lambda x: True):

        communication_models = sorted(self._results.communication_models)
        noise_models = sorted(self._results.noise_models)
        attacker_models = sorted(self._results.attacker_models)
        configurations = sorted(self._results.configurations, key=configuration_rank)
        sizes = sorted(self._results.network_sizes)
        distances = sorted(self._results.distances)
        node_id_orders = sorted(self._results.node_id_orders)
        latest_start_times = sorted(self._results.latest_node_start_times)

        product_all = list(itertools.product(sizes, configurations, attacker_models, noise_models, communication_models, distances, node_id_orders, latest_start_times))

        product_three = list(itertools.ifilter(
            lambda x: x in {(cm, n, a, c, d, nido, lst) for (s, c, a, n, cm, d, nido, lst) in self._results.data.keys()},
            itertools.product(communication_models, noise_models, attacker_models, configurations, distances, node_id_orders, latest_start_times)
        ))

        if not any(table_key in self._results.data for table_key in product_all):
            raise RuntimeError("Could not find any parameter combination in the results")

        for product_three_key in product_three:
            if not param_filter(product_three_key):
                continue

            (communication_model, noise_model, attacker_model, config, distance, node_id_order, latest_start_time) = product_three_key

            print('\\begin{table}[H]', file=stream)
            print('\\vspace{-0.35cm}', file=stream)
            print('\\caption{{Safety Periods for the \\textbf{{{}}} configuration and \\textbf{{{}}} attacker model and \\textbf{{{}}} noise model and \\textbf{{{}}} communication model and \\textbf{{{}}} distance and \\textbf{{{}}} node id order and \\textbf{{{}}} latest start time}}'.format(
                config, latex.escape(attacker_model), noise_model, communication_model, distance, node_id_order, latest_start_time), file=stream)
            print('\\centering', file=stream)
            print('\\begin{tabular}{ | c | c || c | c | c | c || c || c | }', file=stream)
            print('\\hline', file=stream)
            print('Size & Period & Received & Source-Sink   & Latency   & Time After First  & Safety Period & Captured \\tabularnewline', file=stream)
            print('~    & (sec)  & (\\%)    & Distance (hop)& (msec)    & Normal (seconds)  & (seconds)     & (\\%)    \\tabularnewline', file=stream)
            print('\\hline', file=stream)
            print('', file=stream)

            for size in sizes:

                data_key = (size, config, attacker_model, noise_model, communication_model, distance, node_id_order, latest_start_time)

                if data_key not in self._results.data:
                    #print("Skipping {} as it could not be found in the results".format(data_key))
                    continue

                for src_period in sorted(self._results.data[data_key]):

                    result = self._results.data[data_key][src_period][tuple()]

                    def _get_name_and_value(name):
                        return name, result[self._result_names.index(name)]

                    def _get_just_value(name):
                        return result[self._result_names.index(name)][0]

                    safety_period = self.time_after_first_normal_to_safety_period(
                        _get_just_value('time after first normal'))
                
                    print('{} & {} & {} & {}'
                          ' & {} & {}'
                          ' & {:0.2f} & {} \\tabularnewline'.format(
                            size,
                            src_period,
                            self.fmt.format_value(*_get_name_and_value('received ratio')),
                            self.fmt.format_value(*_get_name_and_value('ssd')),
                            self.fmt.format_value(*_get_name_and_value('normal latency')),
                            self.fmt.format_value(*_get_name_and_value('time after first normal')),
                            safety_period,
                            self.fmt.format_value(*_get_name_and_value('captured'))),
                          file=stream)
                    
                print('\\hline', file=stream)
                print('', file=stream)

            print('\\end{tabular}', file=stream)
            print('\\label{{tab:safety-periods-{}}}'.format(config), file=stream)
            print('\\end{table}', file=stream)
            print('', file=stream)


    def _get_result_mapping(self, result_names, accessor):
        # (size, configuration, attacker model, noise model, communication model, distance) -> source period -> individual result
        result = {}

        indexes = [self._result_names.index(result_name) for result_name in result_names]

        for (table_key, other_items) in self._results.data.items():
            for (source_period, items) in other_items.items():

                individual_results = [items[tuple()][index] for index in indexes]

                result.setdefault(table_key, {})[source_period] = accessor(*individual_results)

        return result

    def safety_periods(self):
        # (size, configuration, attacker model, noise model, communication model, distance) -> source period -> safety period
        return self._get_result_mapping(('time after first normal'),
                                        lambda tafn: self.time_after_first_normal_to_safety_period(tafn[0]))

    def time_taken(self):
        # (size, configuration, attacker model, noise model, communication model, distance) -> source period -> time taken
        return self._get_result_mapping(('time taken',),
                                        lambda tt: tt[0])
