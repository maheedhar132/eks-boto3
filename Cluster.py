import vpc
import boto3


client = boto3.client('eks')

response = client.create_cluster(
    name='Cluster_1',
    version='1.28',
    roleArn='string',
    resourcesVpcConfig={
        'subnetIds': [
            'string',
        ],
        'securityGroupIds': [
            'string',
        ],
        'endpointPublicAccess': True|False,
        'endpointPrivateAccess': True|False,
        'publicAccessCidrs': [
            'string',
        ]
    },
    kubernetesNetworkConfig={
        'serviceIpv4Cidr': 'string',
        'ipFamily': 'ipv4'|'ipv6'
    },
    logging={
        'clusterLogging': [
            {
                'types': [
                    'api'|'audit'|'authenticator'|'controllerManager'|'scheduler',
                ],
                'enabled': True|False
            },
        ]
    },
    clientRequestToken='string',
    tags={
        'string': 'string'
    },
    encryptionConfig=[
        {
            'resources': [
                'string',
            ],
            'provider': {
                'keyArn': 'string'
            }
        },
    ],
    outpostConfig={
        'outpostArns': [
            'string',
        ],
        'controlPlaneInstanceType': 'string',
        'controlPlanePlacement': {
            'groupName': 'string'
        }
    }
)

