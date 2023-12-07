import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_mean_with_df(file_name: str, group:str,x_axes:str):
    data = pd.read_csv('../CSV/' + file_name + '.csv')
    sp = data

    sp['Mean time'] = ((sp['Mean time'] * 10) / 60) / 60
    sp['Standard deviation'] = ((sp['Standard deviation'] * 10) / 60) / 60

    sns.set(style="whitegrid")


    for strain, g in sp.groupby(group):
        if strain:
            linestyle = '--'
            color = '#C44E52'
        else:
            linestyle = '-.'
            color = '#4C72B0'
        plt.plot(g[x_axes], g['Mean time'], linestyle=linestyle, marker='', color=color,
                 dashes=[2, 2])

    for i, row in sp.iterrows():
        if row[group]:  # True
            plt.errorbar(row[x_axes], row['Mean time'], yerr=row['Standard deviation'], fmt='none',
                         color='#C44E52', capsize=5, capthick=2)
        else:  # False
            plt.errorbar(row[x_axes], row['Mean time'], yerr=row['Standard deviation'], fmt='none',
                         color='#4C72B0', capsize=5, capthick=2)

    scatter = sns.scatterplot(data=sp, x=x_axes, y='Mean time', hue=group, s=100, zorder=10)
    handles, _ = scatter.get_legend_handles_labels()  # Get legend handles and labels

    # Create custom legend with scatter plot markers
    custom_legend = plt.legend(handles=handles, labels=['npr-1','N2'], loc='best')

    for handle in custom_legend.legendHandles:
        handle.set_alpha(1)  # Set the opacity of legend markers to 1

    plt.xlabel('no. food spots')
    plt.ylabel('time (h)')

    plt.xticks(sp[x_axes])
    plt.yticks(range(0, int(max(sp['Mean time'])) + 3))


    if not os.path.exists("../plots"):
        os.makedirs("../plots")
    plt.savefig("../plots/" + file_name + ".png")
    plt.show()
