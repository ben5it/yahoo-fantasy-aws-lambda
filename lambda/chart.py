#!/usr/bin/env python

from io import BytesIO
import numpy as np
import math
import matplotlib
import matplotlib.cm as cm
matplotlib.use('Agg')
from matplotlib import font_manager
cnFontProp = font_manager.FontProperties(fname='SimSun-01.ttf')
import matplotlib.pyplot as plt

def league_bar_chart(df, title, sort=False):
    """
    Generate a bar chart displaying the total score of each team.
    
    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame containing the data.
    title : str
        The title of the chart.
    sort : bool, optional
        Whether to sort the DataFrame by the 'Total' column.
    """
    if sort:
        # Sort by total
        sorted_df = df.sort_values(by=['Total'], ascending=False)
    else:
        sorted_df = df

    names = sorted_df.index
    scores = sorted_df['Total']

    pos = list(range(1, len(names) + 1))
    width = 0.5

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(12, 9), dpi=100)

    # Create a bar with total scores
    bar_container = ax.bar(pos, scores, width, alpha=0.7, color='#87CEEB', edgecolor='#011f4b')

    # Add labels (values) to each bar
    ax.bar_label(bar_container, padding=3, fontproperties=cnFontProp)

    # Set the y-axis label
    ax.set_ylabel('Point', fontproperties=cnFontProp)

    # Set the chart's title
    ax.set_title(title, fontproperties=cnFontProp, size=15, color='black', y=1.05)

    # Customize the appearance
    ax.tick_params(axis='x', labelsize=10, colors='#222222')
    ax.tick_params(axis='y', labelsize=10, colors='#222222')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#FAFAFA')

    # Set x-ticks and labels
    ax.set_xticks(pos)
    ax.set_xticklabels(names, fontproperties=cnFontProp, rotation=30, ha='right')

    plt.tight_layout()

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close()

    return img_data



def get_radar_chart(stat_names, stat_values, value_limit, labels, title):
    """
    Create a radar chart with stat_names, stat_values, and labels.
    
    Parameters
    ----------
    stat_names : list
        The names of the statistics.
    stat_values : list of lists
        The values of the statistics for each label.
    labels : list
        The labels for each set of stat_values.
    title : str
        The title of the chart.

    """
    # Number of variables
    num_vars = len(stat_names)

    # Compute angle of each axis
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is a circle, so we need to "complete the loop"
    angles += angles[:1]

    # Create the radar chart
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True), dpi=100)

    # Draw one axe per variable and add labels
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(stat_names, fontproperties=cnFontProp)

    # Draw ylabels
    number_of_ticks = math.ceil(value_limit/3)
    value_limit = number_of_ticks * 3
    ax.set_ylim(0, value_limit) # Ensure radar goes from 0 to value_limit.
    ax.set_yticks(np.linspace(0, value_limit, number_of_ticks + 1))
    # Set position of y-stat_names (0-100) to be in the middle of the first two axes.
    ax.set_rlabel_position(180 / num_vars)

    # Plot data
    for i, values in enumerate(stat_values):
        values += values[:1]
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=labels[i])
        ax.fill(angles, values, alpha=0.25)


    # Add a title
    ax.set_title(title, fontproperties=cnFontProp, size=15, color='black', y=1.1)

    # Add a legend
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1), prop=cnFontProp)

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close()

    return img_data


def generate_rank_chart(df, league_name):

    # # Cast the elements of the DataFrame to integer type
    # df = df.astype(int)

    # Calculate the figure width based on the number of columns
    num_columns = len(df.columns)
    fig_width = min(max(12, num_columns), 20)

    # Create the plot
    plt.figure(figsize=(fig_width, 8), dpi=100)

    # Get a colormap
    colormap = cm.get_cmap('tab20', len(df.index))

    # Plot each team's data with unique colors
    for idx, team in enumerate(df.index):
        plt.plot(df.columns, df.loc[team], marker='o', label=team, color=colormap(idx))
        # Annotate the team names on the left side of the plot
        plt.annotate(team, xy=(df.columns[0], df.loc[team][0]), xytext=(-60, 0),
                     textcoords='offset points', ha='right', va='center', color=colormap(idx), fontproperties=cnFontProp)

    # Reverse the y-axis
    plt.gca().invert_yaxis()

     # Ensure rank is integer
    plt.yticks(range(int(df.values.min()), int(df.values.max()) + 1))

    # Add title and labels
    plt.title(f'北伐! 北伐！ - {league_name}', fontproperties=cnFontProp, size=15, weight='bold')

    # Place the legend outside of the plot on the right side
    # plt.legend(title='Teams', bbox_to_anchor=(1.05, 1), loc='upper left', prop=cnFontProp)

    # Adjust layout to make room for the legend
    plt.tight_layout()

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close()

    return img_data

def generate_category_pie_chart_for_team(df, team):
    """
    Generate a pie chart for a specific team.
    
    Parameters:
    - df: The DataFrame with teams as the index and categories as the columns.
    - team: The index label of the team for which to generate the pie chart.
    """
    # Get the data for the specified team
    team_data = df.loc[team]
    
   # Get a colormap
    colormap = cm.get_cmap('tab20', len(team_data))

    # Create a pie chart
    plt.figure(figsize=(6, 6), dpi=100)
    plt.pie(team_data, labels=team_data.index, autopct='%1.1f%%', startangle=140, colors=[colormap(i) for i in range(len(team_data))])

    plt.title(f'Wins by Category for {team}', fontproperties=cnFontProp)

    plt.tight_layout()
    
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close()

    return img_data