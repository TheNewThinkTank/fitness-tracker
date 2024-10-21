
from enum import Flag, auto


class Timezone(Flag):
    CET: int = auto()
    CEST: int = auto()
    ICT: int = auto()
    DK: int = CET | CEST


if __name__ == "__main__":
    dk = Timezone.DK
    print(dk)
    print(Timezone.CET in dk)
    print(Timezone.DK.value)
