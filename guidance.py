"""Explained planning prompts. Source-informed, not agronomist-validated advice."""
VERSION = 'planning-1'
CHECKED = '2026-10-19'
SOURCES = {
    'soil': dict(title='FAO: Soil and water', url='https://www.fao.org/4/r4082e/r4082e03.htm', scope='General soil-water principles; site measurements are still needed.'),
    'maize': dict(title='FAO: Water shortages and crop growth stages', url='https://www.fao.org/4/t7202e/t7202e05.htm', scope='General irrigation guidance; not a locally validated maize schedule.'),
    'rainwater': dict(title='CDC: Collecting rainwater and your health', url='https://www.cdc.gov/drinking-water/about/collecting-rainwater-and-your-health-an-overview.html', scope='General water-quality guidance from the US; check local requirements.'),
}


def add_guidance(approach, values, result):
    """Append actionable prompts once at save time, preserving old check indices."""
    cards = []
    gaps = []
    crop = ' '.join(values.get('crop', '').casefold().split())
    maize = crop in {'maize', 'corn', 'grain maize'} and approach == 'garden-mulch'

    def add(rule, title, action, why, factors, source=None, priority='Plan next'):
        # Explicit allowlisted factors; never infer conditions from free-text notes.
        basis = [{'name': key, 'value': values.get(key, 'unknown')} for key in factors]
        cards.append(dict(rule=rule, title=title, action=action, why=why, factors=basis,
                          priority=priority, source=(SOURCES[source] | {'checked': CHECKED}) if source else None,
                          basis_kind='Source-informed AdaptTrail suggestion' if source else 'AdaptTrail planning suggestion'))

    if approach == 'garden-mulch':
        if values.get('drainage') == 'poor':
            add('drainage-first', 'Check drainage first',
                'Record any standing water and ask a local agricultural adviser to assess poor drainage before changing soil cover or watering.',
                'Saturated soil leaves less air for roots. Low water availability elsewhere does not mean this soil needs more water.',
                ['drainage', 'water'], 'soil', 'Check first')
        if values.get('soil') == 'sandy':
            add('sandy-observation', 'Watch how moisture changes',
                'Record soil moisture observations before and after rain or watering; use these records when discussing a watering plan locally.',
                'Sandy soils generally hold less plant-available water than loam. Soil type alone does not determine a watering amount or interval.',
                ['soil'], 'soil')
        elif values.get('soil') == 'clay' and values.get('drainage') != 'poor':
            add('clay-observation', 'Observe water movement',
                'Check and record whether water remains on the surface after rain or watering before changing your soil-cover plan.',
                'Water usually enters clay more slowly than sand; actual structure and drainage also matter.',
                ['soil', 'drainage'], 'soil')
        if maize:
            stage = values.get('growth', 'unknown')
            if stage in {'flowering', 'grain filling'}:
                add('maize-sensitive-stage', 'Discuss the maize water plan',
                    'Review your maize water supply and current soil moisture with a local agricultural adviser during flowering or grain filling.',
                    'FAO identifies flowering and grain filling as maize stages sensitive to water shortages. This does not tell us whether your field is currently short of water.',
                    ['crop', 'growth', 'water'], 'maize', 'Check first')
            else:
                add('maize-stage-check', 'Identify the maize growth stage',
                    'Confirm whether your maize is at seedling, vegetative, flowering, grain filling or ripening stage before planning water use.',
                    'Maize sensitivity varies with growth stage. An established plant is not necessarily flowering; soil cover alone does not meet crop water needs.',
                    ['crop', 'growth'], 'maize')
                if stage in {'unknown', 'established', 'not applicable'}:
                    gaps.append('Specific maize growth stage')
        else:
            gaps.append('Crop-specific guidance is unavailable: only maize planning prompts are included in this release.')
        if values.get('materials') in {'no', 'unknown'}:
            add('materials-check', 'Check available materials',
                'List possible soil-cover materials and ask a local adviser to check their suitability and cost before obtaining them.',
                'Suitable material has not been confirmed. Free-text resource notes are saved but are not checked for contamination, pests or suitability.',
                ['materials', 'budget'])
        if values.get('water') == 'low':
            add('limited-water', 'Plan around the water available',
                'Record the water you can access and ask for a locally appropriate plan using your crop stage and actual soil moisture.',
                'You report limited water. This answer is not a measurement of soil dryness or a diagnosis of drought.',
                ['water', 'growth'])
    if approach == 'rainwater' and values.get('use') in {'drinking or cooking', 'food crops'}:
        add('rainwater-quality', 'Resolve water-quality questions first',
            'Ask local water-quality or health services about safe sources and testing before using collected rainwater for food crops, drinking or cooking.',
            'Collected rainwater can contain germs or chemicals even when it looks clean. A forecast and an available tank do not establish safety.',
            ['use', 'storage'], 'rainwater', 'Check first')
    if values.get('budget') == 'low':
        add('budget-plan', 'Check costs before spending',
            'List setup and upkeep costs and available support before committing money to this approach.',
            'A low budget changes what may be practical. No local prices or affordability calculation are available.', ['budget'])
    if values.get('maintenance') == 'unavailable':
        add('upkeep-plan', 'Arrange help with upkeep',
            'Identify someone who can maintain the approach, or review an alternative with lower upkeep needs before starting.',
            'You reported no maintenance capacity; having materials alone does not resolve that constraint.', ['maintenance'], priority='Check first')
    if approach == 'water-log':
        add('measurement-plan', 'Make your records comparable',
            'Choose a metric, unit, repeatable method and measurement period; record a baseline before making changes.',
            'Consistent records help describe differences. They do not establish that a particular action caused the change.', ['measurement'])

    weather = result.get('weather')
    if weather:
        rain = any(day['precipitation'] > 0 for day in weather['days'][1:])
        if approach == 'rainwater':
            action = ('Check collection surfaces, storage capacity and overflow before the forecast rain; do not treat forecast rainfall as collected water volume.' if rain else
                      'Check current stored water and supply options; do not assume the collection system will refill during the three forecast days.')
        else:
            action = ('Check actual soil moisture before deciding to water, even when rain is forecast.' if rain else
                      'Check actual soil moisture and available water; three forecast days without rain do not establish drought.')
        add('weather-context', 'Use the forecast as context', action,
            'The saved town forecast may differ from your site and can change. It supplies no crop-specific watering threshold.', [])
        cards[-1]['weather_basis'] = dict(location=weather['location']['label'], retrieved_at=weather['retrieved_at'],
                                         dates=[day['date'] for day in weather['days'][1:]], rain_forecast=rain)
        cards[-1]['source'] = dict(title='Open-Meteo: saved weather data',url='https://open-meteo.com/',checked=CHECKED,
                                  scope='Forecast data only; the planning suggestion is written by AdaptTrail.')
    else:
        gaps.append('No weather snapshot: no weather-based suggestion was generated.')
    if approach == 'garden-mulch':
        gaps.append('Current soil moisture is not measured by this platform.')
    cards.sort(key=lambda card: card['priority'] != 'Check first')
    for card in cards:
        card['check_index'] = len(result['checks'])
        result['checks'].append(card['action'])
    result['guidance'] = dict(version=VERSION, cards=cards, gaps=gaps, maize=maize,
        scope='Maize planning prompts plus selected soil, resource and weather checks.' if maize else 'General planning checks for the selected approach; no crop-specific recommendation.',
        limitation='Source-informed rules, not a locally validated agricultural recommendation. No irrigation amounts, yield forecasts or suitability scores are calculated.')
    return result
