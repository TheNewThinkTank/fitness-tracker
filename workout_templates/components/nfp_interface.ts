
// TODO: add npx eslint nfp_interface.ts to GitHub Actions workflow

interface NfpWorkout {
    LegExercise1: string;
    LegExercise2: string;
    LegExercise3: string;
    BackExercise1: string;
    ChestExercise1: string;
    ShoulderExercise1: string;
    TrapsExercise1: string;
    AbsExercise1: string;
    ArmExercise1: string;
    ArmExercise2: string;
}

const QuadExercises = [
    'squat',
    'leg_extention',
    'bulgarian_split_squat',
    'hack_squat',
    'leg_press',
    'walking_barbell_lunge',
];

const HamstringExercises = [
    'deadlift',
    'romanian_deadlift',
    'straight_leg_deadlift',
    'sumo_deadlift',
    'leg_curl',
];

const CalfExercises = [
    'standing_calf_raise',
    'seated_calf_raise',
];

const BackExercises = [
    'chin_up',
    'machine_bentover_row',
    'lat_pulldown',
    'seated_row',
    'single_arm_bent_over_db_row',
];

const ChestExercises = [
    'barbell_bench_press',
    'incline_db_press',
    'db_flys',
    'cable_crossover',
    'pullover',
];

const ShoulderExercises = [
    'military_press',
    'db_lateral_raises',
    'db_rear_lateral_raises',
    'db_front_raises',
    'arnold_press',
];

const TrapsExercises = [
    'barbell_shrug',
    'face_pull',
];

const AbsExercises = [
    'crunch',
    'reverse_crunch',
    'hanging_leg_raise',
    'side_jackknife',
    'side_crunch',
];

const TricepsExercises = [
    'skull_crusher',
    'french_press',
    'cable_extention',
    'kickback',
];

const BicepsExercises = [
    'ez_bar_curl',
    'hammer_curl',
    'incline_curl',
    'preacher_curl',
    'alternating_db_curl',
];

const split1: NfpWorkout = {
    LegExercise1: '1. ' + QuadExercises[0],
    LegExercise2: '2. ' + HamstringExercises[0],
    LegExercise3: '3. ' + CalfExercises[0],
    BackExercise1: '4. ' + BackExercises[0],
    ChestExercise1: '5. ' + ChestExercises[0],
    ShoulderExercise1: '6. ' + ShoulderExercises[0],
    TrapsExercise1: '7. ' + TrapsExercises[0],
    AbsExercise1: '8. ' + AbsExercises[0],
    ArmExercise1: '9. ' + TricepsExercises[0],
    ArmExercise2: '10. ' + BicepsExercises[0],
};

const split2: NfpWorkout = {
    LegExercise1: '1. ' + QuadExercises[1],
    LegExercise2: '2. ' + HamstringExercises[1],
    LegExercise3: '3. ' + CalfExercises[1],
    BackExercise1: '4. ' + BackExercises[1],
    ChestExercise1: '5. ' + ChestExercises[1],
    ShoulderExercise1: '6. ' + ShoulderExercises[1],
    TrapsExercise1: '7. ' + TrapsExercises[1],
    AbsExercise1: '8. ' + AbsExercises[1],
    ArmExercise1: '9. ' + TricepsExercises[1],
    ArmExercise2: '10. ' + BicepsExercises[1],
};

const split3: NfpWorkout = {
    LegExercise1: '1. ' + QuadExercises[2],
    LegExercise2: '2. ' + HamstringExercises[2],
    LegExercise3: '3. ' + CalfExercises[0],
    BackExercise1: '4. ' + BackExercises[2],
    ChestExercise1: '5. ' + ChestExercises[2],
    ShoulderExercise1: '6. ' + ShoulderExercises[2],
    TrapsExercise1: '7. ' + TrapsExercises[0],
    AbsExercise1: '8. ' + AbsExercises[2],
    ArmExercise1: '9. ' + TricepsExercises[2],
    ArmExercise2: '10. ' + BicepsExercises[2],
};

const split4: NfpWorkout = {
    LegExercise1: '1. ' + QuadExercises[3],
    LegExercise2: '2. ' + HamstringExercises[3],
    LegExercise3: '3. ' + CalfExercises[1],
    BackExercise1: '4. ' + BackExercises[3],
    ChestExercise1: '5. ' + ChestExercises[3],
    ShoulderExercise1: '6. ' + ShoulderExercises[3],
    TrapsExercise1: '7. ' + TrapsExercises[1],
    AbsExercise1: '8. ' + AbsExercises[3],
    ArmExercise1: '9. ' + TricepsExercises[3],
    ArmExercise2: '10. ' + BicepsExercises[3],
};

const split5: NfpWorkout = {
    LegExercise1: '1. ' + QuadExercises[4],
    LegExercise2: '2. ' + HamstringExercises[4],
    LegExercise3: '3. ' + CalfExercises[0],
    BackExercise1: '4. ' + BackExercises[4],
    ChestExercise1: '5. ' + ChestExercises[4],
    ShoulderExercise1: '6. ' + ShoulderExercises[4],
    TrapsExercise1: '7. ' + TrapsExercises[0],
    AbsExercise1: '8. ' + AbsExercises[4],
    ArmExercise1: '9. ' + TricepsExercises[0],
    ArmExercise2: '10. ' + BicepsExercises[4],
};
