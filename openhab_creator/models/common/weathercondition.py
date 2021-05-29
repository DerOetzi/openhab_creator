from __future__ import annotations

from typing import Dict

from openhab_creator import _, CreatorEnum, classproperty


class WeatherCondition(CreatorEnum):
    THUNDERSTORM_WITH_LIGHT_RAIN = 1, _(
        'Thunderstorm with light rain')  # Gewitter mit leichtem Regen
    THUNDERSTORM_WITH_RAIN = 2, _(
        'Thunderstorm with rain')  # Gewitter mit Regen
    THUNDERSTORM_WITH_HEAVY_RAIN = 3, _(
        'Thunderstorm with heavy rain')  # Gewitter mit starkem Regen
    LIGHT_THUNDERSTORM = 4, _('Light thunderstorm')  # Leichtes Gewitter
    THUNDERSTORM = 5, _('Thunderstorm')  # Gewitter
    HEAVY_THUNDERSTORM = 6, _('Heavy thunderstorm')  # Starkes Gewitter
    ROUGH_THUNDERSTORM = 7, _('Rough thunderstorm')  # Raues Gewitter
    THUNDERSTORM_WITH_LIGHT_DRIZZLE = 8, _(
        'Thunderstorm with light drizzle')  # Gewitter mit leichtem Nieselregen
    THUNDERSTORM_WITH_DRIZZLE = 9, _(
        'Thunderstorm with drizzle')  # Gewitter mit Nieselregen
    THUNDERSTORM_WITH_HEAVY_DRIZZLE = 10, _(
        'Thunderstorm with heavy drizzle')  # Gewitter mit starkem Nieselregen

    LIGHT_DRIZZLE = 11, _('Light drizzle')  # Leichtes Nieseln
    DRIZZLE = 12, _('Drizzle')  # Nieselregen
    HEAVY_DRIZZLE = 13, _('Heavy drizzle')  # Starker Nieselregen

    LIGHT_DRIZZLE2 = 14, _('Light drizzle')  # Leichtes Nieseln
    DRIZZLE2 = 15, _('Drizzle')  # Nieselregen
    HEAVY_DRIZZLE2 = 16, _('Heavy drizzle')  # Starker Nieselregen

    # Regenschauer und Nieselregen
    RAIN_SHOWERS_AND_DRIZZLE = 17, _('Rain showers and drizzle')
    # Starker Regenschauer und Nieselregen
    HEAVY_RAIN_SHOWERS_AND_DRIZZLE = 18, _('Rain showers and drizzle')
    DRIZZLE3 = 19, _('Drizzle')  # Nieselschauer

    LIGHT_RAIN = 20, _('Light rain')  # Leichter Regen
    MODERATE_RAIN = 21, _('Moderate rain')  # Mäßiger Regen
    HEAVY_RAIN = 22, _('Heavy rain')  # Starker Regen
    VERY_HEAVY_RAIN = 23, _('Very heavy rain')  # Sehr schwerer Regen
    EXTREME_RAIN = 24, _('Extreme rain')  # Extremer Regen

    FREEZING_RAIN = 25, _('Freezing rain')  # Gefrierender Regen

    LIGHT_RAIN_SHOWER = 26, _('Light rain shower')  # Leichter Regenschauer
    RAIN_SHOWER = 27, _('Rain shower')  # Regenschauer
    HEAVY_RAIN_SHOWER = 28, _('Heavy rain shower')  # Starker Regenschauer
    VERY_HEAVY_RAIN_SHOWER = 29, _(
        'Very heavy rain shower')  # Sehr starker Regenschauer

    MODERATE_SNOW = 30, _('Moderate snow')  # Mäßiger Schnee
    SNOWFALL = 31, _('Snowfall')  # Schneefall
    HEAVY_SNOWFALL = 32, _('Heavy snowfall')  # Starker Schneefall
    SLEET = 33, _('Sleet')  # Schneeregen
    SLEET2 = 34, _('Sleet')  # Graupelschauer
    # Leichter Regen und Schnee
    LIGHT_RAIN_AND_SNOW = 35, _('Light rain and snow')
    RAIN_AND_SNOW = 36, _('Rain and snow')  # Regen und Schnee
    LIGHT_SNOW_SHOWER = 37, _('Light snow shower')  # Leichter Schneeschauer
    SNOW_SHOWER = 38, _('Snow shower')  # Schneeschauer
    HEAVY_SNOW_SHOWER = 39, _('Heavy snow shower')  # Starker Schneeschauer

    GLOOMY = 40, _('Gloomy')  # Trüb
    SMOKE = 41, _('Smoke')  # Rauch
    HAZE = 42, _('Haze')  # Dunst
    SAND = 43, _('Sand')  # Sand
    FOG = 44, _('Fog')  # Nebel
    SAND2 = 45, _('Sand')  # Sand
    DUST = 46, _('Dust')  # Staub
    VOLCANIC_ASH = 47, _('Volcanic ash')  # Vulkanasche
    STORM = 48, _('Storm')  # Sturm
    TORNADO = 49, _('Tornado')  # Tornado

    CLEAR_SKY = 50, _('Clear sky')  # Klarer Himmel

    COUPLE_OF_CLOUDS = 51, _('A couple of clouds')  # Ein paar Wolken
    MOSTLY_CLOUDY = 52, _('Mostly cloudy')  # Überwiegend bewölkt
    MOSTLY_CLOUDY2 = 53, _('Mostly cloudy')  # Überwiegend bewölkt
    CLOUDY = 54, _('Cloudy')  # Bewölkt

    def __init__(self, identifier: int, label: str):
        self.identifier: int = identifier
        self.label: str = label

    @classproperty
    def mappings(self) -> Dict[str, str]:
        return dict(map(lambda condition: (condition.identifier, condition.label), WeatherCondition))
