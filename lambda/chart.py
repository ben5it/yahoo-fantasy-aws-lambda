#!/usr/bin/env python

from io import BytesIO
import numpy as np

import matplotlib
matplotlib.use('Agg')
from matplotlib import font_manager
cnFontProp = font_manager.FontProperties(fname='SimSun-01.ttf')
import matplotlib.pyplot as plt

def league_bar_chart(df, title, sort=False):
    '''Generate a bar chart displaying the total score of each team
    '''
    if sort:
        # sort by total
        sorted_df = df.sort_values(by=['Total'], ascending=False)
    else:
        sorted_df = df

    names = sorted_df.index
    scores = sorted_df['Total']

    pos = list(range(1, len(names)+1))

    width = 0.5

    # Plotting the bars
    fig, ax = plt.subplots(figsize=(12,9), dpi=120)

    # Create a bar with week score,
    # in position pos,
    bar_container = plt.bar([p for p in pos], scores, width, alpha=0.7, color='#03396c', edgecolor='#011f4b')
    # plt.bar([p + width/2 for p in pos], week_scores, width, alpha=0.25, color='#429bf4', edgecolor='#429bf4', label='Week')

    # add label (value) to each team
    ax.bar_label(bar_container, padding = 3)

    # Set the y axis label
    ax.set_ylabel('Score')

    # Set the chart's title
    ax.set_title(title, fontproperties = cnFontProp)

    # Make the y-axis (0-100) labels smaller.
    # ax.tick_params(labelsize=8)

    # Set the position of the x ticks
    ax.set_xticks([p for p in pos])
    # Set the labels for the x ticks
    ax.set_xticklabels(names, rotation=30, ha='right', fontproperties = cnFontProp)



    # Setting the x-axis and y-axis limits
    # plt.xlim(min(pos)-width, max(pos)+width*4)
    # plt.ylim(0, 180 )

    # Adding the legend and showing the plot
    # plt.legend(['Total', 'Week '+ str(week)], loc='upper right')
    plt.grid(linestyle='--', linewidth=1, axis='y', alpha=0.7)

    plt.tight_layout()

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file
    # figdata_png = base64.b64encode(img_data.getvalue())
    # figdata_png = figdata_png.decode('utf8')
    plt.close()

    return img_data

def league_radar_charts(week_df, total_df, week):
    charts = []

    # get the stat names, need to remove the last column 'total'
    stat_names = week_df.columns.values.tolist()[:-1]
    # app.logger.debug(stat_names)
    team_names = week_df.index.tolist()
    # app.logger.debug(team_names)

    labels = ['Total', 'Week {}'.format(week)]

    for team_name in team_names:
        # get the stat scores, need to remove the last column 'total'
        week_score = week_df.loc[team_name].values.tolist()[:-1]
        total_score = total_df.loc[team_name].values.tolist()[:-1]
        chart = get_radar_chart(stat_names, total_score, week_score, len(team_names), labels, team_name)
        charts.append(chart)

    return charts


def get_radar_chart(stat_names, stat_values_1, state_values_2, value_limit, labels, chart_title):
    # app.logger.debug(stat_values_1)
    # app.logger.debug(state_values_2)
    # app.logger.debug(value_limit)

    # Number of variables we're plotting.
    num_vars = len(stat_names)

    # Split the circle into even parts and save the angles
    # so we know where to put each axis.
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()

    # The plot is a circle, so we need to "complete the loop"
    # and append the start value to the end.
    angles += angles[:1]
    stat_values_1 += stat_values_1[:1]
    state_values_2 += state_values_2[:1]

    # ax = plt.subplot(polar=True)
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))


    ax.plot(angles, stat_values_1, color='#1aaf6c', linewidth=1, label=labels[0])
    ax.fill(angles, stat_values_1, color='#1aaf6c', alpha=0.5)

    ax.plot(angles, state_values_2, color='#429bf4', linewidth=1, label=labels[1])
    ax.fill(angles, state_values_2, color='#429bf4', alpha=0.25)

    # Fix axis to go in the right order and start at 12 o'clock.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Draw axis lines for each angle and label.
    ax.set_thetagrids(np.degrees(angles[:-1]), stat_names)

    # Go through stat_names and adjust alignment based on where
    # it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Ensure radar goes from 0 to value_limit.
    ax.set_ylim(0, value_limit)

    # Set position of y-stat_names (0-100) to be in the middle
    # of the first two axes.
    ax.set_rlabel_position(180 / num_vars)

    # Add some custom styling.
    # Change the color of the tick stat_names.
    ax.tick_params(colors='#222222')
    # Make the y-axis (0-100) stat_names smaller.
    ax.tick_params(axis='y', labelsize=8)
    # Change the color of the circular gridlines.
    ax.grid(color='#AAAAAA')
    # Change the color of the outermost gridline (the spine).
    ax.spines['polar'].set_color('#222222')
    # Change the background color inside the circle itself.
    ax.set_facecolor('#FAFAFA')

    ax.set_title(chart_title, y=1.08, fontproperties = cnFontProp)

    # Add a legend as well.
    ax.legend(loc='upper right', frameon=False, bbox_to_anchor=(1.15, 1.1))

    img_data = BytesIO()
    plt.savefig(img_data, format='png')
    img_data.seek(0)  # rewind to beginning of file
    # figdata_png = base64.b64encode(img_data.getvalue())
    # figdata_png = figdata_png.decode('utf8')

    plt.close()

    return img_data


def next_matchup_radar_charts(df, matchups, week):
    charts = []

    # get the stat names, need to remove the last column 'total'
    stat_names = df.columns.values.tolist()[:-1]
    team_names = df.index.tolist()
    chart_title = '第{}周对战参考'.format(week)

    for i in range(0, len(matchups), 2 ): 
        team_name_1 = matchups[i]
        team_name_2 = matchups[i+1]
        labels = [team_name_1,  team_name_2]
        team_score_1 = df.loc[team_name_1].values.tolist()[:-1]
        team_score_2 = df.loc[team_name_2].values.tolist()[:-1]
        chart = get_radar_chart(stat_names, team_score_1, team_score_2, len(team_names), labels, chart_title)
        charts.append(chart)

    return charts