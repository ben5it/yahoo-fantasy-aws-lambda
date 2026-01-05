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
    # Calculate width based on number of columns (weeks). Use a per-week width
    # and clamp to reasonable bounds so images don't become absurdly wide.
    num_columns = len(df.columns)
    per_week_width = 1.1
    fig_width = min(max(12, int(num_columns * per_week_width)), 24)

    # Create figure and axis so we can annotate per-team easily
    fig, ax = plt.subplots(figsize=(fig_width, 8), dpi=100)

    # Get a colormap
    colormap = cm.get_cmap('tab20', len(df.index))

    # Plot each team's data with unique colors and annotate the latest value on the right
    last_pos = len(df.columns) - 1
    for idx, team in enumerate(df.index):
        series = df.loc[team]
        # plot line
        ax.plot(df.columns, series, marker='o', label=team, color=colormap(idx))
        # annotate at the last (latest) point, put label to the right
        try:
            last_x = df.columns[last_pos]
            last_y = series.iat[last_pos]
        except Exception:
            # Fallback in case of unexpected index types
            last_x = df.columns[-1]
            last_y = series.iloc[-1]

        ax.annotate(
            team,
            xy=(last_x, last_y),
            xytext=(8, 0),
            textcoords='offset points',
            ha='left',
            va='center',
            color=colormap(idx),
            fontproperties=cnFontProp,
            clip_on=False,
        )

    # Reverse the y-axis so rank 1 is on top
    ax.invert_yaxis()

    # Ensure rank ticks are integer and cover full range
    try:
        ymin = int(df.values.min())
        ymax = int(df.values.max())
        ax.set_yticks(range(ymin, ymax + 1))
    except Exception:
        # fallback to default behavior
        pass

    # Add title and adjust layout; leave a little right margin so labels aren't clipped
    ax.set_title(f'北伐! 北伐！ - {league_name}', fontproperties=cnFontProp, size=15, weight='bold')
    plt.tight_layout(rect=[0, 0, 0.95, 1])

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close(fig)

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


def generate_line_chart(df, title, y_label, league_name):
    """
    Generate a line chart for each team in the DataFrame.
    
    Parameters:
    - df: The DataFrame with teams as the index and weeks as the columns.
    - title: The title of the chart.
    - y_label: The label for the y-axis.
    - league_name: The name of the league for the title.
    
    Returns:
    - img_data: The image data of the generated chart.
    """
    # Calculate the figure width based on the number of columns
    num_columns = len(df.columns)
    fig_width = min(max(12, num_columns), 20)

    # Create the plot with higher DPI for better resolution
    plt.figure(figsize=(fig_width, 8), dpi=150)

    # Get a colormap
    colormap = cm.get_cmap('tab20', len(df.index))

    # Define line styles and markers
    line_styles = ['-', '-.']
    markers = [ 'o', 's', 'H', 'D', 'd', '^', 'v', '<', '>', 'p', '*', 'h', '+', 'x', 'X', '|', '_']

    # Calculate the midpoint to split the line styles
    midpoint = len(df.index) // 2

    # Plot each team's data with unique colors
    for idx, team in enumerate(df.index):
        if idx < midpoint:
            line_style = line_styles[0]  # First line style for the first half
            marker = markers[idx % len(markers)]
        else:
            line_style = line_styles[1]  # Second line style for the second half
            marker = markers[(idx - midpoint) % len(markers)]
        plt.plot(df.columns, df.loc[team], marker=marker, label=team, color=colormap(idx), linestyle=line_style)


    # Add title and labels
    plt.title(f'{title} - {league_name}', fontproperties=cnFontProp, size=15, weight='bold')
    # plt.xlabel('Weeks', size=12)
    plt.ylabel(y_label, size=12)

    # Place the legend outside of the plot on the right side
    plt.legend(title='Teams', bbox_to_anchor=(1.02, 1), loc='upper left', prop=cnFontProp)

    # Adjust layout to make room for the legend
    plt.tight_layout(rect=[0, 0, 0.95, 1])

    # Save the plot to a BytesIO object
    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file

    plt.close()

    return img_data



