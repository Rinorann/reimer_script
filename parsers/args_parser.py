from .wells_parser import parse_wells
def parse_specs(specs_part):
    """
    Парсит строку с dil спецификациями.
    
    Вход: 'dil 20 B1:B3, dil 10 C1:C3'
    Выход: [
        {'dilution': 20, 'wells': ['B1','B2','B3']},
        {'dilution': 10, 'wells': ['C1','C2','C3']}
    ]
    """
    specs = []
    
    # Разбиваем по 'dil'
    parts = specs_part.split('dil')
    
    for part in parts:
        part = part.strip().strip(',')
        if not part:
            continue
            
        tokens = part.split()
        dilution = int(tokens[0])
        wells = tokens[1:]
        wells = parse_wells(wells)
        
        specs.append({
            'dilution': dilution,
            'wells': wells
        })
    return specs
