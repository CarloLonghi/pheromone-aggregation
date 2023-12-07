import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_mean_with_df(file_name:str):
    data = pd.read_csv('CSV/'+file_name+'.csv')
    sp = data
    sp['Mean time'] /= 100
    sp['Standard deviation'] /= 100
    # Create a plot using Seaborn
    sns.set(style="whitegrid")  # Set the style

    # Create a boxplot with mean and standard deviation
    sns.scatterplot(data=sp, x='Number of spots', y='Mean time', hue='Strain specific', s=100)  # Plot the mean time
    for i, row in sp.iterrows():
        if row['Strain specific']:  # True
            plt.errorbar(row['Number of spots'], row['Mean time'], yerr=row['Standard deviation'], fmt='none',
                         color='red', capsize=5, capthick=2)
        else:  # False
            plt.errorbar(row['Number of spots'], row['Mean time'], yerr=row['Standard deviation'], fmt='none',
                         color='blue', capsize=5, capthick=2)
    for strain, group in sp.groupby('Strain specific'):
        if strain:
            linestyle = '--'
            color = 'red'
        else:
            linestyle = '-.'
            color = 'blue'
        plt.plot(group['Number of spots'], group['Mean time'], linestyle=linestyle, marker='', color=color, dashes=[2, 2])

    # Rename the legend
    plt.legend(labels=['N2', 'nrp-1'])  # Modify the labels here

    plt.xlabel('no. food spots')
    plt.ylabel('time (h)')
    plt.title('Figure 4 (b) replica')
    plt.xticks([1, 2, 4])
    plt.ylim(0)
    plt.savefig("plots/"+file_name+".png")
    plt.show()

plot_mean_with_df("default")