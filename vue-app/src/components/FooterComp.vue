<template>
  <footer class="app-footer">
    <p>
      Fantasy data provided by
      <a href="https://basketball.fantasysports.yahoo.com/" target="_blank" rel="noopener noreferrer">Yahoo Fantasy</a>
    </p>
  </footer>
</template>

<script>
export default {
  name: "FooterComp"
};
</script>

<style scoped>
.app-footer {
  text-align: center;
  margin-top: 30px;
  padding: 4px 20px;
  border-top: 1px solid #e0e0e0;
  background-color: transparent;
  color: #999;
  font-size: 0.7rem;
}

.app-footer p {
  margin: 0;
}

.app-footer a {
  color: #999;
  text-decoration: underline;
}
</style>
