import argparse
import re
import math
from Cosmetics import get_tunic_color_options, get_tatl_color_options, get_sword_color_options
from LocationList import location_table
import Sounds as sfx


# holds the info for a single setting
class Setting_Info():

    def __init__(self, name, type, bitwidth=0, shared=False, args_params={}, gui_params=None):
        self.name = name # name of the setting, used as a key to retrieve the setting's value everywhere
        self.type = type # type of the setting's value, used to properly convert types in GUI code
        self.bitwidth = bitwidth # number of bits needed to store the setting, used in converting settings to a string
        self.shared = shared # whether or not the setting is one that should be shared, used in converting settings to a string
        self.args_params = args_params # parameters that should be pased to the command line argument parser's add_argument() function
        self.gui_params = gui_params # parameters that the gui uses to build the widget components

        # create the choices parameters from the gui options if applicable
        if gui_params and 'options' in gui_params and 'choices' not in args_params \
                and not ('type' in args_params and callable(args_params['type'])):
            if isinstance(gui_params['options'], list):
                self.args_params['choices'] = list(gui_params['options'])
            elif isinstance(gui_params['options'], dict):
                self.args_params['choices'] = list(gui_params['options'].values())


class Setting_Widget(Setting_Info):

    def __init__(self, name, type, choices, default, args_params={},
            gui_params=None, shared=False):

        assert 'default' not in args_params and 'default' not in gui_params, \
                'Setting {}: default shouldn\'t be defined in '\
                'args_params or in gui_params'.format(name)
        assert 'choices' not in args_params, \
                'Setting {}: choices shouldn\'t be defined in '\
                'args_params'.format(name)
        assert 'options' not in gui_params, \
                'Setting {}: options shouldn\'t be defined in '\
                'gui_params'.format(name)

        if 'type' not in args_params: args_params['type'] = type
        if 'type' not in gui_params:  gui_params['type']  = type

        self.choices = choices
        self.default = default
        args_params['choices'] = list(choices.keys())
        args_params['default'] = default
        gui_params['options']  = {v: k for k, v in choices.items()}
        gui_params['default']  = choices[default]

        super().__init__(name, type, self.calc_bitwidth(choices), shared, args_params, gui_params)


    def calc_bitwidth(self, choices):
        count = len(choices)
        if count > 0:
            return math.ceil(math.log(count, 2))
        return 0


class Checkbutton(Setting_Widget):

    def __init__(self, name, args_help, gui_text, gui_group=None,
            gui_tooltip=None, gui_dependency=None, default=False,
            shared=False):

        choices = {
                True:  'checked',
                False: 'unchecked',
                }
        gui_params = {
                'text':    gui_text,
                'widget': 'Checkbutton',
                }
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, bool, choices, default, args_params, gui_params,
                shared)
        self.args_params['type'] = Checkbutton.parse_bool


    def parse_bool(s):
        if s.lower() in ['yes', 'true', 't', 'y', '1']:
            return True
        elif s.lower() in ['no', 'false', 'f', 'n', '0']:
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')


