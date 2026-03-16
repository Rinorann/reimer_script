from .wells_parser import parse_wells
def parse_calibration(parts):
    """
    calibration B1:B3
    """
    wells = parse_wells(parts)
    return {'action' : 'calibration',
            'wells' : wells
            }


def parse_baseline(parts):
    """
    baseline B1:B3
    """
    wells = parse_wells(parts)
    return {'action' : 'baseline',
            'wells' : wells
            }
