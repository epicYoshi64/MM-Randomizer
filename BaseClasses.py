import copy
from enum import Enum, unique
import logging
from collections import OrderedDict, Counter, defaultdict
from version import __version__ as OoTRVersion
import random

"""
World object:
Creates the world we're gonna start with and which will be populated.
Contains the following:
  - All settings/flags set as options
  - The state to track what has been collected
  - Locations
  - Entrances
  - Regions
We might need a better name for Locations/Regions/Entrances,
because they're all words that mean "places" while describing very
different things.
"""
class World(object):

    def __init__(self, settings):
        self.shuffle = 'vanilla'
        self.dungeons = []
        self.regions = []
        self.itempool = []
        self.state = CollectionState(self)
        self._cached_locations = None
        self._entrance_cache = {}
        self._region_cache = {}
        self._entrance_cache = {}
        self._location_cache = {}
        self.required_locations = []
        self.shop_prices = {}

        # dump settings directly into world's namespace
        # this gives the world an attribute for every setting listed in Settings.py
        self.settings = settings
        self.__dict__.update(settings.__dict__)
        # rename a few attributes...
        self.keysanity = self.shuffle_smallkeys != 'dungeon'
        self.check_beatable_only = not self.all_reachable
        # group a few others
        self.tunic_colors = [self.hatcolor, self.shirtcolor, self.pantscolor,
            self.swordcolor, self.deityswordcolor,
            self.dekuspincolor, self.zoraslashcolor,
            self.deitybeamcolor, self.boomerangtrail]
        self.tunic_palettes = [self.dekucolor, self.dekutuniccolor,
            self.goronhatcolor, self.goronpantscolor,
            self.zoracolor, self.zoratuniccolor,
            self.zorafincolor, self.boomerangcolor,
            self.deitycolor]
        self.tatl_colors = [self.tatlcolordefault, self.tatlcolorenemy, self.tatlcolornpc, self.tatlcolorprop, self.tatlcolorboss]
        self.tatl_hint_sounds = [self.tatlsfxoverworld, self.tatlsfxenemytarget]
        self.can_take_damage = True
        self.keys_placed = False
        self.spoiler = Spoiler(self)


    def copy(self):
        ret = World(self.settings)
        # ret.skipped_trials = copy.copy(self.skipped_trials)
        # ret.big_poe_count = copy.copy(self.big_poe_count)
        ret.can_take_damage = self.can_take_damage
        # ret.shop_prices = copy.copy(self.shop_prices)
        ret.id = self.id
        from Regions import create_dungeons, create_regions
        from Rules import set_rules
        create_regions(ret)
        create_dungeons(ret)
        set_rules(ret)

        # connect copied world
        for region in self.regions:
            copied_region = ret.get_region(region.name)
            for entrance in region.entrances:
                ret.get_entrance(entrance.name).connect(copied_region)

        # fill locations
        for location in self.get_locations():
            if location.item is not None:
                item = Item(location.item.name, location.item.advancement, location.item.priority, location.item.type)
                item.world = location.item.world
                ret.get_location(location.name).item = item
                item.location = ret.get_location(location.name)
                item.location.event = location.event

        # copy remaining itempool. No item in itempool should have an assigned location
        for item in self.itempool:
            new_item = Item(item.name, item.advancement, item.priority, item.type)
            new_item.world = item.world
            ret.itempool.append(new_item)

        # copy progress items in state
        ret.state.prog_items = copy.copy(self.state.prog_items)

        # set_shop_rules(ret)

        return ret

    def initialize_regions(self):
        for region in self.regions:
            region.world = self
            for location in region.locations:
                location.world = self

    def initialize_items(self):
        for item in self.itempool:
            item.world = self
        for region in self.regions:
            for location in region.locations:
                if location.item != None:
                    location.item.world = self
        for item in [item for dungeon in self.dungeons for item in dungeon.all_items]:
            item.world = self

    # Checks if `regionname` is actually a Region
    # If not, will try to find that name in `World.regions` if
    # you only gave the name of the Region and cache it to
    # be easily fetched later in `_regions_cache`
    def get_region(self, regionname):
        if isinstance(regionname, Region):
            return regionname
        try:
            return self._region_cache[regionname]
        except KeyError:
            for region in self.regions:
                if region.name == regionname:
                    self._region_cache[regionname] = region
                    return region
            raise RuntimeError('No such region %s' % regionname)

    # Similar to `get_region` but for Entrances
    def get_entrance(self, entrance):
        if isinstance(entrance, Entrance):
            return entrance
        try:
            return self._entrance_cache[entrance]
        except KeyError:
            for region in self.regions:
                for exit in region.exits:
                    if exit.name == entrance:
                        self._entrance_cache[entrance] = exit
                        return exit
            raise RuntimeError('No such entrance %s' % entrance)

    # Similar to `get_region` but for Locations
    def get_location(self, location):
        if isinstance(location, Location):
            return location
        try:
            return self._location_cache[location]
        except KeyError:
            for region in self.regions:
                for r_location in region.locations:
                    if r_location.name == location:
                        self._location_cache[location] = r_location
                        return r_location
        raise RuntimeError('No such location %s' % location)

    def get_items(self):
        return [loc.item for loc in self.get_filled_locations()] + self.itempool

    # get a list of items that should stay in their proper dungeon
    def get_restricted_dungeon_items(self):
        itempool = []
        if self.shuffle_mapcompass == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.shuffle_smallkeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.shuffle_bosskeys == 'dungeon':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool

    # get a list of items that don't have to be in their proper dungeon
    def get_unrestricted_dungeon_items(self):
        itempool = []
        if self.shuffle_mapcompass == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.dungeon_items])
        if self.shuffle_smallkeys == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.small_keys])
        if self.shuffle_bosskeys == 'keysanity':
            itempool.extend([item for dungeon in self.dungeons for item in dungeon.boss_key])

        for item in itempool:
            item.world = self
        return itempool

    # Takes an item(name?) and gives the location(s) where
    # that item can be found.
    def find_items(self, item):
        return [location for location
                in self.get_locations()
                        if location.item is not None
                                        and location.item.name == item]


    # Takes a Location and an Item and tries to put the item in the
    # Location using `location.can_fill`.
    # If collect isn't set to False, also adds the location to
    # `CollectionState.locations_checked` and more
    # (see `CollectionState.collect`)
    def push_item(self, location, item, collect=True):
        if not isinstance(location, Location):
            location = self.get_location(location)

        if location.can_fill(self.state, item, False):
            location.item = item
            item.location = location
            if collect:
                self.state.collect(item, location.event, location)

            logging.getLogger('').debug('Placed %s at %s', item, location)
        else:
            raise RuntimeError('Cannot assign item %s to location %s.' % (item, location))

    # Initializes all locations found in the provided World.regions
    # into `_cached_locations` and returns all locations.
    def get_locations(self):
        if self._cached_locations is None:
            self._cached_locations = []
            for region in self.regions:
                self._cached_locations.extend(region.locations)
        return self._cached_locations

    # Like it says, returns all item locations that aren't filled yet
    def get_unfilled_locations(self):
        return [location for location
                in self.get_locations()
                        if location.item is None]

    # Like above, but returns the ones that ARE filled already.
    def get_filled_locations(self):
        return [location for location
                in self.get_locations()
                        if location.item is not None]

    # Returns all reachable locations from the provided state
    # OR if None give, from the World.state.
    def get_reachable_locations(self, state=None):
        if state is None:
            state = self.state
        return [location for location
                in self.get_locations()
                        if state.can_reach(location)]

    # Same as `get_reachable_locations`, but returns all
    # locations where there's no item and it's reachable.
    def get_placeable_locations(self, state=None):
        if state is None:
            state = self.state
        return [location for location
                in self.get_locations()
                        if location.item is None
                                        and state.can_reach(location)]

    # Checks to see if this item unlocks any new Location
    def unlocks_new_location(self, item):
        # Create hypothetical state
        temp_state = self.state.copy()
        # (Still not sure what this does)
        temp_state.clear_cached_unreachable()
        temp_state.collect(item)

        for location in self.get_unfilled_locations():
            # Check in all locations if we can reach it now (hypothetically)
            # and can't without the item (still the actual `.state`)
            if temp_state.can_reach(location) and not self.state.can_reach(location):
                return True

        return False

    # Checks if the win condition has been satisfied.
    # Used to ignore `location.can_reach` when `beatable_only` is set.
    def has_beaten_game(self, state):
        return state.has('Triforce')


