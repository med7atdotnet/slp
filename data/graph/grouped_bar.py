
import os

from grapher import GrapherBase

from data import latex

class Grapher(GrapherBase):
    def __init__(self, output_directory, results, result_name, shows, extractor = lambda x: x):

        super(Grapher, self).__init__(output_directory)

        self.results = results
        self.result_name = result_name

        self.shows = shows
        self.extractor = extractor

    def create(self):
        self._remove_existing(self.result_name)

        print('Creating {} graph files'.format(self.result_name))

        data = {}

        for ((size, config), items1) in self.results.data.items():
            for (srcPeriod, items2) in items1.items():
                for (params, results) in items2.items():

                    key_names = ('size', 'configuration', 'source period')
                    key_values = (size, config, srcPeriod)

                    print(results)

                    yvalues = []

                    for show in self.shows:
                    	yvalues.append( self.extractor(results[ self.results.result_names.index(show) ]) )

                    data.setdefault((key_names, key_values), {})[params] = yvalues

        for ((key_names, key_values), values) in data.items():
            self._create_plot(key_names, key_values, values)

        self._create_graphs(self.result_name)

    def _create_plot(self, key_names, key_values, values):
        dirName = os.path.join(self.output_directory, self.result_name, *map(str, key_values))

        print(dirName)

        # Ensure that the dir we want to put the files in actually exists
        self._ensureDirExists(dirName)

        allPositive = True

        def quote(s):
        	return "\"{}\"".format(s)

        # Write our data
        with open(os.path.join(dirName, 'graph.dat'), 'w') as datFile:

            xvalues = list(sorted({x for x in values.keys()}))

            table =  [ [ '#' ] + list(map(quote, self.shows)) ]

            for xvalue in xvalues:
                barvalues = values.get(xvalue, '?')
                row = [ quote(xvalue) ] + barvalues

                for value in barvalues:
	                allPositive &= value >= 0

                table.append(row)

            self._pprint_table(datFile, table)


        with open(os.path.join(dirName, 'graph.p'), 'w') as pFile:

            pFile.write('#!/usr/bin/gnuplot\n')

            pFile.write('set terminal pdf enhanced\n')

            pFile.write('set xlabel "Parameters"\n')
            #pFile.write('set ylabel "{}"\n'.format(self.show))

            pFile.write('set style data histogram\n')
            pFile.write('set style histogram cluster gap 1\n')
            pFile.write('set style fill solid border -1\n')

            pFile.write('set xtic rotate by -90 scale 0\n')

            pFile.write('set xtics font ",8"\n')

            pFile.write('set key right top\n')

            # When all data is positive, make sure to include
            # 0 on the y axis.
            if allPositive:
                pFile.write('set yrange [0:]\n')
            
            pFile.write('set output "graph.pdf"\n')
            
            plots = []

            for i, show in enumerate(self.shows):
            	if i == 0:
            		plots.append('"graph.dat" using {}:xticlabels(1) ti "{}"'.format(i + 2, show))
            	else:
            		plots.append('"graph.dat" using {} ti "{}"'.format(i + 2, show))

            pFile.write('plot {}\n\n'.format(', '.join(plots)))
        

        with open(os.path.join(dirName, 'graph.caption'), 'w') as captionFile:
            captionFile.write('Parameters:\\newline\n')
            for (name, value) in zip(key_names, key_values):
                captionFile.write('{}: {}\\newline\n'.format(latex.escape(str(name)), latex.escape(str(value))))
