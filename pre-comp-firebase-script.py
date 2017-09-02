
import tba_interactor as tba
import firebase_interactor as fb

EVENT = "2017cc"

teams = tba.get_teams(EVENT)

fb.authenticate("yj9RT3JDfoj9rou4E90Pl4LXASoyXTIYVvNV9NbH")

for i in teams:
	for stat in ["Tele-Fuel-High-Cycles-Times", "Tele-Gears-Cycles-Times"] + ["Auto-Baseline","Auto-Fuel-High-Cycles","Auto-Fuel-Intake-Hopper","Auto-Fuel-Low-Cycles","Auto-Gears","Auto-Gears-Dropped","Auto-Gears-Intake-Ground","Auto-Robot-Broke-Down","Auto-Robot-No-Action","End-Defense","End-Defense-Rating","End-Fuel-Ground-Intake","End-Fuel-Ground-Intake-Rating","End-Gear-Ground-Intake","End-Gear-Ground-Intake-Rating","End-No-Show","End-Takeoff","End-Takeoff-Speed","Tele-Fuel-High-Cycles","Tele-Fuel-High-Cycles-In-Key","Tele-Fuel-High-Cycles-Out-Of-Key","Tele-Fuel-Intake-Hopper","Tele-Fuel-Intake-Loading-Station","Tele-Fuel-Low-Cycles","Tele-Fuel-Low-Cycles-Times","Tele-Gears-Cycles","Tele-Gears-Dropped","Tele-Gears-Intake-Dropped","Tele-Gears-Intake-Ground","Tele-Gears-Intake-Loading-Station","Tele-Gears-Position-Boiler","Tele-Gears-Position-Loading","Tele-Gears-Position-Middle","Tele-Robot-Broke-Down","Tele-Robot-No-Action"]:
		fb.put(EVENT + "/teams/" + str(i) + "/data", stat + "-Average", "0")
		fb.put(EVENT + "/teams/" + str(i) + "/data", stat + "-Stdev", "0")
	print "Zeroed stats for team #" + str(i)