<template>
  <div class="container">
    <div v-if="currentLeague">
      <h3 class="text-center my-3">{{ currentLeague.name }}</h3>
      <div v-if="analysisResult">
        <nav aria-label="...">
          <ul class="pagination justify-content-end">
            <li v-for="week in weeks" :key="week" class="page-item" :class="{
                active: week === analysisWeek,
                disabled: week > currentLeague.current_week,
              }">
              <a class="page-link" href="#" @click.prevent="setWeek(week)">{{
                week
                }}</a>
            </li>
          </ul>
        </nav>

        <div>
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'week' }"
                @click="setActiveTab('week', 'week_bar')">Weekly</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'season' }"
                @click="setActiveTab('season', 'season_bar')">Season</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'trend' }"
                @click="setActiveTab('trend', 'trend_rank')">Trend</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'luck' }"
                @click="setActiveTab('luck', 'luck_median')">Luck</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeTab === 'forecast' }" @click="activeTab = 'forecast'">Forecast</a>
            </li>
          </ul>

          <div v-if="activeTab === 'week'">
            <div v-if="analysisResult.week">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'week_bar' }"
                    @click="activeSubTab = 'week_bar'">Power Bar Chart</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'week_point' }"
                    @click="activeSubTab = 'week_point'">Power Detail Table</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'week_stats' }"
                    @click="activeSubTab = 'week_stats'">Raw Data Table</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'week_matchup' }"
                    @click="activeSubTab = 'week_matchup'">Virtual Matchup Table</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'week_radar' }"
                    @click="activeSubTab = 'week_radar'">Radar Chart</a>
                </li>
              </ul>
              <div v-if="activeSubTab === 'week_bar'">
                <img :src="analysisResult.week.roto_bar" alt="Bar Chart Week" class="img-fluid" />
              </div>
              <div v-if="activeSubTab === 'week_point'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The power detail table uses Roto scoring,
                  ranking each stat category by strength, with the strongest team scoring the highest. <br />For example, if a league has 18 teams, the strongest team scores 18 points and the weakest scores 1 point.
                </p>
                <div v-html="weekPointHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_stats'">
                <div v-html="weekStatsHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_matchup'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The virtual matchup table calculates the score you would achieve against every other team in the league, then compares the median of those scores with your actual score.
                </p>
                <div v-html="weekMatchupHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_radar'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The radar chart is a graphical view of the power detail table, making it easy to see each team's performance across stat categories.
                </p>
                <div class="row">
                  <div v-for="(image, index) in analysisResult.week.radar_charts" :key="index" class="col-sm-4">
                    <img :src="image" alt="Team Radar Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">Analysis in progress, please wait... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'season'">
            <div v-if="analysisResult.total">
              <ul class="nav nav-pills my-3">
                <li class="nav-item" v-if="analysisResult.total">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_bar' }"
                    @click="activeSubTab = 'season_bar'">Power Bar Chart</a>
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_point' }"
                    @click="activeSubTab = 'season_point'">Power Detail Table</a>
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_stats' }"
                    @click="activeSubTab = 'season_stats'">Raw Data Table</a>
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_radar' }"
                    @click="activeSubTab = 'season_radar'">Radar Chart</a>
                </li>
                <li class="nav-item" v-if="analysisResult.cumulative">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_standing' }"
                    @click="activeSubTab = 'season_standing'">Standings</a>
                </li>
                <li class="nav-item" v-if="analysisResult.cumulative">
                  <a class="nav-link" :class="{ active: activeSubTab === 'season_pie' }"
                    @click="activeSubTab = 'season_pie'">Score Share Chart</a>
                </li>
              </ul>
              <div v-if="activeSubTab === 'season_bar'">
                <img :src="analysisResult.total.roto_bar" alt="Bar Chart season" class="img-fluid" />
              </div>
              <div v-if="activeSubTab === 'season_point'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The power detail table uses Roto scoring,
                  ranking each stat category by strength, with the strongest team scoring the highest. <br />For example, if a league has 18 teams, the strongest team scores 18 points and the weakest scores 1 point.
                </p>
                <div v-html="totalPointHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_stats'">
                <div v-html="totalStatsHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_standing'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The number for each category is the total points you have won in that stat category.
                </p>
                <div v-html="totalStandingHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_radar'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The radar chart is a graphical view of the power detail table, making it easy to see each team's performance across stat categories.
                </p>
                <div class="row">
                  <div v-for="(image, index) in analysisResult.total.radar_charts" :key="index" class="col-sm-4">
                    <img :src="image" alt="Team Radar Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
              <div v-if="activeSubTab === 'season_pie'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The score share chart calculates the proportion of <strong>actual points earned</strong> by each team in every stat category.
                </p>
                <div class="row">
                  <div v-for="(image, index) in analysisResult.cumulative
                      .pie_charts" :key="index" class="col-sm-4">
                    <img :src="image" alt="Team pie Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">Analysis in progress, please wait... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'trend'">
            <div v-if="analysisResult.cumulative">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'trend_rank' }"
                    @click="activeSubTab = 'trend_rank'">Rank</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'trend_point' }"
                    @click="activeSubTab = 'trend_point'">Power</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'trend_score' }"
                    @click="activeSubTab = 'trend_score'">Points</a>
                </li>
              </ul>
              <div v-if="activeSubTab === 'trend_rank'">
                <img :src="analysisResult.cumulative.rank_trend" alt="Rank Trend" class="img-fluid" />
              </div>
              <div v-if="activeSubTab === 'trend_point'">
                <p class="text-center my-3">
                  <strong>Note:</strong> The dashed line represents season-total data, while the solid line represents weekly data.
                </p>
                <div class="row">
                  <div v-for="(image, index) in analysisResult.cumulative
                    .point_trend_charts" :key="index" class="col-sm-6">
                    <img :src="image" alt="Team Power Trend Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
              <div v-if="activeSubTab === 'trend_score'">
                <div class="row">
                  <div v-for="(image, index) in analysisResult.cumulative
                    .score_trend_charts" :key="index" class="col-sm-6">
                    <img :src="image" alt="Team Score Trend Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">Analysis in progress, please wait... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'luck'">
            <div v-if="analysisResult.cumulative">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'luck_median' }"
                    @click="activeSubTab = 'luck_median'">Median Luck</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'luck_total' }"
                    @click="activeSubTab = 'luck_total'">Blowout Luck</a>
                </li>
                <li class="nav-item">
                  <a class="nav-link" :class="{ active: activeSubTab === 'luck_narrow_victory' }"
                    @click="activeSubTab = 'luck_narrow_victory'">Narrow Win</a>
                </li>
              </ul>
              <p class="text-center my-3">
                They say H2H is all about luck — let's see who's actually the luckiest!
              </p>
              <div v-if="activeSubTab === 'luck_median'">
                <p class="text-center my-3">
                  <strong>Note:</strong> Median Luck is the difference between your weekly median score and your actual score. A positive number means good luck; a negative number means bad luck.
                </p>
                <div v-html="medianDiffTrendHtml"></div>
              </div>
              <div v-if="activeSubTab === 'luck_total'">
                <p class="text-center my-3">
                  <strong>Note:</strong> This is the difference between your opponent's power ranking in the week they faced you and their power ranking for the whole season. A positive number means your opponent underperformed that week; a negative number means your opponent had a breakout week.
                </p>
                <div v-html="totalDiffTrendHtml"></div>
              </div>
              <div v-if="activeSubTab === 'luck_narrow_victory'">
                <p class="text-center my-3">
                  <strong>Note:</strong> A narrow win means you won a stat category by just a hair, e.g. you have <b>200</b> rebounds and your opponent has <b>199</b>, so your narrow win count increases by 1.<br>
                  For decimals, a difference of 1 in the last digit counts as a narrow win, e.g. 0.478 vs 0.477, or 1.98 vs 1.97.<br>
                  If you narrowly win three categories in a week but narrowly lose another, your narrow win count for that week is 2.<br>
                  Weekly narrow win counts accumulate into the season-long [Total].
                </p>
                <div v-html="narrowVictorTrendHtml"></div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">Analysis in progress, please wait... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'forecast'">
            <div v-if="analysisResult.forecast">
              <p class="text-center my-3">
                <strong>Note:</strong> Forecasts the next matchups based on <strong>past full-season</strong> data. Player per-game averages and the matchup schedule are <strong>not taken into account</strong> — results are for reference (entertainment) only.
              </p>
              <div v-if="analysisResult.forecast" class="row">
                <div v-for="(image, index) in analysisResult.forecast" :key="index" class="col-sm-4">
                  <img :src="image" alt="Forecast Radar Chart" class="img-fluid" />
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">Analysis in progress, please wait... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <div class="d-flex justify-content-center align-items-center" style="height: 200px">
          <p class="text-center my-3">
            Loading data from yahoo and analyzing...
            <span v-if="percentage !== null">{{ percentage }}%</span>
          </p>
        </div>
        <p class="text-center my-3">
          <strong>Note:</strong> Once progress reaches around 25%, the weekly analysis results will appear. Other analyses continue in the background and the page will update automatically once they finish.
        </p>
      </div>
    </div>
    <div v-else>
      <p class="text-center">No league selected.</p>
    </div>
  </div>
