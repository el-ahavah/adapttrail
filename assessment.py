"""Transparent preliminary checks, not a validated suitability scoring model."""
VERSION = 'preliminary-1'
FIELDS = {
 'climate': ('Climate (self-reported)', ['unknown','seasonal','dry','wet','temperate']),
 'soil': ('Soil type', ['unknown','sandy','clay','loam','not applicable']),
 'drainage': ('Drainage', ['unknown','poor','good','not applicable']),
 'water': ('Water availability', ['unknown','low','medium','high']),
 'growth': ('Growth stage', ['unknown','seedling','established','not applicable']),
 'budget': ('Budget level', ['unknown','low','medium','high']),
 'maintenance': ('Maintenance capacity', ['unknown','available','unavailable']),
 'roof': ('Collection surface available?', ['unknown','yes','no']),
 'storage': ('Water storage available?', ['unknown','yes','no']),
 'materials': ('Suitable mulch materials available?', ['unknown','yes','no']),
 'measurement': ('Consistent measuring method available?', ['unknown','yes','no']),
 'use': ('Intended water use', ['unknown','non-food plants','food crops','drinking or cooking'])
}
SOURCES = {
 'rainwater': [('CDC: Rainwater collection and health', 'https://www.cdc.gov/drinking-water/about/collecting-rainwater-and-your-health-an-overview.html')],
 'garden-mulch': [('FAO: Guidance on realizing real water savings', 'https://openknowledge.fao.org/3/cb3844en/cb3844en.pdf')],
 'water-log': []
}


def assess(approach, values):
    reasons, checks, missing = [], [], []
    relevant = ['maintenance','water','budget']
    if approach == 'rainwater':
        relevant += ['climate','roof','storage','use']
        reasons.append('Rainwater collection needs a collection surface, storage, and ongoing maintenance.')
        for field, label in [('roof','collection surface'),('storage','storage')]:
            if values[field] == 'yes':
                reasons.append(f'You report an available {label}; its condition and capacity still need checking.')
            elif values[field] == 'no':
                checks.append(f'A {label} is missing; assess feasibility and costs before proceeding.')
        checks += ['Check local collection rules, materials, water demand, storage capacity, and overflow with local guidance.', 'Water quality must match the intended use. This assessment does not establish drinking-water safety.']
        if values['use'] in ['drinking or cooking','food crops']:
            checks.append('Seek local water-quality advice before using collected water for consumption or food crops.')
    elif approach == 'garden-mulch':
        relevant += ['soil','drainage','growth','materials']
        reasons.append('Soil cover can conserve moisture; appropriate materials and local growing conditions still matter.')
        if values['materials'] == 'no':
            checks.append('Identify suitable materials and their cost before trying soil cover.')
        if values['drainage'] == 'poor':
            checks.append('Reported poor drainage needs local assessment before adding soil cover.')
        checks.append('Check material suitability, crop needs, pests, and current soil moisture with local agricultural guidance.')
    else:
        relevant += ['measurement']
        reasons.append('A consistent log can help describe changes in water use; it does not prove their cause.')
        if values['measurement'] == 'no':
            checks.append('Choose a repeatable measurement method before comparing entries.')
        checks.append('Use consistent units and periods, and record rain and changes in plants or garden size.')
    if values['maintenance'] == 'unavailable':
        checks.append('Maintenance capacity is unavailable; find support or consider a less demanding approach.')
    for field in relevant:
        if values[field] == 'unknown':
            missing.append(FIELDS[field][0])
    status = 'More information needed' if missing else 'Local checks identified'
    return dict(status=status, reasons=reasons, checks=checks, missing=missing,
                sources=SOURCES[approach], version=VERSION,
                limitation='Preliminary planning guidance, not an expert-reviewed rating. No weather data was fetched. Your answers are self-reported; outcomes are not guaranteed.')
