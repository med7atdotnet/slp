
from __future__ import print_function

import os

from algorithm.common import CommandLineCommon


import algorithm.protectionless as protectionless

# The import statement doesn't work, so we need to use __import__ instead
template = __import__("algorithm.template", globals(), locals(), ['object'], -1)
adaptive = __import__(__package__, globals(), locals(), ['object'], -1)

from data.table import safety_period, fake_result, comparison
from data.graph import summary, heatmap, versus, bar, min_max_versus

from data import results, latex

from data.util import useful_log10, scalar_extractor

class CLI(CommandLineCommon.CLI):

    executable_path = 'run.py'

    distance = 4.5

    sizes = [ 11, 15, 21, 25 ]

    source_periods = [ 1.0, 0.5, 0.25, 0.125 ]

    configurations = [
        ('SourceCorner', 'CHOOSE'),
        #('SinkCorner', 'CHOOSE'),
        #('FurtherSinkCorner', 'CHOOSE'),
        #('Generic1', 'CHOOSE'),
        #('Generic2', 'CHOOSE'),

        #('RingTop', 'CHOOSE'),
        #('RingOpposite', 'CHOOSE'),
        #('RingMiddle', 'CHOOSE'),

        #('CircleEdges', 'CHOOSE'),
        #('CircleSourceCentre', 'CHOOSE'),
        #('CircleSinkCentre', 'CHOOSE'),
    ]

    attacker_models = ['SeqNoReactiveAttacker']

    approaches = ["PB_SINK_APPROACH", "PB_ATTACKER_EST_APPROACH"]

    repeats = 300

    parameter_names = ('approach',)

    protectionless_configurations = [(a) for (a, build) in configurations]
    

    def __init__(self):
        super(CLI, self).__init__(__package__)


    def _execute_runner(self, driver, results_directory, skip_completed_simulations=True):
        safety_period_table_generator = safety_period.TableGenerator()
        safety_period_table_generator.analyse(protectionless.result_file_path)

        safety_periods = safety_period_table_generator.safety_periods()

        runner = adaptive.Runner.RunSimulations(driver, results_directory, safety_periods, skip_completed_simulations)
        runner.run(
            self.executable_path, self.distance, self.sizes, self.source_periods, self.approaches,
            self.configurations, self.attacker_models, self.repeats)


    def _run_table(self, args):
        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=('normal latency', 'ssd', 'captured', 'fake', 'received ratio', 'tfs', 'pfs'))

        result_table = fake_result.ResultTable(adaptive_results)

        def create_adaptive_table(name, param_filter=lambda x: True):
            filename = name + ".tex"

            with open(filename, 'w') as result_file:
                latex.print_header(result_file)
                result_table.write_tables(result_file, param_filter)
                latex.print_footer(result_file)

            latex.compile_document(filename)

        create_adaptive_table("adaptive-results")

    def _run_graph(self, args):
        graph_parameters = {
            'normal latency': ('Normal Message Latency (seconds)', 'left top'),
            'ssd': ('Sink-Source Distance (hops)', 'left top'),
            'captured': ('Capture Ratio (%)', 'left top'),
            'fake': ('Fake Messages Sent', 'left top'),
            'sent': ('Total Messages Sent', 'left top'),
            'received ratio': ('Receive Ratio (%)', 'left bottom'),
            'tfs': ('Number of TFS Created', 'left top'),
            'pfs': ('Number of PFS Created', 'left top'),
        }

        heatmap_results = ['sent heatmap', 'received heatmap']

        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=tuple(graph_parameters.keys() + heatmap_results))    

        for name in heatmap_results:
            heatmap.Grapher(adaptive.graphs_path, adaptive_results, name).create()
            summary.GraphSummary(os.path.join(adaptive.graphs_path, name), 'adaptive-' + name.replace(" ", "_")).run()

        for (yaxis, (yaxis_label, key_position)) in graph_parameters.items():
            name = '{}-v-source-period'.format(yaxis.replace(" ", "_"))

            g = versus.Grapher(adaptive.graphs_path, name,
                xaxis='size', yaxis=yaxis, vary='source period', yextractor=scalar_extractor)

            g.xaxis_label = 'Network Size'
            g.yaxis_label = yaxis_label
            g.vary_label = 'Source Period'
            g.vary_prefix = ' seconds'
            g.key_position = key_position

            g.create(adaptive_results)

            summary.GraphSummary(os.path.join(adaptive.graphs_path, name), 'adaptive-' + name).run()

    def _run_comparison_table(self, args):
        results_to_compare = ('normal latency', 'ssd', 'captured', 'fake', 'received ratio', 'tfs', 'pfs')

        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=results_to_compare)

        template_results = results.Results(template.result_file_path,
            parameters=('fake period', 'temp fake duration', 'pr(tfs)', 'pr(pfs)'),
            results=results_to_compare)

        result_table = comparison.ResultTable(template_results, adaptive_results)

        def create_comparison_table(name, param_filter=lambda x: True):
            filename = name + ".tex"

            with open(filename, 'w') as result_file:
                latex.print_header(result_file)
                result_table.write_tables(result_file, param_filter)
                latex.print_footer(result_file)

            latex.compile_document(filename)

        create_comparison_table("adaptive-template-comparison",
            lambda (fp, dur, ptfs, ppfs): ptfs not in {0.2, 0.3, 0.4})

        create_comparison_table("adaptive-template-comparison-low-prob",
            lambda (fp, dur, ptfs, ppfs): ptfs in {0.2, 0.3, 0.4})

    def _run_comparison_graph(self, args):
        results_to_compare = ('normal latency', 'ssd', 'captured', 'sent', 'received', 'normal', 'fake', 'away', 'choose', 'received ratio', 'tfs', 'pfs')

        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=results_to_compare)

        template_results = results.Results(template.result_file_path,
            parameters=('fake period', 'temp fake duration', 'pr(tfs)', 'pr(pfs)'),
            results=results_to_compare)

        result_table = comparison.ResultTable(template_results, adaptive_results)

        def create_comp_bar(show, pc=False):
            name = 'template-comp-{}-{}'.format(show, "pcdiff" if pc else "diff")

            bar.DiffGrapher(adaptive.graphs_path, result_table, name,
                shows=[show],
                extractor=lambda (diff, pcdiff): pcdiff if pc else diff).create()

            summary.GraphSummary(os.path.join(adaptive.graphs_path, name), 'adaptive-{}'.format(name).replace(" ", "_")).run()

        for result_name in results_to_compare:
            create_comp_bar(result_name, pc=True)
            create_comp_bar(result_name, pc=False)

        def create_comp_bar_pcdiff(pc=True, modified=lambda x: x, name_addition=None, shows=results_to_compare):
            name = 'template-comp-{}'.format("pcdiff" if pc else "diff")
            if name_addition is not None:
                name += '-{}'.format(name_addition)

            # Normalise wrt to the number of nodes in the network
            def normalisor(key_names, key_values, params, yvalue):
                size = key_values[ key_names.index('size') ]
                result = yvalue / (size * size)

                return modified(result)

            g = bar.DiffGrapher(adaptive.graphs_path, result_table, name,
                shows=shows,
                extractor=lambda (diff, pcdiff): pcdiff if pc else diff,
                normalisor=normalisor)

            g.yaxis_label = 'Percentage Difference per Node' if pc else 'Average Difference per Node'
            if name_addition is not None:
                g.yaxis_label += ' ({})'.format(name_addition)

            g.xaxis_label = 'Parameters (P_{TFS}, D_{TFS}, Pr(TFS), Pr(PFS))'

            g.create()

            summary.GraphSummary(os.path.join(adaptive.graphs_path, name), 'adaptive-{}'.format(name).replace(" ", "_")).run()

        results_to_show = ('normal', 'fake', 'away', 'choose')

        create_comp_bar_pcdiff(pc=True,  shows=results_to_show)
        create_comp_bar_pcdiff(pc=False, shows=results_to_show)
        create_comp_bar_pcdiff(pc=True,  shows=results_to_show, modified=useful_log10, name_addition='log10')

    def _run_min_max_versus(self, args):
        graph_parameters = {
            'normal latency': ('Normal Message Latency (seconds)', 'left top'),
            'ssd': ('Sink-Source Distance (hops)', 'left top'),
            'captured': ('Capture Ratio (%)', 'right top'),
            'fake': ('Fake Messages Sent', 'left top'),
            'sent': ('Total Messages Sent', 'left top'),
            'received ratio': ('Receive Ratio (%)', 'left bottom'),
            'tfs': ('Number of TFS Created', 'left top'),
            'pfs': ('Number of PFS Created', 'left top'),
        }

        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=graph_parameters.keys())

        template_results = results.Results(template.result_file_path,
            parameters=('fake period', 'temp fake duration', 'pr(tfs)', 'pr(pfs)'),
            results=graph_parameters.keys())

        def graph_min_max_versus(result_name):
            name = 'min-max-template-versus-{}'.format(result_name)

            g = min_max_versus.Grapher(adaptive.graphs_path, name,
                xaxis='size', yaxis=result_name, vary='approach', yextractor=scalar_extractor)

            g.xaxis_label = 'Network Size'
            g.yaxis_label = graph_parameters[result_name][0]
            g.key_position = graph_parameters[result_name][1]

            g.min_label = 'Static - Lowest'
            g.max_label = 'Static - Highest'
            g.comparison_label = 'Dynamic'
            g.vary_label = ''

            def vvalue_converter(name):
                return {
                    'PB_SINK_APPROACH': 'Pull Sink',
                    'PB_ATTACKER_EST_APPROACH': 'Pull Attacker'
                }[name]
            g.vvalue_label_converter = vvalue_converter

            g.create(template_results, adaptive_results)

            summary.GraphSummary(os.path.join(adaptive.graphs_path, name), 'adaptive-{}'.format(name).replace(" ", "_")).run()

        for result_name in graph_parameters.keys():
            graph_min_max_versus(result_name)

    def _run_time_taken_table(self, args):
        adaptive_results = results.Results(adaptive.result_file_path,
            parameters=parameter_names,
            results=('wall time', 'event count'))

        result_table = fake_result.ResultTable(adaptive_results)

        def create_adaptive_table(name, param_filter=lambda x: True):
            filename = name + ".tex"

            with open(filename, 'w') as result_file:
                latex.print_header(result_file)
                result_table.write_tables(result_file, param_filter)
                latex.print_footer(result_file)

            latex.compile_document(filename)

    def run(self, args):

        if 'cluster' in args:
            self._run_cluster(args)

        if 'run' in args:
            self._run_run(args)

        if 'analyse' in args:
            self._run_analyse(args)

        if 'table' in args:
            self._run_table(args)

        if 'graph' in args:
            self._run_graph(self, args)

        if 'comparison-table' in args:
            self._run_comparison_table(args)

        if 'comparison-graph' in args:
            self._run_comparison_graph(args)

        if 'min-max-versus' in args:
            self._run_min_max_versus(args)

        if 'time-taken-table' in args:
            self._run_time_taken_table(args)