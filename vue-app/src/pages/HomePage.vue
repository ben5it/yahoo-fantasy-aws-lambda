<template>
  <div>
    <div class="container text-center">
      <p></p>
      <p></p>
      <h6 class="text-secondary">Below is a demo. If you would like to have a try, click the 'Sign in with Yahoo' button at the bottom.
      </h6>
      <div class="mb-4"></div>

      <div id="carouselExampleIndicators" class="carousel carousel-dark slide carousel-fade" data-bs-ride="carousel">
          <div class="carousel-indicators">
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="1" aria-label="Slide 2"></button>
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3"></button>
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="3" aria-label="Slide 4"></button>
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="4" aria-label="Slide 5"></button>
            <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="5" aria-label="Slide 6"></button>
          </div>
          <div class="carousel-inner">
            <div class="carousel-item active" data-bs-interval="3000">
              <img src="/images/roto_bar.png" height="480" width="864">
            </div>
            <div class="carousel-item" data-bs-interval="3000">
              <img src="/images/roto_point.png" height="480" width="864">
            </div>
            <div class="carousel-item" data-bs-interval="3000">
              <img src="/images/roto_stats.png" height="480" width="864">
            </div>
            <div class="carousel-item" data-bs-interval="3000">
              <img src="/images/h2h_matchup.png" height="480" width="864">
            </div>
            <div class="carousel-item" data-bs-interval="3000">
              <img src="/images/radar_team.png" height="480" width="864">
            </div>
            <div class="carousel-item" data-bs-interval="3000">
              <img src="/images/radar_forecast.png" height="480" width="864">
            </div>
          </div>
          <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Previous</span>
          </button>
          <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="visually-hidden">Next</span>
          </button>
        </div>
      <div class="mb-4"></div>
      <div>
          <a href="/login">
              <img src="/images/signIn.png" class="img-fluid mw-25" style="height: 40px;" />
          </a>
      </div>
  </div>
  </div>
</template>


<script>
import { inject } from 'vue';
import { useRouter } from 'vue-router';
// import axios from '../axios';

export default {
  name: "HomePage",
  setup() {
    const auth = inject('auth');
    const router = useRouter();

    const checkAuth = async () => {
      try {
        const response = await fetch('/check_auth');
        const data = await response.json();
        auth.setAuthenticated(data.authenticated);
        if (data.authenticated) {
          auth.setUser(data.user_info);
          router.push('/analysis'); // Redirect to AnalysisPage if authenticated
        }
      } catch (error) {
        auth.setAuthenticated(false);
        console.error('Error checking authentication:', error);
      }
    };

    checkAuth();

    return { auth };
  }
};
</script>

<style scoped>
.carousel-container {
  width: 80%;
  max-width: 600px;
  margin: 20px auto;
}

.carousel-container img {
  width: 100%;
  height: auto;
}

button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
  margin-top: 20px;
}
</style>