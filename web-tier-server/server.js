import dotenv from 'dotenv';
import express from 'express';
import AWS from 'aws-sdk';
import cors from 'cors';
import fileupload from "express-fileupload";
import { Consumer } from 'sqs-consumer';
import { nanoid } from 'nanoid';


AWS.config.update({ region: 'us-east-1' });
dotenv.config({ path: '../key.env' });
const application = express();
var PORT = 3001;

application.use(cors({ origin: '*' }));
application.use(fileupload());

const awsKey = process.env.AWS_KEY;
const awsSecKey = process.env.AWS_SECRET;

const s3 = new AWS.S3({
    accessKeyId: awsKey,
    secretAccessKey: awsSecKey
});

const SQS = new AWS.SQS({
    apiVersion: '2012-11-05', 
    accessKeyId: awsKey,
    secretAccessKey: awsSecKey
});

const result = new Map();

//A SQS consumer instance is created to listen to the SQS queue for the response message from the classification service.
const sqsApplication = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/025635606453/cse546-response-sqs', 
    handleMessage: async (message) => {
        var mess = JSON.parse(message.Body)
        console.log("Message received: " + mess.id)
        result.set(mess.id, mess.classification)
    },
    sqs: SQS,
    AttributeNames: [
        "SentTimestamp"
    ],
    MaxNumberOfMessages: 1,
    MessageAttributeNames: [
        "All"
    ],
    VisibilityTimeout: 20,
    WaitTimeSeconds: 10
});
sqsApplication.start();

function logMessage(id, inputBucketKey){ //custom message object 
    this.id = id;
    this.inputBucketKey = inputBucketKey;
}

application.post('/postApi/image', async (request, response) => {
    // unique ID for the image
    var id = nanoid(); // unique ID generated for image
    //upload image to S3
    let inputBucketKey = "demo-test-input_" + request.files.myfile.name; // custom prefix for input images in bucket (like folder)
    const parameters = {
        Bucket: "cse546-input-s3", // input bucket
        Key: inputBucketKey,
        Body: request.files.myfile.data
    }

    await s3.upload(parameters).promise()
    console.log(inputBucketKey + " image uploaded to S3.");

    // sending request to SQS
    const message = {
        DelaySeconds: 0,
        MessageBody: JSON.stringify(new logMessage(id, inputBucketKey)),
        QueueUrl: 'https://sqs.us-east-1.amazonaws.com/025635606453/cse546-request-sqs' //request sqs
    };

    await SQS.sendMessage(message).promise()
    console.log("Message for " + inputBucketKey + " sent to SQS.");

    result.set(id, "");

    await waitUntilKeyPresent(id, 0)

    //sending result 
    response.send(result.get(id))
})

const sleep = millisec => new Promise(resolve => setTimeout(resolve, millisec));

const waitUntilKeyPresent = async (key, retry) => {
    while(retry < 400){
        if(result.get(key) != "")
            break;
        retry++;
        await sleep(1000);
    }
    console.log('key present: ' + key)
}

application.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on ` + PORT)
})