'''
CollectionState object:
Keeps track of all Items/Regions/Entrances/Locations/Events/etc.
while filling in the items in the Locations in the World.
'''
class CollectionState(object):

    def __init__(self, parent):
        self.prog_items = Counter()
        self.world = parent
        self.region_cache = {}
        self.location_cache = {}
        self.entrance_cache = {}
        self.recursion_count = 0
        self.collected_locations = {}

    def clear_cached_unreachable(self):
        # we only need to invalidate results which were False, places we could reach before we can still reach after adding more items
        self.region_cache = {k: v for k, v in self.region_cache.items() if v}
        self.location_cache = {k: v for k, v in self.location_cache.items() if v}
        self.entrance_cache = {k: v for k, v in self.entrance_cache.items() if v}

    # Make a copy of the current state
    def copy(self):
        ret = CollectionState(self.world)
        ret.prog_items = copy.copy(self.prog_items)
        ret.region_cache = copy.copy(self.region_cache)
        ret.location_cache = copy.copy(self.location_cache)
        ret.entrance_cache = copy.copy(self.entrance_cache)
        # ret.events = copy.copy(self.events)
        # ret.path = copy.copy(self.path)
        ret.collected_locations = copy.copy(self.collected_locations)
        ret.recursion_count = copy.copy(self.recursion_count)
        return ret

    '''
    Takes a Region/Entrance/Location
    (Or a name of a R/E/L, and default to Region. If the name is of
    an Entrance or Location, `resolution_hint` should be set to either
    'Entrance' or 'Location')

    Does the following:
    - Checks if we tried to reach this spot already
        (R/E/L's implementation of `can_reach` also uses the `CollectionState.can_reach`
    - If the spot is already in the cache for that spot, return that (will be False if present)
    - Check the `can_reach` of that spot (while increasing the `recursion_count`)
        - If it's reachable, done.
        - If not, put it in the cache as unreachable
            (unless we're still in a recursion, because that means we were checking
             the accessability of a different spot:
                - Regions check Entrances
                - Entrances and Locations check Regions
            )
    '''
    def can_reach(self, spot, resolution_hint=None):
        try:
            spot_type = spot.spot_type
            if spot_type == 'Location':
                correct_cache = self.location_cache
            elif spot_type == 'Region':
                correct_cache = self.region_cache
            elif spot_type == 'Entrance':
                correct_cache = self.entrance_cache
            else:
                raise AttributeError
        except AttributeError:
            # try to resolve a name
            if resolution_hint == 'Location':
                spot = self.world.get_location(spot)
                correct_cache = self.location_cache
            elif resolution_hint == 'Entrance':
                spot = self.world.get_entrance(spot)
                correct_cache = self.entrance_cache
            else:
                # default to Region
                spot = self.world.get_region(spot)
                correct_cache = self.region_cache

        if spot.recursion_count > 0:
            return False

        if spot not in correct_cache:
            # for the purpose of evaluating results, recursion is resolved by always denying recursive access (as that ia what we are trying to figure out right now in the first place
            spot.recursion_count += 1
            self.recursion_count += 1
            can_reach = spot.can_reach(self)
            spot.recursion_count -= 1
            self.recursion_count -= 1

            # we only store qualified false results (i.e. ones not inside a hypothetical)
            if not can_reach:
                if self.recursion_count == 0:
                    correct_cache[spot] = can_reach
            else:
                correct_cache[spot] = can_reach
            return can_reach
        return correct_cache[spot]

    def has(self, item, count=1):
        if count == 1:
            return item in self.prog_items
        return self.item_count(item) >= count

    # Count how many duplicates of an item are in `.prog_items`
    # (Used in `heart_count` and `has`)
    def item_count(self, item):
        return self.prog_items[item]

    # Checks if explosions are possible given the current state.
    def can_blast(self):
        return (self.form('Human') and (self.has_bombs() or self.has_bombchus() or self.can_use('Blast Mask'))) or self.can_use('Powder Keg')

    def has_nuts(self):
        return self.has('Buy Deku Nut (5)') or self.has('Buy Deku Nut (10)') or self.has('Deku Nut Drop')

    def has_sticks(self):
        return self.has('Buy Deku Stick (1)') or self.has('Deku Stick Drop')

    def has_bow(self):
        return self.has('Bow') or self.has('Large Quiver'), self.has('Largest Quiver')

    def has_bomb_bag(self):
        return self.has('Bomb Bag') or self.has('Bigger Bomb Bag'), self.has('Biggest Bomb Bag')

    def has_ocarina(self):
        return self.has("Ocarina of Time")

    def can_play(self, song):
        return self.has_ocarina() and self.has(song)

    def can_use(self, item):
        magic_items = ['Lens of Truth', 'Deku Bubble', 'Deity Beam']
        magic_arrows = ['Fire Arrows', 'Ice Arrows', 'Light Arrows']
        human_items = ['Bow', 'Hookshot', 'Magic Beans', 'Bomb Bag', 'Bombchus', 'Deku Sticks', 'Deku Nuts']
        if item in magic_items:
            return self.has(item) and self.has('Magic Meter')
        elif item in human_items:
            return self.has(item) and self.form('Human')
        elif item in magic_arrows:
            return self.has(item) and self.form('Human') and self.has_bow()
        elif item == 'Hookshot':
            return self.has('Hookshot') and self.form('Human')
        elif item == 'Scarecrow':
            return self.has('Hookshot') and self.form('Human') and self.has_ocarina()
        elif item == 'Powder Keg':
            return self.has('Powder Keg') and self.form('Goron')

    def can_buy_bombchus(self):
        return self.has('Buy Bombchu (5)') or self.has('Buy Bombchu (10)') or self.has('Buy Bombchu (20)') or self.can_reach('Bomb Shop')

    def has_bombchus(self):
        if self.world.bombchus_in_logic:
            return (any(pritem.startswith('Bombchus') for pritem in self.prog_items) and self.can_buy_bombchus())
        else:
            return self.has_bomb_bag() and self.can_buy_bombchus()

    def has_bombchus_item(self):
        return (self.world.bombchus_in_logic and \
                (any(pritem.startswith('Bombchus') for pritem in self.prog_items))) \
            or (not self.world.bombchus_in_logic and self.has_bomb_bag())

    def has_explosives(self):
        return self.has_bombs() or self.has_bombchus() or self.can_use('Blast Mask') or self.can_use('Powder Keg')

    def can_smash(self):
        return self.can_blast() or self.form('Goron')

    def can_dive(self):
        return self.form('Zora')

    def can_see_with_lens(self):
        return (self.has('Magic Meter') and self.has('Lens of Truth')) or self.world.logic_lens != 'all'

    def has_projectile(self):
        # TODO: test for other ways of popping balloons (in the air)
        return self.form('Zora') or (self.form('Deku') and self.has('Magic Meter')) or \
            (self.form('Human') and (self.has('Bow') or self.has('Hookshot')))

    # Checks if bottles have been obtained
    def has_bottle(self):
        is_normal_bottle = lambda item: (item.startswith('Bottle') )
        return any(is_normal_bottle(pritem) for pritem in self.prog_items)

    # Counts the number of bottles in `.prog_items`
    def bottle_count(self):
        return sum([pritem for pritem in self.prog_items if pritem.startswith('Bottle')])

    # Checks if the current heart count is equal or higher than the given `count` number
    def has_hearts(self, count):
        # Warning: This only considers items that are marked as advancement items
        # (Vlix' comment: I don't know what this comment above means, but I'll keep it in)
        return self.heart_count() >= count

    # Checks if paper has been obtained.
    def has_paper(self):
        paper_list = [ 'Town Title Deed'
                     , 'Swamp Title Deed'
                     , 'Mountain Title Deed'
                     , 'Ocean Title Deed'
                     , 'Letter to Kafei'
                     , 'Special Delivery to Mama']  # TODO: needs more? # TODO: no?
        for p in paper_list:
            if self.has(p):
                return True
        return False

    def can_wear(self, mask):
        return self.form('Human') and self.has(mask)

    def stray_fairy_req(self, test=True):
        return self.can_use('Great Fairy Mask') # or (not self.options('ReqGFMask') and test)
    # I think this is what's actually correct for optionally requiring gf mask for all fairies: a test is passed to this
    # fxn which is only needed if you can't use the gf mask and you're not required to

    def lens_req(self):
        return (self.can_use('Lens of Truth') and self.has('Magic Meter')) # or not self.options('ReqLens')

    def dog_track_MoT_req(self):
        return self.can_use('Mask of Truth') # or not self.options('DogTrackMoT')

    def can_kill_lizalfos(self):
        # I figure they use lizalfos as a miniboss enough that this is a check worth abstracting
        # I imagine deku can't deal with them, goron /probably/ can? to test, easy enough to chance later
        return self.form('Human') or self.form('Zora') or self.form('Goron')

    def can_kill_gekkos(self):
        # same as with lizalfos, it's common enough
        # I wonder, can zora hit with their blades in place of the bow? or hookshot maybe?
        return (self.form('Deku') or self.can_blast() or self.form('Goron')) and self.can_use('Bow')

    def can_use(self, item):
        human_items = ['Hookshot', 'Bow']
        # yeah, just write this out at some point
        # all masks (aside from transform ones), plus bombs etc.
        # hold on, better version
        # every item has an associated list of requirements
        # for stuff like transform masks and stuff that everyone can use, it's just []
        # for stuff like 'Bow', it's ['Human']
        # for stuff like 'Fire Arrow', it's ['Human', 'Bow']
        # then just loop through it and check
        if item in human_items:
            return self.form('Human') and self.has(item)
        return self.has(item)

    def can_epona(self):
        return self.has('Eponas Song') and (self.form('Human')) # or self.options('EponaGlitchesOrSomething'))

    # Checks to see if balloons are poppable.
    def can_pop_balloon(self):
        # TODO: test for other ways of popping balloons (in the air)
        return (self.form('Zora')
            or (self.form('Deku') and self.has('Magic Meter'))
            or (self.form('Human') and (self.has('Bow') or self.has('Hookshot'))))

    def can(self, trick):
        # still don't know exactly how this should work, but the idea is to have a collection of tricks the user has
        # selected as allowed
        return True # self.tricks[trick]


    # Gives the number of current full hearts
    def heart_count(self):
        # Warning: This only considers items that are marked as advancement items
        return (
            self.item_count('Heart Container')
            + self.item_count('Piece of Heart') // 4
            + 3 # starting hearts
        )

    # Checks if the given form is accessable.
    # TODO: have logical constraints for starting form
    # `starting_form('Human') or has('Song of Healing')`
    # (or instead of Song of Healing, just Ocarina, or 'Cured by HMS' or something)
    def form(self, form):
        if form == 'Deku':
            return self.has('Deku Mask')
        if form == 'Goron':
            return self.has('Goron Mask')
        if form == 'Zora':
            return self.has('Zora Mask')
        # TODO: This probably needs to change to something like:
        if form == 'Human':
            return self.has('Fierce Deity Mask')

    def any_form_but(self, excl_form):
        return True in [self.form(x) for x in ['Deku', 'Human', 'Goron', 'Zora'] if x != excl_form]

    # Checks to see if fire can be generated autonomously
    def has_fire_source(self):
        return self.can_use('Fire Arrows')

    # Not used anywhere, but used in ZOoTR in `Location.access_rule`s as a requirement?
    def guarantee_hint(self):
        if(self.world.hints == 'mask'):
            # has the mask of truth
            return self.has('Mask of Truth')
        return True

    # Be careful using this function. It will not collect any
    # items that may be locked behind the item, only the item itself.
    def collect(self, item):
        if item.advancement:
            self.prog_items[item.name] += 1
            self.clear_cached_unreachable()

    # Be careful using this function. It will not uncollect any
    # items that may be locked behind the item, only the item itself.
    def remove(self, item):
        if self.prog_items[item.name] > 0:
            self.prog_items[item.name] -= 1
            if self.prog_items[item.name] <= 0:
            	del self.prog_items[item.name]

            # invalidate collected cache. unreachable locations are still unreachable
            self.region_cache =   {k: v for k, v in self.region_cache.items() if not v}
            self.location_cache = {k: v for k, v in self.location_cache.items() if not v}
            self.entrance_cache = {k: v for k, v in self.entrance_cache.items() if not v}
            self.recursion_count = 0

    def __getattr__(self, item):
        if item.startswith('can_reach_'):
            return self.can_reach(item[10])
        elif item.startswith('has_'):
            return self.has(item[4])

        raise RuntimeError('Cannot parse %s.' % item)

    # This function returns a list of states that is each of the base_states
    # with every item still in the itempool. It only adds items that belong
    # to its respective world. See fill_restrictive
    @staticmethod
    def get_states_with_items(base_state_list, itempool):
        new_state_list = []
        for base_state in base_state_list:
            new_state = base_state.copy()
            for item in itempool:
                if item.world.id == base_state.world.id: # Check world
                    new_state.collect(item)
            new_state_list.append(new_state)
        CollectionState.collect_locations(new_state_list)
        return new_state_list

    # This collected all item locations available in the state list given that
    # the states have collected items. The purpose is that it will search for
    # all new items that become accessible with a new item set
    @staticmethod
    def collect_locations(state_list):
        # Get all item locations in the worlds
        item_locations = [location for state in state_list for location in state.world.get_filled_locations() if location.item.advancement]

        # will loop if there is more items opened up in the previous iteration. Always run once
        reachable_items_locations = True
        while reachable_items_locations:
            # get reachable new items locations
            reachable_items_locations = [location for location in item_locations if location.name not in state_list[location.world.id].collected_locations and state_list[location.world.id].can_reach(location)]
            for location in reachable_items_locations:
                # Mark the location collected in the state world it exists in
                state_list[location.world.id].collected_locations[location.name] = True
                # Collect the item for the state world it is for
                state_list[location.item.world.id].collect(location.item)

    # This returns True is every state is beatable. It's important to ensure
    # all states beatable since items required in one world can be in another.
    @staticmethod
    def can_beat_game(state_list, scan_for_items=True):
        if scan_for_items:
            # Check if already beaten
            game_beaten = True
            for state in state_list:
                if not state.has('Majora\'s Mask'):
                    game_beaten = False
                    break
            if game_beaten:
                return True

            # collect all available items
            new_state_list = [state.copy() for state in state_list]
            CollectionState.collect_locations(new_state_list)
        else:
            new_state_list = state_list

        # if the every state got the Triforce, then return True
        for state in new_state_list:
            if not state.has('Majora\'s Mask'):
                return False
        return True

    @staticmethod
    def update_required_items(worlds):
        state_list = [world.state for world in worlds]

        # get list of all of the progressive items that can appear in hints
        all_locations = [location for world in worlds for location in world.get_filled_locations()]
        item_locations = [location for location in all_locations
            if location.item.advancement
            and location.item.type != 'Event'
            and location.item.type != 'Shop'
            and not location.event
            and (worlds[0].shuffle_smallkeys != 'dungeon' or not location.item.smallkey)
            and (worlds[0].shuffle_bosskeys != 'dungeon' or not location.item.bosskey)]

        # if the playthrough was generated, filter the list of locations to the
        # locations in the playthrough. The required locations is a subset of these
        # locations. Can't use the locations directly since they are location to the
        # copied spoiler world, so must try to find the matching locations by name
        if worlds[0].spoiler.playthrough:
            spoiler_locations = defaultdict(lambda: [])
            for location in [location for _,sphere in worlds[0].spoiler.playthrough.items() for location in sphere]:
                spoiler_locations[location.name].append(location.world.id)
            item_locations = list(filter(lambda location: location.world.id in spoiler_locations[location.name], item_locations))

        required_locations = []
        reachable_items_locations = True
        while (item_locations and reachable_items_locations):
            reachable_items_locations = [location for location in all_locations if location.name not in state_list[location.world.id].collected_locations and state_list[location.world.id].can_reach(location)]
            for location in reachable_items_locations:
                # Try to remove items one at a time and see if the game is still beatable
                if location in item_locations:
                    old_item = location.item
                    location.item = None
                    if not CollectionState.can_beat_game(state_list):
                        required_locations.append(location)
                    location.item = old_item
                    item_locations.remove(location)
                state_list[location.world.id].collected_locations[location.name] = True
                state_list[location.item.world.id].collect(location.item)

        # Filter the required location to only include location in the world
        for world in worlds:
            world.spoiler.required_locations = list(filter(lambda location: location.world.id == world.id, required_locations))


