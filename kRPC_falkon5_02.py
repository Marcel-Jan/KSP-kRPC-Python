"""
kRPC Automated Landing of 1st Stage

Description:
Python program for automatic landing of the first stage of my rocket.

To run this KSP kRPC Python program you need:
- Kerbal Space Program (tested in 1.3.1)
- kRPC 0.3.9 (<url>)
  Use the install guide on https://krpc.github.io/krpc/getting-started.html
- I've also installed the Python client library (https://pypi.python.org/pypi/krpc)
- Python 2.7 or 3.4

When installed, install the .craft file (Selflanding First Stage 5R.craft or Selflanding First Stage 5R-1.craft).
Go to the directory with this program, start Python command line and run:
execfile('kRPC_autoland1ststage_5engine_03.py')

Good luck!
"""

import krpc
import time
import logging
import time
import math

conn = krpc.connect(name='Automatic Landing of 1st Stage')

def prepare_screen_message():
	canvas = conn.ui.stock_canvas
	screen_size = canvas.rect_transform.size
	panel = canvas.add_panel()
	# Position the panel on the left of the screen
	rect = panel.rect_transform
	rect.size = (600,150)
	rect.position = (-screen_size[0]*.28, -screen_size[0]*.18)
	
	text = panel.add_text("Countdown")
	text.rect_transform.position = (-120,0)
	text.color = (1,1,1)
	text.size = 13
	return text


def write_screen_message(text_panel, screen_message):
	text_panel.content = screen_message


def interval_print(print_message):
	tens = int(round(time.time() * 10))
	if (tens % 10) == 0:
		print(print_message)


def calc_suicide_burn(current_speed, thrust, mass, gravity):
	acc_engine = thrust/mass
	acceleration = acc_engine - gravity
	return -(current_speed**2)/(2*acceleration)

text_panel = prepare_screen_message()
write_screen_message(text_panel, "Countdown")
time.sleep(1)


target_apoapsis = 75000
island_heading = 117
print("Heading: " + str(island_heading))
print("target_apoapsis: " + str(target_apoapsis))

# Ascent trajectory: {step, [end at altitude, pitch, heading, % thrust}
ascent_trajectory = {1: [1000, 90, island_heading, 100],
					 2: [6000, 85, island_heading, 95],
					 3: [7500, 80, island_heading, 90],
					 3: [9000, 75, island_heading, 85],
					 4: [13000, 70, island_heading, 80],
					 5: [19000, 60, island_heading, 75],
					 6: [25000, 50, island_heading, 70],
					 7: [33000, 45, island_heading, 60]}

print("Trajectory program")
for step, params in ascent_trajectory.items():
	print(step, params[0:4])


# Now we're actually starting
ksc = conn.space_center
rocket = ksc.active_vessel
rocket_name = rocket.name
srf_frame = rocket.orbit.body.reference_frame

ap = rocket.auto_pilot
v = ksc.active_vessel
rocket.auto_pilot.engage()

write_screen_message(text_panel, "3")
time.sleep(1)
write_screen_message(text_panel, "2")
time.sleep(1)
write_screen_message(text_panel, "1")
time.sleep(1)



# =======================
# Engine start
# =======================

rocket.control.activate_next_stage()
write_screen_message(text_panel, 'Engine start')
rocket.control.throttle = 1
time.sleep(1)


# =======================
# Ascent
# =======================

rocket.control.activate_next_stage()
write_screen_message(text_panel, 'Lift off!')


for step, params in ascent_trajectory.items():
	print(step, params[0:4])

	while rocket.flight().mean_altitude < params[0]:
		rocket.auto_pilot.target_pitch_and_heading(params[1], params[2])
		rocket.control.throttle = (params[3]/100)
		write_screen_message(text_panel, "Ptc: " + str(params[1]) + " Hea: " + str(params[2]) + " Thr: " + str(params[3]))
		interval_print("Ptc: " + str(params[1]) + " Hea: " + str(params[2]) + " Thr: " + str(params[3]))


