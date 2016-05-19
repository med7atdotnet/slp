
from data.analysis import AnalyzerCommon

class Analyzer(AnalyzerCommon):
    def __init__(self, results_directory):
        super(Analyzer, self).__init__(results_directory, self.results_header(), self.normalised_parameters())

    @staticmethod
    def normalised_parameters():
        return (
            ('Sent', 'TimeTaken'),
            (('Sent', 'TimeTaken'), 'network_size'),
            ((('Sent', 'TimeTaken'), 'network_size'), 'source_rate'),
            ('FakeSent', 'TimeTaken'),
            (('FakeSent', 'TimeTaken'), 'source_rate'),
            ('NormalSent', 'TimeTaken'),

            ('energy_impact', 'network_size'),
            (('energy_impact', 'network_size'), 'TimeTaken'),
        )

    @staticmethod
    def results_header():
        d = AnalyzerCommon.common_results_header()

        d['approach']           = lambda x: x.opts['approach']

        AnalyzerCommon.common_results(d)
        
        d['captured']           = lambda x: str(x.average_of['Captured'])
        d['attacker moves']     = lambda x: AnalyzerCommon._format_results(x, 'AttackerMoves')
        d['attacker distance']  = lambda x: AnalyzerCommon._format_results(x, 'AttackerDistance')
        d['received ratio']     = lambda x: AnalyzerCommon._format_results(x, 'ReceiveRatio')
        d['normal latency']     = lambda x: AnalyzerCommon._format_results(x, 'NormalLatency')
        d['normal']             = lambda x: AnalyzerCommon._format_results(x, 'NormalSent')
        d['away']               = lambda x: AnalyzerCommon._format_results(x, 'AwaySent')
        d['choose']             = lambda x: AnalyzerCommon._format_results(x, 'ChooseSent')
        d['fake']               = lambda x: AnalyzerCommon._format_results(x, 'FakeSent')
        d['beacon']             = lambda x: AnalyzerCommon._format_results(x, 'BeaconSent')
        d['tfs']                = lambda x: AnalyzerCommon._format_results(x, 'TFS')
        d['pfs']                = lambda x: AnalyzerCommon._format_results(x, 'PFS')
        d['tailfs']             = lambda x: AnalyzerCommon._format_results(x, 'TailFS')
        d['fake to normal']     = lambda x: AnalyzerCommon._format_results(x, 'FakeToNormal')
        d['fake to fake']       = lambda x: AnalyzerCommon._format_results(x, 'FakeToFake')
        d['ssd']                = lambda x: AnalyzerCommon._format_results(x, 'NormalSinkSourceHops')
        
        d['sent heatmap']       = lambda x: AnalyzerCommon._format_results(x, 'SentHeatMap')
        d['received heatmap']   = lambda x: AnalyzerCommon._format_results(x, 'ReceivedHeatMap')

        d['norm(sent,time taken)']   = lambda x: AnalyzerCommon._format_results(x, 'norm(Sent,TimeTaken)')
        d['norm(norm(sent,time taken),network size)']   = lambda x: AnalyzerCommon._format_results(x, 'norm(norm(Sent,TimeTaken),network_size)')
        d['norm(norm(norm(sent,time taken),network size),source rate)']   = lambda x: AnalyzerCommon._format_results(x, 'norm(norm(norm(Sent,TimeTaken),network_size),source_rate)')

        d['norm(fake,time taken)']   = lambda x: AnalyzerCommon._format_results(x, 'norm(FakeSent,TimeTaken)')
        d['norm(norm(fake,time taken),source rate)'] = lambda x: AnalyzerCommon._format_results(x, 'norm(norm(FakeSent,TimeTaken),source_rate)')

        d['norm(normal,time taken)']   = lambda x: AnalyzerCommon._format_results(x, 'norm(NormalSent,TimeTaken)')

        d['energy impact per node']   = lambda x: AnalyzerCommon._format_results(x, 'norm(energy_impact,network_size)')
        d['energy impact per node per second']   = lambda x: AnalyzerCommon._format_results(x, 'norm(norm(energy_impact,network_size),TimeTaken)')

        return d
