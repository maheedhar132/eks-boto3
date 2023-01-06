import boto3
import os
import logging
import random
import botocore.exceptions as exception

region_name = "ap-south-1"

vpc_resource = boto3.resource("ec2", region_name="ap-south-1")

cidr_host = ["32", "64", "128" , "255"]


# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')

def generateTag(resource,visibilty,az):
    if resource.lower() == "subnet":
        tag = visibilty.lower()+"-subnet-"+az
    else:
        tag = "EKS-custom-"+resource.lower()
    return tag



def getAwsSecrets():
    access_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_KEY')
    return access_id,secret_key

def create_vpc(vpc_cidr):
    """
    Creates a custom VPC
    """
    try:
        response = vpc_resource.create_vpc(CidrBlock = vpc_cidr,
        InstanceTenancy = 'default',
        TagSpecifications=[{
                            'ResourceType':
                                'vpc',
                                'Tags': [{
                                    'Key':
                                    'Name',
                                    'Value':
                                    generateTag("vpc","","")
                                }]
                            }])
    except Exception as e:
        logger.exception('Couldn\'t create custom VPC')
        raise
    else:
        return response


def cidr(resource):
    if resource.lower() == "subnet":
        cidr_ip = "192.168."+cidr_host[0]+".0/20"
        cidr_host.pop(0)
    if resource.lower() == "vpc":
        cidr_ip = "192.168.0.0/16"
    return cidr_ip


def create_subnet(vpc_id,subnet_cidr_block, az_region, visibility):
    """
    Creates a custom subnet.
    """
    az = region_name+az_region
    try:
        response = vpc_resource.create_subnet(TagSpecifications=[
            {
                'ResourceType': 'subnet',
                'Tags': [{
                    'Key': 'Name',
                    'Value': generateTag("subnet", visibility ,az)
                }]
            },
        ],
                                            AvailabilityZone=az,
                                            VpcId=vpc_id,
                                            CidrBlock=subnet_cidr_block)
    except exception.ClientError:
        logger.exception(f"cloudn't create subnet")
        raise
    else:
        return response


def createSecurityGroup(vpc_id):
    """
    Creates a security Group
    """
    try:
        response = vpc_resource.create_security_group(Description=generateTag("security-group","",""),
                                                      GroupName=generateTag("security-group","",""),
                                                      VpcId=vpc_id,
                                                      TagSpecifications=[{
                                                          'ResourceType':
                                                          'security-group',
                                                          'Tags': [{
                                                              'Key':
                                                              'Name',
                                                              'Value':
                                                              generateTag("security-group","","")
                                                          }]
                                                      }])
    except exception.ClientError:
        logger.info(f'Couldn\'t create Security Group')
        raise
    else:
        return response


def createAndAttachInternetGateway(vpc_id):
    try:
        igw = vpc_resource.create_internet_gateway(TagSpecifications=[
            {
                'ResourceType': 'internet-gateway',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': generateTag("internet-gateway","","")
                    },
                ]
            },
        ])
    except exception.ClientError:
        logger.info(f'cloudn\'t create Internet Gateway')
        raise
    vpc = vpc_resource.Vpc(vpc_id)
    try:
        response = vpc.attach_internet_gateway(
        InternetGatewayId=igw.id)
    except exception.ClientError:
        logger.info(f'Couldn\'t attach Internet Gateway')
        raise










if __name__ == '__main__':
    az_region = ["a","b"]
    logger.info('Creating custom VPC..')
    custom_vpc = create_vpc(cidr("vpc"))
    logger.info(f'Custom VPC is created with VPC ID: {custom_vpc.id}')
    visibility = ["public","private"]
    for j in visibility:
        for i in az_region:
            logger.info(f'Creating {j} subnet in az {i} and attaching to VPC')
            custom_subnet = create_subnet(custom_vpc.id, cidr("subnet"), i, j)
            logger.info(f'Custom {j} subnet created in az {i} with id: {custom_subnet.id}')
    logger.info(f'creating security group')
    securitygroup = createSecurityGroup(custom_vpc.id)
    logger.info(f'Custom security group {securitygroup.id} created')
    logger.info(f'Creating Internet Gateway')
    InternetGateway = createAndAttachInternetGateway(custom_vpc.id)
    logger.info(f'Created InternetGateway and attached to VPC')