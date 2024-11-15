<template>
  <div class="container">
    <div v-if="currentLeague">
      <h3 class="text-center my-3">{{ currentLeague.name }}</h3>
      <nav aria-label="..." v-if="analysisResult">
        <ul class="pagination justify-content-end">
          <li v-for="week in weeks" :key="week" class="page-item"
            :class="{ active: week === analysisResult.week, disabled: week > currentLeague.current_week }">
            <a class="page-link" href="#" @click.prevent="setWeek(week)">{{ week }}</a>
          </li>
        </ul>
      </nav>

      <div v-if="analysisResult">
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'roto-week' }"
              @click="activeTab = 'roto-week'">Roto-Week</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'roto-total' }"
              @click="activeTab = 'roto-total'">Roto-Total</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'h2h-matchup' }"
              @click="activeTab = 'h2h-matchup'">H2H-Matchup</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'team-radar' }" @click="activeTab = 'team-radar'">Team
              Radar</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'forecast' }"
              @click="activeTab = 'forecast'">Forecast</a>
          </li>
        </ul>
        <div v-if="activeTab === 'roto-week' || activeTab === 'roto-total'">
          <ul class="nav nav-pills my-3">
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'bar' }" @click="activeSubTab = 'bar'">Bar</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'point' }"
                @click="activeSubTab = 'point'">Point</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'stats' }"
                @click="activeSubTab = 'stats'">Stats</a>
            </li>
          </ul>
          <div v-if="activeSubTab === 'bar'">
            <img v-if="activeTab === 'roto-week'" :src="analysisResult.result.bar_chart_week" alt="Bar Chart Week"
              class="img-fluid">
            <img v-if="activeTab === 'roto-total'" :src="analysisResult.result.bar_chart_total" alt="Bar Chart Total"
              class="img-fluid">
          </div>
          <div v-if="activeSubTab === 'point'">
            <div v-if="activeTab === 'roto-week'" v-html="weekRotoPointHtml"></div>
            <div v-if="activeTab === 'roto-total'" v-html="totalRotoPointHtml"></div>
          </div>
          <div v-if="activeSubTab === 'stats'">
            <div v-if="activeTab === 'roto-week'" v-html="weekRotoStatsHtml"></div>
            <div v-if="activeTab === 'roto-total'" v-html="totalRotoStatsHtml"></div>
          </div>
        </div>
        <div v-if="activeTab === 'h2h-matchup'" v-html="h2hMatchupHtml"></div>
        <div v-else-if="activeTab === 'team-radar'" class="row">
          <h5 class="text-center my-4">Comparision between total and week for each team.</h5>
          <div v-for="(image, index) in analysisResult.result.radar_chart_teams" :key="index" class="col-sm-4">
            <img :src="image" alt="Team Radar Chart" class="img-fluid">
          </div>
        </div>
        <div v-else-if="activeTab === 'forecast'" class="row">
          <h5 class="text-center my-4">TOTAL stats comparision for each matchup next week.</h5>
          <div v-for="(image, index) in analysisResult.result.radar_chart_forecast" :key="index" class="col-sm-4">
            <img :src="image" alt="Forecast Radar Chart" class="img-fluid">
          </div>s
        </div>
      </div>
      <div v-else class="d-flex justify-content-center align-items-center" style="height: 200px;">
        <p>Loading data from yahoo and analyzing... <span v-if="percentage !== null">{{ percentage }}%</span></p>
      </div>
    </div>
    <div v-else>
      <p class="text-center">No league selected.</p>
    </div>
  </div>
</template>

<script>
import { ref, inject, computed, onMounted, onUnmounted, shallowReactive } from 'vue';

export default {
  name: 'AnalysisResult',
  setup() {
    const leagueStore = inject('leagueStore');
    const currentLeague = leagueStore.state.currentLeague;
    const analysisResult = ref(null);
    const intervalId = ref(null);
    const percentage = ref(null);
    const activeTab = ref('roto-week');
    const activeSubTab = ref('bar');
    
    const weekRotoPointHtml = ref(null);
    const weekRotoStatsHtml = ref(null);
    const totalRotoPointHtml = ref(null);
    const totalRotoStatsHtml = ref(null);
    const h2hMatchupHtml = ref(null);

    const loadHtmlContent = async(url) => {
      try {
        const response = await fetch(url);
        if (response.ok) {
          return await response.text();
        } else {
          console.error('Failed to load HTML content:', response.statusText);
          return null;
        }
      } catch (error) {
        console.error('Error loading HTML content:', error);
        return null;
      }
    }

    const fetchData = async (week) => {
      try {
        let url = `/api/getdata?league_id=${currentLeague.league_id}`;
        if (week) {
          url += `&week=${week}`;
        }
        const response = await fetch(url);
        const data = await response.json();
        if (data.state === 'COMPLETED') {
          analysisResult.value = data;
          clearInterval(intervalId.value);

          weekRotoPointHtml.value = await loadHtmlContent(data.result.roto_point_week);
          weekRotoStatsHtml.value = await loadHtmlContent(data.result.roto_stats_week);
          totalRotoPointHtml.value = await loadHtmlContent(data.result.roto_point_total);
          totalRotoStatsHtml.value = await loadHtmlContent(data.result.roto_stats_total);
          h2hMatchupHtml.value = await loadHtmlContent(data.result.h2h_matchup_week);

        } else if (data.state === 'IN_PROGRESS') {
            percentage.value = data.percentage;
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

    if (currentLeague) {
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

    onMounted(() => {
      if (currentLeague) {
        intervalId.value = setInterval(fetchData, 5000);
      }
    });

    onUnmounted(() => {
      if (intervalId.value) {
        clearInterval(intervalId.value);
      }
    });

    const setWeek = (week) => {
      if (week <= currentLeague.current_week) {
        // clear the previous result
        analysisResult.value = null; 
        percentage.value = null;

        // Call the function immediately
        fetchData(week);

        // Set the interval to call the function every 5 seconds
        intervalId.value = setInterval(() => fetchData(week), 5000);
      }
    };

    return {
      currentLeague,
      analysisResult,
      percentage,
      activeTab,
      activeSubTab,
      weekRotoPointHtml,
      weekRotoStatsHtml,
      totalRotoPointHtml,
      totalRotoStatsHtml,
      h2hMatchupHtml,
      weeks,
      setWeek
    };
  }
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