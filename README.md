# protex_take_home

## Instrunctions for pipeline
I have developed and tested this on my windows 10 laptop. I haven't developed on this laptop in about 5 years. It was painful enough resolving all the different environment issues. 
I don't have the ability currently to test this on multiple environments, I have added some code in the make file to try enable multi platform operations, but again, I can't confirm if it works. 

To run all code here, once you have make installed on the machine, it should just be a matter of running

'''sh
make end-2-end
'''

This will i) create a python virtual environment and install all requirements defined in the requirements/base & requirements/test files
It will then run ii) the unit tests. 
it will then iii) build the docker image, installing all requirements from the requirements file, copying all required files into the image and then finally, iv) running the docker container.
 
The docker container will run the main method in the script data_generation/main_logic/main_app.py, and will write all contents to the docker container running  

## Report
### Summary of Pipeline functionality
we take as input when running the docker container i) INPUT_PATH and ii) OUTPUT_PATH. I did want to add logic to pass in config file from docker arguements, but I ran out of time.
The input and output paths can be overwritten, but for the input path, requiring having a video in the location specified. an error would be thrown otherwise, since were expecting a video to be there and it isnt etc. 

The actual pipeline follows the logic of the jupyter notebook provided, with a little extra.

i. get the configuration needed for the task
ii. extract the frames from the video
i11. generate the coco output
iv. save the annotations
v. output all results & logs generated

### Dataset Statistic & Observability Metrics

When we run the main function, it will output a logs.csv file to resources/outputs/logs.csv, and from this, I generate a MD table of the logs. I have added the table to the project root. 
I won't rehash everything in this file, but in short, it took 14.2759 seconds for this video to run end to end. It took  7.90636 seconds to pre tag the video and it took 6.32288 seconds to extract the frames. 

depending on the hash threshold, we get more or less classes as we were removing more or less images from our processing. (disclaimer - I don't have much knowledge on CV, so for the image duplication there was a lot of help from SO)

### Improvements for Production
With regards to making this more production ready, I would have several steps I would take, and some things I would iron out first in terms of functional requirements. 

1. How we intend on running this workload. 
   1. For this task, I made the assumption that we would have the video at build & run time for the docker container. With this, its pretty 'static' and would be 1 video per image (unless we input multiple video's in which case, a for loop can extend that). 
   2. If I needed to get this production ready, I think I would wrap this workload into a flask / fastapi rest service, and have it running in the cloud, either as EC2, or EKS, if we wanted to go own the K8s route - but that may be over kill for this kind of application. When a we want to process a new video, we upload the video to S3 (or similar) and trigger a SNS / SQS event, or similar. This will send a request to our rest service. in the payload, we can send the pipeline required information, video location, model parameters etc. WE can then use boto to download the video, then process it as we do in this pipeline.
   3. If we would rather not have a persistent deployment, we could configure an AWS Lambda to run, spinning up the docker container, pulling down the information based on the payload in the lambda and running the pipeline 
2. I would integrate it into a log monitoring service, such as coralogix. This way, we can monitor trends in our pipeline over time. For example, we can try monitor things like classification distribution drift over time, is that's important. 
3. I would configure a more robust CI/CD pipeline using something like Jenkins. In this, I would split it into 2 sections, the first would be testing PRs the second for release the final docker image with the Pipeline code. 
   1. In the test job I would look for things like code coverage, linting & formatting checks are in place to ensure we have consistent & cleanly structured code following whatever desired standards, and then, unit tests testing functionality of the pipeline. 
   2. for the release job, this job will release a docker image to a repository such as ECR. We could setup dev & staging repos too if we need to test the images in other level environments. 
   3. Then, during the deployments, we could have a final step of integration tests, where, depending on the needs, we can run performance or load tests, or that, we get a 200 responce if we are using a rest service etc. 
4. I would also setup more robust git management - for example, I only developed my work in main branch (bad practice), but for an actual repo, with a prod project, I would enforce branch rules such as, only PR's that are approved by a maintainer or otherwise can be merged, the branch can only be merged after a successful run of our test job etc. 
5. on the deployment side, I would be interested in testing different hardware configurations, and try strike a balance between performance and cost. This would require testing the Pipeline on different hardware resources, cpu vs gpu, how much memory etc.
6. Finally, I would then 'release' the results of the pipeline. for this, we can either return the contents in a https response, create a report and publish to S3 etc. 