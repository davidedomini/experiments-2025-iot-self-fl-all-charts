import glob
import matplotlib
import pandas as pd
import seaborn as sns
from pathlib import Path
import matplotlib.pyplot as plt

def get_test_data(area, cluster):
    files = glob.glob(f'ifca-wrong-clusters/data/*areas-{area}_clusters-{cluster}*test.csv')
    print(f'For area: {area} and cluster: {cluster} ---> {len(files)} files')
    dataframes = []
    for file in files:
        df = pd.read_csv(file)
        df['Clusters'] = cluster
        df['Areas'] = area
        dataframes.append(df)
    return pd.concat(dataframes)

def box_plot(data, area, cluster):
    plt.figure(figsize=(10, 6))
    sns.boxplot(y='Accuracy', data=data)
    plt.title(f'Areas {area} and clusters {cluster}')
    # plt.xlabel('Test')
    plt.ylabel('Value')
    plt.savefig(f'charts/box_plot_area_{area}_cluster_{cluster}.pdf')
    plt.close()

def box_plot_all(data):
    plt.figure(figsize=(12, 6))
    sns.barplot(data=data, x="Clusters", y="Accuracy", hue="Areas", palette="colorblind", linewidth=1.5, errorbar="sd", capsize=0.3)
    plt.xlabel("Number of Clusters")
    plt.ylabel("$Accuracy - Test$")
    plt.legend(title="Real Areas")
    plt.tight_layout()
    plt.savefig('charts/box_plot_all.pdf', dpi = 300)

if __name__ == '__main__':

    output_directory = 'charts/'
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    matplotlib.rcParams.update({'axes.titlesize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 40})
    matplotlib.rcParams.update({'xtick.labelsize': 35})
    matplotlib.rcParams.update({'ytick.labelsize': 35})
    matplotlib.rcParams.update({'legend.fontsize': 30})
    matplotlib.rcParams.update({'legend.title_fontsize': 35})
    plt.rcParams.update({"text.usetex": True})
    plt.rc('text.latex', preamble=r'\usepackage{amsmath,amssymb,amsfonts}')


    areas = [3, 5, 9]
    clusters = {
        3 : [1, 2], 
        5 : [1, 2, 3],
        9 : [1, 3, 5]
    }
    dfs = []
    for area in areas:
        for cluster in clusters[area]:
            data = get_test_data(area, cluster)
            # box_plot(data, area, cluster)
            dfs.append(data)
    data = pd.concat(dfs)
    box_plot_all(data)
    