"""
Converts a length measurement from one unit to another.
"""


def convert_length(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a length measurement from one unit to another.
    """

    conversion_factors = {
        'meters': 1,
        'kilometers': 0.001,
        'centimeters': 100,
        'millimeters': 1000,
        'inches': 39.3701,
        'feet': 3.28084,
        'yards': 1.09361
    }

    # Convert to meters
    if from_unit in conversion_factors:
        value_in_meters = value / conversion_factors[from_unit]
    else:
        raise ValueError(f"Unknown from_unit: {from_unit}")

    # Convert from meters to target unit
    if to_unit in conversion_factors:
        return value_in_meters * conversion_factors[to_unit]
    else:
        raise ValueError(f"Unknown to_unit: {to_unit}")


def main() -> None:
    """Main function to demonstrate the length converter.
    This module is not intended to be run directly, but can be used as a library.
    """

    import sys

    if len(sys.argv) != 4:
        print("Usage: python3 length_converter.py <value> <from_unit> <to_unit>")
        sys.exit(1)

    try:
        value = float(sys.argv[1])
        from_unit = sys.argv[2]
        to_unit = sys.argv[3]
        converted_value = convert_length(value, from_unit, to_unit)
        print(f"{value} {from_unit} is {converted_value} {to_unit}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