write_screen_message(text_panel, 'Pitch to 45 until apoapsis=75000 m')
while rocket.orbit.apoapsis_altitude < target_apoapsis:
	rocket.auto_pilot.target_pitch_and_heading(45,island_heading)
	#rocket.control.throttle = .40

rocket.control.throttle = 0
write_screen_message(text_panel, 'Engine stop')
time.sleep(1)

rocket.control.activate_next_stage()
write_screen_message(text_panel, 'Deploy payload fairing')
time.sleep(3)

rocket.control.activate_next_stage()
write_screen_message(text_panel, 'Bye bye, ..')
time.sleep(2)
write_screen_message(text_panel, '.. second stage')
time.sleep(2)




# =======================
# Running as second stage
# =======================


for vess in conn.space_center.vessels:
	print("Gevonden vessel: " + vess.name)
	if (vess.name == rocket_name + " Relay"):
		ksc.active_vessel = vess
		print("Switch naar " + vess.name)
		write_screen_message(text_panel, 'Temporary switch to second stage')
		second_stage = ksc.active_vessel
		#second_stage = vess.auto_pilot
		second_stage.auto_pilot.reference_frame = vess.surface_velocity_reference_frame

secondst_heading = 0
print("Second stage: pitch to 0, head to " + str(secondst_heading))
second_stage.auto_pilot.target_pitch_and_heading(0, secondst_heading)
rocket.auto_pilot.target_pitch_and_heading(0,secondst_heading)
print("Auto pilot engage")
second_stage.auto_pilot.engage()


#second_stage = conn.space_center.active_vessel
print("Second stage: throttle 10%")
second_stage.control.throttle = .1
time.sleep(2)
print("Second stage: pitch to 0, head to " + str(secondst_heading))
second_stage.auto_pilot.target_pitch_and_heading(0, secondst_heading)
print("Second stage: throttle 100%")
second_stage.control.throttle = 1
time.sleep(5)

#second_stage.auto_pilot.disengage()




# =============================
# Running as first stage again
# =============================

for vess in conn.space_center.vessels:
	if (vess.name == rocket_name):
		ksc.active_vessel = vess
		print("Switch naar " + vess.name)
		write_screen_message(text_panel, 'Back to 1st stage')
		rocket = ksc.active_vessel
		#rocket = vess.auto_pilot
		rocket.auto_pilot.reference_frame = vess.surface_velocity_reference_frame


print("First stage: SAS on")
rocket.control.throttle = 0
#rocket.auto_pilot.sas = True
print("First stage: retrograde")
#rocket.auto_pilot.sas_mode = rocket.auto_pilot.sas_mode.retrograde
rocket.auto_pilot.engage()

srf_frame = rocket.orbit.body.reference_frame
print("First stage: speed - surface mode")
rocket.control.speed_mode = rocket.control.speed_mode.surface




# =============================
# 
# =============================



write_screen_message(text_panel, 'RCS on')
rocket.control.rcs=True
rocket.control.throttle = 0



# =============================
# Reentry burn
# =============================

firstst_heading = 0
rocket.auto_pilot.target_pitch_and_heading(135, firstst_heading)
#ap.target_pitch_and_heading(185, firstst_heading)

for i in range(20,0,-1):
	write_screen_message(text_panel, "Wait " + str(i))
	time.sleep(1)

write_screen_message(text_panel, 'Slight throttle')
rocket.control.throttle = 0.05

for i in range(3,0,-1):
	write_screen_message(text_panel, "Wait " + str(i))
	time.sleep(1)

write_screen_message(text_panel, 'Retrograde burn')
rocket.control.throttle = 1

for i in range(7,0,-1):
	write_screen_message(text_panel, "Wait " + str(i))
	time.sleep(1)


write_screen_message(text_panel, 'Reentry')
rocket.control.rcs=False
rocket.control.throttle = 0



# =============================
# Air brakes
# =============================


while rocket.flight().mean_altitude > 20000:
	write_screen_message(text_panel, "Alt: " + str(math.ceil(rocket.flight().mean_altitude)) + " spd: " + str(math.ceil(rocket.flight(srf_frame).speed)))

rocket.control.set_action_group(1, True)
write_screen_message(text_panel, "Airbrakes deployed")

