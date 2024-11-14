@echo off
REM Define the S3 bucket name as a variable
set BUCKET_NAME=yahoo-fantasy-website

REM Delete all files and folders under the bucket except the data folder
aws s3 rm s3://%BUCKET_NAME% --recursive --exclude "data/*"

REM Sync JavaScript files with the correct MIME type
aws s3 sync ./dist/assets s3://%BUCKET_NAME%/assets --exclude "*" --include "*.js" --content-type "application/javascript"

REM Sync CSS files with the correct MIME type
aws s3 sync ./dist/assets s3://%BUCKET_NAME%/assets --exclude "*" --include "*.css" --content-type "text/css"

REM Sync other files without changing their MIME types
aws s3 sync ./dist s3://%BUCKET_NAME% --exclude "assets/*.js" --exclude "assets/*.css"