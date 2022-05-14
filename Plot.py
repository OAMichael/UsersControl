#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os


def main():
    file = open("./Hist.dat", "r")
    lines = file.readlines()

    win_list = []
    percent_list = []

    if len(lines) > 0:
        win_list.append( ('...' + lines[0][-32:]) if len(lines[0]) > 35 else lines[0])
        percent_list.append(float(lines[1]))

    if len(lines) > 2:
        win_list.append( ('...' + lines[2][-32:]) if len(lines[2]) > 35 else lines[2])
        percent_list.append(float(lines[3]))

    if len(lines) > 4:
        win_list.append( ('...' + lines[4][-32:]) if len(lines[4]) > 35 else lines[4]) 
        percent_list.append(float(lines[5]))

    data = {"Windows":    win_list,
            "Percentage": percent_list}
    file.close()

    # Now convert this dictionary type data into a pandas dataframe
    # specifying what are the column names
    df = pd.DataFrame(data, columns=['Windows', 'Percentage'])

    # Defining the plotsize
    plt.figure(figsize=(12, 9))

    sns.set(rc={'axes.labelsize':10,
                'xtick.labelsize':16,
                'font.size':20,
                'ytick.labelsize':20})
    plots = sns.barplot(x="Windows", y="Percentage", data=df, edgecolor=(0,0,0), linewidth=2)

    # Iterrating over the bars one-by-one
    for bar in plots.patches:
        plots.annotate( str(format(bar.get_height(), '.2f')) + "%", (bar.get_x() + bar.get_width() / 2, 
                        bar.get_height()), ha='center', va='center',
                        size=15, xytext=(0, 8),
                        textcoords='offset points')

    ax = plt.gca()
    ax.set_ylim([0, 100])

    # Setting the x-axis label and its size
    plt.xlabel("Windows", fontsize=25)
    plt.xticks(fontsize=10)
     
    # Setting the y-axis label and its size
    plt.ylabel("Percentage", fontsize=25)

    plt.title("Most used windows",fontsize=30)

    # Finally plotting the graph
    #plt.show()
    plt.savefig("./Graphs/Windows.png")

if __name__ == '__main__':
    main()
