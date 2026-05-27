"""
World Cup 2026 — Static reference data.

Everything that doesn't change during a simulation lives here:
- The 12 groups and 48 teams
- The 72 group-stage fixtures with venues
- Training base coordinates for all 48 teams
- 2026 venue coordinates
- The knockout-round pairing logic
"""

# ============================================================
# GROUPS (the 12 groups of 4 teams as drawn)
# ============================================================

GROUPS_2026 = {
    "A": ["Mexico", "South Korea", "South Africa", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curaçao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

ALL_TEAMS_2026 = [t for group in GROUPS_2026.values() for t in group]


# ============================================================
# GROUP-STAGE FIXTURES (real schedule)
# ============================================================

GROUP_FIXTURES = [
    # Group A
    ("Mexico", "South Africa", "Mexico City"),
    ("South Korea", "Czech Republic", "Guadalajara"),
    ("Mexico", "South Korea", "Guadalajara"),
    ("Czech Republic", "South Africa", "Atlanta"),
    ("Czech Republic", "Mexico", "Mexico City"),
    ("South Africa", "South Korea", "Monterrey"),
    # Group B
    ("Canada", "Bosnia and Herzegovina", "Toronto"),
    ("Qatar", "Switzerland", "San Francisco"),
    ("Canada", "Qatar", "Vancouver"),
    ("Switzerland", "Bosnia and Herzegovina", "Los Angeles"),
    ("Switzerland", "Canada", "Vancouver"),
    ("Bosnia and Herzegovina", "Qatar", "Seattle"),
    # Group C
    ("Brazil", "Morocco", "New York/NJ"),
    ("Haiti", "Scotland", "Boston"),
    ("Scotland", "Morocco", "Boston"),
    ("Brazil", "Haiti", "Philadelphia"),
    ("Scotland", "Brazil", "Miami"),
    ("Morocco", "Haiti", "Atlanta"),
    # Group D
    ("United States", "Paraguay", "Los Angeles"),
    ("Australia", "Turkey", "Vancouver"),
    ("United States", "Australia", "Seattle"),
    ("Turkey", "Paraguay", "San Francisco"),
    ("Turkey", "United States", "Los Angeles"),
    ("Paraguay", "Australia", "San Francisco"),
    # Group E
    ("Germany", "Curaçao", "Houston"),
    ("Ivory Coast", "Ecuador", "Philadelphia"),
    ("Germany", "Ivory Coast", "Toronto"),
    ("Ecuador", "Curaçao", "Kansas City"),
    ("Ecuador", "Germany", "New York/NJ"),
    ("Curaçao", "Ivory Coast", "Philadelphia"),
    # Group F
    ("Netherlands", "Japan", "Dallas"),
    ("Sweden", "Tunisia", "Monterrey"),
    ("Tunisia", "Japan", "Monterrey"),
    ("Netherlands", "Sweden", "Houston"),
    ("Japan", "Sweden", "Dallas"),
    ("Tunisia", "Netherlands", "Kansas City"),
    # Group G
    ("Belgium", "Egypt", "Vancouver"),
    ("Iran", "New Zealand", "Los Angeles"),
    ("Belgium", "Iran", "Los Angeles"),
    ("New Zealand", "Egypt", "Vancouver"),
    ("Egypt", "Iran", "Seattle"),
    ("New Zealand", "Belgium", "Vancouver"),
    # Group H
    ("Spain", "Cape Verde", "Atlanta"),
    ("Saudi Arabia", "Uruguay", "Miami"),
    ("Spain", "Saudi Arabia", "Atlanta"),
    ("Uruguay", "Cape Verde", "Miami"),
    ("Uruguay", "Spain", "Guadalajara"),
    ("Cape Verde", "Saudi Arabia", "Houston"),
    # Group I
    ("France", "Senegal", "New York/NJ"),
    ("Iraq", "Norway", "Boston"),
    ("France", "Iraq", "Philadelphia"),
    ("Norway", "Senegal", "New York/NJ"),
    ("Norway", "France", "Boston"),
    ("Senegal", "Iraq", "Toronto"),
    # Group J
    ("Argentina", "Algeria", "Kansas City"),
    ("Austria", "Jordan", "San Francisco"),
    ("Argentina", "Austria", "Dallas"),
    ("Jordan", "Algeria", "San Francisco"),
    ("Algeria", "Austria", "Kansas City"),
    ("Jordan", "Argentina", "Dallas"),
    # Group K
    ("Portugal", "DR Congo", "Houston"),
    ("Uzbekistan", "Colombia", "Mexico City"),
    ("Portugal", "Uzbekistan", "Houston"),
    ("Colombia", "DR Congo", "Guadalajara"),
    ("Colombia", "Portugal", "Miami"),
    ("DR Congo", "Uzbekistan", "Atlanta"),
    # Group L
    ("England", "Croatia", "Dallas"),
    ("Ghana", "Panama", "Toronto"),
    ("England", "Ghana", "Boston"),
    ("Panama", "Croatia", "Toronto"),
    ("Panama", "England", "New York/NJ"),
    ("Croatia", "Ghana", "Philadelphia"),
]


# ============================================================
# VENUE COORDINATES (16 cities)
# ============================================================

VENUES_2026 = {
    "Atlanta":       (33.7553, -84.4006),
    "Boston":        (42.0909, -71.2643),
    "Dallas":        (32.7473, -97.0945),
    "Houston":       (29.6847, -95.4107),
    "Kansas City":   (39.0489, -94.4839),
    "Los Angeles":   (33.9535, -118.3392),
    "Miami":         (25.9580, -80.2389),
    "New York/NJ":   (40.8136, -74.0744),
    "Philadelphia":  (39.9008, -75.1675),
    "San Francisco": (37.4030, -121.9700),
    "Seattle":       (47.5952, -122.3316),
    "Mexico City":   (19.3029, -99.1505),
    "Guadalajara":   (20.6817, -103.4625),
    "Monterrey":     (25.6692, -100.2444),
    "Toronto":       (43.6332, -79.4187),
    "Vancouver":     (49.2768, -123.1117),
}


# ============================================================
# TRAINING BASES (from official FIFA list, May 2026)
# ============================================================

TRAINING_BASES = {
    "Algeria":                {"city": "Kansas City, KS",     "coords": (38.9543, -95.2558)},
    "Argentina":              {"city": "Kansas City, KS",     "coords": (38.9543, -94.4900)},
    "Australia":              {"city": "Oakland, CA",         "coords": (37.7510, -122.2008)},
    "Austria":                {"city": "Goleta, CA",          "coords": (34.4140, -119.8489)},
    "Belgium":                {"city": "Renton, WA",          "coords": (47.4829, -122.2171)},
    "Bosnia and Herzegovina": {"city": "Sandy, UT",           "coords": (40.5649, -111.8389)},
    "Brazil":                 {"city": "New Jersey",          "coords": (40.7945, -74.0237)},
    "Cape Verde":             {"city": "Tampa, FL",           "coords": (27.9506, -82.4572)},
    "Ivory Coast":            {"city": "Philadelphia, PA",    "coords": (39.9008, -75.1675)},
    "Croatia":                {"city": "Alexandria, VA",      "coords": (38.8048, -77.0469)},
    "Curaçao":                {"city": "Boca Raton, FL",      "coords": (26.3683, -80.1289)},
    "Czech Republic":         {"city": "Mansfield, TX",       "coords": (32.5632, -97.1417)},
    "DR Congo":               {"city": "Houston, TX",         "coords": (29.7604, -95.3698)},
    "Ecuador":                {"city": "Columbus, OH",        "coords": (40.0019, -83.0204)},
    "Egypt":                  {"city": "Spokane, WA",         "coords": (47.6671, -117.4025)},
    "England":                {"city": "Kansas City, MO",     "coords": (39.0489, -94.5786)},
    "France":                 {"city": "Waltham, MA",         "coords": (42.3884, -71.2200)},
    "Germany":                {"city": "Winston-Salem, NC",   "coords": (36.1349, -80.2784)},
    "Ghana":                  {"city": "Smithfield, RI",      "coords": (41.9176, -71.5444)},
    "Haiti":                  {"city": "Galloway, NJ",        "coords": (39.4969, -74.5378)},
    "Iraq":                   {"city": "Greenbrier, WV",      "coords": (37.7826, -80.3092)},
    "Japan":                  {"city": "Nashville, TN",       "coords": (36.1627, -86.7816)},
    "Jordan":                 {"city": "Portland, OR",        "coords": (45.5712, -122.7270)},
    "Morocco":                {"city": "Basking Ridge, NJ",   "coords": (40.7029, -74.5532)},
    "Netherlands":            {"city": "Kansas City, MO",     "coords": (39.1059, -94.5778)},
    "New Zealand":            {"city": "San Diego, CA",       "coords": (32.7710, -117.1880)},
    "Norway":                 {"city": "Greensboro, NC",      "coords": (36.0726, -79.8108)},
    "Paraguay":               {"city": "San Jose, CA",        "coords": (37.3346, -121.8810)},
    "Portugal":               {"city": "Palm Beach Gardens, FL", "coords": (26.8447, -80.1373)},
    "Qatar":                  {"city": "Santa Barbara, CA",   "coords": (34.4566, -119.6555)},
    "Saudi Arabia":           {"city": "Austin, TX",          "coords": (30.3886, -97.7197)},
    "Scotland":               {"city": "Charlotte, NC",       "coords": (35.2249, -80.8459)},
    "Senegal":                {"city": "Piscataway, NJ",      "coords": (40.5187, -74.4624)},
    "Spain":                  {"city": "Chattanooga, TN",     "coords": (35.0182, -85.2811)},
    "Sweden":                 {"city": "Frisco, TX",          "coords": (33.1551, -96.8358)},
    "Switzerland":            {"city": "San Diego, CA",       "coords": (32.8131, -117.1380)},
    "Turkey":                 {"city": "Mesa, AZ",            "coords": (33.4152, -111.8315)},
    "United States":          {"city": "Irvine, CA",          "coords": (33.6839, -117.7947)},
    "Uzbekistan":             {"city": "Atlanta, GA",         "coords": (33.7600, -84.3900)},
    "Colombia":               {"city": "Guadalajara",         "coords": (20.6597, -103.3496)},
    "Iran":                   {"city": "Tijuana",             "coords": (32.5149, -117.0382)},
    "South Korea":            {"city": "Guadalajara",         "coords": (20.6597, -103.3496)},
    "Mexico":                 {"city": "Mexico City",         "coords": (19.4326, -99.1332)},
    "South Africa":           {"city": "Pachuca",             "coords": (20.1011, -98.7591)},
    "Tunisia":                {"city": "Monterrey",           "coords": (25.6866, -100.3161)},
    "Uruguay":                {"city": "Cancún",              "coords": (21.1619, -86.8515)},
    "Canada":                 {"city": "Vancouver",           "coords": (49.2827, -123.1207)},
    "Panama":                 {"city": "New Tecumseth, ON",   "coords": (44.1500, -79.8667)},
}


# ============================================================
# KNOCKOUT ROUND PAIRING (which prior match feeds which slot)
# ============================================================

R16_PAIRS = {89: (74, 77), 90: (73, 75), 91: (76, 78), 92: (79, 80),
             93: (83, 84), 94: (81, 82), 95: (86, 88), 96: (85, 87)}
QF_PAIRS = {97: (89, 90), 98: (93, 94), 99: (91, 92), 100: (95, 96)}
SF_PAIRS = {101: (97, 98), 102: (99, 100)}