</template>

<script>
import {
  ref,
  inject,
  computed,
  shallowReactive,
} from "vue";

export default {
  name: "AnalysisResult",
  setup() {
    const leagueStore = inject("leagueStore");
    const currentLeague = leagueStore.state.currentLeague;

    const analysisWeek = ref(null);
    const analysisResult = ref(null);
    const percentage = ref(null);

    const activeTab = ref("week");
    const activeSubTab = ref("week_bar");

    // html tables for week tab
    const weekPointHtml = ref(null);
    const weekStatsHtml = ref(null);
    const weekMatchupHtml = ref(null);

    // html tables for season tab
    const totalPointHtml = ref(null);
    const totalStatsHtml = ref(null);
    const totalStandingHtml = ref(null);

    // html tables for luck tab
    const medianDiffTrendHtml = ref(null);
    const totalDiffTrendHtml = ref(null);
    const narrowVictorTrendHtml = ref(null);

    const loadHtmlContent = async (url) => {
      try {
        const response = await fetch(url);
        if (response.ok) {
          return await response.text();
        } else {
          console.error("Failed to load HTML content:", response.statusText);
          return null;
        }
      } catch (error) {
        console.error("Error loading HTML content:", error);
        return null;
      }
    };

    const fetchData = async (week) => {
      try {
        let url = `/api/getdata?league_id=${currentLeague.league_id}`;
        if (week) {
          url += `&week=${week}`;
        }
        const response = await fetch(url);

        if (response.ok) {
          // 202 means the analysis is still in progress, so send another request after 7 seconds
          if (response.status == 202) {
            setTimeout(fetchData, 7000);
          }

          const data = await response.json();

          analysisWeek.value = data.week;
          percentage.value = data.percentage;
          // no result yet
          if (Object.keys(data.result).length > 0) {
            analysisResult.value = data.result;

            if (data.result.week) {
              if (!weekPointHtml.value) {
                weekPointHtml.value = await loadHtmlContent(
                  data.result.week.roto_point
                );
              }

              if (!weekStatsHtml.value) {
                weekStatsHtml.value = await loadHtmlContent(
                  data.result.week.roto_stats
                );
              }
              if (!weekMatchupHtml.value) {
                weekMatchupHtml.value = await loadHtmlContent(
                  data.result.week.matchup_score
                );
              }
            }

            if (data.result.total) {
              if (!totalPointHtml.value) {
                totalPointHtml.value = await loadHtmlContent(
                  data.result.total.roto_point
                );
              }
              if (!totalStatsHtml.value) {
                totalStatsHtml.value = await loadHtmlContent(
                  data.result.total.roto_stats
                );
              }
            }

            if (data.result.cumulative) {
              if (!totalStandingHtml.value) {
                totalStandingHtml.value = await loadHtmlContent(
                  data.result.cumulative.standing
                );
              }
              if (!medianDiffTrendHtml.value) {
                medianDiffTrendHtml.value = await loadHtmlContent(
                  data.result.cumulative.median_diff_trend
                );
              }
              if (!totalDiffTrendHtml.value) {
                totalDiffTrendHtml.value = await loadHtmlContent(
                  data.result.cumulative.total_diff_trend
                );
              }
              if (!narrowVictorTrendHtml.value) {
                narrowVictorTrendHtml.value = await loadHtmlContent(
                  data.result.cumulative.narrow_victory_trend
                );
              }
            }
          }
        } else {
          console.error("Failed to fetch data:", response.statusText);
          return;
        }
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    if (currentLeague) {
      // run analysis for all previous weeks stealthily in the background
      // because user may want to see the previous weeks analysis
      // so that they can get those result faster,
      // but we don't need to wait for those results.
      const startWeek = parseInt(currentLeague.start_week);
      const current_week = currentLeague.current_week;
      const playoffStart = parseInt(currentLeague.playoff_start_week);

      let endWeek;
      // if playoffs started, only analyze up to the week before playoffs
      if (playoffStart > startWeek && current_week >= playoffStart) {
        endWeek = playoffStart - 1;
      } else {
        endWeek = current_week;
      }

      for (let week = startWeek; week < endWeek; week++) {
        let url = `/api/getdata?league_id=${currentLeague.league_id}&week=${week}`;
        fetch(url);
      }

      fetchData();
    }

    const weeks = computed(() => {
      const startWeek = parseInt(currentLeague.start_week);
      const endWeek = currentLeague.current_week;
      const weeksArray = [];
      for (let week = startWeek; week <= endWeek; week++) {
        weeksArray.push(week);
      }

      // show only last 8 weeks, otherwise it will be too long
      if (weeksArray.length > 8) {
        weeksArray.splice(0, weeksArray.length - 8);
      }

      return weeksArray;
    });

    const setWeek = (week) => {
      if (week <= currentLeague.current_week) {
        // clear the previous result
        analysisResult.value = null;
        percentage.value = null;

        // these three pages need to reload if switch week
        weekStatsHtml.value = null;
        weekPointHtml.value = null;
        weekMatchupHtml.value = null;

        // Call the function immediately
        fetchData(week);
      }
    };

    const setActiveTab = (tab, subTab) => {
      activeTab.value = tab;
      activeSubTab.value = subTab;
    };

    return {
      currentLeague,
      analysisWeek,
      analysisResult,
      percentage,
      activeTab,
      activeSubTab,

      weekPointHtml,
      weekStatsHtml,
      weekMatchupHtml,
      totalPointHtml,
      totalStatsHtml,
      totalStandingHtml,
      medianDiffTrendHtml,
      totalDiffTrendHtml,
      narrowVictorTrendHtml,
      weeks,
      setWeek,
      setActiveTab,
    };
  },
};
</script>

<style scoped>
.container {
  padding: 16px;
}

h2 {
  margin-bottom: 24px;
}

h3 {
  margin-top: 16px;
}

p {
  margin: 8px 0;
}

.img-fluid {
  max-width: 100%;
  height: auto;
}
</style>
