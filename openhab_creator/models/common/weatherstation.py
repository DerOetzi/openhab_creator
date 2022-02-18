from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from openhab_creator import CreatorEnum, _, classproperty


class WeatherCondition(CreatorEnum):
    THUNDERSTORM_WITH_LIGHT_RAIN = 1, _(
        'Thunderstorm with light rain')  # Gewitter mit leichtem Regen
    THUNDERSTORM_WITH_RAIN = 2, _(
        'Thunderstorm with rain'), 1  # Gewitter mit Regen
    THUNDERSTORM_WITH_HEAVY_RAIN = 3, _(
        'Thunderstorm with heavy rain'), 1  # Gewitter mit starkem Regen
    LIGHT_THUNDERSTORM = 4, _('Light thunderstorm'), 1  # Leichtes Gewitter
    THUNDERSTORM = 5, _('Thunderstorm'), 1  # Gewitter
    HEAVY_THUNDERSTORM = 6, _('Heavy thunderstorm'), 1  # Starkes Gewitter
    ROUGH_THUNDERSTORM = 7, _('Rough thunderstorm'), 1  # Raues Gewitter
    THUNDERSTORM_WITH_LIGHT_DRIZZLE = 8, _(
        'Thunderstorm with light drizzle'), 1  # Gewitter mit leichtem Nieselregen
    THUNDERSTORM_WITH_DRIZZLE = 9, _(
        'Thunderstorm with drizzle'), 1  # Gewitter mit Nieselregen
    THUNDERSTORM_WITH_HEAVY_DRIZZLE = 10, _(
        'Thunderstorm with heavy drizzle'), 1  # Gewitter mit starkem Nieselregen

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
    VERY_HEAVY_RAIN = 23, _('Very heavy rain'), 22  # Sehr schwerer Regen
    EXTREME_RAIN = 24, _('Extreme rain'), 22  # Extremer Regen

    FREEZING_RAIN = 25, _('Freezing rain')  # Gefrierender Regen

    LIGHT_RAIN_SHOWER = 26, _('Light rain shower')  # Leichter Regenschauer
    RAIN_SHOWER = 27, _('Rain shower')  # Regenschauer
    HEAVY_RAIN_SHOWER = 28, _('Heavy rain shower')  # Starker Regenschauer
    VERY_HEAVY_RAIN_SHOWER = 29, _(
        'Very heavy rain shower'), 28  # Sehr starker Regenschauer

    MODERATE_SNOW = 30, _('Moderate snow')  # Mäßiger Schnee
    SNOWFALL = 31, _('Snowfall')  # Schneefall
    HEAVY_SNOWFALL = 32, _('Heavy snowfall')  # Starker Schneefall
    SLEET = 33, _('Sleet')  # Schneeregen
    SLEET2 = 34, _('Sleet'), 33  # Graupelschauer
    # Leichter Regen und Schnee
    LIGHT_RAIN_AND_SNOW = 35, _('Light rain and snow'), 33
    RAIN_AND_SNOW = 36, _('Rain and snow'), 33  # Regen und Schnee
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
    MOSTLY_CLOUDY = 52, _('Mostly cloudy'), 51  # Überwiegend bewölkt
    MOSTLY_CLOUDY2 = 53, _('Mostly cloudy')  # Überwiegend bewölkt
    CLOUDY = 54, _('Cloudy'), 53  # Bewölkt

    def __init__(self, identifier: int, label: str, icon: Optional[int] = None):
        self.identifier: int = identifier
        self.label: str = label
        self.icon: Optional[int] = icon

    @classproperty
    def mappings(cls) -> Dict[str, str]:
        #pylint: disable=no-self-argument
        return dict(map(lambda condition: (condition.identifier, condition.label),
                        cls))

    @classproperty
    def mapping_icons(cls) -> List[Tuple[int, int]]:
        #pylint: disable=no-self-argument
        return list(map(lambda condition: (condition.identifier, condition.icon),
                        filter(lambda condition: condition.identifier != '-'
                               and condition.icon is not None, cls)))


class DWDSeverity(CreatorEnum):
    MINOR = 'Minor', _('Minor weather warning')
    MODERATE = 'Moderate', _('Moderate weather warning')
    SEVERE = 'Severe', _('Severe weather warning')
    EXTREME = 'Extreme', _('Extreme weather warning')
    NULL = 'NULL', _('Weather warning')
    UNKNOWN = '-', _('Weather warning')

    def __init__(self, severity: int, label: str):
        self.severity: int = severity
        self.label: str = label

    @classproperty
    def mappings(cls) -> Dict[str, str]:
        #pylint: disable=no-self-argument
        return dict(map(lambda severity: (severity.severity, severity.label),
                        cls))


