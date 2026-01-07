"""Constants for the CHMI Alerts integration."""

DOMAIN = "chmi_alerts"

# Configuration
CONF_AREA_FILTER = "area_filter"
CONF_LANGUAGE_FILTER = "language_filter"

# Defaults
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour
CHMI_FEED_URL = "https://vystrahy-cr.chmi.cz/data/XOCZ50_OKPR.xml"

# Entity name translations
# Maps language code to the translated word for "Alerts"
ENTITY_NAME_TRANSLATIONS = {
    "cs": "Výstrahy",
    "en": "Alerts",
}

# Attributes
ATTR_HEADLINE = "headline"
ATTR_DESCRIPTION = "description"
ATTR_SEVERITY = "severity"
ATTR_URGENCY = "urgency"
ATTR_CERTAINTY = "certainty"
ATTR_AREA = "area"
ATTR_EFFECTIVE = "effective"
ATTR_EXPIRES = "expires"
ATTR_EVENT = "event"
ATTR_SENDER = "sender"
ATTR_INSTRUCTION = "instruction"
ATTR_CATEGORY = "category"
ATTR_RESPONSE_TYPE = "response_type"
ATTR_AWARENESS_LEVEL = "awareness_level"
ATTR_AWARENESS_TYPE = "awareness_type"

# Awareness levels (compatible with meteoalarm)
AWARENESS_LEVEL_GREEN = "green"
AWARENESS_LEVEL_YELLOW = "yellow"
AWARENESS_LEVEL_ORANGE = "orange"
AWARENESS_LEVEL_RED = "red"

# CAP Severity to awareness level mapping
# Maps CAP severity levels to meteoalarm-compatible awareness levels:
# - Minor: Yellow (Be aware)
# - Moderate/Severe: Orange (Be prepared)
# - Extreme: Red (Take action)
SEVERITY_TO_AWARENESS = {
    "Minor": AWARENESS_LEVEL_YELLOW,
    "Moderate": AWARENESS_LEVEL_ORANGE,
    "Severe": AWARENESS_LEVEL_ORANGE,
    "Extreme": AWARENESS_LEVEL_RED,
}

# Icons for awareness levels
AWARENESS_ICONS = {
    AWARENESS_LEVEL_GREEN: "mdi:check-circle",
    AWARENESS_LEVEL_YELLOW: "mdi:alert",
    AWARENESS_LEVEL_ORANGE: "mdi:alert-circle",
    AWARENESS_LEVEL_RED: "mdi:alert-octagon",
}

# MeteoalarmCard-compatible awareness level format
# Format: "level_id; Color" where level_id is 2-4
AWARENESS_LEVEL_METEOALARM = {
    AWARENESS_LEVEL_GREEN: "1; Green",
    AWARENESS_LEVEL_YELLOW: "2; Yellow",
    AWARENESS_LEVEL_ORANGE: "3; Orange",
    AWARENESS_LEVEL_RED: "4; Red",
}

# Common CAP event types to Meteoalarm event type mapping
# Meteoalarm uses numeric event types (1-13, ID 11 is reserved/unused): https://meteoalarm.org/
# Format: event type ID from 1-13
EVENT_TYPE_METEOALARM = {
    # Weather events
    "Wind": "1; Wind",
    "Snow": "2; Snow/Ice",
    "Ice": "2; Snow/Ice",
    "Snow/Ice": "2; Snow/Ice",
    "Thunderstorm": "3; Thunderstorm",
    "Thunderstorms": "3; Thunderstorm",
    "Fog": "4; Fog",
    "High Temperature": "5; High Temperature",
    "Heat": "5; High Temperature",
    "Low Temperature": "6; Low Temperature",
    "Cold": "6; Low Temperature",
    "Coastal Event": "7; Coastal Event",
    "Forest Fire": "8; Forest Fire",
    "Fire": "8; Forest Fire",
    "Avalanche": "9; Avalanches",
    "Avalanches": "9; Avalanches",
    "Rain": "10; Rain",
    "Flooding": "12; Flooding",
    "Flood": "12; Flooding",
    "Rain-Flood": "13; Rain-Flood",
}

