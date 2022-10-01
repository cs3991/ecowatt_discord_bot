import locale
from dataclasses import dataclass
from datetime import datetime, time, date
from enum import Enum

locale.setlocale(locale.LC_TIME, "fr_FR")


class EcoWattValue(Enum):
    GREEN = 1
    ORANGE = 2
    RED = 3


@dataclass
class EcoWattDay:
    day: date
    value: EcoWattValue
    hours: tuple["EcoWattHour"]

    @staticmethod
    def from_json(day_json) -> "EcoWattDay":
        """Create an EcoWattDay from a JSON object"""
        return EcoWattDay(day=datetime.strptime(day_json["jour"], "%Y-%m-%dT%H:%M:%S%z").date(),
                          value=EcoWattValue(day_json['dvalue']),
                          hours=tuple(EcoWattHour.from_json(hour_json) for hour_json in day_json['values']))

    def __str__(self) -> str:
        formatted_hours = '\n'.join([str(s) for s in self.hours])
        return f"{self.day}: {self.value}\n" \
               f" {formatted_hours}"

    def _get_hour_ranges_of_stress(self) -> list[list[time, time]]:
        """Return a tuple of tuples of time objects, each tuple representing a range of hours where the consumption
        is too high"""
        ranges = []
        current_range = None
        for hour in self.hours:
            if hour.value != EcoWattValue.GREEN:
                current_hour = hour.hour
                next_hour_int = current_hour.hour + 1
                if next_hour_int == 24:
                    next_hour_int = 0
                next_hour = time(hour=next_hour_int)
                if current_range is None:
                    current_range = [current_hour, next_hour]
                    ranges.append(current_range)
                else:
                    current_range[1] = next_hour
            else:
                current_range = None
        return ranges

    def pretty_print(self) -> str:
        color_map = {
            EcoWattValue.GREEN: "🟩",
            EcoWattValue.ORANGE: "🟧",
            EcoWattValue.RED: "🟥"
            }
        message_map = {
            EcoWattValue.GREEN: f"✅ Notre consommation électrique sera normale.",
            EcoWattValue.ORANGE: f"⚠️ Notre consommation électrique sera trop élevée, le système électrique sera "
                                 f"tendu.",
            EcoWattValue.RED: f"🚨️ Notre consommation électrique sera beaucoup trop élevée, les coupures seront "
                              f"inévitables si nous ne baissons pas notre consommation."
            }
        hour_colors = ""
        for hour in self.hours:
            hour_colors += color_map[hour.value]
        if self.value != EcoWattValue.GREEN:
            consumption_advice = 'Réduisez votre consommation électrique entre :\n'
        else:
            consumption_advice = ''
        for hour_range in self._get_hour_ranges_of_stress():
            consumption_advice += f"- {hour_range[0].strftime('%H:%M')} et {hour_range[1].strftime('%H:%M')}\n"
        return f"**{self.day.strftime('%A %d %B %Y').capitalize()}** {color_map[self.value]}\n" \
               f"{message_map[self.value]}\n" \
               f"`{hour_colors}`\n" \
               f"{consumption_advice}" \
               f"Plus d'informations sur <https://www.monecowatt.fr>\n"


@dataclass
class EcoWattHour:
    hour: time
    value: EcoWattValue

    @staticmethod
    def from_json(hour_json) -> "EcoWattHour":
        """Create an EcoWattHour from a json of the form  {'pas': 0,'hvalue': 1}"""
        return EcoWattHour(hour=time(hour=hour_json['pas']), value=EcoWattValue(hour_json['hvalue']))

    def __str__(self) -> str:
        return f"{self.hour}: {self.value.name}"
