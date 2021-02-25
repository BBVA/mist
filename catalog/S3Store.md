# *S3Store* command

## Description

This command stores a local file in the given S3Uri.

## Concurrency Type

Sync

## Input parameters

- **localPath**: Path of the local file to store
- **remoteUri**: S3Uri of the remote object to create. Must contain bucket, prefix and object

## Output parameters

None.

## Dependencies

This command requires the AWS CLI and the credentials configuration in place.

## Examples

Store the local file ~/list.txt as s3://myBucket/facts/list.txt.

``` text
S3Store("~/list.txt", "s3://myBucket/facts/list.txt")
```
