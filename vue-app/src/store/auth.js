import { reactive } from 'vue';

const state = reactive({
  authenticated: false,
  user: {
    nickname: '',
    email: '',
    profile_image: ''
  }
});

const setAuthenticated = (value) => {
  state.authenticated = value;
};

const setUser = (user) => {
  state.user = user;
};

export default {
  state,
  setAuthenticated,
  setUser
};