# sc2downtime
Baseline script for computing structure downtime from SC2 replays.

## Description

This is a hacked-together bit of code that computes the time your structures spent NOT producing units like they should have been doing. Note that it computes these numbers for all structures in a "type" (ie, all `Factory`, all `OrbitalCommand`) - it does not attribute a unit to a specific building (ie, the second `Factory` you build that game).

## Incomplete

There are some hardcoded `dict`s and `list`s in this code that I only populated as far as they were useful for the replay I debugged this with. They need to be populated with the remaining units/buildings in the game.

## Unit Attribution

Attributing a unit to a specific building is harder than it seems. The only way to do it would be using the `location` of the `UnitBornEvent`, and selecting the closest building there.

The script does this already, but it will mis-attribute if you build structures very close to one another.

Example: you build all your `Factory` North-South stacked on top of each other, and pump out `Thors`. There's a good chance the `Thor` coming out of the Northern-most `Factory` will be attributed to the 2nd-most Northern `Factory`.

I haven't computed any metrics on how often this occurs, or how far apart buildings need to be. The best I hacked was to attribute to the closest `parent` building (so the Thor won't go to the nearby `Barracks`).

## Usage

Simply update the path to the replay file, or comment that line and uncomment the `tkinter` block.

Update the `PLAYER` variable to your handle. Running the script should then work fine.

The script requires the `sc2reader` and `pandas` libraries, both can be installed with `pip install`.

## Maintenance

Honestly, I don't plan on maintaining this code or repo - just wanted a way to hand it off to anyone who's interested. Feel free to fork it, clone it, etc :)

## Bonus Level

The obvious next improvement would be to create a timeseries dataframe, appending each new `UnitBornEvent` - instead of just adding the times within the loop.

GLHF!
