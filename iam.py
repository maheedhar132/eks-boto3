import boto3

client = boto3.client('iam')

response = client.create_role(
    Path='/aws_eks',
    RoleName='aws_eks',
    AssumeRolePolicyDocument='cluster.json',
    Description='IAM role for creating cluster',
    MaxSessionDuration=120,
    PermissionsBoundary=''
)