def generate_power_trend_charts(trend_df, average_df, y_label_1, y_label_2, league_name):
    """
    Generate a matplotlib trend chart for each team showing actual values (left axis) and weekly rank (right axis) over weeks.
    Each chart will have the title: '{league_name} - {team} 战力趋势图'.
    Returns a list of BytesIO image data, one per team (order matches DataFrame index).
    """

    img_list = []
    weeks = trend_df.columns

    # Calculate global min/max for y-axis (actual values)
    y_min = trend_df.min().min()
    y_max = trend_df.max().max()
    # Add padding to y-axis limits for better visibility of the average line
    y_range = y_max - y_min
    y_pad = y_range * 0.08 if y_range > 0 else 1
    y_min_adj = y_min - y_pad
    y_max_adj = y_max + y_pad

    # Calculate weekly rank (descending, 1 is best)
    rank_df = trend_df.rank(axis=0, method='min', ascending=False)

    # Calculate global min/max for rank axis
    rank_min = rank_df.min().min()
    rank_max = rank_df.max().max()
    # Add padding to rank axis limits for better visibility of the average rank line
    rank_range = rank_max - rank_min
    rank_pad = rank_range * 0.08 if rank_range > 0 else 1
    rank_min_adj = rank_min - rank_pad
    rank_max_adj = rank_max + rank_pad

    # Handle average and average rank
    avg_map = average_df['Total'].to_dict()
    avg_rank_map = average_df['Total'].rank(ascending=False, method='min').to_dict()

    # Define more distinguishable colors
    color_actual = '#0057b7'      # Deep blue
    color_avg = '#ffb300'         # Vivid orange
    color_rank = '#008744'        # Strong green
    color_avg_rank = '#d62d20'    # Strong red

    for team in trend_df.index:
        fig, ax1 = plt.subplots(figsize=(10, 6), dpi=120)

        # 1. Plot actual values (no marker, no legend)
        ax1.plot(weeks, trend_df.loc[team], color=color_actual, marker='o')
        # 2. Plot average line (no legend)
        avg_val = avg_map[team]
        ax1.axhline(avg_val, color=color_avg, linestyle='--')
        avg_val_str = f'{int(avg_val)}' if avg_val == int(avg_val) else f'{avg_val:.1f}'
        mid_idx = (len(weeks) - 1) / 2
        ax1.annotate(
            avg_val_str,
            xy=(mid_idx, avg_val),
            xytext=(0, -15),
            textcoords='offset points',
            color=color_avg,
            fontproperties=cnFontProp,
            fontsize=14,
            va='bottom',
            ha='center'
        )
        ax1.set_ylabel(y_label_1, color=color_actual)
        ax1.tick_params(axis='y', labelcolor=color_actual)
        ax1.set_ylim(y_min_adj, y_max_adj)
        ax1.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        # 3. Plot rank on right axis (no marker, no legend)
        ax2 = ax1.twinx()
        ax2.plot(weeks, rank_df.loc[team], color=color_rank, marker='o')
        avg_rank_val = avg_rank_map[team]
        avg_rank_val_str = f'{int(avg_rank_val)}' if avg_rank_val == int(avg_rank_val) else f'{avg_rank_val:.1f}'
        ax2.axhline(avg_rank_val, color=color_avg_rank, linestyle='--')
        ax2.annotate(
            avg_rank_val_str,
            xy=(mid_idx, avg_rank_val),
            xytext=(0, 10),
            textcoords='offset points',
            color=color_avg_rank,
            fontproperties=cnFontProp,
            fontsize=12,  # normal font size
            va='bottom',
            ha='center'
        )
        ax2.set_ylabel(y_label_2, color=color_rank)
        ax2.tick_params(axis='y', labelcolor=color_rank)
        ax2.invert_yaxis()  # Rank 1 at the top
        ax2.set_ylim(rank_max_adj, rank_min_adj)
        ax2.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

        # Draw grid using the right axis (so lines are placed at rank tick positions)
        ax2.grid(True, linestyle='--', alpha=0.7)

        # Set x-ticks/labels
        ax1.set_xticks(list(weeks))
        ax1.set_xticklabels(weeks, fontproperties=cnFontProp)

        plt.title(f"{league_name} - {team} 战力走势图", fontproperties=cnFontProp, size=15)
        plt.tight_layout()

        img_data = BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        plt.close()
        img_list.append(img_data)

    return img_list

def generate_score_line_charts(best_score_df, worst_score_df, medium_score_df, actual_score_df, league_name):
    """
    Generate a matplotlib line chart for each team showing best, worst, medium, and actual scores over weeks.
    Each chart will have the title: '{league_name} - {team_name} Score Trend'.
    Returns a list of BytesIO image data, one per team (order matches DataFrame index).
    """

    teams = best_score_df.index
    weeks = best_score_df.columns
    img_list = []
    # Calculate global min/max for y-axis (score values) across all DataFrames
    y_min = min(
        best_score_df.min().min(),
        worst_score_df.min().min(),
        medium_score_df.min().min(),
        actual_score_df.min().min()
    )
    y_max = max(
        best_score_df.max().max(),
        worst_score_df.max().max(),
        medium_score_df.max().max(),
        actual_score_df.max().max()
    )
    y_range = y_max - y_min
    y_pad = y_range * 0.08 if y_range > 0 else 1
    y_min_adj = y_min - y_pad
    y_max_adj = y_max + y_pad

    for team in teams:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        ax.plot(weeks, best_score_df.loc[team], label='Best', color='green', marker='o')
        ax.plot(weeks, worst_score_df.loc[team], label='Worst', color='red', marker='o')
        ax.plot(weeks, medium_score_df.loc[team], label='Medium', color='orange', marker='o')
        ax.plot(weeks, actual_score_df.loc[team], label='Actual', color='blue', marker='o')

        ax.set_title(f"{league_name} - {team} 得分走势图", fontproperties=cnFontProp, size=15)
        ax.set_ylabel('Score', fontproperties=cnFontProp)
        ax.legend(prop=cnFontProp)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_xticks(list(weeks))
        ax.set_xticklabels(weeks, fontproperties=cnFontProp)
        ax.set_ylim(y_min_adj, y_max_adj)
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.tight_layout()

        img_data = BytesIO()
        plt.savefig(img_data, format='png')
        img_data.seek(0)
        plt.close(fig)
        img_list.append(img_data)

    return img_list