rocket.sas = True
rocket.sasmode = "retrograde"




while rocket.flight().mean_altitude > 2000:
	interval_print("Alt: " + str(rocket.flight().mean_altitude) + " spd: " + str(rocket.flight(srf_frame).speed) + " Sit: " + str(rocket.situation))
	#print("Hsp: " + str(rocket.flight().horizontal_speed) + " Vsp: " + str(rocket.flight().vertical_speed) + " Vel: " + str(rocket.flight().velocity))
	#print("Osp: " + str(rocket.orbit.speed) + " Orsp: " + str(rocket.orbit.orbital_speed))
	write_screen_message(text_panel, "Wait for burn")


current_speed = rocket.flight(srf_frame).speed
thrust = rocket.thrust
mass = rocket.mass
gravity = rocket.orbit.body.surface_gravity

crude_suicide_burn_alt = (calc_suicide_burn(current_speed, thrust, mass, gravity) + 100)



write_screen_message(text_panel, str(rocket.flight().mean_altitude))
print('Mean altitude: ' + str(rocket.flight().mean_altitude))

write_screen_message(text_panel, "Burn at: " + str(crude_suicide_burn_alt) + " m")
print("Burn at: " + str(crude_suicide_burn_alt) + " m")

while rocket.flight().mean_altitude > crude_suicide_burn_alt:
	write_screen_message(text_panel, 'Suicide burn at ' + str(crude_suicide_burn_alt) + " m")
	#print('Here we go!')
	interval_print("Alt: " + str(rocket.flight().mean_altitude) + " spd: " + str(rocket.flight(srf_frame).speed) + " Sit: " + str(rocket.situation))

#rocket.control.rcs=True
#conn.space_center.sasmode(retrograde)

#write_screen_message(text_panel, 'Auto pilot retrograde')
ap = rocket.auto_pilot
ap.reference_frame = rocket.surface_velocity_reference_frame
ap.target_direction = (0, -1, 0)
ap.engage()
srf_frame = rocket.orbit.body.reference_frame

#rocket.sasmode(retrograde)

while rocket.flight().mean_altitude > 1:
	#print('In the last while loop.')
	if rocket.flight(srf_frame).speed > 50 and rocket.flight().mean_altitude > 100:
		rocket.control.throttle = 1
		write_screen_message(text_panel, 'Throttle ' + str(rocket.control.throttle*100) + '%' )
		interval_print("Throttle 100% at " + str(rocket.flight().mean_altitude) + " m, speed: " + str(rocket.flight(srf_frame).speed) + " m/s")
	elif rocket.flight(srf_frame).speed > 20 and rocket.flight().mean_altitude > 100:
		rocket.control.throttle = .5
		write_screen_message(text_panel, 'Throttle ' + str(rocket.control.throttle*100) + '%' )
		interval_print("Throttle 50% at " + str(rocket.flight().mean_altitude) + " m, speed: " + str(rocket.flight(srf_frame).speed) + " m/s")
	elif rocket.flight(srf_frame).speed > 8:
		ap.target_pitch_and_heading = (0, island_heading)
		ap.engage()
		rocket.control.throttle = .26
		write_screen_message(text_panel, 'Throttle ' + str(rocket.control.throttle*100) + '%' )
		interval_print("Throttle " + str(rocket.control.throttle*100) + "%  at " + str(rocket.flight().mean_altitude) + " m, speed: " + str(rocket.flight(srf_frame).speed) + " m/s")
	elif rocket.flight(srf_frame).speed < 8:
		write_screen_message(text_panel, 'Deploy landing gear')
		rocket.control.gear = True
		ap.disengage()
		rocket.control.throttle = 0


if rocket.flight(srf_frame).speed < 12:
	write_screen_message(text_panel, 'Touchdown! Well done!')
	print('Touchdown! Well done!')
else:
	write_screen_message(text_panel, 'Crashed with speed: ' + str(round(rocket.flight(srf_frame).speed)) + " m/s")
	print('Crashed with speed: ' + str(round(rocket.flight(srf_frame).speed)) + " m/s")	

