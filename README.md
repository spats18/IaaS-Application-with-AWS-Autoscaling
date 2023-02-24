## CSE 546 CC Project 1

### List of functions to work on
**AWS functions:**

1. S3 -> Upload and Download 
2. SQS -> Send and Long poll messages

**Utility functions:** 
1. Create a folder
2. Check folder existence
3. Create custom JSON/string messages for both SQS queues
4. Run the DL model (cmd execution)


### Frontend Workflow
1. Application accepts the image and downloads it locally onto the VM its running. 
2. Uploads the downloaded image to S3 
3. If step 2 successful, then we end a custom message to Request SQS else we exit the process ue to S3 upload failure.
4. Long poll the Response SQS after Step 3 (If part) to receive the response message to send results back to workload generator.


### Backend Workflow
1. Application long polls the SQS queue 
2. Upon message receival, extract the S3 file path from message
3. Download the Image from S3
4. Run the DL model using _cmd_ function
5. Extract the results from cmd execution
6. Put this results into an S3 output bucket
7. Send the custom message to SQS response
 

### Node JS Code Checkpoints
#### Commands to run the server
```
node server.js
```