class Combobox(Setting_Widget):

    def __init__(self, name, choices, default, args_help, gui_text=None,
            gui_group=None, gui_tooltip=None, gui_dependency=None,
            shared=False):

        type = str
        gui_params = {
                'widget': 'Combobox',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


class Scale(Setting_Widget):

    def __init__(self, name, min, max, default, args_help, step=1,
            gui_text=None, gui_group=None, gui_tooltip=None,
            gui_dependency=None, shared=False):

        type = int
        choices = {}
        for i in range(min, max+1, step):
            choices = {**choices, i: str(i)}
        gui_params = {
                'min':     min,
                'max':     max,
                'step':    step,
                'widget': 'Scale',
                }
        if gui_text       is not None: gui_params['text']       = gui_text
        if gui_group      is not None: gui_params['group']      = gui_group
        if gui_tooltip    is not None: gui_params['tooltip']    = gui_tooltip
        if gui_dependency is not None: gui_params['dependency'] = gui_dependency
        args_params = {
                'help':    args_help,
                }

        super().__init__(name, type, choices, default, args_params, gui_params,
                shared)


def parse_custom_tunic_color(s):
    return parse_color(s, get_tunic_color_options())

def parse_custom_tatl_color(s):
    return parse_color(s, get_tatl_color_options())

def parse_custom_sword_color(s):
    return parse_color(s, get_sword_color_options())

def parse_color(s, color_choices):
    if s == 'Custom Color':
        raise argparse.ArgumentTypeError('Specify custom color by using \'Custom (#xxxxxx)\'')
    elif re.match(r'^Custom \(#[A-Fa-f0-9]{6}\)$', s):
        return re.findall(r'[A-Fa-f0-9]{6}', s)[0]
    elif s in color_choices:
        return s
    else:
        raise argparse.ArgumentTypeError('Invalid color specified')

def logic_tricks_entry_tooltip(widget, pos):
    val = widget.get()
    if val in logic_tricks:
        text = val + '\n\n' + logic_tricks[val]['tooltip']
        text = '\n'.join([line.strip() for line in text.splitlines()]).strip()
        return text
    else:
        return None

def logic_tricks_list_tooltip(widget, pos):
    index = widget.index("@%s,%s" % (pos))
    val = widget.get(index)
    if val in logic_tricks:
        text = val + '\n\n' + logic_tricks[val]['tooltip']
        text = '\n'.join([line.strip() for line in text.splitlines()]).strip()
        return text
    else:
        return None


# The 'name' of all options can be used in the '.json' files as booleans
# for item/entrance logic or in Patches.py as flags.

logic_tricks = {
    'CT Tingle Balloon with Sword': {
        'name'    : 'logic_tingle_balloon_jumpslash',
        'tooltip' : '''\
                    Allow Tingle's balloon to be popped from
                    jump-slashing from the tree in North Clock Town.
                    '''},
}


# a list of the possible settings
setting_infos = [
    Setting_Info('check_version', bool, 0, False,
    {
        'help': '''\
                Checks if you are on the latest version
                ''',
        'action': 'store_true'
    }),
    Setting_Info('checked_version', str, 0, False, {
            'default': '',
            'help': 'Supress version warnings if checked_version is less than __version__.'}),
    Setting_Info('rom', str, 0, False, {
            'default': '',
            'help': 'Path to an MM 1.0 rom to use as a base.'}),
    Setting_Info('output_dir', str, 0, False, {
            'default': '',
            'help': 'Path to output directory for rom generation.'}),
    Setting_Info('output_file', str, 0, False, {
            'default': '',
            'help': 'File name base to use for all generated files.'}),
    Setting_Info('seed', str, 0, False, {
            'help': 'Define seed number to generate.'}),
    Setting_Info('patch_file', str, 0, False, {
            'default': '',
            'help': 'Path to a patch file.'}),
    Setting_Info('cosmetics_only', bool, 0, False, {
            'help': 'Patched file will only have cosmetics applied.',
            'action': 'store_true'}),
    Setting_Info('count', int, 0, False, {
            'help': '''\
                    Use to batch generate multiple seeds with same settings.
                    If --seed is provided, it will be used for the first seed, then
                    used to derive the next seed (i.e. generating 10 seeds with
                    --seed given will produce the same 10 (different) roms each
                    time).
                    ''',
            'type': int}),
    Setting_Info('world_count', int, 5, True, {
            'default': 1,
            'help': '''\
                    Use to create a multi-world generation for co-op seeds.
                    World count is the number of players. Warning: Increasing
                    the world count will drastically increase generation time.
                    ''',
            'type': int}, {}),
    Setting_Info('player_num', int, 0, False,
        {
            'default': 1,
            'help': '''\
                    Use to select world to generate when there are multiple worlds.
                    ''',
            'type': int
        },
        # Takes a 'lambda settings:' and None disables the option in the GUI
        {
            'dependency': lambda settings: 1 if settings.compress_rom in ['None', 'Patch'] else None,
        }),
    Checkbutton(
            name           = 'create_spoiler',
            args_help      = '''\
                             Output a Spoiler File
                             ''',
            gui_text       = 'Create Spoiler Log',
            gui_group      = 'rom_tab',
            gui_tooltip    = '''\
                             Enabling this will change the seed.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
        name='create_cosmetics_log',
        args_help='''\
                  Output a Cosmetics Log
                  ''',
        gui_text='Create Cosmetics Log',
        gui_group='rom_tab',
        gui_dependency=lambda settings: False if settings.compress_rom in ['None', 'Patch'] else None,
        default=True,
        shared=False,
    ),
    Setting_Widget(
        name='compress_rom',
        type=str,
        default='True',
        choices={
            'True' : 'Compressed [Stable]',
            'False': 'Uncompressed [Crashes]',
            'Patch': 'Patch File',
            'None' : 'No Output',
        },
        args_params={
            'help': '''\
                    Create a compressed version of the output ROM file.
                    True : Compresses. Improves stability. Will take longer to generate
                    False: Uncompressed. Unstable. Faster generation
                    Patch: Patch file. No ROM, but used to send the patch data
                    None : No ROM Output. Creates spoiler log only
                    ''',
        },
        gui_params={
            'text': 'Output Type',
            'group': 'rom_tab',
            'widget': 'Radiobutton',
            'horizontal': True,
            'tooltip': '''\
                       The first time compressed generation will take a while,
                       but subsequent generations will be quick. It is highly
                       recommended to compress or the game will crash
                       frequently except on real N64 hardware.

                       Patch files are used to send the patched data to other
                       people without sending the ROM file.
                       '''
        },
        shared=False,
    ),
    # A checkbox option
    Checkbutton(
            # Used in .json logic files and Patches.py
            name           = 'start_second_cycle',
            # Text for the CLI
            args_help      = '''\
                             The game starts on the second cycle. Link in human
                             form with the Ocarina of Time.
                             ''',
            # Text next to the checkbox
            gui_text       = 'Start Second Cycle',
            # Which GUI frame this option belongs to
            gui_group      = 'skip',
            # Mouse hover tooltip
            gui_tooltip    = '''\
                             The game starts with Link in human form and with
                             the Ocarina of Time.

                             When this option is off, you will have to find the
                             Ocarina of Time before the 3rd Night. It is guaranteed
                             to be in or around Clock Town.
                             ''',
            # Default state of this option on GUI startup
            default        = True,
            # FIXME: Don't know what this 'shared' option means...
            shared         = True,
            ),
    # A dropdown box
    Combobox(
            name           = 'moon',
            # Which key in 'choices' is chosen on GUI startup
            default        = 'normal',
            # Options in the dropdown
            # 'key': 'Display text'
            choices        = {
                'normal': 'Default Behavior',
                'fast':   'Only need Oath to Order',
                'open':   'Moon always accessible',
                },
            args_help      = '''\
                             Select the requirements to gain access to the Moon.
                             Normal: All four Remains, the Ocarina of Time and the Oath to Order are needed.
                             Fast:   Only the Ocarina of Time and the Oath to Order are required.
                             Open:   Going into the clock on the 3rd Night goes straight to the Moon.
                             ''',
            gui_text       = 'Moon access',
            gui_group      = 'skip',
            gui_tooltip    = '''\
                             'Only need Oath to Order': The Ocarina of Time and Oath to Order are needed.
                             But not the four Remains.

                             'Moon always accessible': The Moon is always accessible by entering the clock
                             on the 3rd Night.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'logic_rules',
            default        = 'glitchless',
            choices        = {
                'trickless':  'Trickless',
                'glitchless': 'Glitchless',
                'none':       'No Logic',
                },
            args_help      = '''\
                             Sets the rules the logic uses to determine accessibility:
                             trickless:   No tricks or glitches required. Advised for casual players.
                             glitchless:  No glitches are required, but may require some minor tricks.
                             none:        All locations are considered available. May not be beatable.
                             ''',
            gui_text       = 'Logic Rules',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Sets the rules the logic uses
                             to determine accessibility.

                             'Trickless': No tricks or glitches are required.
                             Advised for casual players.

                             'Glitchless': No glitches are required,
                             but may require some minor tricks

                             'No Logic': All locations are considered available.
                             May not be beatable.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'all_reachable',
            args_help      = '''\
                             When disabled, only check if the game is beatable with
                             placement. Do not ensure all locations are reachable.
                             ''',
            gui_text       = 'All Locations Reachable',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             When this option is enabled, the randomizer will
                             guarantee that every item is obtainable and every
                             location is reachable.

                             When disabled, only required items and locations
                             to beat the game will be guaranteed reachable.

                             Even when enabled, some locations may still be able
                             to hold the keys needed to reach them.
                             ''',
            default        = True,
            shared         = True,
            ),
    # Checkbutton(
    #         name           = 'bombchus_in_logic',
    #         args_help      = '''\
    #                          Bombchus will be considered in logic. This has a few effects:
    #                          -Back Alley shop will open once you've found Bombchus.
    #                          -It will sell an affordable pack (5 for 60) and never sell out.
    #                          -Bombchus refills cannot be bought until Bombchus have been obtained.
    #                          ''',
    #         gui_text       = 'Bombchus Are Considered in Logic',
    #         gui_group      = 'world',
    #         gui_tooltip    = '''\
    #                          Bombchus are properly considered in logic.

    #                          The first Bombchu pack will always be 20.
    #                          Subsequent packs will be 5 or 10 based on
    #                          how many you have.

    #                          Bombchus can be purchased for 60/99/180
    #                          rupees once they have been found.

    #                          Bombchu Bowling opens with Bombchus.
    #                          Bombchus are available at Kokiri Shop
    #                          and the Bazaar. Bombchu refills cannot
    #                          be bought until Bombchus have been
    #                          obtained.
    #                          ''',
    #         default        = True,
    #         shared         = True,
    #         ),
    Checkbutton(
            name           = 'one_item_per_dungeon',
            args_help      = '''\
                             Each dungeon will have exactly one major item.
                             Does not include dungeon items.
                             ''',
            gui_text       = 'Dungeons Have One Major Item',
            gui_group      = 'world',
            gui_tooltip    = '''\
                             Dungeons have exactly one major
                             item. This naturally makes each
                             dungeon similar in value instead
                             of valued based on chest count.

                             Dungeon items do not count as major items.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'trials_random',
            args_help      = '''\
                             Sets the number of trials that must be cleared
                             to fight Majora.
                             ''',
            gui_text       = 'Random Number of Remains Trials',
            gui_group      = 'skip',
            gui_tooltip    = '''\
                             Sets a random number of trials before fighting Majora.

                             Requiring all four trials means collecting all 20 masks.
                             ''',
            shared         = True,
            ),
    Scale(
            name           = 'trials',
            default        = 4,
            min            = 0,
            max            = 4,
            args_help      = '''\
                             Select how many trials must be cleared to fight Majora.
                             The trials you must complete will be selected randomly.
                             ''',
            gui_group      = 'skip',
            gui_tooltip    = '''\
                             Trials are randomly selected. If hints are
                             enabled, then there will be hints for which
                             trials need to be completed.
                             ''',
            gui_dependency = lambda settings: 0 if settings.trials_random else None,
            shared         = True,
            ),
    Checkbutton(
            name           = 'no_epona_race',
            args_help      = '''\
                             Having Epona's Song will allow you to summon Epona
                             without passing Romani's test on the 1st Day.
                             ''',
            gui_text       = 'Skip Epona Test',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Epona can be summoned with Epona's Song
                             without needing to pass Romani's test.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'fast_chests',
            args_help      = '''\
                             Makes all chests open without the large chest opening cutscene.
                             ''',
            gui_text       = 'Fast Chest Cutscenes',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             All chest animations are fast. If disabled,
                             the animation time is slow for major items.
                             ''',
            default        = True,
            shared         = True,
            ),
    Checkbutton(
            name           = 'free_scarecrow',
            args_help      = '''\
                             Scarecrow's Song is no longer needed to summon Pierre.
                             ''',
            gui_text       = 'Free Scarecrow\'s Song',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Pulling out the Ocarina near a
                             spot at which Pierre can spawn will
                             do so, without needing the song.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'start_with_fast_travel',
            args_help      = '''\
                             Start with the Song of Soaring.
                             ''',
            gui_text       = 'Start with Fast Travel',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with Song of Soaring.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'start_with_rupees',
            args_help      = '''\
                             Start with 99 rupees.
                             ''',
            gui_text       = 'Start with Max Rupees',
            gui_group      = 'convenience',
            gui_tooltip    = '''\
                             Start the game with 99 rupees.
                             ''',
            shared         = True,
            ),
    # Checkbutton(
    #         name           = 'start_with_wallet',
    #         args_help      = '''\
    #                          Start with Tycoon's Wallet.
    #                          ''',
    #         gui_text       = 'Start with Tycoon\'s Wallet',
    #         gui_group      = 'convenience',
    #         gui_tooltip    = '''\
    #                          Start the game with the largest wallet (999 max).
    #                          ''',
    #         shared         = True,
    #         ),
    # Checkbutton(
    #         name           = 'start_with_deku_equipment',
    #         args_help      = '''\
    #                          Start with full Deku sticks, nuts, and a shield.
    #                          ''',
    #         gui_text       = 'Start with Deku Equipment',
    #         gui_group      = 'convenience',
    #         gui_tooltip    = '''\
    #                          Start the game with 10 Deku sticks and 20 Deku nuts.
    #                          Additionally, start the game with a Deku shield equipped,
    #                          unless playing with the Shopsanity setting.
    #                          ''',
    #         shared         = True,
    #         ),
    # Checkbutton(
    #         name           = 'shuffle_kokiri_sword',
    #         args_help      = '''\
    #                          Shuffles the Kokiri Sword into the pool.
    #                          ''',
    #         gui_text       = 'Shuffle Kokiri Sword',
    #         gui_group      = 'shuffle',
    #         gui_tooltip    = '''\
    #                          Enabling this shuffles the Kokiri Sword into the pool.

    #                          This will require extensive use of sticks until the
    #                          sword is found.
    #                          ''',
    #         default        = True,
    #         shared         = True,
    #         ),
    Checkbutton(
            name           = 'shuffle_song_items',
            args_help      = '''\
                             Shuffles the songs into the rest of the item pool so that
                             they can appear at other locations and items can appear at
                             the song locations.
                             ''',
            gui_text       = 'Shuffle Songs with Items',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Enabling this shuffles the songs into the rest of the
                             item pool.

                             This means that song locations can contain other items,
                             and any location can contain a song. Otherwise, songs
                             are only shuffled among themselves.
                             ''',
            default        = True,
            shared         = True,
            ),
    # TODO: Not sure how much overlap this would have with MM
    Combobox(
            name           = 'shopsanity',
            default        = 'off',
            choices        = {
                'off':    'Off',
                '0':      'Shuffled Shops (0 Items)',
                '1':      'Shuffled Shops (1 Items)',
                '2':      'Shuffled Shops (2 Items)',
                '3':      'Shuffled Shops (3 Items)',
                '4':      'Shuffled Shops (4 Items)',
                'random': 'Shuffled Shops (Random)',
                },
            args_help      = '''\
                             Shop contents are randomized. Non-shop items
                             are one time purchases. This setting also
                             changes the item pool to introduce a new Wallet
                             upgrade and more money.
                             off:        Normal Shops*
                             0-4:        Shop contents are shuffled and N non-shop
                                         items are added to every shop. So more
                                         possible item locations.
                             random:     Shop contents are shuffles and each shop
                                         will have a random number of non-shop items
                             ''',
            gui_text       = 'Shopsanity',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             Shop contents are randomized.
                             (X Items): Shops have X random non-shop (Special
                             Deal!) items. They will always be on the left
                             side, and some of the lower value shop items
                             will be replaced to make room for these.

                             (Random): Each shop will have a random number
                             of non-shop items up to a maximum of 4.

                             The non-shop items have no requirements except
                             money, while the normal shop items (such as
                             200/300 rupee tunics) have normal vanilla
                             requirements. This means that, for example,
                             as a child you cannot buy 200/300 rupee
                             tunics, but you can buy non-shop tunics.

                             Non-shop Bombchus will unlock the chu slot
                             in your inventory, which, if Bombchus are in
                             logic, is needed to buy Bombchu refills.
                             Otherwise, the Bomb Bag is required.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_mapcompass',
            default        = 'dungeon',
            choices        = {
                'remove':    'Maps/Compasses: Remove',
                'startwith': 'Maps/Compasses: Start With',
                'dungeon':   'Maps/Compasses: Dungeon Only',
                'keysanity': 'Maps/Compasses: Anywhere'
                },
            args_help      = '''\
                             Sets the Map and Compass placement rules
                             remove:      Maps and Compasses are removed from the world.
                             startwith:   Start with all Maps and Compasses.
                             dungeon:     Maps and Compasses are put in their dungeon.
                             keysanity:   Maps and Compasses can appear anywhere.
                             ''',
            gui_text       = 'Shuffle Dungeon Items',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Maps and Compasses are removed.
                             This will add a small amount of money and
                             refill items to the pool.

                             'Start With': Maps and Compasses are given to
                             you from the start. This will add a small
                             amount of money and refill items to the pool.

                             'Dungeon': Maps and Compasses can only appear
                             in their respective dungeon.

                             'Anywhere': Maps and Compasses can appear
                             anywhere in the world.

                             Setting 'Remove', 'Start With, or 'Anywhere' will
                             add 2 more possible locations to each Dungeons.
                             This makes dungeons more profitable.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'shuffle_smallkeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Small Keys: Remove (Keysy)',
                'dungeon':   'Small Keys: Dungeon Only',
                'keysanity': 'Small Keys: Anywhere (Keysanity)'
                },
            args_help      = '''\
                             Sets the Small Keys placement rules
                             remove:      Small Keys are removed from the world.
                             dungeon:     Small Keys are put in their dungeon.
                             keysanity:   Small Keys can appear anywhere.
                             ''',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Small Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.

                             'Dungeon': Small Keys can only appear in their
                             respective dungeon.

                             'Anywhere': Small Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.

                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            shared=True,
    ),
    Combobox(
            name           = 'shuffle_bosskeys',
            default        = 'dungeon',
            choices        = {
                'remove':    'Boss Keys: Remove (Keysy)',
                'dungeon':   'Boss Keys: Dungeon Only',
                'keysanity': 'Boss Keys: Anywhere (Keysanity)',
                },
            args_help      = '''\
                             Sets the Boss Keys placement rules
                             remove:      Boss Keys are removed from the world.
                             dungeon:     Boss Keys are put in their dungeon.
                             keysanity:   Boss Keys can appear anywhere.
                             ''',
            gui_group      = 'shuffle',
            gui_tooltip    = '''\
                             'Remove': Boss Keys are removed. All locked
                             doors in dungeons will be unlocked. An easier
                             mode.

                             'Dungeon': Boss Keys can only appear in their
                             respective dungeon.

                             'Anywhere': Boss Keys can appear
                             anywhere in the world. A difficult mode since
                             it is more likely to need to enter a dungeon
                             multiple times.

                             Try different combination out, such as:
                             'Small Keys: Dungeon' + 'Boss Keys: Anywhere'
                             for a milder Keysanity experience.
                             ''',
            shared         = True,
            ),
    # TODO: Not sure MM would be impacted if the remains were shuffled
    #       and the knowledge of where which one is would not be worth much, right?
    # Checkbutton(
    #         name           = 'enhance_map_compass',
    #         args_help      = '''\
    #                          Gives the Map and Compass extra functionality.
    #                          Map will tell if a dungeon is vanilla or Master Quest.
    #                          Compass will tell what medallion or stone is within.
    #                          If the maps and compasses are removed then
    #                          the information will be unavailable.
    #                          ''',
    #         gui_text       = 'Maps and Compasses Give Information',
    #         gui_group      = 'shuffle',
    #         gui_tooltip    = '''\
    #                          Gives the Map and Compass extra functionality.
    #                          Map will tell if a dungeon is vanilla or Master Quest.
    #                          Compass will tell what medallion or stone is within.

    #                          'Maps/Compasses: Remove': The dungeon information is
    #                          not available anywhere in the game.

    #                          'Maps/Compasses: Start With': The dungeon information
    #                          is available immediately from the dungeon menu.
    #                          ''',
    #         default        = False,
    #         shared         = True,
    #         ),
    Setting_Info('disabled_locations', list, math.ceil(math.log(len(location_table) + 2, 2)), True,
        {
            'default': [],
            'help': '''\
                    Choose a list of locations that will never be required to beat the game.
                    '''
        },
        {
            'text': 'Exclude Locations',
            'widget': 'SearchBox',
            'group': 'logic_tab',
            'options': list(location_table.keys()),
            'tooltip':'''
                      Prevent locations from being required. Major
                      items can still appear there, however they
                      will never be required to beat the game.
                      '''
        }),
    Setting_Info('allowed_tricks', list, math.ceil(math.log(len(logic_tricks) + 2, 2)), True,
        {
            'default': [],
            'help': '''\
                    Choose a list of allowed logic tricks that the
                    logic may expect to beat the game.
                    '''
        },
        {
            'text': 'Enable Tricks',
            'widget': 'SearchBox',
            'group': 'logic_tab',
            'options': {gui_text: val['name'] for gui_text, val in logic_tricks.items()},
            'entry_tooltip': logic_tricks_entry_tooltip,
            'list_tooltip': logic_tricks_list_tooltip,
        }),
    Combobox(
            name           = 'logic_lens',
            default        = 'all',
            choices        = {
                'all':     'Required Everywhere',
                'darunia': 'Darunia\'s Ghost',
                },
            args_help      = '''\
                             Choose what expects the Lens of Truth:
                             all:     All lens spots expect the lens (except those that did not in the original game)
                             darunia: Only the Darunia's ghost check needs the lens
                             ''',
            gui_group      = 'tricks',
            gui_tooltip    = '''\
                             'Required everywhere': every invisible or
                             fake object will expect you to have the
                             Lens of Truth and Magic.

                             'Darunia's Ghost': The lens is needed to speak to Darunia's Ghost.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'ocarina_songs',
            args_help      = '''\
                             Randomizes the notes needed to play each ocarina song.
                             ''',
            gui_text       = 'Randomize Ocarina Song Notes',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will need to memorize a new set of songs.
                             Can be silly, but difficult. Songs are
                             generally sensible, and warp songs are
                             typically more difficult.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'correct_chest_sizes',
            args_help      = '''\
                             Updates the chest sizes to match their contents.
                             Small Chest = Non-required Item
                             Big Chest = Progression Item
                             ''',
            gui_text       = 'Chest Size Matches Contents',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Chests will be large if they contain a major
                             item and small if they don't. Boss keys will
                             be in gold chests. This allows skipping
                             chests if they are small. However, skipping
                             small chests will mean having low health,
                             ammo, and rupees, so doing so is a risk.
                             ''',
            shared         = True,
            ),
    Checkbutton(
            name           = 'clearer_hints',
            args_help      = '''\
                             The hints provided by Gossip Stones are
                             very direct.
                             ''',
            gui_text       = 'Clearer Hints',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             The hints provided by Gossip Stones will
                             be very direct if this option is enabled.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'hints',
            default        = 'mask',
            choices        = {
                'none':   'No Hints',
                'mask':   'Hints; Need Mask of Truth',
                'always': 'Hints; Need Nothing',
                },
            args_help      = '''\
                             Choose how Gossip Stones behave
                             none:   Default behavior
                             mask:   Have useful hints that are read with the Mask of Truth.
                             always: Have useful hints which can always be read.
                             ''',
            gui_text       = 'Gossip Stones',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Gossip Stones can be made to give hints
                             about where items can be found.

                             The settings can require the Mask of Truth
                             to speak to Gossip Stones, or just turn
                             them on or off.

                             Hints for 'on the way of the hero' are
                             locations that contain items that are
                             required to beat the game.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'hint_dist',
            default        = 'balanced',
            choices        = {
                'useless':     'Useless',
                'balanced':    'Balanced',
                'strong':      'Strong',
                'very_strong': 'Very Strong',
                'tournament':  'Tournament',
                },
            args_help      = '''\
                             Choose how Gossip Stones hints are distributed
                             useless: Nothing but junk hints.
                             balanced: Use a balanced distribution of hint types
                             strong: Use a strong distribution of hint types
                             very_strong: Use a very strong distribution of hint types
                             tournament: Similar to strong but has no variation in hint types
                             ''',
            gui_text       = 'Hint Distribution',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Useless has nothing but junk
                             hints.
                             Strong distribution has some
                             duplicate hints and no junk
                             hints.
                             Very Strong distribution has
                             only very useful hints.
                             Tournament distribution is
                             similar to Strong but with no
                             variation in hint types.
                             ''',
            shared         = True,
            ),
    # This will be low priority, I'd wager.
    Combobox(
            name           = 'text_shuffle',
            default        = 'none',
            choices        = {
                'none':         'No Text Shuffled',
                'except_hints': 'Shuffled except Hints and Keys',
                'complete':     'All Text Shuffled',
                },
            args_help      = '''\
                             Choose how to shuffle the game's messages.
                             none:          Default behavior
                             except_hints:  All non-useful text is shuffled.
                             complete:      All text is shuffled.
                             ''',
            gui_text       = 'Text Shuffle',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Will make things confusing for comedic value.

                             'Shuffled except Hints and Keys': Key texts
                             are not shuffled because in keysanity it is
                             inconvenient to figure out which keys are which
                             without the correct text. Similarly, non-shop
                             items sold in shops will also retain standard
                             text for the purpose of accurate price checks.
                             ''',
            shared         = True,
            ),
    # TODO: I'm pretty sure ice traps aren't a thing in Majora's Mask.
    # Though would be cool if they could be added?
    # Combobox(
    #         name           = 'junk_ice_traps',
    #         default        = 'normal',
    #         choices        = {
    #             'off':       'No Ice Traps',
    #             'normal':    'Normal Ice Traps',
    #             'on':        'Extra Ice Traps',
    #             'mayhem':    'Ice Trap Mayhem',
    #             'onslaught': 'Ice Trap Onslaught',
    #             },
    #         args_help      = '''\
    #                          Choose how Ice Traps will be placed in the junk item pool
    #                          off:       Ice traps are removed.
    #                          normal:    Default behavior; no ice traps in the junk item pool.
    #                          on:        Ice Traps will be placed in the junk item pool.
    #                          mayhem:    All added junk items will be ice traps.
    #                          onslaught: All junk items will be ice traps, even those in the base item pool.
    #                          ''',
    #         gui_text       = 'Ice Traps',
    #         gui_group      = 'other',
    #         gui_tooltip    = '''\
    #                          Off: All Ice Traps are removed.
    #                          Normal: Only Ice Traps from the base item pool
    #                          are placed.
    #                          Extra Ice Traps: Chance to add extra Ice Traps
    #                          when junk items are added to the itempool.
    #                          Ice Trap Mayhem: All added junk items will
    #                          be Ice Traps.
    #                          Ice Trap Onslaught: All junk items will be
    #                          replaced by Ice Traps, even those in the
    #                          base pool.
    #                          ''',
    #         shared         = True,
    #         ),
    Combobox(
            name           = 'item_pool_value',
            default        = 'balanced',
            choices        = {
                'plentiful': 'Plentiful',
                'balanced':  'Balanced',
                'scarce':    'Scarce',
                'minimal':   'Minimal'
                },
            args_help      = '''\
                             Change the item pool for an added challenge.
                             plentiful:      Duplicates most of the major items, making it easier to find progression.
                             balanced:       Default items
                             scarce:         Double defense, double magic, 4 heart containers and 16 heart pieces are removed. Ammo
                                             for each type can only be expanded once and you can only find three Bombchu packs.
                             minimal:        Double defense, double magic, and all health upgrades are removed.
                                             No ammo expansions are available and you can only find one Bombchu pack.
                             ''',
            gui_text       = 'Item Pool',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of bonus items that
                             are available in the game.

                             'Plentiful': Extra major items are added.

                             'Balanced': Original item pool.

                             'Scarce': Some excess items are removed,
                             including health upgrades.

                             'Minimal': Most excess items are removed.
                             ''',
            shared         = True,
            ),
    Combobox(
            name           = 'damage_multiplier',
            default        = 'normal',
            choices        = {
                'half':      'Half',
                'normal':    'Normal',
                'double':    'Double',
                'quadruple': 'Quadruple',
                'ohko':      'One Hit KO',
                },
            args_help      = '''\
                             Change the amount of damage taken.
                             half:           Half damage taken.
                             normal:         Normal damage taken.
                             double:         Double damage taken.
                             quadruple:      Quadruple damage taken.
                             ohko:           Link will die in one hit.
                             ''',
            gui_text       = 'Damage Multiplier',
            gui_group      = 'other',
            gui_tooltip    = '''\
                             Changes the amount of damage taken.

                             'One Hit KO': Link dies in one hit.
                             ''',
            shared         = True,
            ),
    # TODO: Starting on a different day/time might be an ok option?
    # Combobox(
    #         name           = 'starting_tod',
    #         default        = 'default',
    #         choices        = {
    #             'default':       'Default',
    #             'random':        'Random Choice',
    #             'early-morning': 'Early Morning',
    #             'morning':       'Morning',
    #             'noon':          'Noon',
    #             'afternoon':     'Afternoon',
    #             'evening':       'Evening',
    #             'dusk':          'Dusk',
    #             'midnight':      'Midnight',
    #             'witching-hour': 'Witching Hour',
    #             },
    #         args_help      = '''\
    #                          Change up Link's sleep routine.

    #                          Daytime officially starts at 6:30,
    #                          nighttime at 18:00 (6:00 PM).

    #                          Default is 10:00 in the morning.
    #                          The alternatives are multiples of 3 hours.
    #                          ''',
    #         gui_text       = 'Starting Time of Day',
    #         gui_group      = 'other',
    #         gui_tooltip    = '''\
    #                          Change up Link's sleep routine.

    #                          Daytime officially starts at 6:30,
    #                          nighttime at 18:00 (6:00 PM).

    #                          Default is 10:00 in the morning.
    #                          The alternatives are multiples of 3 hours.
    #                          ''',
    #         shared         = True,
    #         ),
    Combobox(
            name           = 'default_targeting',
            default        = 'hold',
            choices        = {
                'hold':   'Hold',
                'switch': 'Switch',
                },
            args_help      = '''\
                             Choose what the default Z-targeting is.
                             ''',
            gui_text       = 'Default Targeting Option',
            gui_group      = 'cosmetic',
            ),
    Combobox(
            name           = 'background_music',
            default        = 'normal',
            choices        = {
                'normal': 'Normal',
                'off':    'No Music',
                'random': 'Random',
                },
            args_help      = '''\
                             Sets the background music behavior
                             normal:      Areas play their normal background music
                             off:         No background music
                             random:      Areas play random background music
                             ''',
            gui_text       = 'Background Music',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                              'No Music': No background music.
                              is played.

                              'Random': Area background music is
                              randomized.
                             ''',
            ),

    Checkbutton(
            name           = 'display_dpad',
            args_help      = '''\
                             Shows an additional HUD element displaying current available options on the DPAD
                             ''',
            gui_text       = 'Display D-Pad HUD',
            gui_group      = 'cosmetic',
            gui_tooltip    = '''\
                             Shows an additional HUD element displaying
                             current available options on the D-Pad.
                             ''',
            default        = True,
            ),
    Setting_Info('kokiri_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Kokiri Tunic. (default: %(default)s)
                    Color:             Make the Kokiri Tunic this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Kokiri Tunic',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    # TODO: is it even possible to set the colors of the other forms
    # to something different than Link's Human colors?
    Setting_Info('deku_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color, # technically not a tunic
            'help': '''\
                    Choose the color for Link's Deku Form. (default: %(default)s)
                    Color:             Make the Deku Form this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Deku Form',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('goron_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color, # technically not a tunic
            'help': '''\
                    Choose the color for Link's Goron Form. (default: %(default)s)
                    Color:             Make the Goron Form this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Goron Form',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('zora_color', str, 0, False,
        {
            'default': 'Kokiri Green',
            'type': parse_custom_tunic_color,
            'help': '''\
                    Choose the color for Link's Zora Form. (default: %(default)s)
                    Color:              Make the Zora Form this color.
                    Random Choice:      Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Zora Form',
            'group': 'tunic_colors',
            'widget': 'Combobox',
            'default': 'Kokiri Green',
            'options': get_tunic_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('tatl_color_default', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_tatl_color,
            'help': '''\
                    Choose the color for Tatl when she is idle. (default: %(default)s)
                    Color:             Make the Tatl this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Tatl Idle',
            'group': 'tatl_colors',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_tatl_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('tatl_color_enemy', str, 0, False,
        {
            'default': 'Yellow',
            'type': parse_custom_tatl_color,
            'help': '''\
                    Choose the color for Tatl when she is targeting an enemy. (default: %(default)s)
                    Color:             Make the Tatl this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Tatl Targeting Enemy',
            'group': 'tatl_colors',
            'widget': 'Combobox',
            'default': 'Yellow',
            'options': get_tatl_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('tatl_color_npc', str, 0, False,
        {
            'default': 'Light Blue',
            'type': parse_custom_tatl_color,
            'help': '''\
                    Choose the color for Tatl when she is targeting an NPC. (default: %(default)s)
                    Color:             Make the Tatl this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Tatl Targeting NPC',
            'group': 'tatl_colors',
            'widget': 'Combobox',
            'default': 'Light Blue',
            'options': get_tatl_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Setting_Info('tatl_color_prop', str, 0, False,
        {
            'default': 'Green',
            'type': parse_custom_tatl_color,
            'help': '''\
                    Choose the color for Tatl when she is targeting a prop. (default: %(default)s)
                    Color:             Make the Tatl this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    '''
        },
        {
            'text': 'Tatl Targeting Prop',
            'group': 'tatl_colors',
            'widget': 'Combobox',
            'default': 'Green',
            'options': get_tatl_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      '''
        }),
    Combobox(
            name           = 'sword_trail_duration',
            default        = 4,
            choices        = {
                    4: 'Default',
                    10: 'Long',
                    15: 'Very Long',
                    20: 'Lightsaber',
                 },
            args_help      = '''\
                             Select the duration of the sword trail
                             ''',
            gui_text       = 'Sword Trail Duration',
            gui_group      = 'sword_trails',
            gui_tooltip    = '''\
                             Select the duration for sword trails.
                             ''',
            ),
    Setting_Info('sword_trail_color_inner', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_sword_color,
            'help': '''\
                    Choose the color for your sword trail when you swing. This controls the inner color. (default: %(default)s)
                    Color:             Make your sword trail this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    Rainbow:           Rainbow sword trails.

                    '''
        },
        {
            'text': 'Inner Color',
            'group': 'sword_trails',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_sword_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      'Rainbow': Rainbow sword trails.
                      '''
        }),
    Setting_Info('sword_trail_color_outer', str, 0, False,
        {
            'default': 'White',
            'type': parse_custom_sword_color,
            'help': '''\
                    Choose the color for your sword trail when you swing. This controls the outer color. (default: %(default)s)
                    Color:             Make your sword trail this color.
                    Random Choice:     Choose a random color from this list of colors.
                    Completely Random: Choose a random color from any color the N64 can draw.
                    Rainbow:           Rainbow sword trails.
                    '''
        },
        {
            'text': 'Outer Color',
            'group': 'sword_trails',
            'widget': 'Combobox',
            'default': 'White',
            'options': get_sword_color_options(),
            'tooltip':'''\
                      'Random Choice': Choose a random
                      color from this list of colors.
                      'Completely Random': Choose a random
                      color from any color the N64 can draw.
                      'Rainbow': Rainbow sword trails.
                      '''
        }),
    Combobox(
            name           = 'sfx_low_hp',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.HP_LOW),
            args_help      = '''\
                             Select the sound effect that loops at low health. (default: %(default)s)
                             Sound:         Replace the sound effect with the chosen sound.
                             Random Choice: Replace the sound effect with a random sound from this list.
                             None:          Eliminate heart beeps.
                             ''',
            gui_text       = 'Low HP',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                             'Random Choice': Choose a random
                             sound from this list.
                             'Default': Beep. Beep. Beep.
                             ''',
            ),
    Combobox(
            name           = 'sfx_tatl_overworld',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_OVERWORLD),
            args_help      = '''\
                             ''',
            gui_text       = 'Tatl Overworld',
            gui_group      = 'npc_sfx',
            ),
    Combobox(
            name           = 'sfx_tatl_enemy',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NAVI_ENEMY),
            args_help      = '''\
                             ''',
            gui_text       = 'Tatl Enemy',
            gui_group      = 'npc_sfx',
            ),
    Combobox(
            name           = 'sfx_menu_cursor',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_CURSOR),
            args_help      = '''\
                             ''',
            gui_text       = 'Menu Cursor',
            gui_group      = 'menu_sfx',
            ),
    Combobox(
            name           = 'sfx_menu_select',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.MENU_SELECT),
            args_help      = '''\
                             ''',
            gui_text       = 'Menu Select',
            gui_group      = 'menu_sfx',
            ),
    Combobox(
            name           = 'sfx_horse_neigh',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.HORSE_NEIGH),
            args_help      = '''\
                             ''',
            gui_text       = 'Horse',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_nightfall',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.NIGHTFALL),
            args_help      = '''\
                             ''',
            gui_text       = 'Nightfall',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_hover_boots',
            default        = 'default',
            choices        = sfx.get_setting_choices(sfx.SoundHooks.BOOTS_HOVER),
            args_help      = '''\
                             ''',
            gui_text       = 'Hover Boots',
            gui_group      = 'sfx',
            ),
    Combobox(
            name           = 'sfx_ocarina',
            default        = 'ocarina',
            choices        = {
                'ocarina':       'Default',
                'random-choice': 'Random Choice',
                'flute':         'Flute',
                'harp':          'Harp',
                'whistle':       'Whistle',
                'malon':         'Malon',
                'grind-organ':   'Grind Organ',
                },
            args_help      = '''\
                             Change the sound of the ocarina.

                             default: ocarina
                             ''',
            gui_text       = 'Ocarina',
            gui_group      = 'sfx',
            gui_tooltip    = '''\
                             Change the sound of the ocarina.
                             ''',
            ),
]

si_dict = {si.name: si for si in setting_infos}
def get_setting_info(name):
    return si_dict[name]
