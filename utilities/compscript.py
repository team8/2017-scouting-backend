import tba_interactor as tba


def main():
    keys = []
    count = []
    for team in tba.get_teams("2017cc"):
        events = tba.get_data("/team/frc" + str(team) + "/2017/events")
        for event in events:
            key = event["name"]
            if key not in keys:
                keys.append(key)
                count.append(0)
            count[keys.index(key)] += 1
    for i, key in enumerate(keys):
        print key + " - " + str(count[i])
main()
