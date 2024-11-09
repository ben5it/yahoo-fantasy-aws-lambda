<template>
  <header>
    <nav class="nav-bar">
      <div class="nav-links">
        <router-link to="/">Analysis</router-link>
        <router-link to="/tools">Tools</router-link>
        <router-link to="/about">About</router-link>
        <router-link to="/contact">Contact</router-link>
      </div>
      <div class="user-icon-container" v-if="authenticated">
        <img src="/path/to/user-icon.png" alt="User Icon" class="user-icon" @mouseover="showPopup = true" @mouseleave="showPopup = false">
        <div class="user-popup" v-if="showPopup">
          <p>Nickname: {{ user.nickname }}</p>
          <p>Email: {{ user.email }}</p>
          <router-link to="/signout">Sign Out</router-link>
          <!-- <button @click="logout">Sign Out</button> -->
        </div>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: "HeaderComp",
  data() {
    return {
      authenticated: true,
      showPopup: false,
      user: {
        nickname: 'JohnDoe',
        email: 'john.doe@example.com'
      }
    };
  },
  methods: {
    async checkAuth() {
      try {
        // const response = await fetch('/check_auth');
        // const data = await response.json();
        const data = {
          authenticated: true,
          user_info: {
            nickname: 'JohnDoe',
            email: 'aaa@bb.cc'
          }  
        }
        this.authenticated = data.authenticated;
        if (data.authenticated) {
          this.user = data.user_info;
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
      }
    },
    logout() {
      // Implement logout logic here
      this.authenticated = false;
      this.$router.push("/");
    }
  },
  created() {
    // this.checkAuth();
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
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
}

.user-popup {
  position: absolute;
  top: 30px;
  right: 0;
  background-color: white;
  color: black;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
</style>