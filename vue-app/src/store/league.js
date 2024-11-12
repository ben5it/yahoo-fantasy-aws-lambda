import { reactive } from 'vue';

const state = reactive({
  currentLeague: null
});

const setCurrentLeague = (league) => {
  state.currentLeague = league;
};

export default {
  state,
  setCurrentLeague
};