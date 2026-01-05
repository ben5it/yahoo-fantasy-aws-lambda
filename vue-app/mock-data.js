// Description: Mock data for the getdata API


export function get_resp_data(league_id, week, numCalled) {

    let resp_data = {
        "league_id": league_id,
        "week": week,
        "state": "IN_PROGRESS",
        "percentage": 20,
        "result": {
        }
    };

    if (numCalled > 1) {
        resp_data.percentage = 40;
        resp_data.result.week = {
            "roto_bar": `data/2025/${league_id}/${week}/roto_bar.png`,
            "roto_stats": `data/2025/${league_id}/${week}/roto_stats.html`,
            "roto_point": `data/2025/${league_id}/${week}/roto_point.html`,
            "matchup_score": `data/2025/${league_id}/${week}/matchup_score.html`,
            "radar_charts": [
                `data/2025/${league_id}/${week}/radar_team_01.png`,
                `data/2025/${league_id}/${week}/radar_team_02.png`,
                `data/2025/${league_id}/${week}/radar_team_03.png`,
                `data/2025/${league_id}/${week}/radar_team_04.png`,
                `data/2025/${league_id}/${week}/radar_team_05.png`,
                `data/2025/${league_id}/${week}/radar_team_06.png`,
                `data/2025/${league_id}/${week}/radar_team_07.png`,
                `data/2025/${league_id}/${week}/radar_team_08.png`,
                `data/2025/${league_id}/${week}/radar_team_09.png`,
                `data/2025/${league_id}/${week}/radar_team_10.png`,
                `data/2025/${league_id}/${week}/radar_team_11.png`,
                `data/2025/${league_id}/${week}/radar_team_12.png`,
                `data/2025/${league_id}/${week}/radar_team_13.png`,
                `data/2025/${league_id}/${week}/radar_team_14.png`,
                `data/2025/${league_id}/${week}/radar_team_15.png`,
                `data/2025/${league_id}/${week}/radar_team_16.png`,
                `data/2025/${league_id}/${week}/radar_team_17.png`,
                `data/2025/${league_id}/${week}/radar_team_18.png`
            ]
        }
    }

    if (numCalled > 2) {
        resp_data.percentage = 60;
        resp_data.result.total = {
            "roto_bar": `data/2025/${league_id}/season/roto_bar.png`,
            "roto_stats": `data/2025/${league_id}/season/roto_stats.html`,
            "roto_point": `data/2025/${league_id}/season/roto_point.html`,
            "radar_charts": [
                `data/2025/${league_id}/season/radar_team_01.png`,
                `data/2025/${league_id}/season/radar_team_02.png`,
                `data/2025/${league_id}/season/radar_team_03.png`,
                `data/2025/${league_id}/season/radar_team_04.png`,
                `data/2025/${league_id}/season/radar_team_05.png`,
                `data/2025/${league_id}/season/radar_team_06.png`,
                `data/2025/${league_id}/season/radar_team_07.png`,
                `data/2025/${league_id}/season/radar_team_08.png`,
                `data/2025/${league_id}/season/radar_team_09.png`,
                `data/2025/${league_id}/season/radar_team_10.png`,
                `data/2025/${league_id}/season/radar_team_11.png`,
                `data/2025/${league_id}/season/radar_team_12.png`,
                `data/2025/${league_id}/season/radar_team_13.png`,
                `data/2025/${league_id}/season/radar_team_14.png`,
                `data/2025/${league_id}/season/radar_team_15.png`,
                `data/2025/${league_id}/season/radar_team_16.png`,
                `data/2025/${league_id}/season/radar_team_17.png`,
                `data/2025/${league_id}/season/radar_team_18.png`
            ]
        }
    }

    if (numCalled > 3) {
        resp_data.percentage = 80;
        resp_data.result.cumulative = {
            "rank_trend": `data/2025/${league_id}/season/rank_trend.png`,
            "standing": `data/2025/${league_id}/season/standing.html`,
            "median_diff_trend": `data/2025/${league_id}/season/median_diff_trend.html`,
            "total_diff_trend": `data/2025/${league_id}/season/total_diff_trend.html`,
            "narrow_victory_trend": `data/2025/${league_id}/season/narrow_victory_trend.html`,
            "pie_charts": [
                `data/2025/${league_id}/season/pie_chart_01.png`,
                `data/2025/${league_id}/season/pie_chart_02.png`,
                `data/2025/${league_id}/season/pie_chart_03.png`,
                `data/2025/${league_id}/season/pie_chart_04.png`,
                `data/2025/${league_id}/season/pie_chart_05.png`,
                `data/2025/${league_id}/season/pie_chart_06.png`,
                `data/2025/${league_id}/season/pie_chart_07.png`,
                `data/2025/${league_id}/season/pie_chart_08.png`,
                `data/2025/${league_id}/season/pie_chart_09.png`,
                `data/2025/${league_id}/season/pie_chart_10.png`,
                `data/2025/${league_id}/season/pie_chart_11.png`,
                `data/2025/${league_id}/season/pie_chart_12.png`,
                `data/2025/${league_id}/season/pie_chart_13.png`,
                `data/2025/${league_id}/season/pie_chart_14.png`,
                `data/2025/${league_id}/season/pie_chart_15.png`,
                `data/2025/${league_id}/season/pie_chart_16.png`,
                `data/2025/${league_id}/season/pie_chart_17.png`,
                `data/2025/${league_id}/season/pie_chart_18.png`
            ],
            "point_trend_charts": [
                `data/2025/${league_id}/season/point_trend_01.png`,
                `data/2025/${league_id}/season/point_trend_02.png`,
                `data/2025/${league_id}/season/point_trend_03.png`,
                `data/2025/${league_id}/season/point_trend_04.png`,
                `data/2025/${league_id}/season/point_trend_05.png`,
                `data/2025/${league_id}/season/point_trend_06.png`,
                `data/2025/${league_id}/season/point_trend_07.png`,
                `data/2025/${league_id}/season/point_trend_08.png`,
                `data/2025/${league_id}/season/point_trend_09.png`,
                `data/2025/${league_id}/season/point_trend_10.png`,
                `data/2025/${league_id}/season/point_trend_11.png`,
                `data/2025/${league_id}/season/point_trend_12.png`,
                `data/2025/${league_id}/season/point_trend_13.png`,
                `data/2025/${league_id}/season/point_trend_14.png`,
                `data/2025/${league_id}/season/point_trend_15.png`,
                `data/2025/${league_id}/season/point_trend_16.png`,
                `data/2025/${league_id}/season/point_trend_17.png`,
                `data/2025/${league_id}/season/point_trend_18.png`
            ],
            "score_trend_charts": [
                `data/2025/${league_id}/season/score_trend_01.png`,
                `data/2025/${league_id}/season/score_trend_02.png`,
                `data/2025/${league_id}/season/score_trend_03.png`,
                `data/2025/${league_id}/season/score_trend_04.png`,
                `data/2025/${league_id}/season/score_trend_05.png`,
                `data/2025/${league_id}/season/score_trend_06.png`,
                `data/2025/${league_id}/season/score_trend_07.png`,
                `data/2025/${league_id}/season/score_trend_08.png`,
                `data/2025/${league_id}/season/score_trend_09.png`,
                `data/2025/${league_id}/season/score_trend_10.png`,
                `data/2025/${league_id}/season/score_trend_11.png`,
                `data/2025/${league_id}/season/score_trend_12.png`,
                `data/2025/${league_id}/season/score_trend_13.png`,
                `data/2025/${league_id}/season/score_trend_14.png`,
                `data/2025/${league_id}/season/score_trend_15.png`,
                `data/2025/${league_id}/season/score_trend_16.png`,
                `data/2025/${league_id}/season/score_trend_17.png`,
                `data/2025/${league_id}/season/score_trend_18.png`
            ]
        }
    }

    if (numCalled > 4) {
        resp_data.state = "COMPLETED";
        resp_data.percentage = 100;
        resp_data.result.forecast = [
            `data/2025/${league_id}/season/radar_forecast_01.png`,
            `data/2025/${league_id}/season/radar_forecast_02.png`,
            `data/2025/${league_id}/season/radar_forecast_03.png`,
            `data/2025/${league_id}/season/radar_forecast_04.png`,
            `data/2025/${league_id}/season/radar_forecast_05.png`,
            `data/2025/${league_id}/season/radar_forecast_06.png`,
            `data/2025/${league_id}/season/radar_forecast_07.png`,
            `data/2025/${league_id}/season/radar_forecast_08.png`,
            `data/2025/${league_id}/season/radar_forecast_09.png`
        ];
    }

    return resp_data;
}