class DWDEvent(CreatorEnum):
    HITZE = 10, 'HITZE', 'Hitze'
    STARKE_HITZE = 11, 'STARKEHITZE', 'Starke Hitze', 10
    FROST = 22, 'FROST', 'Frost'
    GLAETTE = 24, 'GLÄTTE', 'Glätte', 22
    VERBREITET_GLAETTE = 25, 'VERBREITETGLÄTTE', 'Verbreitet Glätte', 22
    GEWITTER = 31, 'GEWITTER', 'Gewitter'
    STARKES_GEWITTER = 33, 'STARKESGEWITTER', 'Starkes Gewitter', 31
    SCHWERES_GEWITTER_MIT_ORKANBOEEN = 40,\
        'SCHWERESGEWITTERmitORKANBÖEN',\
        'Schweres Gewitter mit Orkanböen',\
        31
    SCHWERES_GEWITTER_MIT_EXTREMEN_ORKANBOEEN = 41,\
        'SCHWERESGEWITTERmitEXTREMENORKANBÖEN',\
        'Schweres Gewitter mit extremen Orkanböen',\
        31
    SCHWERES_GEWITTER_MIT_HEFTIGEM_STARKREGEN = 42,\
        'SCHWERESGEWITTERmitHEFTIGEMSTARKREGEN',\
        'Schweres Gewitter mit heftigem Starkregen',\
        31
    SCHWERES_GEWITTER_MIT_ORKANBOEEN_UND_HEFTIGEM_STARKREGEN = 44,\
        'SCHWERESGEWITTERmitORKANBÖENundHEFTIGEMSTARKREGEN',\
        'Schweres_Gewitter mit Orkanböen und hefitgem Starkregen',\
        31
    SCHWERES_GEWITTER_MIT_EXTREMEN_ORKANBOEEN_UND_HEFTIGEM_STARKREGEN = 45,\
        'SCHWERESGEWITTERmitEXTREMENORKANBÖENundHEFTIGEMSTARKREGEN',\
        'Schweres Gewitter mit extremen Orkanböen und heftigem Starkregen',\
        31
    SCHWERES_GEWITTER_MIT_HEFTIGEM_STARKREGEN_UND_HAGEL = 46,\
        'SCHWERESGEWITTERmitHEFTIGEMSTARKREGENundHAGEL',\
        'Schweres Gewitter mit heftigem Starkregen und Hagel',\
        31
    SCHWERES_GEWITTER_MIT_ORKANBOEEN_HEFTIGEM_STARKREGEN_UND_HAGEL = 48,\
        'SCHWERESGEWITTERmitORKANBÖEN, HEFTIGEMSTARKREGENundHAGEL',\
        'Schweres Gewitter mit Orkanböen, heftige Starkregen und Hagel',\
        31
    SCHWERES_GEWITTER_MIT_EXTREMEN_ORKANBOEEN_HEFTIGEM_STARKREGEN_UND_HAGEL = 49,\
        'SCHWERESGEWITTERmitEXTREMENORKANBÖEN, HEFTIGEMSTARKREGENundHAGEL', \
        'Schweres Gewitter mit extremen Orkanböen, heftigem Starkregen und Hagel',\
        31
    WINDBOEN = 51, 'WINDBÖEN', 'Windböen'
    STURMBÖEN = 52, 'STURMBÖEN', 'Sturmböen', 51
    SCHWERE_STURMBOEEN = 53, 'SCHWERESTURMBÖEN', 'Schwere Sturmböen', 51
    ORKANARTIGE_BOEEN = 54, 'ORKANARTIGEBÖEN', 'Orkanartige Böen', 51
    ORKANBOEEN = 55, 'ORKANBÖEN', 'Orkanböen', 51
    EXTREME_ORKANBOEEN = 56, 'EXTREMEORKANBÖEN', 'Extreme Orkanböen', 51
    NEBEL = 59, 'NEBEL', 'Nebel'
    STARKREGEN = 61, 'STARKREGEN', 'Starkregen'
    HEFTIGER_STARKREGEN = 62, 'HEFTIGERSTARKREGEN', 'Heftiger Starkregen', 61
    DAUERREGEN = 64, 'DAUERREGEN', 'Dauerregen', 61
    ERGIEBIGER_DAUERREGEN = 64, 'ERGIEBIGERDAUERREGEN', 'Ergiebiger Dauerregen', 61
    EXTREM_ERGIEBIGER_DAUERREGEN = 65, \
        'EXTREMERGIEBIGERDAUERREGEN', \
        'Extrem ergiebiger Dauerregen', \
        61
    EXTREM_HEFTIGER_STARKREGEN = 66, 'EXTREMHEFTIGERSTARKREGEN', 'Extrem heftiger Starkregen', 61
    LEICHTER_SCHNEEFALL = 70, 'LEICHTERSCHNEEFALL', 'Leichter Schneefall'
    SCHNEEFALL = 71, 'SCHNEEFALL', 'Schneefall'
    STARKER_SCHNEEFALL = 72, 'STARKERSCHNEEFALL', 'Starker Schneefall', 71
    EXTREM_STARKER_SCHNEEFALL = 73, 'EXTREMSTARKERSCHNEEFALL', 'Extrem starker Schneefall', 71
    SCHNEEVERWEHUNG = 74, 'SCHNEEVERWEHUNG', 'Schneeverwehung', 71
    STARKE_SCHNEEVERWEHUNG = 75, 'STARKESCHNEEVERWEHUNG', 'Starke Schneeverwehung', 71
    SCHNEEFALL_UND_SCHNEEVERWEHUNG_EXTREM_STARKE_SCHNEEVERWEHUNG = 76,\
        'SCHNEEFALLundSCHNEEVERWEHUNGEXTREMSTARKESCHNEEVERWEHUNG',\
        'Schneefall und Schneeverwehung extrem starke Schneeverwehung',\
        71
    STARKER_SCHNEEFALL_UND_SCHNEEVERWEHUNG = 77,\
        'STARKERSCHNEEFALLundSCHNEEVERWEHUNG',\
        'Starker Schneefall und Schneeverwehung',\
        71
    EXTREM_STARKER_SCHNEEFALL_UND_SCHNEEVERWEHUNG = 78,\
        'EXTREMSTARKERSCHNEEFALLundSCHNEEVERWEHUNG',\
        'Extrem starker Schneefall und Schneeverwehung',\
        71
    LEITERSEILSCHWINGUNGEN = 79, 'LEITERSEILSCHWINGUNGEN', 'Leiterseilschwingungen'
    STRENGER_FROST = 82, 'STRENGERFROST', 'Strenger Frost'
    GLATTEIS = 85, 'GLATTEIS', 'Glatteis', 82
    TAUWETTER = 88, 'TAUWETTER', 'Tauwetter', 82
    STARKES_TAUWETTER = 89, 'STARKESTAUWETTER', 'Starkes Tauwetter', 82
    SCHWERES_GEWITTER = 93, 'SCHWERESGEWITTER', 'Schweres Gewitter', 90
    EXTREMES_GEWITTER = 93, 'EXTREMESGEWITTER', 'Extremes Gewitter', 90
    SCHWERES_GEWITTER_MIT_EXTREM_HEFTIGEM_STARKREGEN_UND_HAGEL = 95,\
        'SCHWERESGEWITTERmitEXTREMHEFTIGEMSTARKREGENundHAGEL',\
        'Schweres Gewitter mit extrem heftigem Starkregen und Hagel',\
        90
    EXTREMES_GEWITTER_MIT_ORKANBOEEN_EXTREM_HEFTIGEM_STARKREGEN_UND_HAGEL = 96,\
        'EXTREMESGEWITTERmitORKANBÖEN, EXTREMHEFTIGEMSTARKREGENundHAGEL',\
        'Extremes Gewitter mit Orkanböen, extrem heftigem Starkregen und Hagel',\
        90
    TEST_WARNUNG = 98, 'TEST-WARNUNG', 'Testwarnung'
    TEST_UNWETTERWARNUNG = 99, 'TEST-UNWETTERWARNUNG', 'Testunwetterwarnung'
    KEINE_WARNUNG = 0, '', 'Keine Warnung'
    KEINE_WARNUNG2 = '-', '', 'Keine Warnung'

    def __init__(self, identifier: int, keyword: str, label: str, icon: Optional[int] = None):
        self.identifier: int = identifier
        self.keyword: str = keyword
        self.label: str = label
        self.icon: Optional[int] = icon

    @classproperty
    def mappings_keyword(cls) -> Dict[str, str]:
        #pylint: disable=no-self-argument
        return dict(map(lambda dwdevent: (dwdevent.keyword, dwdevent.identifier),
                        cls))

    @classproperty
    def mappings_label(cls) -> Dict[str, str]:
        #pylint: disable=no-self-argument
        return dict(map(lambda dwdevent: (dwdevent.identifier, dwdevent.label),
                        cls))

    @classproperty
    def mapping_icons(cls) -> List[Tuple[int, int]]:
        #pylint: disable=no-self-argument
        return list(map(lambda dwdevent: (dwdevent.identifier, dwdevent.icon),
                        filter(lambda dwdevent: dwdevent.identifier != '-'
                               and dwdevent.icon is not None, cls)))
