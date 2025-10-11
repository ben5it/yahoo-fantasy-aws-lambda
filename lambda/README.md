# Introduction

The backend contains two services:
- web server: served as the web site server, if data already exists in S3, no need to run analysis again, just return from S3 bucket.
- long running job: run analysis, usually the whole analysis would take about 1~2 minutes so this is a separate program. result will be saved to S3 bucket.


## Prerequsite

* Create an application at [Yahoo developer console] (https://developer.yahoo.com/apps/)
  
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)

  
## Local Development

**Configurations**

1. Open fantasy.laohuang.org
2. Login with Yahoo
3. Get the sessionId from debug tool, request header cookie
4. Update sessionId in file 'events/analysis_payload.json'
5. Modify league id and week in that same file if needed

**Run**

```
sam local invoke LongRunningJobFunction --event events/analysis_payload.json --env-vars env.json
```


**Debug**

```
sam local invoke LongRunningJobFunction --event events/analysis_payload.json --env-vars env.json --debug
```

## Deploy

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.


```
sam build
sam deploy
```


**NOTES**
1. We use container type of lambda function other than zip type because the size (layer+code) exceeds 250M , this is due to we use three big packages: numpy, pandas and matplotlib.