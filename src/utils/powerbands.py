"""
see https://www.blkboxfitness.com/collections/resistance-bands/products/blk-box-power-bands
"""

class PowerBand:
    """BLK BOX Power Bands.
    """
    def __init__(self, color, length, width, resistance):
        self.color = color
        self.length = length
        self.width = width
        self.resistance = resistance


bands: list[PowerBand] = [
    PowerBand("Red", "1040mm", "13mm", "4-18kg"),
    PowerBand("Black", "1040mm", "20mm", "7-25kg"),
    PowerBand("Purple", "1040mm", "29mm", "12-37kg"),
    PowerBand("Green", "1040mm", "45mm", "22-57kg"),
]

def parse_resistance_range(resistance_str: str) -> float:
    low, high = map(float, resistance_str.replace("kg", "").split("-"))
    return (low + high) / 2

# Build mapping: {"GREEN": 39.5, "PURPLE": 24.5, ...}
bands_mapping = {
    band.color.upper(): parse_resistance_range(band.resistance)
    for band in bands
}