@unique
class RegionType(Enum):
    Overworld = 1
    Interior = 2
    Dungeon = 3
    Grotto = 4

    # !!! NEVER USED
    @property
    def is_indoors(self):
        """Shorthand for checking if Interior or Dungeon"""
        return self in (RegionType.Interior, RegionType.Dungeon, RegionType.Grotto)


'''
Region object:
Information about a region (e.g. South Clock Town, Termina Field, Stock Pot Inn)

Contains entrances and exits to other Regions, and item Locations.
'''
class Region(object):

    def __init__(self, name, type):
        self.name = name    # Name of the Region
        self.type = type    # RegionType set by `create_{type}_region` in Regions.py
        self.entrances = [] # Entrances that go to this Region
        self.exits = []     # Entrances found in this Region that connect to other Regions
        self.locations = [] # Item Locations found in this Region
        self.dungeon = None # True if this Region is (in) a Dungeon
        self.world = None   # World object
        self.spot_type = 'Region'
        self.recursion_count = 0
        self.price = None

    # Checks if this Region is reachable
    # - Checks if any of the entrances are reachable
    # - Adds itself to the `CollectionState.path` if not already in there
    def can_reach(self, state):
        for entrance in self.entrances:
            if state.can_reach(entrance):
                # if not self in state.path:
                #     state.path[self] = (self.name, state.path.get(entrance, None))
                return True
        return False

    # Checks to see if the item give can be filled in this Region.
    # Used to check that, if the item is a dungeon item, that this
    # Region is (in) a dungeon for it to be fillable here.
    def can_fill(self, item):
        is_dungeon_restricted = False
        if item.map or item.compass:
            is_dungeon_restricted = self.world.shuffle_mapcompass == 'dungeon'
        elif item.smallkey:
            is_dungeon_restricted = self.world.shuffle_smallkeys == 'dungeon'
        elif item.bosskey:
            is_dungeon_restricted = self.world.shuffle_bosskeys == 'dungeon'
        elif item.type != 'Event' and item.type != 'Shop' and item.advancement and self.world.one_item_per_dungeon and self.dungeon:
            return self.dungeon.major_items == 0

        if is_dungeon_restricted:
            return self.dungeon and self.dungeon.is_dungeon_item(item) and item.world.id == self.world.id
        return True

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return '%s' % self.name

    '''
Entrance object:
Information about exits of Regions (being Entrances to someplace else)
'''
class Entrance(object):

    def __init__(self, name='', parent=None):
        self.name = name            # Name of the Entrance
        self.parent_region = parent # Region this Entrance is in
        self.connected_region = None # Region this Entrance connects to
        self.target = None          # Only used in Rom.py (???)
        self.addresses = None       # Only used in Rom.py (???)
        self.spot_type = 'Entrance'
        self.recursion_count = 0    # Used to stop infinite loops when calling `can_reach`
        self.vanilla = None         # !!! NEVER USED
        # Function that takes a state and determines if the Entrance is reachable
        self.access_rule = lambda state: True

    # Checks if the Entrance is reachable
    # - Checks `self.access_rule` and if the region this Entrance is in is reachable
    # - Then, if not already in `CollectionState.path`, inserts itself into the path
    def can_reach(self, state):
        if self.access_rule(state) and state.can_reach(self.parent_region):
            return True

        return False

    # Connect this Entrance to the given Region. Also adds this Entrance
    # to the `.entrances` of the given Region.
    # (optional overriding of addresses/target/vanilla)
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

