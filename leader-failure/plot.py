import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
import glob
import re

def extract_dimension(name, dimension):
    for elem in name.split('_'):
        if dimension in elem:
            value = int(float(elem.split('-')[1]))
            return value

def extractVariableNames(filename):
    """
    Gets the variable names from the Alchemist data files header.

    Parameters
    ----------
    filename : str
        path to the target file

    Returns
    -------
    list of list
        A matrix with the values of the csv file

    """
    with open(filename, 'r') as file:
        dataBegin = re.compile(r'\d')
        lastHeaderLine = ''
        for line in file:
            if dataBegin.match(line[0]):
                break
            else:
                lastHeaderLine = line
        if lastHeaderLine:
            regex = re.compile(r' (?P<varName>\S+)')
            return regex.findall(lastHeaderLine)
        return []


def openCsv(path):
    """
    Converts an Alchemist export file into a list of lists representing the matrix of values.

    Parameters
    ----------
    path : str
        path to the target file

    Returns
    -------
    list of list
        A matrix with the values of the csv file

    """
    regex = re.compile(r'\d')
    with open(path, 'r') as file:
        lines = filter(lambda x: regex.match(x[0]), file.readlines())
        return [[float(x) for x in line.split()] for line in lines]


def load_data_from_csv(path):  
    files = glob.glob(f'{path}/*.csv')
    dataframes = []
    print(f'Loaded {len(files)} files')
    for file in files:
        areas_value = extract_dimension(file, 'areas')
        seed = extract_dimension(file, 'seed')
        columns = extractVariableNames(file)
        data = openCsv(file)
        df = pd.DataFrame(data, columns=columns)
        df['Areas'] = areas_value
        df['Seed'] = seed
        dataframes.append(df)
    return dataframes

def beutify(metric):
    if 'AreaCount' in metric:
        return '$|F|$'
    elif 'AreaCorrectness' in metric:
        return 'Area Correctness'
    elif 'ValidationLoss' in metric:
        return '$NLL - Validation$'
    elif 'Accuracy' in metric:
        return '$Accuracy - Validation$'
    elif 'TrainLoss' in metric:
        return  '$NLL - Train$'
    else:
        return 'Unknown Metric'

def plot(dataframes, metrics, charts_path):
    for metric in metrics:
        df_grouped = dataframes.groupby('time')[metric].agg(['mean', 'std'])
        time = df_grouped.index
        mean = df_grouped['mean']
        std = df_grouped['std']
        plt.plot(time, mean, linewidth=3, label='$|F|$')
        plt.fill_between(time, mean - std, mean + std, alpha=0.2)
        if 'AreaCount' in metric:
            plt.axvline(x=7.5, color='#d62728', linestyle='--', linewidth=3, label='Failure')
            plt.axhline(y=5, color='#2ca02c', linestyle='--', linewidth=3, label='Target')
            plt.legend()
            plt.ylim(0, 55)
        plt.ylabel(beutify(metric))
        # plt.title(f'{beutify(metric)}')
        plt.xlabel('Global Round')
        # plt.ylabel(metric_to_symbol(metric))
        # plt.legend(title="Areas")
        # if 'Accuracy' in metric:
            # plt.ylim(0, 1)
        # plt.ylim(0, 1)
        plt.tight_layout()
        # plt.grid(True)
        plt.savefig(f'{charts_path}/{metric}.pdf')
        plt.close()


if __name__ == '__main__':
    
    matplotlib.rcParams.update({'axes.titlesize': 20})
    matplotlib.rcParams.update({'axes.labelsize': 25})
    matplotlib.rcParams.update({'xtick.labelsize': 25})
    matplotlib.rcParams.update({'ytick.labelsize': 25})
    matplotlib.rcParams.update({'legend.fontsize': 22})
    matplotlib.rcParams.update({'legend.title_fontsize': 35})
    plt.rcParams.update({"text.usetex": True})
    plt.rc('text.latex', preamble=r'\usepackage{amsmath,amssymb,amsfonts}')

    data_path = 'leader-failure/data'
    charts_path = 'charts/leader-failure'
    metrics = ['AreaCorrectness', 'AreaCount', 'ValidationLoss[mean]', 'ValidationAccuracy[mean]', 'TrainLoss[mean]']

    Path(charts_path).mkdir(parents=True, exist_ok=True)

    dataframes = load_data_from_csv(data_path)
    dataframes = pd.concat(dataframes, ignore_index=True)
    dataframes = dataframes.dropna()
    plot(dataframes, metrics, charts_path)
    