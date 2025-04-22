import glob
import pandas as pd
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt


def beutify_name(name):
    if 'direct' in name:
        return 'direct'
    else :
        return 'Life cycle'

def box_plot(dataframes, column):
    combined_df = pd.concat(dataframes, ignore_index=True)
    palette = sns.set_palette("colorblind")
    sns.boxplot(x='Zone name', y=column, data=combined_df, palette=palette, hue='Zone name')
    sns.despine()
    plt.title(column)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{beutify_name(column)}.pdf')
    plt.close() 

def map_plot(dataframes, column):

    data = {
        'country': [],
        'avg_co2': []
    }

    for df in dataframes:
        # print(df['Zone name'].loc[0], '--------', df[column].mean())
        if 'italy' in df['Zone name'].loc[0].lower():
            country = 'Italy'
        else:
            country = df['Zone name'].loc[0]
        data['country'].append(country)
        data['avg_co2'].append(df[column].mean())
    # raise Exception()
    df = pd.DataFrame(data)
    world = gpd.read_file('data/naturalearth/ne_110m_admin_0_countries.shp')
    merged = world.merge(df, how='left', left_on='NAME', right_on='country')
    merged = merged[merged['avg_co2'].notnull()]
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    world.boundary.plot(ax=ax, linewidth=0.5, color='gray')  # bordi del mondo
    merged.plot(column='avg_co2', ax=ax, legend=True, cmap='OrRd', edgecolor='black')
    ax.set_title("Media Emissioni CO₂ per Nazione")
    ax.set_xlim([-10, 20])  # longitudes
    ax.set_ylim([30, 55])   # latitudes
    plt.axis('off')
    plt.savefig('map_plot.pdf')
    plt.close()

if __name__ == "__main__":

    data_path = 'data'
    files = glob.glob(f"{data_path}/*.csv")
    dataframes = []

    for file in files:
        df = pd.read_csv(file, sep=',', index_col=False)
        dataframes.append(df)
    
    # Carbon intensity gCO₂eq/kWh (direct),Carbon intensity gCO₂eq/kWh (Life cycle)
    map_plot(dataframes, 'Carbon intensity gCO₂eq/kWh (direct)')
    box_plot(dataframes, 'Carbon intensity gCO₂eq/kWh (direct)')
    box_plot(dataframes, 'Carbon intensity gCO₂eq/kWh (Life cycle)')