# COVID-19 stats tracker, by Randy Glenn - February 2021
# MIT License
# See https://api.covid19tracker.ca/docs/1.0/overview for API info

# Libraries required in the lib/ folder:
# - adafruit_bitmap_font/
# - adafruit_display_text/
# - adafruit_imageload/
# - adafruit_io/
# - adafruit_magtag/
# - adafruit_portalbase/
# - adafruit_fakerequests.mpy
# - adafruit_requests.mpy
# - neopixel.mpy
# - simpleio.mpy

import time
from adafruit_magtag.magtag import MagTag

# in seconds, we can refresh about 100 times on a battery
TIME_BETWEEN_REFRESHES = 4 * 60 * 60  # once every 4 hours delay

# Set up data location
DATA_SOURCE_CA = "https://api.covid19tracker.ca/summary/"
DATA_SOURCE_PROV = "https://api.covid19tracker.ca/summary/split/"

# Set up the MagTag with a bitmap background.
# Originally tried using text fields, but MagTag library only allows 15
magtag = MagTag(
    default_bg="/background.bmp",
)

# Function to pull the data from COVID19Tracker.ca API,
# and extract relevant parameters
# idx = -1 for all-Canada, and index number from summary/split API for provinces
def get_data(idx=-1):
    if idx == -1:
        resp = magtag.network.fetch(DATA_SOURCE_CA)
        idx = 0
    else:
        resp = magtag.network.fetch(DATA_SOURCE_PROV)
    json_data = resp.json()
    return int(json_data["data"][idx]["total_cases"]), int(json_data["data"][idx]["change_cases"]), int(json_data["data"][idx]["total_vaccinations"]), int(json_data["data"][idx]["change_vaccinations"]), int(json_data["data"][idx]["total_vaccinated"]), int(json_data["data"][idx]["change_vaccinated"])

# FUN FACT! You probably don't have the Nu Sans font family, and I can't distribute it.
# Visit http://www.scootergraphics.com/nusans/ to buy it, because it's awesome,
# and then visit https://learn.adafruit.com/custom-fonts-for-pyportal-circuitpython-display/conversion
# to learn how to convert the .ttf fonts to .bdf here. Use nusansa.ttf to convert, in 10 and 12 pixel heights.
# Or, just switch it to another font. But Nu Sans looks much cooler.

# Index 0, total cases for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 42),
)

# Index 1, new cases for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 54),
)

# Index 2, total shots for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 66),
)

# Index 3, new shots for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 78),
)

# Index 4, total vaccinated (both shots) for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 90),
)

# Index 5, new vaccinated (both shots) for Canada
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(120, 102),
)

# Index 6, total cases for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 42),
)

# Index 7, new cases for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 54),
)

# Index 8, total shots for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 66),
)

# Index 9, new shots for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 78),
)

# Index 10, total vaccinated (both shots) for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 90),
)

# Index 11, new vaccinated (both shots) for province
magtag.add_text(
    text_font="NuSans-12.bdf",
    text_position=(210, 102),
)

# Index 12, last updated timestamp
magtag.add_text(
    text_font="NuSans-10.bdf",
    text_position=(10, 118),
    is_data=False
)

# Index 13, battery status widget
magtag.add_text(
    text_font="NuSans-10.bdf",
    text_position=(235, 118),
    is_data=False
)

try:
    # Have the MagTag connect to the internet
    try:
        magtag.network.connect()
    except (ConnectionError, ValueError, RuntimeError) as e:
        # We wait 4h if network connect fails. Which it does sometimes, for no reason.
        # But if we connect more often when it fails, we'll drain the battery faster.
        # Could probably shorten the delay on connect failure
        magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)

    # Display update time! We turn off auto-refresh on all but the last set_text call to only refresh the display once. Saves battery, fewer flashes.

    # We're pulling the time from adafruit.io. Could probably pull this time from the COVID API instead.
    magtag.get_local_time()
    myTime = time.localtime()
    print("Last updated: {}-{}-{} {}:{:02d}".format(myTime.tm_mday, myTime.tm_mon, myTime.tm_year, myTime.tm_hour, myTime.tm_min))
    magtag.set_text(val="Last updated: {}-{}-{} {}:{:02d}".format(myTime.tm_mday, myTime.tm_mon, myTime.tm_year, myTime.tm_hour, myTime.tm_min), index=12, auto_refresh=False)

    # An experiment showed that the battery lasted all the way down to about 2.71 volts, but the falloff from 3.2 to 2.71 was around a day.
    # This gives enough warning to charge it, without having to do it immediately.
    if (magtag.peripherals.battery < 3.5):
        magtag.set_text(val="Battery low", index=13, auto_refresh=False)

    # Pulling data for all-Canada and the selected province.
    # Why don't we use magtag.fetch()? Because it only works with one JSON source, and we need two.
    ca_cases, ca_new_cases, ca_shots, ca_new_shots, ca_vaccinated, ca_new_vaccinated = get_data(-1)
    on_cases, on_new_cases, on_shots, on_new_shots, on_vaccinated, on_new_vaccinated = get_data(0)

    # Put it all on the screen
    magtag.set_text(val="{:,d}".format(ca_cases), index=0, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(ca_new_cases), index=1, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(ca_shots), index=2, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(ca_new_shots), index=3, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(ca_vaccinated), index=4, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(ca_new_vaccinated), index=5, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_cases), index=6, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_new_cases), index=7, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_shots), index=8, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_new_shots), index=9, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_vaccinated), index=10, auto_refresh=False)
    magtag.set_text(val="{:,d}".format(on_new_vaccinated), index=11)
    
except (ValueError, RuntimeError) as e:
    print("Some error occured, retrying! -", e)

# wait 2 seconds for display to complete
time.sleep(2)
magtag.exit_and_deep_sleep(TIME_BETWEEN_REFRESHES)
