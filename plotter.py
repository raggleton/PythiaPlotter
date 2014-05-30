# import makeGraphFromPythia
import numpy as np
import matplotlib.pyplot as plt

# This plots a bar chart of # particles for each status code, for skipped and
# not-skipped particles in event listing
# Just for interest, to see if you could determine which to skip
# purely based on status code


def plotStatuses(fullEvent):
    # Do some analysis of statuses
    N = 92  # plto for statuses 11 to 91, inclusive

    notSkippedList = [0]*N
    skippedList = [0]*N
    for p in fullEvent:
        if p.skip:
            skippedList[abs(p.status)] += 1
        else:
            notSkippedList[abs(p.status)] += 1

    ind = np.arange(N)  # the x locations for the groups
    width = 0.5       # the width of the bars

    fig, ax = plt.subplots()

    notSkippedTuple = tuple(notSkippedList)
    rects1 = ax.bar(ind, notSkippedTuple, width, color='r')

    skippedTuple = tuple(skippedList)
    rects2 = ax.bar(ind+width, skippedTuple, width, color='y')

    # add some
    ax.set_ylabel('# Particles')
    ax.set_title('# Particles skipped and not skipped, for each status code')
    ax.set_xticks(ind+width)
    # ax.set_xticklabels( ('G1', 'G2', 'G3', 'G4', 'G5') )

    ax.legend((rects1[0], rects2[0]), ('Not skipped', 'Skipped'))

    def autolabel(rects):
        # attach some text labels
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x()+rect.get_width()/2.,
                    1.05*height, '%d' % int(height),
                    ha='center', va='bottom')

    # autolabel(rects1)
    # autolabel(rects2)

    # plt.show()
    print "Saving plot"
    plt.savefig("skipped_status.pdf")