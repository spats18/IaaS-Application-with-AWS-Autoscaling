import dotenv from 'dotenv';
import express from 'express';
import AWS from 'aws-sdk';
import cors from 'cors';
import fileupload from "express-fileupload";
import { Consumer } from 'sqs-consumer';

dotenv.config({path: '../key.env'})
const application = express()
// dotenv.config()

application.use(cors({
    origin: '*'
}));
application.use(fileupload());

// map [uniqueID, classification_result]
const result = new Map();

AWS.config.update({region: 'us-east-1'}); // AWS region

const s3 = new AWS.S3({
    accessKeyId: process.env.AWS_KEY, //env variables for AWS secret Key and Access ID
    secretAccessKey: process.env.AWS_SECRET
})

var logMessage = function(id, name) { //custom message object 
    this.id = id;
    this.name = name;
}

const SQS = new AWS.SQS({apiVersion: '2012-11-05',accessKeyId: process.env.AWS_KEY,
    secretAccessKey: process.env.AWS_SECRET})
    
const sqsApplication = Consumer.create({
    queueUrl: 'https://sqs.us-east-1.amazonaws.com/025635606453/cse546-response-sqs', // response SQS
    handleMessage: async (data) => {
        var mess = JSON.parse(data.Body)
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

application.post('/api/image', async(request, response) => {
    // unique ID for the image
    var id = require("shortid").generate(); // unique ID generated for image
    //upload image to S3
    let inputBucketKey = "demo-test-input_" + request.files.myfile.name; // custom prefix for input images in bucket (like folder)
    const parameters = {
        Bucket: "cse546-input-s3", // input bucket
        Key: inputBucketKey,
        Body: request.files.myfile.data
    }

    await s3.upload(parameters).promise()
    console.log(inputBucketKey+" image uploaded to S3.");
    
    // sending request to SQS
    const message = {
        DelaySeconds: 0,
        MessageBody: JSON.stringify(new logMessage(id, inputBucketKey)),
        QueueUrl: 'https://sqs.us-east-1.amazonaws.com/025635606453/cse546-request-sqs' //request sqs
    };

    await SQS.sendMessage(message).promise()
    console.log("Message for "+inputBucketKey+" sent to SQS.");
    
    result.set(id,"");
    
    await waitUntilKeyPresent(id, 0)

    //sending result 
    response.send(result.get(id))
})

const sleep = millisec => new Promise(resolve => setTimeout(resolve, millisec));

const waitUntilKeyPresent = async(key, retry) => {
    while (result.get(key) == "" && retry < 400) {
        retry++;
        await sleep(1000);
    }
    console.log('key present: ' + key)
}

application.listen(3001, "0.0.0.0", () => { // changed to 0.0.0.0
    console.log(`Server running on 3001`)
})