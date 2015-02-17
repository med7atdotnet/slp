
from simulator.Simulator import OutputCatcher

class Attacker(object):
    def __init__(self, sim, source_id, start_node_id):
        self.sim = sim

        out = OutputCatcher(self.process)
        self.sim.tossim.addChannel('Attacker-RCV', out.write)
        self.sim.add_output_processor(out)

        self.position = None

        self.has_found_source = False

        # Create the moves variable and then make sure it
        # is set to 0 after the position has been set up.
        self.moves = 0
        self.move(start_node_id)
        self.moves = 0

    def process(self, line):
        raise NotImplementedError()

    def found_source_slow(self):
        """Checks if the source has been found using the attacker's position."""
        # Well this is a horrible hack.
        # We cannot attach ourselves to the same output catcher more than
        # once, so we have to rely on metrics grabbing and updating
        # the information about which nodes are sources.
        return self.position in self.sim.metrics.source_ids

    def found_source(self):
        """Checks if the source has been found, using a cached variable."""
        return self.has_found_source

    def move(self, node_id):
        """Moved the source to a new location."""
        self.position = node_id
        self.has_found_source = self.found_source_slow()

        self.moves += 1

    def draw(self, time, node_id):
        """Updates the attacker position on the GUI if one is present."""
        if not self.sim.run_gui:
            return

        (x, y) = self.sim.node_location(node_id)

        shape_id = "attacker"

        color = '1,0,0'

        options = 'line=LineStyle(color=({0})),fill=FillStyle(color=({0}))'.format(color)

        self.sim.scene.execute(time, 'delshape("{}")'.format(shape_id))
        self.sim.scene.execute(time, 'circle(%d,%d,5,ident="%s",%s)' % (x, y, shape_id, options))

    def _process_line(self, line):
        (time, msg_type, node_id, from_id, sequence_number) = line.split(',')

        time = float(time) / self.sim.tossim.ticksPerSecond() # Get time to be in sec
        node_id = int(node_id)
        from_id = int(from_id)
        sequence_number = int(sequence_number)

        return (time, msg_type, node_id, from_id, sequence_number)


class BasicReactiveAttacker(Attacker):
    def process(self, line):
        # Don't want to move if the source has been found
        if self.found_source():
            return

        (time, msg_type, node_id, from_id, sequence_number) = self._process_line(line)

        if self.position == node_id:

            self.move(from_id)
            
            self.draw(time, self.position)

class IgnorePreviousLocationReactiveAttacker(Attacker):
    def __init__(self, sim, source_id, start_node_id):
        super(IgnorePreviousLocationReactiveAttacker, self).__init__(sim, source_id, start_node_id)
        self.previous_location = None

    def process(self, line):
        # Don't want to move if the source has been found
        if self.found_source():
            return

        (time, msg_type, node_id, from_id, sequence_number) = self._process_line(line)

        if self.position == node_id and self.previous_location != from_id:

            self.move(from_id)

            self.draw(time, self.position)

    def move(self, node_id):
        self.previous_location = self.position
        super(IgnorePreviousLocationReactiveAttacker, self).move(node_id)

class SeqNoReactiveAttacker(Attacker):
    def __init__(self, sim, source_id, start_node_id):
        super(SeqNoReactiveAttacker, self).__init__(sim, source_id, start_node_id)
        self.sequence_numbers = {}

    def process(self, line):
        # Don't want to move if the source has been found
        if self.found_source():
            return

        (time, msg_type, node_id, from_id, sequence_number) = self._process_line(line)

        if self.position == node_id and (msg_type not in self.sequence_numbers or self.sequence_numbers[msg_type] < sequence_number):

            self.sequence_numbers[msg_type] = sequence_number
            
            self.move(from_id)

            self.draw(time, self.position)

def models():
    """A list of the names of the available attacker models."""
    return [cls.__name__ for cls in Attacker.__subclasses__()]

def default():
    """Gets the name of the default attacker model"""
    return SeqNoReactiveAttacker.__name__
