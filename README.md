# solvefit

So many activities, so little time. This tool uses integer programming to optimise your workout schedule based on your priorities. 

### Caveats
I've built this for my own purposes. There are no guarantees that it produces a sensible (or even safe) training programme. In fact, most likely it won't.

### Installation
Clone repo and install with `pip install -e .`.

### Usage
To set activities and priorities, edit `activities.toml`. To add at least one trail run (but no more than two) per week, for example:
```
[activities.trail_running]
arm_strength = 0
core_strength = 4
leg_strength = 9
cardio = 10
balance = 4
min_sessions = 1
max_sessions = 2
```

Adjust values based on your own training. Admittedly, the values are somewhat arbitrary.

Then optimise with `solvefit`. The output will look something like this:
```
Status: Optimal

Recommended training schedule:
  strength_training: 0
  erg: 0
  trail_running: 2
  road_running: 2
  bouldering: 0
  ww_kayaking: 0
  cycling: 1

Maximum weighted score: 9.950
```
In this case, I have clearly put very heavy emphasis on cardio when assigning weights. 

There are currently two optional arguments if you wish to set the number of sessions in a week (default `5`), or the path to another ToML file (default `activities.toml`):
```
$ solvefit --help
Usage: solvefit [OPTIONS]

Options:
  --n_sessions INTEGER RANGE  Number of sessions in a week  [1<=x<=7]
  --toml-path TEXT            Path to TOML file defining activities
  --help                      Show this message and exit.
```