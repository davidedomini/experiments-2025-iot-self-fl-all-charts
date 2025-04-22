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

def beutify_algorithm_name(name):
    if 'fedavg' in name:
        return 'FedAvg'
    elif 'fedprox' in name:
        return 'FedProx'
    elif 'scaffold' in name:
        return 'Scaffold'
    elif 'ifca' in name:
        return 'IFCA'
    else:
        return 'Unknown'

def get_data(directory, metric, algorithm):
    files = glob.glob(directory)
    df = pd.DataFrame(columns=['Test accuracy', 'Areas', 'Algorithm'])
    for f in files:
        area = get_areas(f)
        acc = pd.read_csv(f)[metric].iloc[0]
        df = df._append({'Test accuracy': acc, 'Areas': area, 'Algorithm': beutify_algorithm_name(algorithm)}, ignore_index=True)
    return df

def get_data_alchemist(directory, algorithm):
    files = glob.glob(directory)
    df = pd.DataFrame(columns=['Test accuracy', 'Areas', 'Algorithm'])
    for f in files:
        area = get_areas(f)
        acc = pd.read_csv(f).iloc[0].mean()
        df = df._append({'Test accuracy': acc, 'Areas': area, 'Algorithm': algorithm}, ignore_index=True)
    return df

def plot(data, ax, sigma):
    order = ['FedAvg', 'FedProx', 'Scaffold', 'IFCA', 'PSFL']
    # df_mean = data.groupby(['Areas', 'Algorithm'], as_index=False)['Test accuracy'].mean()
    sns.barplot(data=data, x='Areas', y='Test accuracy', hue='Algorithm', hue_order=order, palette="colorblind", ax=ax, ci="sd", capsize=0.3)
    ax.set_ylabel('$Accuracy - Test$')
    ax.set_ylim(0, 1)
    ax.yaxis.grid(True)
    ax.xaxis.grid(True)
    ax.set_xlabel('')
    ax.set_title(f'$\sigma$ = {sigma}')
    ax.legend_.remove()

if __name__ == '__main__':

    output_directory = 'charts/'
    Path(output_directory).mkdir(parents=True, exist_ok=True)

    matplotlib.rcParams.update({'axes.titlesize': 52})
    matplotlib.rcParams.update({'axes.labelsize': 52})
    matplotlib.rcParams.update({'xtick.labelsize': 46})
    matplotlib.rcParams.update({'ytick.labelsize': 46})
    matplotlib.rcParams.update({'legend.fontsize': 34})
    matplotlib.rcParams.update({'legend.title_fontsize': 34})
    plt.rcParams.update({'text.usetex': True})
    plt.rc('text.latex', preamble=r'\usepackage{amsmath,amssymb,amsfonts}')

    baselines = ['fedproxy', 'scaffold', 'ifca', 'fedavg']

    data_baseline = []

    for b in baselines:
        print(f'Processing {b}')
        if b == 'fedavg': 
            path = 'general-comparison/data-test-baseline/*.csv'
        elif b == 'ifca':
            path = 'general-comparison/ifca/*-test.csv'
        else:
            path = f'general-comparison/data-baseline-non-iid/*{b}*-test.csv'
        metric = 'Node-0' if b == 'fedavg' else 'Accuracy'
        d = get_data(path, metric, b)
        data_baseline.append(d)

    # data_baseline = get_data('data-test-baseline/*.csv', 'Baseline')
    data_self_fl = {}

    for th in [20, 40, 80]:
        d = get_data_alchemist(f'general-comparison/data-test/*lossThreshold-{th}.0.csv', 'PSFL')
        data_self_fl[th] = d
        
    fig, axs = plt.subplots(1, 3, figsize=(25, 8), sharey=True)
    for index, th in enumerate(data_self_fl.keys()):
        data_comparison = pd.concat([*data_baseline, data_self_fl[th]])
        plot(data_comparison, axs[index], th)
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='center right', bbox_to_anchor=(1.1, 0.5), title="Algorithm")

    
    fig.supxlabel("Areas", fontsize=52)
    fig.tight_layout(rect=[0, 0, 0.95, 1])
    plt.savefig(f'{output_directory}/test-accuracy-comparison-all.pdf', dpi=500, bbox_inches='tight')
    plt.close()