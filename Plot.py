#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os
from sys import argv
import CreateDB
import DB_access


def main():
    # Get information about what we are going to graph
    name = argv[1]
    # Lists of active windows and their percentage
    win_list, percent_list = DB_access.MostUsableWindows(DB_access.Session(), name)

    deleted_i = []
    for i in range(3):
        if percent_list[i] == 0.00:
            deleted_i.insert(0, i)

    for i in deleted_i:
        del win_list[i]
        del percent_list[i]

    for i in range(len(win_list)):
        win_list[i] = (win_list[i][:16] + '...' + win_list[i][-16:]) if len(win_list[i]) > 35 else win_list[i]

    # Preparing for dataframe
    data = {"Windows":    win_list,
            "Percentage": percent_list}

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

    plt.title("Most used windows by " + name, fontsize=30, x=0.5, y=1.05)

    # Finally plotting the graph
    plt.savefig("./Graphs/Windows" + name + ".png")

if __name__ == '__main__':
    main()
