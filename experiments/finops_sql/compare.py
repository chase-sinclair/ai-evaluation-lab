"""Compare complete result multisets and protect ranked output order."""

from decimal import ROUND_HALF_UP, Decimal

RATES = {9, 10, 12, 14, 25, 29}
IDS = {
    2: {0},
    3: {0},
    5: {0},
    6: {0},
    11: {0},
    13: {0},
    15: {0},
    16: {0},
    20: {0},
    23: {0, 1},
    24: {0},
    28: {0},
    30: {0, 1},
    32: {0},
}


def normalize(number, rows):
    def value(i, v):
        if v is None:
            return None
        d = Decimal(str(v))
        if i in IDS.get(number, ()):
            if d != int(d):
                raise ValueError("non-integral quantity or identifier")
            return int(d)
        rounded = d.quantize(
            Decimal(".000001" if number in RATES else ".01"), rounding=ROUND_HALF_UP
        )
        return str(abs(rounded) if rounded == 0 else rounded)

    result = [tuple(value(i, v) for i, v in enumerate(row)) for row in rows]
    return result if number in {2, 6} else sorted(result)
