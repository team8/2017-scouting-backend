import firebase_interactor as fb
import json

csv_out = open("roe-csv-scouting-data.csv", "w")

stats = ["Auto-Baseline-Achieve-Rate","Auto-Fuel-High-Cycles-Average","Auto-Fuel-High-Cycles-Stdev","Auto-Fuel-High-i-Position-Prob","Auto-Fuel-High-o-Position-Prob","Auto-Fuel-Low-Cycles-Average","Auto-Fuel-Low-Cycles-Stdev","Auto-Gears-Achieve-Rate","Auto-Gears-Average","Auto-Gears-Intake-Ground-Average","Auto-Gears-Intake-Ground-Stdev","Auto-Gears-Stdev","Auto-Gears-b-Position-Prob","Auto-Gears-b-Success-Rate","Auto-Gears-l-Position-Prob","Auto-Gears-l-Success-Rate","Auto-Gears-m-Position-Prob","Auto-Gears-m-Success-Rate","Auto-Robot-Broke-Down-Average","Auto-Robot-Broke-Down-Stdev","Auto-Robot-No-Action-Average","Auto-Robot-No-Action-Stdev","End-Defense-Average","End-Defense-Rating-Average","End-Defense-Rating-Stdev","End-Defense-Stdev","End-Driver-Rating-Average","End-Driver-Rating-Stdev","End-Fuel-Ground-Intake-Rating-Average","End-Fuel-Ground-Intake-Rating-Stdev","End-Gear-Ground-Intake-Rating-Average","End-Gear-Ground-Intake-Rating-Stdev","End-No-Show-Average","End-No-Show-Stdev","End-Takeoff-Achieve-Rate","End-Takeoff-Speed-Average","End-Takeoff-Speed-Stdev","End-Takeoff-Success-Rate","Loading-Station-Reliability","Reliability","Strategy-Rate-End-Defense","Strategy-Rate-Tele-Fuel-High-Cycles","Strategy-Rate-Tele-Fuel-Low-Cycles","Strategy-Rate-Tele-Gears-Cycles","Tele-Fuel-High-Cycles-Average","Tele-Fuel-High-Cycles-Stdev","Tele-Fuel-High-Cycles-Times-Average","Tele-Fuel-High-In-Key-Position-Prob","Tele-Fuel-High-Out-Of-Key-Position-Prob","Tele-Fuel-Low-Cycles-Average","Tele-Fuel-Low-Cycles-Stdev","Tele-Fuel-Low-Cycles-Times-Average","Tele-Gears-Boiler-Position-Prob","Tele-Gears-Cycles-Average","Tele-Gears-Cycles-Stdev","Tele-Gears-Cycles-Times-Average","Tele-Gears-Cycles-Upper-Limit","Tele-Gears-Dropped-Average","Tele-Gears-Dropped-Stdev","Tele-Gears-Intake-Dropped-Average","Tele-Gears-Intake-Dropped-Stdev","Tele-Gears-Intake-Ground-Average","Tele-Gears-Intake-Ground-Stdev","Tele-Gears-Intake-Loading-Station-Average","Tele-Gears-Intake-Loading-Station-Stdev","Tele-Gears-Loading-Position-Prob","Tele-Gears-Middle-Position-Prob"]

firebase_data = json.loads(open("roe-export-2.json").read())

csv_out.write("team," + ",".join(stats) + "\n")

for i in firebase_data["teams"].keys():
	print i
	to_write = [i]

	for k in stats:
		to_write.append(firebase_data["teams"][i]["data"][k])

	csv_out.write(",".join([str(i) for i in to_write]) + "\n")

csv_out.close()
