#!/bin/bash

# Define the S3 bucket name as a variable
BUCKET_NAME="yahoo-fantasy-website"

# Delete all files and folders under the bucket except the data folder
aws s3 rm s3://$BUCKET_NAME --recursive --exclude "data/*" --include "*"

# Sync JavaScript files with the correct MIME type
aws s3 sync dist/assets s3://$BUCKET_NAME/assets --exclude "*" --include "*.js" --content-type "application/javascript"

# Sync CSS files with the correct MIME type
aws s3 sync dist/assets s3://$BUCKET_NAME/assets --exclude "*" --include "*.css" --content-type "text/css"

# Sync other files without changing their MIME types
aws s3 sync dist s3://$BUCKET_NAME --exclude "assets/*.js" --exclude "assets/*.css"