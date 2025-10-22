<template>
  <div class="container">
    <h2 class="text-center my-4">Leagues</h2>
    <p class="text-center">
      <strong>注：</strong>只支持 Head-to-Head 盟，且仅限于已完成选秀的联赛。
    </p>
    <div v-if="leagues?.length" class="row">
      <div v-for="league in leagues" :key="league.id" class="col-md-6">
        <div class="league-card">
          <a :href="league.url" target="_blank">
            <img :src="league.logo_url" alt="League Logo" class="league-logo" />
          </a>
          <h3>{{ league.name }}</h3>
          <p>Type: {{ league.scoring_type }}</p>
          <p>Status: {{ league.draft_status }}</p>
          <button
            :class="['btn', leagueButtonState(league).cls]"
            :disabled="leagueButtonState(league).disabled"
            @click="analyzeLeague(league)"
          >
            {{ leagueButtonState(league).label }}
          </button>
        </div>
      </div>
    </div>
    <div v-else-if="leagues === null">
      <p class="text-center">Retrieving leagues...</p>
    </div>
    <div v-else>
      <p class="text-center">No leagues available.</p>
    </div>
  </div>
</template>


<script>
import { inject, ref, onBeforeMount } from "vue";
import { useRouter } from "vue-router";


export default {
  name: "LeagueListPage",
  setup() {
    const leagues = ref(null);
    const leagueStore = inject('leagueStore');
    const router = useRouter();

    const fetchLeagues = async () => {
      try {
        const response = await fetch("/api/leagues");
        const data = await response.json();
        leagues.value = data;
      } catch (error) {
        leagues.value = [];
        console.error("Error fetching leagues:", error);
      }
    };

    fetchLeagues();

    const analyzeLeague = (league) => {
      // Store the current league information globally
      leagueStore.setCurrentLeague(league);
      router.push("/result");
    };

    const leagueButtonState = (league) => {
      // 1. scoring type not supported
      if (league.scoring_type !== 'head') {
        return { label: 'Not Supported', disabled: true, cls: 'btn-secondary' };
      }
      // 2. draft not finished
      if (league.draft_status !== 'postdraft') {
        return { label: 'Not Drafted', disabled: true, cls: 'btn-secondary' };
      }

      // 3. check if season not started or not enough data
      const start = new Date(`${league.start_date}T00:00:00-08:00`); 
      const now = new Date();
      // Compute difference in hours
      const diffHours = Math.round((now - start) / (1000 * 60 * 60 ));

      // usually the season open day only have few games, so that some team may not have data
      // we require at least 48 hours after season start to ensure enough data is available
      if (diffHours > 48) { 
        return { label: 'Analyze', disabled: false, cls: 'btn-primary' };
      } else if (diffHours < 0) { // season not started
        return { label: 'Not Started', disabled: true, cls: 'btn-secondary' };
      } else { // season already started, not enough data
        return { label: 'Analyze', disabled: true, cls: 'btn-secondary' };
      }
    };

    return {
      leagues,
      analyzeLeague,
      leagueButtonState,
    };
  },
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
