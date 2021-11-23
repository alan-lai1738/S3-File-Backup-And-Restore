# S3-File-Backup-And-Restore
Backup and restore files from directory to AWS S3 cloud storage.
# Requirements
•	AWS S3 Configured (aws configure)<br />
•	Python 3.9+
This program is an S3 Backup/Restore system that can upload files from your local directory to S3 cloud or restore a directory from the S3 cloud to your local directory. You will need to set up your AWS credentials before using this program.

# Backup – backup(args, s3, session)
Backup method takes in user arguments, s3 object, and s3 session. 
1.	Check if the given bucket from arguments exists in all of the user’s buckets. If the bucket does not exist, attempt to create the bucket, otherwise exit program.
2.	Create an OS Path with directory path from arguments, and an array to keep track of parent folder names. This will help us mirror the local directory on our cloud upload too.
3.	Iterate through every file in local directory. Check to see if the file is new, or already exists on the cloud(Helper method). If the file is a different modified date since last upload, proceed to upload it. Otherwise, do not waste an upload operating on a same file with no new modifications.

# Restore – restore(args, s3)
Restore method takes in command line arguments and S3 object. Restore will download files directory from S3, and store to local directory path.
1.	Check if the given bucket name exists in user’s bucket list. If not, exit program.
2.	Iterate through the buckets starting from the directory given in the user arguments.
3.	For every element, check if it’s a folder. In cases a folder is found, do not attempt to download, but instead continue until we find a file instead. Proceed to download. 


# Starting the Program
 
You can start the program by running the program through your IDE or using command line. The program will commands you can use.  
To Backup, run the program, and type in:
backup local-directory-name s3-bucket-name::s3-directory-name 
To restore, run the program, and type in:
restore s3-bucket-name::s3-directory-name local-directory-name

# Examples:
restore 1230128380123::linkedin/ C:\Users\Alan\Downloads\LIPicsRestore 
backup C:\Users\Alan\Documents\Capstone\Reports alainewbucketlol::buckettest

# Screenshots
Backing up a directory to cloud to a new bucket will work.
 
 
Backing up old files to a bucket that already contains those files will skip those files.
 
Backing up to a bucket that isn’t yours will stop the program.
 




Restoring from the cloud to system. Folder is created on cases where your system is missing directory and downloaded.
 
Restoring from an invalid bucket will stop the program.
 
Restoring from an invalid directory will  give a success prompt, because nothing was found. I would add this feature if I had more time(to tell the directory isn’t there).
 
