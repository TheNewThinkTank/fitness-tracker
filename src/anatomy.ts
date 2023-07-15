// human anatomy - the muscular system

// LEG
type Glute = {
    large: 'gluteus maximus'
    small: 'gluteus minimus'
}

type Thigh = {
    anterior: 'quadriceps'
    posterior: 'hamstrings'
}

type Calf = {
    large: 'gastrocnemius'
    small: 'soleus'
}

type LowerLeg = {
    anterior: 'tibialis_anterior'
    posterior: Calf
}

type Leg = {
    glute: Glute
    thigh: Thigh
    lowerLeg: LowerLeg
}

// ARM
type UpperArm = {
    anterior: 'biceps'
    posterior: 'triceps'
}

type Forearm = {
    anterior: 'flexor muscles'
    posterior: 'extensor muscles'
}

type Hand = {
    palm: 'palmar muscles'
    fingers: 'digital muscles'
}

type Arm = {
    upperArm: UpperArm
    forearm: Forearm
    hand: Hand
}


// TORSO
type Chest = {
    large: 'pectoralis major'
    small: 'pectoralis minor'
}

type Abdomen = {
    front: 'rectus abdominis'
    side: 'obliques'
}

type Back = {
    upper: 'trapezius'
    middle: ['rhomboids', 'latissimus dorsi']
    center: 'erector spinae'
}

type Torso = {
    chest: Chest
    abdomen: Abdomen
    back: Back
}

// BODY

type body = {
    leg: Leg
    arm: Arm
    torso: Torso
}

// const BODY: body = []
