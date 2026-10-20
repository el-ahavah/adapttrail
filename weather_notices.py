"""User-requested weather reminders; never official hazard or crop alerts."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import math

VERSION = 'weather-notices-1'
_UNSET = object()


def snapshot_current(snapshot, now=None):
    """A six-hour UI freshness limit, also invalidated at local midnight."""
    if not snapshot:
        return False
    now = now or datetime.now(timezone.utc)
    try:
        retrieved = datetime.fromisoformat(snapshot['retrieved_at'])
        if retrieved.tzinfo is None or not timedelta(0) <= now - retrieved < timedelta(hours=6):
            return False
        today = now.astimezone(ZoneInfo(snapshot['timezone'])).date()
        return [d['date'] for d in snapshot['days'][1:]] == [(today + timedelta(days=i)).isoformat() for i in range(3)]
    except (KeyError, ValueError, TypeError):
        return False


def parse_preferences(form):
    preferences = {key: form.get(key) == 'yes' for key in ['rain', 'dry', 'temperature']}
    preferences['temperature_limit'] = None
    errors = []
    if preferences['temperature']:
        try:
            limit = float(form.get('temperature_limit', ''))
            if not math.isfinite(limit) or not -60 <= limit <= 60:
                raise ValueError
            preferences['temperature_limit'] = limit
        except (TypeError, ValueError):
            errors.append('Enter your temperature reminder limit between -60 and 60 °C.')
    if not any(preferences[key] for key in ['rain', 'dry', 'temperature']):
        errors.append('Choose at least one reminder, or turn off weather notices.')
    return preferences, errors


def make_notices(snapshot, preferences, context):
    days = snapshot['days'][1:]
    notices = []
    rain_days = [day for day in days if day['precipitation'] > 0]
    if preferences['rain'] and rain_days:
        action = 'Check actual soil moisture before changing watering. If collecting water, check surfaces, storage and overflow.'
        if context.get('drainage') == 'poor':
            action = 'You reported poor drainage. Check for standing water and seek local drainage advice before adding water or soil cover.'
        notices.append(dict(kind='rain',title='Precipitation in the forecast',dates=[day['date'] for day in rain_days],
                            reason='At least one forecast day has more than 0 mm precipitation. This includes rain, showers or snow; it is not a heavy-rain or flood warning.',action=action))
    if preferences['dry'] and all(day['precipitation'] == 0 for day in days):
        notices.append(dict(kind='dry',title='No precipitation in this three-day forecast',dates=[day['date'] for day in days],
                            reason='All three forecast days show 0 mm. This does not establish drought or soil dryness.',
                            action='Check actual soil moisture and the water available before planning your next action.'))
    if preferences['temperature']:
        limit = preferences['temperature_limit']
        warm_days = [day for day in days if day['high'] >= limit]
        if warm_days:
            notices.append(dict(kind='temperature',title='Your temperature reminder limit is reached',dates=[day['date'] for day in warm_days],
                                reason=f'Forecast daily maximum temperature reaches your chosen {limit:g} °C limit. This is not a crop-damage or health threshold.',
                                action='Review local guidance for your crop and growth stage and check site conditions before changing your plan.'))
    return notices


def notice_state(watch, now=None, context_values=_UNSET):
    if not watch.get('enabled'):
        return 'Off'
    if watch.get('last_error'):
        return 'Last check failed — refresh needed'
    if not watch.get('snapshot'):
        return 'Ready for your first check'
    if context_values is not _UNSET and watch.get('context_values') != context_values:
        return 'Project information changed — refresh needed'
    if not snapshot_current(watch['snapshot'], now):
        return 'Outdated — refresh needed'
    count = len(watch.get('notices', []))
    return f'{count} reminder' + ('' if count == 1 else 's') + ' from the last check'
