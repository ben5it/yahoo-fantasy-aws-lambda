// src/axios.js
import axios from 'axios';

const instance = axios.create({
  baseURL: 'https://fantasy.laohuang.org', // Replace with the target domain
  headers: {
    'Content-Type': 'application/json'
  }
});

export default instance;