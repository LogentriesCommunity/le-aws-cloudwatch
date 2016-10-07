# le-aws-cloudwatch
##### AWS Lambda function for sending AWS CloudWatch logs to Logentries in near real-time for processing and analysing

###### Example use cases:
* Forwarding AWS VPC flow Logs
* Forwarding AWS Lambda function logs
* [Forwarding AWS CloudTrail logs](http://docs.aws.amazon.com/awscloudtrail/latest/userguide/send-cloudtrail-events-to-cloudwatch-logs.html)
* Forwarding any other AWS CloudWatch logs

## Obtain log token(s)
1. Log in to your Logentries account
2. Add a new [token based log](https://logentries.com/doc/input-token/)
   * Optional: repeat to add second log for debugging

## Deploy the script on AWS Lambda
1. Create a new Lambda function

2. On the "Select Blueprint" screen, press "Skip"

3. Configure function:
   * Give your function a name
   * Set runtime to Python 2.7

4. Edit code:
   * Edit the contents of ```le_config.py```
   * Replace values of ```log_token``` and ```debug_token``` with tokens obtained earlier.
   * Create a .ZIP file, containing the updated ```le_config.py```, ```le_cloudwatch.py``` and the folder ```certifi```
     * Make sure the files and ```certifi``` folder are in the **root** of the ZIP archive
   * Choose "Upload a .ZIP file" in "Code entry type" dropdown and upload the archive created in previous step

5. Lambda function handler and role
   * Change the "Handler" value to ```le_cloudwatch.lambda_handler```
   * Create a new basic execution role (your IAM user must have sufficient permissions to create & assign new roles)

6. Allocate resources:
   * Set memory to 128 MB
   * Set timeout to ~2 minutes (script only runs for seconds at a time)

8. Enable function:
   * Click "Create function"

## Configure CloudWatch Stream
1. Create a new stream:
   * Select CloudWatch log group
   * Navigate to "Actions / Stream to AWS Lambda"

   ![Stream to Lambda](https://raw.githubusercontent.com/LogentriesCommunity/le-aws-cloudwatch/master/doc/step9.png)

2. Choose destination Lambda function:
   * Select the AWS Lambda function deployed earlier from drop down menu
   * Click "Next" at the bottom of the page

   ![Select Function](https://raw.githubusercontent.com/LogentriesCommunity/le-aws-cloudwatch/master/doc/step10.png)

3. Configure log format:
   * Choose the correct log format from drop down menu
   * Specify subscription filter pattern
     * [Please see AWS Documentation for more details](http://docs.aws.amazon.com/AmazonCloudWatch/latest/DeveloperGuide/FilterAndPatternSyntax.html)
     * If this is blank / incorrect, only raw data will be forwarded to Logentries
     * Amazon provide preconfigured filter patterns for some logs
   * Click "Next" at the bottom of the page

   ![Log Format](https://raw.githubusercontent.com/LogentriesCommunity/le-aws-cloudwatch/master/doc/step11.png)

4. Review and start log stream
   * Review your configuration and click "Start Streaming" at the bottom of the page

   ![Start stream](https://raw.githubusercontent.com/LogentriesCommunity/le-aws-cloudwatch/master/doc/step6.png)

5. Watch your logs come in:
   * Navigate to [your Logentries account](https://logentries.com/app) and watch your CloudWatch logs appear
