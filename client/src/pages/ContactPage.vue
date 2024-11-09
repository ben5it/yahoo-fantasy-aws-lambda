<template>
  <div>
    <h1>Contact me</h1>
    <p>Email: <a :href="mailtoLink">{{ email }}</a></p>
    <p>Hupu ID: 黄老邪</p>
  </div>
</template>

<script>
export default {
  name: "ContactPage",
  data() {
    return {
      email: 'husthsz@gmail.com'
    };
  },
  computed: {
    mailtoLink() {
      return `mailto:${this.email}`;
    }
  }
};
</script>