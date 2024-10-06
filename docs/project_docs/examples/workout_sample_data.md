# Workout Sample Data

```YAML
# yaml-language-server: $schema=<MY_PROJECT_PATH>/fitness-tracker/.config/yaml_schema.json
date: "2024-10-05"
start_time: "11:57"
end_time: "12:38"
timezone: CEST
split: arms_abs_calf
gym: PureGym Valby
warmup: "rowing 5 minutes, 1112 meters"
cooldown: "15 minutes yoga"
notes: "seated_calf_raise was dropsets, without pause between"
exercises:
  military_press:
  - set_number: 1
    reps: 12
    weight: 25 kg
  - set_number: 2
    reps: 10
    weight: 35 kg
  - set_number: 3
    reps: 10
    weight: 35 kg
  db_side_laterals:
  - set_number: 1
    reps: 12
    weight: 14 kg
  - set_number: 2
    reps: 12
    weight: 18 kg
  - set_number: 3
    reps: 12
    weight: 18 kg
  cable_french_press:
  - set_number: 1
    reps: 20
    weight: 20 kg
  - set_number: 2
    reps: 6
    weight: 40 kg
  db_rear_laterals:
  - set_number: 1
    reps: 12
    weight: 11.4 kg
  - set_number: 2
    reps: 10
    weight: 11.4 kg
  - set_number: 3
    reps: 8
    weight: 11.4 kg
  db_curl:
  - set_number: 1
    reps: 12
    weight: 28 kg
  - set_number: 2
    reps: 9
    weight: 28 kg
  seated_calf_raise:
  - set_number: 1
    reps: 9
    weight: 50 kg
  - set_number: 2
    reps: 10
    weight: 30 kg
  - set_number: 3
    reps: 15
    weight: 20 kg
  swiss_ball_crunch:
  - set_number: 1
    reps: 25
    weight: BODYWEIGHT kg
  - set_number: 2
    reps: 20
    weight: BODYWEIGHT kg
  - set_number: 3
    reps: 15
    weight: BODYWEIGHT kg
```

## Time and duration

For this workout data, the `start_time` begins immediately before the first working set, not counting the warmup.<br>
The `end_time` is recorded immediately after the last working set, disregarding the cooldown.<br>
The workout duration is then calculated as the difference between the two.

## Weight

Exercises that only involves the bodyweight are marked with `BODYWEIGHT` under the `weight` field, which is later replaced dynamically by lookup in a google sheet, before analysis is performed.
In general, the total weight is recorded, e.g. including weight of barbell or EZ-bar.<br>
In the case of dumbbell or cable exercises, the sum of the two dumbbells or cables are recorded.
