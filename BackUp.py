"""
Alan Lai
AWS S3 File Backup and Restore
"""
import logging
import boto3
import botocore
from botocore.exceptions import ClientError
from botocore.errorfactory import ClientError
from datetime import datetime, timezone
import os
import glob
from posixpath import dirname

"""
localFileIsNew(local_file, s3_file))
Method checks if a local file is new, by comparing the last modified date
of the local file to the file on the cloud.
"""
def localFileIsNew(local_file, s3_file):
    s3_LMT = ""
    try:
        s3_LMT = s3_file.last_modified.timestamp()
    except botocore.exceptions.ClientError as err:
        # If the file doesn't exist, the file were uploading to the cloud is NEW, so return true.
        return True
    local_file_LMT = os.path.getmtime(local_file)
    return (s3_LMT < local_file_LMT)

"""
backup(args, s3, session)
Backup method takes in arguments, s3 object, and s3 session.
Backs up local directory to the S3 directory given.
"""
def backup(args, s3, session):
    # Get bucket name and directory in bucket from user input: {backup directory-name bucket-name::directory-name}
    bucketName = args[2].split("::")[0]            # Get bucket name by splitting by :: then grabbing the first element.
    directoryInBucket = args[2].split("::")[1]     # Get S3 directory name by splitting by :: then grabbing the second element.
    directoryPath = args[1]                        # Get local directory path that we are backing up.

    # Directory Check. If not a directory, exit program.
    if(os.path.isdir(directoryPath)):
        print("")
    else:
        print("Non-directory given, please input a directory. Example: 'C:/Users/James/Downloads/OfficePowerPoints'")
        exit() 

    # Check if given bucket exists or is accessible.
    # try:
    #     s3.meta.client.head_bucket(Bucket=bucketName)
    # except ClientErroor:
    if not s3.Bucket(bucketName) in s3.buckets.all():
        print(bucketName + "  does not exist. Will attempt to create " + bucketName + " in S3.")
        try: 
            s3.create_bucket(Bucket = bucketName, CreateBucketConfiguration={"LocationConstraint": session.region_name})
        except (s3.meta.client.exceptions.BucketAlreadyExists, botocore.exceptions.ClientError) as err: 
            # If bucket already exists throw error.
            print("The requested bucket name is not available or invalid. The bucket namespace is shared by all users of the system. Please select a different bucket name on program rerun and try again. Make sure bucket name is valid(check Boto3 documentation for valid bucket names") 
            exit()

    # Adding files to directory
    # Get OS Path directory path
    name = os.path.basename(os.path.normpath(directoryPath))

    # Keep track of previous folders to build path names in the S3 code for later loops.
    prevLoc = []

    # For every subdirectory and file in directory path, attempt to upload file to cloud directory
    for subdir, dirs, files in os.walk(directoryPath):
        # Iterate through every file in sub-directory
        for file in files:
            name = os.path.basename(os.path.normpath(subdir))
            # Keep track of previous locations/parent folders for later iterations
            if not name in prevLoc:
                prevLoc.append(name)
            # String to track file name and location. Will be added to the s3 file substrin.
            file_name = ""
            # Adds previous parent folder location names to tell S3 to imitate our folder relationships of our local directory.
            for location in prevLoc:
                file_name += location + "/"

            # Local file and S3 file directory paths.
            local_file = subdir + "/" + file
            s3_file = directoryInBucket + "/" + file_name + file
            
            # Check if the file was modified since the last time we uploaded.
            # If the file is new, upload the file, else, do not do an unecessary operation of uploading a file with the same last modification date.
            if localFileIsNew(local_file, s3.Object(bucketName, s3_file)):
                print("Backing up " +  subdir + "/" + file + "...")
                s3.Bucket(bucketName).upload_file(Filename = local_file, Key = s3_file)
            else: 
                print("Did not back up " + file + " because no modifications made since last backup.")

    print("Successfully finished backup operations from " + directoryPath + " to " + bucketName + ".")

"""
restore(args, s3)
Restore method takes in command line arguments and S3 object.
Restore will download files directory from S3, and store to local directory path.
"""
def restore(args, s3):
    # Split command argument and get given bucket name 
    bucketName = args[1].split("::")[0] 
    
    # Check if the bucket exists in your current buckets.
    # If bucket does not exist, exit program.
    if not s3.Bucket(bucketName) in s3.buckets.all():
        print(bucketName + "  does not exist or isn't your bucket. Please try again.")
        exit()
    # Else, run restore operations.
    else:
        # Split command line argument and get directory of bucket we'll download from.
        directoryInBucket = args[1].split("::")[1]
        # Get local directory path that we will upload to.
        directoryPath = args[2]

        # Get bucket object through S3 bucket name.
        bucket = s3.Bucket(bucketName)

        # Iterate through all items in the bucket's directory
        for item in bucket.objects.filter(Prefix = directoryInBucket):
            os.path.join(directoryInBucket, os.path.relpath(item.key, directoryPath))

            # Check if Directory Exists on system. If not, create folder for use.
            if not os.path.exists(directoryPath):
                print(directoryPath + " not found on your system. Will create the folder for you.")
                os.makedirs(directoryPath)
            # If item is a folder, do not download anything, just continue iterating.
            if item.key[-1] == '/':
                continue
            
            # Download files to system.
            bucket.download_file(item.key, directoryPath +"/" + item.key.split("/")[len(item.key.split("/")) - 1])
            print("Restoring " + directoryPath +"/" + item.key.split("/")[len(item.key.split("/")) - 1])

        print("Successfully restored " + bucketName + " : " + directoryInBucket + " to " + directoryPath)

def main():
    # Program start Message
    print("Welcome to Backup.PY. Please use one of the following commands:")
    print("{backup local-directory-name s3-bucket-name::s3-directory-name} or {restore s3-bucket-name::s3-directory-name local-directory-name}")

    # Split input into strings.
    userInput = input()             # Input is taken in with input()
    args = userInput.split(" ")     # User Input is split by spaces
    choice = args[0].lower()        # Lower case choice just in case.

    # Edge case: If arguments not 3, command is invalid.
    if len(args) != 3:
        print("Too less/too many arguments. Correct usage: {backup local-directory-name s3-bucket-name::s3-directory-name} or {restore s3-bucket-name::s3-directory-name local-directory-name}")
        exit()
    # Check if user put in backup or restore, otherwise it is considered invalid.
    elif args[0] != "backup" and args[0] != "restore": 
        print("Please use backup or restore. Correct usage: {backup local-directory-name s3-bucket-name::s3-directory-name} or {restore s3-bucket-name::s3-directory-name local-directory-name}")
        exit()

    # Initialize S3 Object, Session(for grabbing region area), and buckets(for checking if buckets exists in user's S3 later in code)
    s3 = boto3.resource("s3")
    session = boto3.session.Session()

    if(choice == "backup"):
        backup(args,s3, session)
    else:
        restore(args,s3)

if __name__ == "__main__":
    main()
