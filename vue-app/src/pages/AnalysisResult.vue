<template>
  <div class="container">
    <h2 class="text-center my-4">Analysis Result</h2>
    <div v-if="currentLeague">
      <h3>{{ currentLeague.name }}</h3>
      <p>Type: {{ currentLeague.scoring_type }}</p>
      <p>Status: {{ currentLeague.draft_status }}</p>
      <div v-if="analysisResult">
        <p>Data: {{ analysisResult }}</p>
      </div>
      <div v-else>
        <p>Loading data... {{ progress }}%</p>
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
    const progress = ref(null);

    const fetchData = async () => {
      try {
        const response = await fetch(`/api/getdata?league_id=${currentLeague.league_id}&week=${currentLeague.current_week}`);
        const data = await response.json();
        if (data.state === 'COMPLETED') {
            analysisResult.value = data;
          clearInterval(intervalId.value);
        } else if (data.state === 'IN_PROGRESS') {
          progress.value = data.progress;
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };

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

    return {
      currentLeague,
      analysisResult
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
</style>