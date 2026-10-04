"""Optional Open-Meteo context. Fixed endpoints, bounded cache and timeouts."""
from collections import OrderedDict
from datetime import datetime, timezone, date, timedelta
from zoneinfo import ZoneInfo
import json
import math
from threading import Lock
from time import monotonic
from urllib.parse import urlencode
from urllib.request import urlopen

_cache = OrderedDict()
_lock = Lock()


class WeatherUnavailable(Exception):
    pass


def request_json(endpoint, params):
    url = endpoint + '?' + urlencode(params)
    with _lock:
        cached = _cache.get(url)
        if cached and monotonic() - cached[0] < 900:
            return cached[1]
    try:
        with urlopen(url, timeout=4) as response:
            raw = response.read(100001)
        if len(raw) > 100000:
            raise ValueError('Oversized response')
        data = json.loads(raw)
        if not isinstance(data, dict) or data.get('error'):
            raise ValueError('Invalid response')
    except (OSError, ValueError) as error:
        raise WeatherUnavailable('Weather service unavailable. You can save without weather and try again later.') from error
    with _lock:
        _cache[url] = (monotonic(), data)
        _cache.move_to_end(url)
        while len(_cache) > 128:
            _cache.popitem(last=False)
    return data


def search_locations(query):
    data = request_json('https://geocoding-api.open-meteo.com/v1/search',
                        dict(name=query, count=5, language='en', format='json'))
    try:
        locations = []
        for item in data.get('results', []):
            lat, lon = float(item['latitude']), float(item['longitude'])
            if not math.isfinite(lat) or not math.isfinite(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError('Invalid coordinates')
            label = ', '.join(str(item[key])[:100] for key in ['name','admin1','country'] if item.get(key))
            locations.append(dict(id=str(item['id']), label=label, latitude=lat, longitude=lon))
        return locations
    except (KeyError, TypeError, ValueError) as error:
        raise WeatherUnavailable('Location results unavailable. Try again or save without weather.') from error


def forecast(location):
    data = request_json('https://api.open-meteo.com/v1/forecast', dict(
        latitude=location['latitude'], longitude=location['longitude'], timezone='auto',
        daily='temperature_2m_max,temperature_2m_min,precipitation_sum', past_days=1, forecast_days=3))
    try:
        daily = data['daily']
        units = data['daily_units']
        if units['temperature_2m_max'] != '°C' or units['temperature_2m_min'] != '°C' or units['precipitation_sum'] != 'mm':
            raise ValueError('Unexpected units')
        keys = ['time','temperature_2m_min','temperature_2m_max','precipitation_sum']
        if any(len(daily[key]) != 4 for key in keys):
            raise ValueError('Incomplete forecast')
        today = datetime.now(ZoneInfo(data['timezone'])).date()
        days = []
        for i in range(4):
            if date.fromisoformat(daily['time'][i]) != today + timedelta(days=i-1):
                raise ValueError('Stale or unordered forecast')
            low, high, rain = [daily[key][i] for key in keys[1:]]
            if any(isinstance(n, bool) or not isinstance(n, (float,int)) or not math.isfinite(n) for n in [low,high,rain]):
                raise ValueError('Missing weather data')
            if rain < 0 or low > high:
                raise ValueError('Invalid weather data')
            days.append(dict(date=daily['time'][i], low=low, high=high, precipitation=rain,
                             kind='Recent model estimate' if i == 0 else 'Forecast'))
        # The cached payload retains its original retrieval date, never a fresh-looking timestamp.
        with _lock:
            if '_retrieved_at' not in data:
                data['_retrieved_at'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
        return dict(location=location, days=days, timezone=data['timezone'],
                    retrieved_at=data['_retrieved_at'], source='https://open-meteo.com/',
                    limitation='Model estimates, not measurements at your farm. Saved snapshot; forecasts can change. This is not a drought prediction or a crop-specific suitability rating.')
    except (KeyError, TypeError, ValueError) as error:
        raise WeatherUnavailable('Weather data incomplete. Assessment saved without weather guidance.') from error


def planning_notes(approach, values, snapshot):
    notes = []
    if any(day['precipitation'] > 0 for day in snapshot['days'][1:]):
        if approach == 'rainwater':
            notes.append('Precipitation is forecast. Check collection surfaces, storage capacity and overflow before collection; forecast volume is not your expected water yield.')
        else:
            notes.append('Precipitation is forecast. Check actual soil moisture before deciding to water; a forecast does not guarantee rain at your site.')
        if values['drainage'] == 'poor':
            notes.append('You report poor drainage. Check for standing water and seek local drainage advice before adding water or soil cover.')
    else:
        notes.append('The forecast shows no precipitation for these three days. Check actual soil moisture and available water; this short forecast does not establish drought.')
    if values['growth'] == 'seedling':
        notes.append('You report seedlings. Check their actual moisture needs and local crop guidance rather than relying on the forecast alone.')
    notes.append('Compare the displayed temperature range with local guidance for your crop and growth stage. This version has no validated crop temperature thresholds.')
    return notes