'''
Dungeon object:
Information about a dungeon.

Used to check what kind of items need to be limited to Dungeons
'''
class Dungeon(object):

    def __init__(self, name, regions, boss_key, small_keys, dungeon_items):
        def to_array(obj):
            if obj == None:
                return []
            if isinstance(obj, list):
                return obj
            else:
                return [obj]

        self.name = name
        self.regions = regions
        self.boss_key = to_array(boss_key)
        self.small_keys = to_array(small_keys)
        self.dungeon_items = to_array(dungeon_items)
        self.major_items = 0

    # Returns all Small and Boss keys of this Dungeon
    @property
    def keys(self):
        return (self.small_keys + self.boss_key if self.boss_key else self.keys)

    # Returns all items in this Dungeon (Keys and others)
    @property
    def all_items(self):
        return self.dungeon_items + self.keys

    # Returns the name of the item, if the item is found in `self.all_items`
    def is_dungeon_item(self, item):
        return item.name in [dungeon_item.name for dungeon_item in self.all_items]

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return '%s' % self.name


    '''
Location object:
Information about the location where an item can be or is placed.

!!! Type of Location is only used in Rom.py to differentiate
between handling of certain Locations.

* `.default` is only used at the bottom of Rom.py. unclear
'''
class Location(object):

    def __init__(self, name='', address=None, address2=None, default=None, type='Chest', scene=None, hint='Termina', parent=None):
        self.name = name
        self.parent_region = parent
        self.item = None        # Item filled in this Location
        self.address = address
        self.address2 = address2
        self.default = default
        self.type = type
        self.scene = scene
        self.hint = hint
        self.spot_type = 'Location'
        self.recursion_count = 0 # Used to stop infinite loops when calling `can_reach`
        # Function that takes an item and a state and determines
        # if the item can (always) be filled into this Location.
        self.always_allow = lambda item, state: False
        # Function that takes a state and determines if the Location is reachable
        self.access_rule = lambda state: True
        # Function that takes an item and determines if the item
        # can be filled into this Location
        self.item_rule = lambda item: True

    '''
    Takes a state and item and checks if the item can be filled into this Location.
    - Checks if it is always allowed (`self.always_allow`) or
    - Checks if the item is a dungeon item
        - if so, checks if the Location is in a dungeon
        - if not, uses `self.item_rule` and `self.can_reach` to determine
          whether it's fillable.

    * Check_access can be set to False to ignore the `self.can_reach` rule
      This is done when `has_beaten_game` is True and `beatable_only` is set.
    '''
    def can_fill(self, state, item, check_access=True):
        return self.always_allow(item, self) or (self.parent_region.can_fill(item)
                    and self.item_rule(item)
                    and (not check_access or self.can_reach(state))
                   )


    # Like `can_fill`, but only checks `self.item_rule`
    def can_fill_fast(self, item):
        return self.item_rule(item)

    # Checks to see if the Location is reachable.
    # Uses `self.access_rule` and checks if the Region this Location
    # is in is also reachable.
    def can_reach(self, state):
        if self.access_rule(state) and state.can_reach(self.parent_region):
            return True
        return False

    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return '%s' % self.name

