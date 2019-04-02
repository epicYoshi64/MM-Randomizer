class Entrance(object):

    def __init__(self, name='', parent=None):
        self.name = name              # Name of the Entrance
        self.parent_region = parent   # Region this Entrance is in
        self.connected_region = None  # Region this Entrance connects to
        self.target = None            # Only used in Rom.py (???)
        self.addresses = None         # Only used in Rom.py (???)
        self.spot_type = 'Entrance'
        self.recursion_count = 0      # Used to stop infinite loops when calling `can_reach`
        self.vanilla = None           # !!! Never used
        # Function that takes a state and determines if the Entrance is reachable
        self.access_rule = lambda state: True


    def copy(self, new_region):
        new_entrace = Entrance(self.name, new_region)

        new_entrace.connected_region = self.connected_region.name
        new_entrace.addresses = self.addresses
        new_entrace.spot_type = self.spot_type
        new_entrace.vanilla = self.vanilla
        new_entrace.access_rule = self.access_rule

        return new_entrace


    def can_reach(self, state):
        if self.access_rule(state) and state.can_reach(self.parent_region):
            return True

        return False


    def connect(self, region, addresses=None, target=None, vanilla=None):
        self.connected_region = region
        self.target = target
        self.addresses = addresses
        self.vanilla = vanilla
        region.entrances.append(self)


    def __str__(self):
        return str(self.__unicode__())


    def __unicode__(self):
        return '%s' % self.name
