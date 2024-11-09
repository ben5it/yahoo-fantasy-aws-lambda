// Simple auth service to mock authentication
let isAuthenticated = false;

export default {
  login() {
    isAuthenticated = true;
  },
  logout() {
    isAuthenticated = false;
  },
  isAuthenticated() {
    return isAuthenticated;
  },
};
