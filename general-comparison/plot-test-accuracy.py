import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import pandas as pd
import matplotlib
import glob


def get_areas(name):
    for elem in name.split('_'):
        if 'areas' in elem:
            n_areas = int(elem[-1])
            return n_areas


def get_data(directory, algorithm):
    files = glob.glob(directory)
    df = pd.DataFrame(columns=['Test accuracy', 'Areas', 'Algorithm'])
    for f in files:
        area = get_areas(f)
        acc = pd.read_csv(f)['Accuracy'].iloc[0]
        print(acc)
        df = df._append({'Test accuracy': acc, 'Areas': area, 'Algorithm': algorithm}, ignore_index=True)
    return df

def get_data_alchemist(directory, algorithm):
    files = glob.glob(directory)
    df = pd.DataFrame(columns=['Test accuracy', 'Areas', 'Algorithm'])
    for f in files:
        area = get_areas(f)
        print(f)
        acc = pd.read_csv(f).iloc[0].mean()
        df = df._append({'Test accuracy': acc, 'Areas': area, 'Algorithm': algorithm}, ignore_index=True)
        print(df)
    return df

if __name__ == '__main__':

    output_directory = 'charts/iot'
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    matplotlib.rcParams.update({'axes.titlesize': 52})
    matplotlib.rcParams.update({'axes.labelsize': 52})
    matplotlib.rcParams.update({'xtick.labelsize': 46})
    matplotlib.rcParams.update({'ytick.labelsize': 46})
    matplotlib.rcParams.update({'legend.fontsize': 34})
    matplotlib.rcParams.update({'legend.title_fontsize': 34})
    plt.rcParams.update({'text.usetex': True})
    plt.rc('text.latex', preamble=r'\usepackage{amsmath,amssymb,amsfonts}')

    baselines = ['fedproxy', 'scaffold', 'ifca']#'fedavg']

    data_baseline = []

    for b in baselines:
        if b == 'fedavg': 
            path = 'data-test'
        elif b == 'ifca':
            path = 'ifca/*-test.csv'
        else:
            path = f'data-baseline-non-iid/*{b}*-test.csv'
        d = get_data(path, b)
        data_baseline.append(d)

    # data_baseline = get_data('data-test-baseline/*.csv', 'Baseline')
    data_self_fl = {}

    for th in [20, 40, 80]:
        d = get_data_alchemist(f'data-test/*lossThreshold-{th}.0.csv', 'Self-FL')
        data_self_fl[th] = d

    for th in data_self_fl.keys():
        plt.figure(figsize=(12, 8))
        data_comparison = pd.concat([*data_baseline, data_self_fl[th]])
        # sns.color_palette('colorblind', as_cmap=True)
        # sns.set_palette('colorblind')
        colors = sns.color_palette("viridis", as_cmap=True)
        palette = [colors(0.1), colors(0.3), colors(0.7), colors(0.9)]
        ax = sns.boxplot(data=data_comparison, x='Areas', y='Test accuracy', hue='Algorithm', palette=palette, fill = False)
        sns.move_legend(ax, 'lower left')
        plt.title(f'$ \psi = 0.0$')
        plt.ylabel('$Accuracy - Test$')
        plt.ylim(0, 1)
        ax.yaxis.grid(True)
        ax.xaxis.grid(True)
        plt.tight_layout()
        plt.savefig(f'{output_directory}/test-accuracy-comparison-threshold-{th}.0.pdf', dpi=500)
        plt.close()
