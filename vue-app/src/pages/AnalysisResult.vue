<template>
  <div class="container">

    <div v-if="currentLeague">
      <h3 class="text-center my-3">{{ currentLeague.name }}</h3>
      <div v-if="analysisResult">
        <h4 class="text-center my-4">Week {{ analysisResult.week }} Analysis Result</h4>
        <ul class="nav nav-tabs">
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'roto-week' }" @click="activeTab = 'roto-week'">Roto-Week</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'roto-total' }" @click="activeTab = 'roto-total'">Roto-Total</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'h2h-matchup' }" @click="activeTab = 'h2h-matchup'">H2H-Matchup</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'team-radar' }" @click="activeTab = 'team-radar'">Team Radar</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" :class="{ active: activeTab === 'forecast' }" @click="activeTab = 'forecast'">Forecast</a>
          </li>
        </ul>
        <div v-if="activeTab === 'roto-week' || activeTab === 'roto-total'">
          <ul class="nav nav-pills my-3">
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'bar' }" @click="activeSubTab = 'bar'">Bar</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'point' }" @click="activeSubTab = 'point'">Point</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ active: activeSubTab === 'stats' }" @click="activeSubTab = 'stats'">Stats</a>
            </li>
          </ul>
          <div v-if="activeSubTab === 'bar'">
            <img v-if="activeTab === 'roto-week'" :src="analysisResult.result.bar_chart_week" alt="Bar Chart Week" class="img-fluid">
            <img v-if="activeTab === 'roto-total'" :src="analysisResult.result.bar_chart_total" alt="Bar Chart Total" class="img-fluid">
          </div>
          <div v-if="activeSubTab === 'point'">
            <iframe v-if="activeTab === 'roto-week'" :src="analysisResult.result.roto_point_week" width="100%" height="1600px" frameborder="0"></iframe>
            <iframe v-if="activeTab === 'roto-total'" :src="analysisResult.result.roto_point_total" width="100%" height="1600px" frameborder="0"></iframe>
          </div>
          <div v-if="activeSubTab === 'stats'">
            <iframe v-if="activeTab === 'roto-week'" :src="analysisResult.result.roto_stats_week" width="100%" height="1600px" frameborder="0"></iframe>
            <iframe v-if="activeTab === 'roto-total'" :src="analysisResult.result.roto_stats_total" width="100%" height="1600px" frameborder="0"></iframe>
          </div>
        </div>
        <div v-else-if="activeTab === 'h2h-matchup'">
          <iframe :src="analysisResult.result.h2h_matchup_week" width="100%" height="1600px" frameborder="0"></iframe>
        </div>
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
import { ref, inject, onMounted, onUnmounted } from 'vue';

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

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/getdata?league_id=${currentLeague.league_id}`);
        const data = await response.json();
        if (data.state === 'COMPLETED') {
          analysisResult.value = data;
          clearInterval(intervalId.value);
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

    onMounted(() => {
      if (currentLeague) {
        intervalId.value = setInterval(fetchData, 3000);
      }
    });

    onUnmounted(() => {
      if (intervalId.value) {
        clearInterval(intervalId.value);
      }
    });

    return {
      currentLeague,
      analysisResult,
      percentage,
      activeTab,
      activeSubTab
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