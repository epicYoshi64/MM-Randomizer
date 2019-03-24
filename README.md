# MMRandomizer

This is a randomizer for _The Legend of Zelda: Majora's Mask_ for the Nintendo 64.

## This program is currently __*not functional*__.

If you'd like to help out in any way, feel free to join the discord where we are coordinating things: https://discord.gg/2xpZYQq or submit a pull request, and somebody will take a look at it.

The rest of this README is a direct copy from the OoT Randomizer (v4.0) on which the majority of this code is based. Everything in this file is subject to change at any time, and makes no promises or commitments. Again, this is just a direct copy which will be adjusted when we get closer to a first release.

---

* [Installation](#installation)
* [General Description](#general-description)
  * [Plans for the future](#future-plans)
  * [Getting Stuck](#getting-stuck)
* [Quirks to Know](#quirks-to-know)
* [Settings](#settings)
* [Known Issues](#known-issues)
* [Changelog](#changelog)

# Installation

Clone this repository and then run ```MMRandomizer.py``` as a command line tool. Or, alternatively, run ```Gui.py``` for a simple graphical user interface. Both require Python 3.6+.

 <!-- For releases, a Windows standalone executable is available for users without Python 3. -->

This randomizer requires The Legend of Zelda: Majora's Mask version 1.0. This will first support the NTSC-U version before eventually maybe supporting NTSC-J and NTSC-E. Upon first being run, the randomizer will automatically create a decompressed version of this ROM that can be used for input for slightly faster seed generation times. Please be sure your input ROM filename is either a .n64 or .z64 file. For users playing via any means other than on real N64 hardware, the use of the "Compress patched ROM" flag is strongly encouraged as uncompressed ROMs are impossible to inject for the Virtual Console and have random crashing problems on all emulators.

For general use, the recommended emulators are Bizhawk and Mupen64plus. If you want to play on Project 64 for whatever reason, you can but you will need to set the rando to use 8 MB of RAM. For the eventual release, there will probably still be suspected crashing issues specifically with Project 64. I cannot emphasize enough that it is a discouraged emulator to use.

# General Description

This program takes _The Legend of Zelda: Majora's Mask_ and randomizes the locations of the items for a new, more dynamic play experience.
Proper logic is used to ensure every seed is possible to complete without the use of glitches and will be safe from the possibility of softlocks
with any possible usage of keys in dungeons.

The randomizer will ensure a glitchless path through the seed will exist, but the randomizer will not prevent the use of glitches for those players who enjoy that sort of thing though we offer no guarantees that all glitches will have identical behavior to the original game. Glitchless can still mean that clever or unintuitive strategies may be required.

The items that randomize firstly are all items within chests, and maybe items given as rewards by NPCs. All dungeons will always have the same number of Maps, Compasses, Small Keys, and Boss Keys they had in the original game, but which chests within those dungeons have those things is random. The item pool will contain all Stray Fairies that are placed in chests, eventually/hopefully. Stray Fairies not found within a chest will be shuffled among themselves, if possible.

## Plans for the future

Certain types of items will be "progressive", meaning that no matter what order the player encounters these items they will function as a series of upgrades.
The following item types will be progressive chains:

-Bomb Bag to Big Bomb Bag to Biggest Bomb Bag
-Bow to Big Quiver to Biggest Quiver
-Adult Wallet to Giant's Wallet
-Magic Meter to Double Magic

The Ocarina songs will be shuffled in a pool amongst themselves, and each learn spot will still have the original conditions it has always had. These conditions may not have all been obvious, but here are some high points (later).

Freestanding Pieces of Heart (those not in chests or given directly by NPCs) are not randomized yet, but the logic will pretend they are until any part of this actually hacks the ROM.

As this randomizer progresses, the aim will be to add options to remove the most time wasting of cutscenes.

## Getting Stuck

With a game the size of _Majora's Mask_, it's quite easy for new Randomizer players to get stuck in certain situations with no apparent path to progressing. Before reporting an issue, please make sure to check out *our Logic wiki page* (__UNDER CONSTRUCTION__).

---

# Quirks to Know

This will expand as this develops (obviously)

- In the randomizer, possessing the Bomb Bag is the requirement to get bomb drops, buy bombs or Bombchus.

# Settings

## Moon Entry

This determines the condition under which the moon meadows will open for exploration. Entry will occur upon playing Oath to Order on the top of the Clock Tower.

### Open

Oath to Order is all that is required to enter the moon meadows.

### Vanilla

The moon meadows are reached under the same conditions they were in the original game, possession of all four boss remains.

### All Masks

Entering the moon meadows requires all 20 non transformation masks to be in the player's possession.

---

## Give Ocarina of Time

Skip the entire first cycle of the game up until obtaining the Ocarina of Time.

---

## Initial Form

Change which Link you start the game as. Except for when starting as human Link, learning the Song of Healing will award you the mask of the form you started in and return you to your human form. Note that changing to another transformation mask before finding the Song of Healing will leave you unable to return to this form. This by extension means that the Song of Healing will never be found in a location which requires you to use your initial form to obtain.

### Vanilla

Everything proceeds as it did in the original game. Link gets bullied by Skull Kid and human Link chases his horse until being transformed a Deku to do the rest.

### Human

Opening plays as usual until Link confronts the Skull Kid, and Skull Kid's magic has no effect, and then you spawn in the Clock Tower as human Link.

### Deku

The game now starts with the Deku consuming ritual cutscene and you proceed as a Deku child.

### Goron

It might be a future consideration to find a way to spawn at Darmani's Grave, however, for now we'll stick with the more realistic situation of Goron Link spawning in the Clock Tower.

### Zora

Similarly, we could have Zora Link start in Great Bay, but we'll stick with spawning in the Clock Tower.

### Randomize

Game will start as any of the four Links inside the Clock Tower.

---

## Stray Fairy Shuffle

There are five Great Fairy Fountains scattered across Termina. These five fountains are randomized amongst themselves. The two that give variations on the Magic Meter in vanilla are modelled as progressives; the first Great Fairy the player activates will give a Magic Meter while the second will give the Double Magic upgrade. With the Great Fairy Sword being in the pool, one of the Great Fairies will hold an item as a reward. Talking to the Great Fairy with the Great Fairy Mask will reveal which reward is given by that Great Fairy.

Stray Fairies can be found floating around in each of the four main dungeons. There are 15 found in each of these dungeons which can be returned to the nearby Great Fairy Fountain for a prize. Which prize is awarded at a given fountain is randomized, but stray fairies must be returned to their appropriate fountain to claim the reward.

There are two different types of stray fairies, which can each be randomized differently. Freestanding Stray Fairies will always stay in the location they were found in their dungeon, but which fountain they belong to can be different. Chest Stray Fairies however can be placed in any chest in the game (I hope. No part of this theory has been tested, but Stone Tower will get a whole lot more interesting if this works). There's going to tweaking since with this system, I've already run into corner cases that break the system

### Home Dungeon

All Stray Fairies will be from the same fountain that shares its name with the dungeon it's found in.

### Random Dungeon

All Stray Fairies within a particular dungeon will belong to the same fairy fountain.

### Random

Any Freestanding Stray Fairy can be found in any dungeon.

---

## Chest Stray Fairy Locations

### All in Dungeon

Every Chest Stray Fairy will be found within dungeons according to the conditions for Stray Fairy Shuffle.

### Partially Randomized

Specify a minimum number of Stray Fairies to be randomized in with the non dungeon chests. This number might be exceeded if Random Dungeon is selected for Stray Fairy Shuffle.

### Anywhere

Can be found in any chest in the game (barring technical limitations)

### Randomize Clock Town Stray Fairy

It might be possible to change which type of Stray Fairy is found in Clock Town. This could add a Freestanding Stray Fairy to the pool (Possibly two).

---

## Owl Statue Shuffle

If set, the warp points opened up by activating an owl statue will be randomized among themselves. For example, you could activate the owl statue in Clock Town, and using the Song of Soaring would be able to take you to Stone Tower since the Clock Town owl statue randomized to the Stone Tower warp point.

### Include Hidden Owl

If set along with Owl Statue Shuffle, this will make one of the warp locations hidden behind the aesthetic owl statue in West Clock Town. This means that one owl statue will not add a warp point to the list. Be careful, if this happens and you see no warp points on your map after playing the Song of Soaring, press A to select whatever the game selected for you. This is called Index Warping and if this feature ever gets off the ground, I might put the table in here. This wording is not optimal or accurate, and I'll fix it later.

---

## Gossip Stone Hints with Mask of Truth

If set, the Gossip Stones scattered across Termina will have various hints informing the player of which items are in various inconvenient locations. The Stone of Agony is the condition to be able to talk to the Gossip Stones in this mode instead of the Mask of Truth out of mercy to the player.

The locations we regarded as the most generally inconvenient for all medallions play will always have hints, those hints will appear in two places, and the logic will guarantee access to the Mask of Truth before those places must be checked.

There will be other hints that only exist once for other somewhat inconvenient places for which there is no guarantee of Mask of Truth access, and there will be other sorts of remarks from the Gossip Stones in the hint pool that may bring a smile to your face but will not provide you with unique information for your quest.

# Boring Settings

## Create Spoiler Log

Output a Spoiler File.

## Do not Create Patched Rom

If set, will not produce a patched rom as output. Useful in conjunction with the spoiler log option to batch generate spoilers for statistical analysis.

## Compress patched Rom

If set, the randomizer will additionally output a compressed ROM using Grant Man's bundled compressor. This compressor is the fastest compressor out there and tuned specifically for this game, but in order to achieve its incredibly high speed, it does utilize every last bit of CPU your computer will give it so your computer will slow to a crawl otherwise during the couple of minutes this will take.

## Place Dungeon Items

Dungeons will have the same internal layout as they did in the original The Legend of Zelda: Majora's Mask.

## Only Ensure Seed Beatable

If set, will only ensure that Majora's Mask can be defeated, but not necessarily that all locations are reachable.

# Known Issues

Sadly for this 0.0.1 README design draft, we have plenty of ideas, so problems have yet to be identified. We do have a grievance list:

* We don't know much N64 assembly level stuff, so making this playable is waaaaaaay further down the line. We intend to do most of this by testing spoiler logs until all the logic is in place. Once that monster is taken care of, then we'll get to the juicy payload. That said, if anybody wants to help out, let me (epicYoshi64) know. I can be found around Twitch and Discord pretty frequently under this name.
* The Title Deeds and Kafei fetch quest items are bad, and unless we find a way to hack the menu, they may not get randomized even though they have some of the best potential. The fact that these items will overwrite each other is a problem which will be tackled further down the line.
* Thief Bird worst bird
* Gossip Stones will be counted, and the hints will be rewritten to make sense to Majora's Mask. Couple's Mask and the Skulltula Houses will probably be definite hints.


# Command Line Options

## __*These are all bogus and will definitely change in the future*__

There will be more of these, but this fork is nowhere near prepared enough to figure out how to line up command args.

```
-h, --help
```

Show the help message and exit.

```
--check_version
```

Check for the latest version number online (default: False)

```
--rom ROM
```

Path to a The Legend of Zelda: Majora's Mask NTSC-US v1.0 ROM. (default: ZELOOTROMDEC.z64)

```
--output_dir OUTPUT_DIR
```

Path to output directory for rom generation.

```
--seed SEED
```

Define seed number to generate. (default: None)

```
--count COUNT
```

Set the count option (default: None)

```
--nodungeonitems
```

Select how much of Gerudo Fortress is required. (default: normal)

```
--bridge [{medallions,vanilla,dungeons,open}]
```

Select the condition to spawn the Rainbow Bridge to Ganon's Castle. (default: medallions)

```
--all_reachable
```

Enables the "Only Ensure Seed Beatable" option (default: False)

```
--all_reachable
```

Gossip Stones provide helpful hints about which items are in inconvenient locations if the Mask of Truth is in the player's inventory. (default: False)

```
--bombchus_in_logic
```

Changes how the logic considers Bombchus and other Bombchu related mechanics (default: False)

```
--one_item_per_dungeon
```

Each dungeon will have exactly one major item. (default: False)

```
--trials_random
```

Sets the number of trials that must be cleared in Ganon's Castle to a random value (default: False)

```
--trials [{0,1,2,3,4,5,6}]
```

Sets the number of trials that must be cleared in Ganon's Castle (default: 6)

```
--no_escape_sequence
```

Removes the tower collapse sequence after defeating Ganondorf (default: False)

```
--no_guard_stealth
```

Removes the guard evasion sequence in Hyrule Castle (default: False)

```
--no_epona_race
```

Removes the need to race Ingo to acquire Epona (default: False)

```
--fast_chests
```

Causes all chests to open with a fast animation (default: False)

```
--big_poe_count_random
```

Sets the number of Big Poes that must be sold to the vendor for an item to a random value (default: False)

```
--big_poe_count [{1,2,3,4,5,6,7,8,9,10}]
```

Sets the number of Big Poes that must be sold to the vendor for an item (default: 10)

```
--free_scarecrow
```

Start the game with the Scarecrow's Song activated and Pierre possible for the adult to summon (default: False)

```
--scarecrow_song [SCARECROW_SONG]
```

Set Scarecrow's Song if --free_scarecrow is used. Valid notes: A, U, L, R, D (default: DAAAAAAA)

```
--shuffle_kokiri_sword
```

Include the Kokiri Sword as a randomized item (default: False)

```
--shuffle_weird_egg
```

Include the Weird Egg as a randomized item (default: False)

```
--shuffle_ocarinas
```

Include the two ocarinas as randomized items (default: False)

```
--shuffle_song_items
```

Treat the ocarina songs as normal items and shuffle them into the general item pool (default: False)

```
--shuffle_gerudo_card
```

Include the Gerudo Card to access Gerudo Training Grounds as a randomized item (default: False)

```
--shuffle_scrubs
```

Include all Deku Scrub Salesmen as randomized item locations (default: False)

```
--shopsanity [{off,0,1,2,3,4,random}]
```

Randomize shop items and add the chosen number of items from the general item pool to shop inventories (default: off)

```
--shuffle_mapcompass [{remove,dungeon,keysanity}]
```

Choose the locations Maps and Compasses can be found (default: dungeon)

```
--shuffle_smallkeys [{remove,dungeon,keysanity}]
```

Choose the locations Small Keys can be found (default: dungeon)

```
--shuffle_bosskeys [{remove,dungeon,keysanity}]
```

Choose the locations Boss Keys can be found (default: dungeon)

```
--enhance_map_compass
```

Change the functionality of the Map and Compass to give information about their dungeons. Requires --shuffle_mappcompass keysanity (default: False)

```
--unlocked_ganondorf
```

Remove the Boss Key door leading to Ganondorf (default: False)

```
--tokensanity [{off,dungeons,all}]
```

Include the chosen Gold Skulltulla Token locations in the item shuffle (default: off)

```
--quest [{vanilla,master,mixed}]
```

Choose the internal layout of the dungeons (default: vanilla)

```
--logic_skulltulas [{0,10,20,30,40,50}]
```

Choose the maximum number of Gold Skulltulla Tokens that could be required (default: 50)

```
--logic_no_night_tokens_without_suns_song
```

Change logic to expect Sun's Song to defeat nighttime Gold Skulltullas (default: False)

```
--logic_no_big_poes
```

Prevent the Big Poe vendor from having a required item (default: False)

```
--logic_no_child_fishing
```

Prevent the prize from fishing as a child from being a required item (default: False)

```
--logic_no_adult_fishing
```

Prevent the prize from fishing as an adult from being a required item (default: False)

```
--logic_no_trade_skull_mask
```

Prevent the item obtained by showing the Skull Mask at the Deku Theater from being a required item (default: False)

```
--logic_no_trade_mask_of_truth
```

Prevent the item obtained by showing the Mask of Truth at the Deku Theater from being a required item (default: False)

```
--logic_no_1500_archery
```

Prevent the item obtained by scoring 1500 points at horseback archery from being a required item (default: False)

```
--logic_no_memory_game
```

Prevent the item obtained by completing the ocarina memory game in the Lost Woods from being a required item (default: False)

```
--logic_no_second_dampe_race
```

Prevent the prize won by finishing the second Dampe race in under 1 minute from being a required item (default: False)

```
--logic_no_trade_biggoron
```

Prevent the item obtained by showing the Claim Check to Biggoron from being a required item (default: False)

```
--logic_earliest_adult_trade [{pocket_egg,pocket_cucco,cojiro,odd_mushroom,poachers_saw,broken_sword,prescription,eyeball_frog,eyedrops,claim_check}]
```

Set the earliest item in the adult trade sequence that can be found in the item pool (default: pocket_egg)

```
--logic_latest_adult_trade [{pocket_egg,pocket_cucco,cojiro,odd_mushroom,poachers_saw,broken_sword,prescription,eyeball_frog,eyedrops,claim_check}]
```

Set the latest item in the adult trade sequence that can be found in the item pool (default: claim_check)

```
--logic_tricks
```

Enable the logic to consider a large number of minor tricks (default: False)

```
--logic_man_on_roof
```

Enable the logic to consider the trick to reach the man on the roof in Kakariko Village with a sidehop from the tower (default: False)

```
--logic_child_deadhand
```

Enable the logic to consider the child defeating Deadhand with only Deku Sticks (default: False)

```
--logic_dc_jump
```

Enable the logic to consider the trick to bypass the second Lizalfos fight room in Dodongo's Cavern as an adult with a simple jump (default: False)

```
--logic_windmill_poh
```

Enable the logic to consider the trick to reach the Piece of Heart in the windmill as an adult with nothing (default: False)

```
--logic_crater_bean_poh_with_hovers
```

Enable the logic to consider the trick to reach the Piece of Heart on the volcano in Death Mountain Crater with Hover Boots (default: False)

```
--logic_zora_with_cucco
```

Enable the logic to consider the trick to enter Zora's Domain as a child using a Cucco instead of playing Zelda's Lullaby (default: False)

```
--logic_zora_with_hovers
```

Enable the logic to consider the trick to enter Zora's Domain as an adult using Hover Boots instead of playing Zelda's Lullaby (default: False)

```
--logic_fewer_tunic_requirements
```

Reduce the number of locations for which the logic expects a tunic upgrade (default: False)

```
--logic_lens [{chest,chest-wasteland,all}]
```

Set which hidden objects the logic expects the Lens of Truth to be used on (default: all)

```
--ocarina_songs
```

Randomize the particular notes that must be played for each of the 12 standard ocarina songs (default: False)

```
--correct_chest_sizes
```

Set chest sizes based on contents (default: False)

```
--clearer_hints
```

Reword hints to be incredibly direct (default: False)

```
--hints [{none,mask,agony,always}]
```

Enable hints from Gossip Stones and select the condition to read them (default: agony)

```
--text_shuffle [{none,except_hints,complete}]
```

Shuffle the chosen text randomly (default: none)

```
--difficulty [{normal,hard,very_hard,ohko}]
```

Alter the item pool to increase difficulty. The ohko option also causes Link to die in one hit. (default: normal)

```
--default_targeting [{hold,switch}]
```

Set the default Z-targeting setting. It can still be changed in the game's options menu. (default: hold)

```
--background_music [{normal,off,random}]
```

Choose whether the game's background music will be left alone, disabled, or shuffled randomly. (default: normal)

```
--kokiricolor [{'Random Choice', 'Completely Random', 'Kokiri Green', 'Goron Red', 'Zora Blue', 'Black', 'White', 'Purple', 'Yellow', 'Orange', 'Pink', 'Gray', 'Brown', 'Gold', 'Silver', 'Beige', 'Teal', 'Royal Blue', 'Sonic Blue', 'Blood Red', 'Blood Orange', 'NES Green', 'Dark Green', 'Lumen'}]
```

Select the color of Link's Kokiri Tunic. (default: Kokiri Green)

```
--goroncolor [{'Random Choice', 'Completely Random', 'Kokiri Green', 'Goron Red', 'Zora Blue', 'Black', 'White', 'Purple', 'Yellow', 'Orange', 'Pink', 'Gray', 'Brown', 'Gold', 'Silver', 'Beige', 'Teal', 'Royal Blue', 'Sonic Blue', 'Blood Red', 'Blood Orange', 'NES Green', 'Dark Green', 'Lumen'}]
```

Select the color of Link's Goron Tunic. (default: Goron Red)

```
--zoracolor [{'Random Choice', 'Completely Random', 'Kokiri Green', 'Goron Red', 'Zora Blue', 'Black', 'White', 'Purple', 'Yellow', 'Orange', 'Pink', 'Gray', 'Brown', 'Gold', 'Silver', 'Beige', 'Teal', 'Royal Blue', 'Sonic Blue', 'Blood Red', 'Blood Orange', 'NES Green', 'Dark Green', 'Lumen'}]
```

Select the color of Link's Zora Tunic. (default: Zora Blue)

```
--tatlcolordefault [{'Random Choice', 'Completely Random', 'Gold', 'White', 'Green', 'Light Blue', 'Yellow', 'Red', 'Magenta', 'Black', 'Tatl', 'Tael', 'Fi', 'Ciela', 'Epona', 'Ezlo', 'King of Red Lions', 'Linebeck', 'Loftwing', 'Midna', 'Phantom Zelda'}]
```

Select the color of Tatl in idle. (default: White)

```
--tatlcolorenemy [{'Random Choice', 'Completely Random', 'Gold', 'White', 'Green', 'Light Blue', 'Yellow', 'Red', 'Magenta', 'Black', 'Tatl', 'Tael', 'Fi', 'Ciela', 'Epona', 'Ezlo', 'King of Red Lions', 'Linebeck', 'Loftwing', 'Midna', 'Phantom Zelda'}]
```

Select the color of Tatl when she is targeting an enemy. (default: Yellow)

```
--tatlcolornpc [{'Random Choice', 'Completely Random', 'Gold', 'White', 'Green', 'Light Blue', 'Yellow', 'Red', 'Magenta', 'Black', 'Tatl', 'Tael', 'Fi', 'Ciela', 'Epona', 'Ezlo', 'King of Red Lions', 'Linebeck', 'Loftwing', 'Midna', 'Phantom Zelda'}]
```

Select the color of Tatl when she is targeting an NPC. (default: Light Blue)

```
--tatlcolorprop [{'Random Choice', 'Completely Random', 'Gold', 'White', 'Green', 'Light Blue', 'Yellow', 'Red', 'Magenta', 'Black', 'Tatl', 'Tael', 'Fi', 'Ciela', 'Epona', 'Ezlo', 'King of Red Lions', 'Linebeck', 'Loftwing', 'Midna', 'Phantom Zelda'}]
```

Select the color of Tatl when she is targeting a prop. (default: Green)

```
--tatlsfxoverworld [{Default,Notification,Rupee,Timer,Tamborine,Recovery Heart,Carrot Refill,Tatl - Hey!,Tatl - Random,Zelda - Gasp,Cluck,Mweep!,Random,None}]
```

Select the sound effect that plays when Tatl wishes to speak with the player. (default: Default)

```
--tatlsfxenemytarget [{Default,Notification,Rupee,Timer,Tamborine,Recovery Heart,Carrot Refill,Tatl - Hey!,Tatl - Random,Zelda - Gasp,Cluck,Mweep!,Random,None}]
```

Select the sound effect that plays when Tatl targets an enemy. (default: Default)

```
--healthSFX [{'Default', 'Softer Beep', 'Rupee', 'Timer', 'Tamborine', 'Recovery Heart', 'Carrot Refill', 'Tatl - Hey!', 'Zelda - Gasp', 'Cluck', 'Mweep!', 'Random', 'None'}]
```

Select the sound effect that loops at low health. (default: Default)

```
--gui
```

Open the graphical user interface. Preloads selections with set command line parameters.

```
--loglevel [{error,info,warning,debug}]
```

Select level of logging for output. (default: info)

```
--settings_string SETTINGS_STRING
```

Enter a settings string that will encode and override most individual settings.


# Changelog

## 0.0.1

* _TestRunner_'s OoT-Randomizer fork has been merged into the partially worked on fork of _epicYoshi64_.
* Most files are still OoT-specific and will have to be adjusted.
* All changes for Majora's Mask in the existing _epicYoshi65_ fork have been preserved as much as possible. In case of major changes, the old file has been appended with _.backup_ to indicate it still needs processing into the new structure. Minor changes are already integrated as much as possible. Search for `TODO` in the code to find spots that still need adjusting/integrating.