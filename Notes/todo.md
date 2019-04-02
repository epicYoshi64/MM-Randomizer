# Todo List

These lists contain the files which have been checked, or still need work.

---

This list contains what has been reviewed and deemed ready for a working MVP:

- Dungeon.py
- DungeonList.py:
    - Adjusted for MM
    - Still depends on {dungeon name}.json files! __Those are not done!__
- Entrance.py
- GuiUtils.py

---

This list contains further work to be done:

- BaseClasses.py:
    - Inspect to see if it can be scrapped (all objects are in their own file now)
    - Remove any object from BaseClasses that are represented correctly in their respective files
    - Remove BaseClasses.py when empty
- Cosmetics.py:
    - Needs double checking of all `patch` functions.
    - `bgm_sequence_ids` need adjusting for MM
    - randomize_/disable_/restore_music functions need double checking for HEX values
- EntranceShuffle.py:
    - Not used by the new OoT randomizer, but kept for potential entrance shuffling in the future.
- Fill.py:
    - Song locations need adjusting to the actual song locations that'll be used.
    - Ice traps aren't a thing in MM, what do?
    - MM doesn't have an equivalent of the Spirit Temple (temple with 2 major items)
      so any logic considering Spirit Temple can probably be removed.
    - Two uses of `world` in `fill_restrictive_fast` are undefined... wtf?
- Gui.py:
    - Most OoT options/tabs are still present in the GUI. Unused options/tabs should be commented out.
      (or removed if not at all applicable to MM)
- HintList.py:
    - `getHintGroup` has a special case for Big Poes, this isn't needed for MM.
    - All hints need to be checked for OoT-specificness (obviously)
- Hints.py:
    - Gossip stones need adjusting for MM.
    - `colorText` needs double checking that the HEX values signify the right colors.
    - `hint_func` and `hint_dist_sets` should be adjusted for MM
    - Trials aren't a thing in MM. Might want to do something with the Masked Kids on the Moon,
      but that will have to wait for much later.
    - `buildBossRewardHints` is still OoT specific. This is probably used for the Altar of Time in OoTR
      and MMR will probably not have a need for any of this (MM just has 4 remains)
    - `buildGanonText` could maybe be changed to `buildMajoraText`? Otherwise unnecessary.
    - `get_raw_text` sets some HEX values, need to be verified to function the same in MM.
      (Some other HEX values in this file as well)
- InitialSave.py:
    - Might need some tweaking since MM is a different ROM than OoT.
- Item.py:
    - `majoritem` might need tweaking if MM uses bombchus in logic.
    - Depends on `item_table` in ItemList.py!
- ItemList.py:
    - All MM items should be added to `item_table` with the relevant settings for each item.
    - All OoT items should be removed (Afterwards! They can help as examples)
- ItemPool.py:
    - Needs __TONS__ of adjusting.
    - All MM items should be placed where they belong.
    - All OoT items should be removed.
    - Dungeons should have their own collection of non-primary items.
    - All lists should be either adjusted for MM or removed if unnecessary.
    - All functions need an MM overhaul. This is a big part of the randomization logic.

- World.py:
    - `update_useless_areas` has some OoT specific logic/names, needs adjusting.