'''
Item Object:
Information about an item.
Examples of these can be found in Items.py (`item_table`)
(`code` and `index` are used in Rom.py for "fix"es
and changing values at `location.address`es)
'''
class Item(object):

    def __init__(self, name='', advancement=False, priority=False, type=None, code=None, index=None, object=None, model=None):
        self.name = name
        self.advancement = advancement
        self.priority = priority
        self.type = type
        self.code = code
        self.index = index
        self.location = None
        self.object = object
        self.model = model
        self.price = None

    def copy(self):
        return Item(self.name, self.advancement, self.priority, self.type, self.code, self.index)

    @property
    def key(self):
        return self.type == 'SmallKey' or self.type == 'BossKey'

    @property
    def smallkey(self):
        return self.type == 'SmallKey'

    @property
    def bosskey(self):
        return self.type == 'BossKey'

    # DEPRECATED DEPRECATED DEPRECATED DEPRECATED
    # `crystal` not used anywhere. I opt for removing this function
    # DEPRECATED DEPRECATED DEPRECATED DEPRECATED
    @property
    def crystal(self):
        return self.type == 'Crystal'

    # Returns True is item is a 'Map'
    @property
    def map(self):
        return self.type == 'Map'

    # Returns True is item is a 'Compass'
    @property
    def compass(self):
        return self.type == 'Compass'

    @property
    def dungeonitem(self):
        return self.type == 'SmallKey' or self.type == 'BossKey' or self.type == 'Map' or self.type == 'Compass'


    def __str__(self):
        return str(self.__unicode__())

    def __unicode__(self):
        return '%s' % self.name

