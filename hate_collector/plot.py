import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

def distplot_dates(dates, **kwargs):
    """
    Convenient method for distplot of dates
    """
    if not len(dates):
        return

    if type(dates[0]) is str:
        dates = [datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%SZ") for d in dates]

    # Convert dates to numbers so seaborn recognises them
    ordinal_dates = np.array([d.toordinal() for d in dates])

    ret = sns.distplot(ordinal_dates, **kwargs)
    ticks_locations, _ = plt.xticks();

    labels = [
        datetime.datetime.fromordinal(int(t)).date() for t in ticks_locations
    ]

    plt.xticks(ticks_locations, labels, rotation=90)
    return ret
