"""
#
# baseline.py
#
# Copyright (c) 2020 Antoine Emil Zambelli. MIT License.
#
"""


import sc2reader
import pandas as pd

## tkinter file dialog version.
# import os
# from tkinter.filedialog import askopenfilename


# root_fp = os.environ['USERPROFILE']  # To get user name.
# sc2_root_fp = os.path.join(root_fp, 'Documents/StarCraft II/Accounts')  # Drill-down.

# replay_fp = askopenfilename(initialdir=sc2_root_fp)  # Open dialog to select replay.

# replay = sc2reader.load_replay(replay_fp)  # Load it.

replay = sc2reader.load_replay(
    '/path/to/Documents/StarCraft II/Accounts/xxxx/yyyy/Replays/Multiplayer/the_replay.SC2Replay'
)

NON_PROD_BUILDINGS = [
    'Armory',
    'Bunker',
    'EngineeringBay',
    'Refinery',
    'SupplyDepot',
    'TechLab',
    'Turret',
]  # list of non-production buildings to exclude - has to be hardcoded.

ADD_ONS = [
    'TechLab'
]  # list add-on buildings to account for prod time - has to be hardcoded.

UNITS = {
    'Hellion': {'time': 21, 'parent': 'Factory'},
    'Marine': {'time': 18, 'parent': 'Barracks'},
    'SCV': {'time': 12, 'parent': 'Command'},
    'Thor': {'time': 43, 'parent': 'Factory'}
}  # dict of units with build times and parent building - has to be hardcoded.

PLAYER = 'Genie'  # Player name, could easily loop over unique player names.

# Get all buildings that belong to player and can produce (hardcoded).
buildings = {}
for e in replay.events:
    if e.name == 'UnitDoneEvent' and e.second > 0:
        if e.unit.owner.name == PLAYER and \
           all(ss not in e.unit._type_class.name for ss in NON_PROD_BUILDINGS):

            buildings[e.unit] = {
                't_0': e.second,  # Building creation time.
                'id': e.unit_id,  # Unique id for building.
                't_build': 0,  # Time spent producing (in seconds).
                'name': e.unit._type_class.name  # Name.
            }

# Get buildings location - filter for player.
for e in replay.events:
    if e.name == 'UnitInitEvent' and e.second > 0:
        if e.unit in buildings:
            buildings[e.unit]['loc'] = e.location

# Track add-on construction like it was a unit.
for e in replay.events:
    if e.name == 'UnitInitEvent' and e.second > 0:
        if e.unit.owner.name == PLAYER and \
           any(ss in e.unit._type_class.name for ss in ADD_ONS):

            # Match add-on to nearest building.
            best_match = min(
                buildings.items(),
                key=lambda x: (x[1]['loc'][0] - e.location[0]) ** 2 + (x[1]['loc'][1] - e.location[1]) ** 2
            )[0]

            # Add build time as per UnitDoneEvent of that unit.
            delta_t = next(
                ee.second for ee in replay.events if ee.name == 'UnitDoneEvent' and ee.unit == e.unit
            ) - e.second
            buildings[best_match]['t_build'] = buildings[best_match]['t_build'] + delta_t

# Track unit creation - ignore MULEs.
for e in replay.events:
    if e.name == 'UnitBornEvent' and e.second > 0:
        if e.unit.owner.name == PLAYER and \
           any(ss in e.unit._type_class.name for ss in UNITS):

            # Match unit to nearest building.
            unit_parent_buildings = next(
                v['parent'] for (k, v) in UNITS.items() if k in e.unit._type_class.name
            )  # hardcoded parent building for a unit.

            best_match = sorted(
                buildings.items(),
                key=lambda x: (x[1]['loc'][0] - e.location[0]) ** 2 + (x[1]['loc'][1] - e.location[1]) ** 2
            )  # sorted list of buildings by distance.
            best_match = next(
                k for k, v in best_match if unit_parent_buildings in v['name']
            )  # item selected based on closest parent.

            # Add build time as per hardcoded time of that unit.
            buildings[best_match]['t_build'] = buildings[best_match]['t_build'] + next(
                v['time'] for (k, v) in UNITS.items() if k in e.unit._type_class.name
            )

# Get game end time in seconds - from first player leave event.
for e in replay.events:
    if e.name == 'PlayerLeaveEvent' and e.second > 0:
        t_final = e.second
        break

# Populate prod_time info.
for b in buildings:
    buildings[b]['prod_time'] = (t_final - buildings[b]['t_0']) - buildings[b]['t_build']
    buildings[b]['prod_time_perc'] = buildings[b]['prod_time'] / (t_final - buildings[b]['t_0'])

print(buildings)
print()

df = pd.DataFrame.from_dict(buildings, orient='index')[['t_0', 'prod_time', 'prod_time_perc', 'name']]
df['available_time'] = t_final - df['t_0']
df = df.groupby('name').agg({'prod_time': 'sum', 'available_time': 'sum'})
df['prod_time_perc'] = df['prod_time'] / df['available_time']
df = df.sort_values(by='prod_time_perc')
df['prod_time_perc'] = df['prod_time_perc'].apply(lambda x: '{:.2f}%'.format(100 * x))

print('Sums of time across building types.')
print(df)

# Obvious improvement (OI):
# 1) don't just add build times, store them with their init time so
# we can build a graph over time: ie, after 7:00 you lost focus and stopped using Factory.
# For this, likely want to store events in a timeseries df with a 'parent' column.
# After that, we can window(), rolling() and cumsum() our little hearts out.
