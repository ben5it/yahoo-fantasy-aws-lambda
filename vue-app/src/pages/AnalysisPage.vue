<template>
  <div>
    <h2>Leagues</h2>
    <div v-if="leagues.length">
      <div v-for="league in leagues" :key="league.id" class="league-card">
        <img :src="league.logo_url" alt="League Logo" class="league-logo">
        <h3>{{ league.name }}</h3>
        <p>Type: {{ league.scoring_type }}</p>
        <button v-if="league.scoring_type === 'head'" @click="analyzeLeague(league)">Analyze</button>
      </div>
    </div>
    <div v-else>
      <p>No leagues available.</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
// import axios from '../axios';

export default {
  name: 'AnalysisPage',
  setup() {
    const leagues = ref([]);

    const fetchLeagues = async () => {
      try {
        const response = await fetch('/api/leagues');
        const data = await response.json();
        leagues.value = data;
      } catch (error) {
        console.error('Error fetching leagues:', error);
      }
    };

    const analyzeLeague = (league) => {
      // Implement your analyze logic here
      console.log('Analyzing league:', league);
    };

    onMounted(() => {
      fetchLeagues();
    });

    return {
      leagues,
      analyzeLeague
    };
  }
};
</script>

<style scoped>
.league-card {
  border: 1px solid #ccc;
  padding: 16px;
  margin: 16px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.league-logo {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 50%;
  margin-bottom: 16px;
}

h3 {
  margin: 0;
  font-size: 1.5em;
}

p {
  margin: 8px 0;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>