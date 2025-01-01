<template>
  <div class="container">
    <div v-if="currentLeague">
      <h3 class="text-center my-3">{{ currentLeague.name }}</h3>
      <div v-if="analysisResult">
        <nav aria-label="...">
          <ul class="pagination justify-content-end">
            <li
              v-for="week in weeks"
              :key="week"
              class="page-item"
              :class="{
                active: week === analysisWeek,
                disabled: week > currentLeague.current_week,
              }"
            >
              <a class="page-link" href="#" @click.prevent="setWeek(week)">{{
                week
              }}</a>
            </li>
          </ul>
        </nav>

        <div>
          <ul class="nav nav-tabs">
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'week' }"
                @click="setActiveTab('week', 'week_bar')"
                >单周</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'season' }"
                @click="setActiveTab('season', 'season_bar')"
                >整季</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'trend' }"
                @click="setActiveTab('trend', 'trend_rank')"
                >走势</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'luck' }"
                @click="setActiveTab('luck', 'luck_median')"
                >运势</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                :class="{ active: activeTab === 'forecast' }"
                @click="activeTab = 'forecast'"
                >神棍</a
              >
            </li>
          </ul>

          <div v-if="activeTab === 'week'">
            <div v-if="analysisResult.week">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'week_bar' }"
                    @click="activeSubTab = 'week_bar'"
                    >战力柱状图</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'week_point' }"
                    @click="activeSubTab = 'week_point'"
                    >战力明细表</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'week_stats' }"
                    @click="activeSubTab = 'week_stats'"
                    >原始数据表</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'week_matchup' }"
                    @click="activeSubTab = 'week_matchup'"
                    >虚拟对阵表</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'week_radar' }"
                    @click="activeSubTab = 'week_radar'"
                    >雷达图</a
                  >
                </li>
              </ul>
              <div v-if="activeSubTab === 'week_bar'">
                <img
                  :src="analysisResult.week.roto_bar"
                  alt="Bar Chart Week"
                  class="img-fluid"
                />
              </div>
              <div v-if="activeSubTab === 'week_point'">
                <p class="text-center my-3">
                  <strong>注：</strong>战力明细表采用Roto计分方式，
                  即将每项数据按强弱排名，最强的队得分最高。<br />举例来说，如联盟有18支球队，则最强的队得分为18分，最弱的队得分为1分。
                </p>
                <div v-html="weekPointHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_stats'">
                <div v-html="weekStatsHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_matchup'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >虚拟对阵表是计算你对阵联盟所有其他球队能取得的比分，取其中位数和你实际得分做对比。
                </p>
                <div v-html="weekMatchupHtml"></div>
              </div>
              <div v-if="activeSubTab === 'week_radar'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >雷达图是战力明细表的图形化显示，可以直观看出队伍在各项数据上的表现。
                </p>
                <div class="row">
                  <div
                    v-for="(image, index) in analysisResult.week.radar_charts"
                    :key="index"
                    class="col-sm-4"
                  >
                    <img
                      :src="image"
                      alt="Team Radar Chart"
                      class="img-fluid"
                    />
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">持续分析中，请稍等... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'season'">
            <div v-if="analysisResult.total">
              <ul class="nav nav-pills my-3">
                <li class="nav-item" v-if="analysisResult.total">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_bar' }"
                    @click="activeSubTab = 'season_bar'"
                    >战力柱状图</a
                  >
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_point' }"
                    @click="activeSubTab = 'season_point'"
                    >战力明细表</a
                  >
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_stats' }"
                    @click="activeSubTab = 'season_stats'"
                    >原始数据表</a
                  >
                </li>
                <li class="nav-item" v-if="analysisResult.total">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_radar' }"
                    @click="activeSubTab = 'season_radar'"
                    >雷达图</a
                  >
                </li>
                <li class="nav-item" v-if="analysisResult.cumulative">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_standing' }"
                    @click="activeSubTab = 'season_standing'"
                    >排行榜</a
                  >
                </li>
                <li class="nav-item" v-if="analysisResult.cumulative">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'season_pie' }"
                    @click="activeSubTab = 'season_pie'"
                    >得分占比图</a
                  >
                </li>
              </ul>
              <div v-if="activeSubTab === 'season_bar'">
                <img
                  :src="analysisResult.total.roto_bar"
                  alt="Bar Chart season"
                  class="img-fluid"
                />
              </div>
              <div v-if="activeSubTab === 'season_point'">
                <p class="text-center my-3">
                  <strong>注：</strong>战力明细表采用Roto计分方式，
                  即将每项数据按强弱排名，最强的队得分最高。<br />举例来说，如联盟有18支球队，则最强的队得分为18分，最弱的队得分为1分。
                </p>
                <div v-html="totalPointHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_stats'">
                <div v-html="totalStatsHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_standing'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >各分项的数字为您在该项数据总计赢得的分数。
                </p>
                <div v-html="totalStandingHtml"></div>
              </div>
              <div v-if="activeSubTab === 'season_radar'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >雷达图是战力明细表的图形化显示，可以直观看出队伍在各项数据上的表现。
                </p>
                <div class="row">
                  <div
                    v-for="(image, index) in analysisResult.total.radar_charts"
                    :key="index"
                    class="col-sm-4"
                  >
                    <img
                      :src="image"
                      alt="Team Radar Chart"
                      class="img-fluid"
                    />
                  </div>
                </div>
              </div>
              <div v-if="activeSubTab === 'season_pie'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >得分占比图是计算队伍各项数据<strong>实际拿分</strong>的占比。
                </p>
                <div class="row">
                  <div
                    v-for="(image, index) in analysisResult.cumulative
                      .pie_charts"
                    :key="index"
                    class="col-sm-4"
                  >
                    <img :src="image" alt="Team pie Chart" class="img-fluid" />
                  </div>
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">持续分析中，请稍等... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'trend'">
            <div v-if="analysisResult.cumulative">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'trend_rank' }"
                    @click="activeSubTab = 'trend_rank'"
                    >排名</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'trend_point' }"
                    @click="activeSubTab = 'trend_point'"
                    >战力</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'trend_score' }"
                    @click="activeSubTab = 'trend_score'"
                    >拿分</a
                  >
                </li>
              </ul>
              <div v-if="activeSubTab === 'trend_rank'">
                <img
                  :src="analysisResult.cumulative.rank_trend"
                  alt="Rank Trend"
                  class="img-fluid"
                />
              </div>
              <div v-if="activeSubTab === 'trend_point'">
                <img
                  :src="analysisResult.cumulative.point_trend"
                  alt="Point Trend"
                  class="img-fluid"
                />
              </div>
              <div v-if="activeSubTab === 'trend_score'">
                <img
                  :src="analysisResult.cumulative.score_trend"
                  alt="Score Trend"
                  class="img-fluid"
                />
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">持续分析中，请稍等... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'luck'">
            <div v-if="analysisResult.cumulative">
              <ul class="nav nav-pills my-3">
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'luck_median' }"
                    @click="activeSubTab = 'luck_median'"
                    >走位</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'luck_total' }"
                    @click="activeSubTab = 'luck_total'"
                    >爆种</a
                  >
                </li>
                <li class="nav-item">
                  <a
                    class="nav-link"
                    :class="{ active: activeSubTab === 'luck_narrow_victory' }"
                    @click="activeSubTab = 'luck_narrow_victory'"
                    >险胜</a
                  >
                </li>
              </ul>
              <p class="text-center my-3">
                都说 H2H 全靠运气，那么就让我们看看到底谁的运气最好吧！
              </p>
              <div v-if="activeSubTab === 'luck_median'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >走位是计算你每周中位数得分和实际得分的差值，正数表示你的运气好，负数表示你的运气差。
                </p>
                <div v-html="medianDiffTrendHtml"></div>
              </div>
              <div v-if="activeSubTab === 'luck_total'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >计算对手在和你对阵时的战力排名和他整季的战力排名之差。正数表示你当周对手拉跨，负数表示你当周对手爆种。
                </p>
                <div v-html="totalDiffTrendHtml"></div>
              </div>
              <div v-if="activeSubTab === 'luck_narrow_victory'">
                <p class="text-center my-3">
                  <strong>注：</strong
                  >险胜是指你某项数据刚好就赢了一点点，比如你篮板<b>200</b>个，你对手<b>199</b>个，那么你的险胜次数就加1。<br>
                  对于小数，最后一位相差1，则认为是险胜, 如 0.478 对 0.477， 或者 1.98 对 1.97。<br>
                  倘若当周你有三项数据险胜对面，但是另有一项数据被对面险胜，那么你当周的险胜次数就是2。<br>
                  每周的险胜次数会累加到整季【Total】中。
                </p>
                <div v-html="narrowVictorTrendHtml"></div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">持续分析中，请稍等... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>

          <div v-else-if="activeTab === 'forecast'">
            <div v-if="analysisResult.forecast">
              <p class="text-center my-3">
                <strong>注：</strong
                >根据<strong>过往整季</strong>数据，预测下组对阵。<strong>未考虑</strong>球员场均数据以及对阵场次，结果仅供参考(娱乐)。
              </p>
              <div v-if="analysisResult.forecast" class="row">
                <div
                  v-for="(image, index) in analysisResult.forecast"
                  :key="index"
                  class="col-sm-4"
                >
                  <img
                    :src="image"
                    alt="Forecast Radar Chart"
                    class="img-fluid"
                  />
                </div>
              </div>
            </div>
            <div v-else>
              <p class="text-center my-3">持续分析中，请稍等... <span v-if="percentage !== null">{{ percentage }}%</span></p>
            </div>
          </div>
        </div>
      </div>
      <div v-else>
        <div
          class="d-flex justify-content-center align-items-center"
          style="height: 200px"
        >
          <p class="text-center my-3">
            Loading data from yahoo and analyzing...
            <span v-if="percentage !== null">{{ percentage }}%</span>
          </p>
        </div>
        <p class="text-center my-3">
          <strong>注：</strong
          >进度到25%左右的时候,会有单周分析结果出现。其它分析会在后台继续进行，分析完后会自动更新页面。
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
      const endWeek = currentLeague.current_week;
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
