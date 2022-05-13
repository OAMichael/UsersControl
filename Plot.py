#!/usr/bin/python3

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import os


def main():
    file = open("./Hist.dat", "r")
    data = {"Windows":    [file.readline(), file.readline(), file.readline()],
            "Percentage": [           float(file.readline()),            float(file.readline()),            float(file.readline())]}
 
    file.close()
    # Now convert this dictionary type data into a pandas dataframe
    # specifying what are the column names
    df = pd.DataFrame(data, columns=['Windows', 'Percentage'])

    # Defining the plotsize
    plt.figure(figsize=(8, 6))

    plots = sns.barplot(x="Windows", y="Percentage", data=df)

    # Iterrating over the bars one-by-one
    for bar in plots.patches:
        plots.annotate( format(bar.get_height(), '.2f'), (bar.get_x() + bar.get_width() / 2, 
                        bar.get_height()), ha='center', va='center',
                        size=15, xytext=(0, 8),
                        textcoords='offset points')

    ax = plt.gca()
    ax.set_ylim([0, 100])

    # Setting the x-axis label and its size
    plt.xlabel("Windows", size=15)
     
    # Setting the y-axis label and its size
    plt.ylabel("Percentage", size=15)

    #plt.rc('xtick', labelsize=5)    

     
    plt.title("Most used windows")

    # Finally plotting the graph
    plt.savefig("./Graphs/Windows.png")

if __name__ == '__main__':
    main()
