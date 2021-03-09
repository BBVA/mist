# *S3Store* command

## Description

This command stores the data received as lines in the given S3 URI. This command
is intended to be used with a stream.

## Input parameters

- **text**: Source stream to read text lines from
- **remoteUri**: S3Uri of the remote object to create. Must contain bucket, prefix
and object name

## Output parameters

None.

## Dependencies

This command requires the AWS CLI and the credentials configuration in place.

## Examples

Store the data received from the stream *:source* as s3://myBucket/facts/list.txt.

``` text
S3Store(:source, "s3://myBucket/facts/list.txt")
```

## Auxiliar functions

### *S3Writer*

This function copies a local file in the given S3Uri.

### Input parameters

- **localPath**: Path of the local file to copy
- **remoteUri**: S3Uri of the remote object to create
