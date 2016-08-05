"""
kRPC Handsfree2Orbit 1.0

Description:
Python program to bring my Handsfree 1 rocket in orbit in Kerbal Space Program.

To run this KSP kRPC Python program you need:
- Kerbal Space Program (tested in 1.1.3)
- kRPC 0.3.5 (https://mods.curse.com/ksp-mods/kerbal/220219-krpc-control-the-game-using-c-c-java-lua-python)
  Use the install guide on https://krpc.github.io/krpc/getting-started.html
- I've also installed the Python client library (https://pypi.python.org/pypi/krpc)
- Python 2.7 (https://www.python.org/download/releases/2.7/)

When installed, install the .craft file (Handsfree 1.craft).
Go to the directory with this program, start Python command line and run:
execfile('kRPC_Orbital1_scrout.py')

Good luck!
"""

import krpc
import time


conn = krpc.connect(name='Orbital flight script')
canvas = conn.ui.stock_canvas

# Get the size of the game window in pixels
screen_size = canvas.rect_transform.size

# Add a panel to contain the UI elements
panel = canvas.add_panel()

# Position the panel on the left of the screen
rect = panel.rect_transform
rect.size = (400,100)
rect.position = (210-(screen_size[0]/2),-200)

# Settings for text size in the panel on screen
text = panel.add_text("Countdown")
text.rect_transform.position = (0,-20)
text.color = (1,1,1)
text.size = 18

# Some values for altitudes
gravityturn = 12000
target_apoapsis = 100000
target_periapsis = 72000


print "gravity turn at: " + str(gravityturn)
print "target_apoapsis: " + str(target_apoapsis)

# Now we're actually starting
vessel = conn.space_center.active_vessel

vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90,90)
vessel.control.throttle = 1

text.content = '3...'
print('3...'); time.sleep(1)
text.content = '2...'
print('2...'); time.sleep(1)
text.content = '1...'
print('1...'); time.sleep(1)
text.content = 'Engine start'
print('Launch!')

vessel.control.activate_next_stage()
text.content = 'First stage burn'


# Burn until the solid fuel in the boosters is out.
while vessel.resources.amount('SolidFuel') > 0.1:
    time.sleep(1)

text.content = 'Booster separation'
print('Booster separation')
vessel.control.activate_next_stage()

# Pitch 10 degrees to the west.
text.content = 'Turn to 80 degrees west'
vessel.auto_pilot.target_pitch_and_heading(80,90)


# Burn until we are at the altitude for the gravity turn.
while vessel.flight().mean_altitude < gravityturn:
   time.sleep(1)
   # Display the targeted apoapsis on screen
   text.content = 'Apoapsis: ' + str(vessel.orbit.apoapsis_altitude)
   # Display the altitude and apoapsis in command line.
   print "Mean altitude: " + str(vessel.flight().mean_altitude)
   print "Apoapsis: " + str(vessel.orbit.apoapsis_altitude)
   

text.content = 'Gravity turn'
print('Gravity turn')

# Turn 45 degrees west
vessel.auto_pilot.target_pitch_and_heading(45,90)

# Keep burning until the apoapsis is 100000 meters
while vessel.orbit.apoapsis_altitude < target_apoapsis:
   time.sleep(1)
   # Display the targeted apoapsis on screen
   text.content = 'Apoapsis: ' + str(vessel.orbit.apoapsis_altitude)
   # Display the altitude and apoapsis in command line.
   print "Mean altitude: " + str(vessel.flight().mean_altitude)
   print "Apoapsis: " + str(vessel.orbit.apoapsis_altitude)


text.content = 'Engine off'
vessel.control.throttle = 0
time.sleep(1)


text.content = 'First stage separation'
print('First stage separation')
vessel.control.activate_next_stage()
time.sleep(1)
time.sleep(1)

text.content = 'Short burn of second stage'
# This short burn with 25% thrust isn't really necessary.
vessel.control.throttle = 0.25
time.sleep(1)
vessel.control.throttle = 0

# Pitch to 20 degrees above the horizon. And burn the second stage for 10 seconds (just to make the trajectory a bit .. wider?
vessel.auto_pilot.target_pitch_and_heading(20,90)
vessel.control.throttle = 1

time.sleep(10)

vessel.control.throttle = 0

# Wait until we're on 90% of the apoapsis.
while vessel.flight().mean_altitude < target_apoapsis*0.9:
   time.sleep(1)
   text.content = 'Burn after %d meters' % (target_apoapsis*0.9 - vessel.flight().mean_altitude)


text.content = 'Turn to prograde'
print('Turn to prograde')

ap = vessel.auto_pilot
ap.reference_frame = vessel.orbital_reference_frame
ap.engage()

# Point the vessel in the prograde direction
# Not necessarily the most efficient way to get into orbit, but hey.
ap.target_direction = (0,1,0)


text.content = 'Extend solar panels'
vessel = conn.space_center.active_vessel
for solar_panel in vessel.parts.solar_panels:
    print solar_panel.state
    solar_panel.deployed=True

text.content = 'Orbital burn'
vessel.control.throttle = 1

# Keep burning until the periapsis is 72000 meters.
while vessel.orbit.periapsis_altitude < target_periapsis:
   time.sleep(1)
   text.content = 'Periapsis: %d ' % vessel.orbit.periapsis_altitude


vessel.control.throttle = 0

# And... we're in orbit.. hopefully.
text.content = 'Welcome in orbit!'
print('Welcome in orbit!')

