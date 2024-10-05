## create the deployment package

1. Create a new directory named package into which you will install your dependencies.

 ```
cd yahoo-fantasy
mkdir package
```

Note that for a .zip deployment package, Lambda expects your source code and its dependencies all to be at the root of the .zip file. However, installing dependencies directly in your project directory can introduce a large number of new files and folders and make navigating around your IDE difficult. You create a separate package directory here to keep your dependencies separate from your source code.


2. Install your required libraries using pip.

```
pip install --target ./package -r requirements.txt
```

1. Create a .zip file with the installed libraries at the root.


```
cd package
zip -r ../my_deployment_package.zip .
```
This generates a my_deployment_package.zip file in your project directory.

1. Add the lambda_function.py file to the root of the .zip file
```
cd ..
zip my_deployment_package.zip *.py *.ttf
```

Your .zip file should have a flat directory structure, with your function's handler code and all your dependency folders installed at the root as follows.


```
my_deployment_package.zip
|- bin
|  |-jp.py
|- boto3
|  |-compat.py
|  |-data
|  |-docs
...
|- lambda_function.py
```


Reference: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html
