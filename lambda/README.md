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

AWS SAM CLI’s sam local is a function-level emulator for rapid Lambda logic testing. It runs function code in a Docker container mimicking the AWS Lambda runtime and provides a local API server to trigger functions. You can also generate and manage test events for supported AWS services and pass them to local resources.

Some of its core commands include:

sam local invoke: Executes a one-time invocation of your Lambda function by running it inside a Docker container.
sam local start-api: Spins up a local HTTP server that emulates API Gateway, letting you test your API-triggered functions.


### Configurations

1. Open fantasy.laohuang.org
2. Login with Yahoo
3. Get the sessionId from browser debug tool, in request header cookie
4. Update sessionId in file 'events/analysis_payload.json'
5. Modify league id and week in that same file if needed

### Run

Using SAM CLI

`sam build`

**One-time Invoke**

```
sam local invoke WebServerFunction -e events/login.json --env-vars env.json --profile husthsz2025
sam local invoke WebServerFunction -e events/leagues.json --env-vars env.json --profile husthsz2025
sam local invoke WebServerFunction -e events/data.json --env-vars env.json --profile husthsz2025
sam local invoke WebServerFunction -e events/download.json --env-vars env.json --profile husthsz2025
sam local invoke LongRunningJobFunction -e events/analysis.json --env-vars env.json --profile husthsz2025

```
NOTE:

1. If you would like to see debug level log, then add --debug to the end of the command, like

```
sam local invoke WebServerFunction -e events/leagues.json --env-vars env.json --debug
```

1. '--profile' is a profile in your aws credential file 'C:\Users\huang\.aws\credentials'， like below
   
   ```
   [husthsz2025]
    # This key identifies your AWS account.
    aws_access_key_id = XXXXXXXXXXXXXX
    # Treat this secret key like a password. Never share it or store it in source
    # control. If your secret key is ever disclosed, immediately use IAM to delete
    # the key pair and create a new one.
    aws_secret_access_key = YYYYYYYYYYYYYYYYY
    region = us-east-1
    ```

1.  add '> output.json' if you would like to output the response to a json file
   

**start as a server, then trigger many times**
```
sam local invoke LongRunningJobFunction -d 5678 -e events/analysis.json --env-vars env.json --profile husthsz2025
```



### Debug

**AWS Toolkit**


**Manual sam local invoke with debug port**

On
```
sam local invoke LongRunningJobFunction --event events/analysis_payload.json --env-vars env.json --debug

sam local start-lambda --debug-function WebServerFunction --env-vars env.json --profile husthsz2025 -d 5678
```



## Deploy

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.


```
sam build
sam deploy --profile husthsz2025
```


**NOTES**
1. We use container type of lambda function other than zip type because the size (layer+code) exceeds 250M , this is due to we use three big packages: numpy, pandas and matplotlib.