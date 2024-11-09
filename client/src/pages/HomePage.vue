<template>
    <div>
      <LeagueListComp v-if="authenticated" />
      <LoginComp v-else />
    </div>
  </template>
  
  <script>
  import LeagueListComp from '../components/LeagueListComp.vue';
  import LoginComp from '../components/LoginComp.vue';
  
  export default {
    name: "HomePage",
    components: {
      LeagueListComp,
      LoginComp
    },
    data() {
      return {
        authenticated: false
      };
    },
    methods: {
      async checkAuth() {
        try {
          const response = await fetch('/check_auth');
          const data = await response.json();
          this.authenticated = data.authenticated;
        } catch (error) {
          console.error('Error checking authentication:', error);
        }
      }
    },
    created() {
      this.checkAuth();
    }
  };
  </script>
  
  <style scoped>
  /* Add any styles you need here */
  </style>