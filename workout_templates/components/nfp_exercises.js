let split1 = new Map()
split1.set('LegExercise1', '1. squat')
split1.set('LegExercise2', '2. deadlift')
split1.set('BackExercise1', '3. machine_bentover_row')
split1.set('ChestExercise1', '4. barbell_bench_press')
let split2 = new Map()
split2.set('LegExercise1', '1. leg_extention')
split2.set('LegExercise2', '2. leg_curl')
split2.set('BackExercise1', '3. lat_pulldown')
split2.set('ChestExercise1', '4. incline_dumbbell_press')
let split3 = new Map()
split3.set('LegExercise1', '1. front_squat')
split3.set('LegExercise2', '2. sumo_deadlift')
split3.set('BackExercise1', '3. chin_ups')
split3.set('ChestExercise1', '4. dumbbell_flys')
let split4 = new Map()
split4.set('LegExercise1', '1. hack_squat')
split4.set('LegExercise2', '2. hungarian_split_squat')
split4.set('BackExercise1', '3. t_bar_row')
split4.set('ChestExercise1', '4. dip')
let split5 = new Map()
split5.set('LegExercise1', '1. leg_press')
split5.set('LegExercise2', '2. walking_lunge')
split5.set('BackExercise1', '3. seated_row')
split5.set('ChestExercise1', '4. pullover')

let splits = new Map()
splits.set(1, split1)
splits.set(2, split2)
splits.set(3, split3)
splits.set(4, split4)
splits.set(5, split5)

export {splits};