# CISORP location codes from https://apl2.czso.cz/iSMS/cisdet.jsp?kodcis=65
# Dictionary mapping code to name, sorted alphabetically by name using Czech collation
CISORP_CODE_TO_NAME = {
    "4101": "Aš",
    "2101": "Benešov",
    "2102": "Beroun",
    "6201": "Blansko",
    "3101": "Blatná",
    "3201": "Blovice",
    "8102": "Bohumín",
    "6202": "Boskovice",
    "2103": "Brandýs nad Labem-Stará Boleslav",
    "6203": "Brno",
    "5201": "Broumov",
    "8103": "Bruntál",
    "6205": "Bučovice",
    "6101": "Bystřice nad Pernštejnem",
    "7201": "Bystřice pod Hostýnem",
    "4201": "Bílina",
    "8101": "Bílovec",
    "6204": "Břeclav",
    "4102": "Cheb",
    "4203": "Chomutov",
    "6104": "Chotěboř",
    "5304": "Chrudim",
    "2104": "Čáslav",
    "2105": "Černošice",
    "5101": "Česká Lípa",
    "5301": "Česká Třebová",
    "3102": "České Budějovice",
    "2106": "Český Brod",
    "3103": "Český Krumlov",
    "8104": "Český Těšín",
    "3104": "Dačice",
    "5202": "Dobruška",
    "2107": "Dobříš",
    "3202": "Domažlice",
    "5203": "Dvůr Králové nad Labem",
    "4202": "Děčín",
    "8105": "Frenštát pod Radhoštěm",
    "8106": "Frýdek-Místek",
    "5102": "Frýdlant",
    "8107": "Frýdlant nad Ostravicí",
    "6102": "Havlíčkův Brod",
    "8108": "Havířov",
    "5302": "Hlinsko",
    "8109": "Hlučín",
    "6206": "Hodonín",
    "7202": "Holešov",
    "5303": "Holice",
    "3203": "Horažďovice",
    "3204": "Horšovský Týn",
    "5204": "Hořice",
    "2108": "Hořovice",
    "5205": "Hradec Králové",
    "7101": "Hranice",
    "6103": "Humpolec",
    "6207": "Hustopeče",
    "6208": "Ivančice",
    "5103": "Jablonec nad Nisou",
    "8110": "Jablunkov",
    "5206": "Jaroměř",
    "7102": "Jeseník",
    "6105": "Jihlava",
    "5104": "Jilemnice",
    "3105": "Jindřichův Hradec",
    "5207": "Jičín",
    "4204": "Kadaň",
    "3106": "Kaplice",
    "4103": "Karlovy Vary",
    "8111": "Karviná",
    "2109": "Kladno",
    "3205": "Klatovy",
    "2110": "Kolín",
    "7103": "Konice",
    "8112": "Kopřivnice",
    "5208": "Kostelec nad Orlicí",
    "3206": "Kralovice",
    "2111": "Kralupy nad Vltavou",
    "4104": "Kraslice",
    "8113": "Kravaře",
    "8114": "Krnov",
    "7203": "Kroměříž",
    "5305": "Králíky",
    "2112": "Kutná Hora",
    "6209": "Kuřim",
    "6210": "Kyjov",
    "5306": "Lanškroun",
    "5105": "Liberec",
    "7104": "Lipník nad Bečvou",
    "5307": "Litomyšl",
    "4205": "Litoměřice",
    "7105": "Litovel",
    "4206": "Litvínov",
    "4207": "Louny",
    "4208": "Lovosice",
    "7204": "Luhačovice",
    "2113": "Lysá nad Labem",
    "4105": "Mariánské Lázně",
    "6211": "Mikulov",
    "3107": "Milevsko",
    "2115": "Mladá Boleslav",
    "2116": "Mnichovo Hradiště",
    "7106": "Mohelnice",
    "5308": "Moravská Třebová",
    "6106": "Moravské Budějovice",
    "6212": "Moravský Krumlov",
    "4209": "Most",
    "2114": "Mělník",
    "3207": "Nepomuk",
    "2117": "Neratovice",
    "5210": "Nová Paka",
    "6108": "Nové Město na Moravě",
    "5211": "Nové Město nad Metují",
    "5106": "Nový Bor",
    "5212": "Nový Bydžov",
    "8115": "Nový Jičín",
    "2118": "Nymburk",
    "5209": "Náchod",
    "6107": "Náměšť nad Oslavou",
    "3208": "Nýřany",
    "8116": "Odry",
    "7107": "Olomouc",
    "8117": "Opava",
    "8118": "Orlová",
    "8119": "Ostrava",
    "4106": "Ostrov",
    "7205": "Otrokovice",
    "6109": "Pacov",
    "5309": "Pardubice",
    "6110": "Pelhřimov",
    "3209": "Plzeň",
    "4210": "Podbořany",
    "2119": "Poděbrady",
    "6213": "Pohořelice",
    "5310": "Polička",
    "3109": "Prachatice",
    "1000": "Praha",
    "7108": "Prostějov",
    "3108": "Písek",
    "5311": "Přelouč",
    "7109": "Přerov",
    "3210": "Přeštice",
    "2120": "Příbram",
    "2121": "Rakovník",
    "2122": "Říčany",
    "3211": "Rokycany",
    "6214": "Rosice",
    "4211": "Roudnice nad Labem",
    "7206": "Rožnov pod Radhoštěm",
    "4212": "Rumburk",
    "5213": "Rychnov nad Kněžnou",
    "8120": "Rýmařov",
    "2123": "Sedlčany",
    "5107": "Semily",
    "2124": "Slaný",
    "6215": "Slavkov u Brna",
    "3110": "Soběslav",
    "4107": "Sokolov",
    "3212": "Stod",
    "3111": "Strakonice",
    "3213": "Stříbro",
    "3214": "Sušice",
    "5312": "Svitavy",
    "6111": "Světlá nad Sázavou",
    "6216": "Šlapanice",
    "7110": "Šternberk",
    "7111": "Šumperk",
    "3215": "Tachov",
    "5108": "Tanvald",
    "6112": "Telč",
    "4213": "Teplice",
    "6217": "Tišnov",
    "3113": "Trhové Sviny",
    "5214": "Trutnov",
    "5109": "Turnov",
    "3112": "Tábor",
    "3115": "Týn nad Vltavou",
    "3114": "Třeboň",
    "6113": "Třebíč",
    "8121": "Třinec",
    "7207": "Uherské Hradiště",
    "7208": "Uherský Brod",
    "7112": "Uničov",
    "4214": "Ústí nad Labem",
    "5313": "Ústí nad Orlicí",
    "7209": "Valašské Klobouky",
    "7210": "Valašské Meziříčí",
    "4215": "Varnsdorf",
    "6114": "Velké Meziříčí",
    "6218": "Veselí nad Moravou",
    "3116": "Vimperk",
    "7211": "Vizovice",
    "2125": "Vlašim",
    "3117": "Vodňany",
    "2126": "Votice",
    "5215": "Vrchlabí",
    "7212": "Vsetín",
    "5314": "Vysoké Mýto",
    "6219": "Vyškov",
    "8122": "Vítkov",
    "5315": "Žamberk",
    "4216": "Žatec",
    "6115": "Žďár nad Sázavou",
    "5110": "Železný Brod",
    "6221": "Židlochovice",
    "7213": "Zlín",
    "6220": "Znojmo",
    "7113": "Zábřeh",
}
