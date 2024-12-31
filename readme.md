# Yahoo Fantasy

This project delivers a web applicaition which fetches raw data via Yahoo [Fantasy Sports API](https://developer.yahoo.com/fantasysports/guide/), run analysis based on the data, then display the result in the web applicaiton.

Play with https://fantasy.laohuang.org.

Login with your Yahoo id.  You need to be able to access Yahoo webiste (Yahoo prohibits users from some couuntries like China)


## Architecture

This project adopts a front-end and back-end separation architecture, with the front-end developed using Vue 3 and the back-end developed using AWS SAM framework.

## Prerequsite

* Create an application at [Yahoo developer console] (https://developer.yahoo.com/apps/)
  
* [Python 3 installed](https://www.python.org/downloads/)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)
* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)


  
## Local Development


If you prefer to use an integrated development environment (IDE) to build and test your application, you can use the AWS Toolkit.  
The AWS Toolkit is an open source plug-in for popular IDEs that uses the SAM CLI to build and deploy serverless applications on AWS. The AWS Toolkit also adds a simplified step-through debugging experience for Lambda function code. See the following links to get started.

* [VS Code](https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/welcome.html)

Run locally:
sam local invoke LongRunningJobFunction --event events/analysis_payload.json --env-vars env.json

Run With debug
sam local invoke LongRunningJobFunction --event events/analysis_payload.json --env-vars env.json --debug

Web Server:


## Deploy



The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.



## License
This project is licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE).

