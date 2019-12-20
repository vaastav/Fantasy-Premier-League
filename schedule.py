from getters import get_fixtures_data
from dateutil.parser import parse
from datetime import timedelta

def generate_schedule():
    fixtures = get_fixtures_data()
    gw_dict = {}
    for f in fixtures:
        gw = f['event']
        time = f['kickoff_time']
        if gw is None:
            continue
        if gw not in gw_dict:
            gw_dict[gw] = [time]
        else:
            gw_dict[gw] += [time]

    sched_dates = []
    for k,dates in gw_dict.items():
        dates = [parse(d) for d in dates]
        dates.sort(reverse=True) 
        run_date = dates[0] + timedelta(hours=12)
        sched_dates += [run_date]

    for run_date in sorted(sched_dates):
        print(run_date.strftime("%M %H %d %m *"))

def main():
    generate_schedule()    

if __name__ == '__main__':
    main()