'''
Spoiler object:

'''
class Spoiler(object):

    def __init__(self, world):
        self.world = world
        self.playthrough = {}
        self.locations = {}
        self.metadata = {}
        self.required_locations = []
        self.hints = {}

    def parse_data(self):
        spoiler_locations = [location for location in self.world.get_locations() if location.type != 'Event']
        sort_order = {"Song": 0, "Boss": -1}
        # Sort all items first, then songs, then bosses
        spoiler_locations.sort(key=lambda item: sort_order.get(item.type, 1))
        if self.world.settings.world_count > 1:
            self.locations = {'other locations': OrderedDict([(str(location), "%s [Player %d]" % (str(location.item), location.item.world.id + 1) if location.item is not None else 'Nothing') for location in spoiler_locations])}
        else:
            self.locations = {'other locations': OrderedDict([(str(location), str(location.item) if location.item is not None else 'Nothing') for location in spoiler_locations])}
        self.version = OoTRVersion
        self.settings = self.world.settings

    # Prints the spoiler log to a file.
    def to_file(self, filename):
        self.parse_data()
        with open(filename, 'w') as outfile:
            outfile.write('MM Randomizer Version %s  -  Seed: %s\n\n' % (self.version, self.settings.seed))
            outfile.write('Settings (%s):\n%s' % (self.settings.get_settings_string(), self.settings.get_settings_display()))

            if self.settings.world_count > 1:
                outfile.write('\n\nLocations [World %d]:\n\n' % (self.settings.player_num))
            else:
                outfile.write('\n\nLocations:\n\n')
            outfile.write('\n'.join(['%s: %s' % (location, item) for (location, item) in self.locations['other locations'].items()]))
            outfile.write('\n\nPlaythrough:\n\n')
            outfile.write('\n'.join(['%s: {\n%s\n}' % (sphere_nr, '\n'.join(['  %s: %s' % (location, item) for (location, item) in sphere.items()])) for (sphere_nr, sphere) in self.playthrough.items()]))
            # outfile.write('\n\nPaths:\n\n')
            #
            # path_listings = []
            # for location, path in sorted(self.paths.items()):
            #     path_lines = []
            #     for region, exit in path:
            #         if exit is not None:
            #             path_lines.append("{} -> {}".format(region, exit))
            #         else:
            #             path_lines.append(region)
            #     path_listings.append("{}\n        {}".format(location, "\n   =>   ".join(path_lines)))
            #
            # outfile.write('\n'.join(path_listings))
