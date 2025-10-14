# Introduction

This is the front-end website built with Vue 3 in Vite. 

The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).


## Development

1. Run command `npm install` to install dependencies.

1. Run `npm run dev` to test your code,  this will start a mock sever and also the web site.


NOTE:

If you would like to modify the mock data, you can modify below two files:
- mock-server.js
- mock-data.js

## Deploy

You need to configure your AWS credential first

   1. Create a user in AWS, and generate credential for it.
   2. Edit file  'C:\Users\\<username\>\\.aws\credentials' 

        ```
        [default]
        aws_access_key_id = XXXXXXXXXXXXXX
        aws_secret_access_key = YYYYYYYYYYYYYYY
        ```

   3. Edit file 'C:\Users\\<username\>\\.aws\config' to set you AWS region

        ```
        [default]
        region = us-east-1
        ```

Then run command `npm run deploy`