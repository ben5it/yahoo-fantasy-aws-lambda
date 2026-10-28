<template>
  <div id="app" class="container">
    <HeaderComp/>
    <main class="app-main">
      <router-view />
    </main>
    <FooterComp/>
  </div>
</template>

<script>
import HeaderComp from "./components/HeaderComp.vue";
import FooterComp from "./components/FooterComp.vue";

export default {
  name: "App",
  components: { HeaderComp, FooterComp }
};
</script>

<style>
html, body {
  height: 100%;
}

body {
  font-family: Arial, sans-serif;
}

#app.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-main {
  flex: 1;
}
</style>

