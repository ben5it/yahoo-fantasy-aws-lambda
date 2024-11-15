<template>
  <header>
    <nav class="nav-bar">
      <div class="nav-logo">
        <img src="/images/logo.png" alt="Logo" class="logo">
      </div>
      <div class="nav-links">
        <router-link to="/leagues">Analysis</router-link>
        <router-link to="/tools">Tools</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/contact">Contact</router-link>
      </div>
      <div class="user-icon-container" v-if="auth.state.authenticated">
        <img :src="auth.state.user.profile_image" alt="User Icon" class="user-icon" @mouseover="showUserPopup = true" @mouseleave="showUserPopup = false">
        <div class="user-popup" v-if="showUserPopup">
          <p>Nickname: {{ auth.state.user.nickname }}</p>
          <p>Email: {{ auth.state.user.email }}</p>
          <!-- <router-link to="/signout">Sign Out</router-link> -->
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
import { inject, ref } from 'vue';
import { useRouter } from 'vue-router';

export default {
  name: "HeaderComp",
  setup() {
    const auth = inject('auth');
    const router = useRouter();
    const showUserPopup = ref(false);

    const logout = () => {
      // Implement your logout logic here
      auth.setAuthenticated(false);
      auth.setUser({});
      // Redirect to home or login page
      router.push('/');
    };

    return {
      auth,
      showUserPopup,
      logout
    };
  }
};
</script>

<style scoped>
.nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #333;
  color: white;
  height: 40px;
}

.nav-logo {
  display: flex;
  align-items: center;
}

.logo {
  width: 32px;
  height: 32px;
}

.nav-links {
  display: flex;
  gap: 20px;
}

.nav-links a {
  color: white;
  text-decoration: none;
}

.user-icon-container {
  position: relative;
}

.user-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
}

.user-popup {
  position: absolute;
  top: 40px;
  right: 0;
  background-color: white;
  color: black;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000; /* Ensure it appears above other elements */
}
</style>