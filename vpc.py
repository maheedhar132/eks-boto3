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
    else:
        return igw


def allocateIP(vpc_id):
    """
    Allocates an Elastic IP address to use with a NAT gateway
    """
    vpc = boto3.client("ec2")
    try:
        response = vpc.allocate_address(Domain = 'vpc')
    except exception.ClientError:
        logger.exception(f'Cloudn\'t allocate IP for NAT gateway')
        raise
    else:
        return response['AllocationId']

def waitForNatCreation(nat_gateway_id):
    """
    Check if successful state is reached every 15 seconds until a successful state is reached.
    An error is returned after 40 failed checks.
    """
    vpc = boto3.client("ec2")
    try:
        waiter = vpc.get_waiter('nat_gateway_available')
        waiter.wait(NatGatewayIds=[nat_gateway_id])
    except exception.ClientError:
        logger.exception(f'Clouldn\'t create NAT gatway')
        raise


def create_nat(subnet_id,vpc_id,visibility):
    """
    Creates a NAT gateway in the specified subnet.
    """
    if visibility.lower() == "public":
        vpc = boto3.client("ec2")
        try:
            # allocate IPV4 address for NAT gateway
            public_ip_allocation_id = allocateIP(vpc_id)

            # create NAT gateway
            response = vpc.create_nat_gateway(
                AllocationId=public_ip_allocation_id,
                SubnetId=subnet_id,
                TagSpecifications=[{
                    'ResourceType':
                    'natgateway',
                    'Tags': [{
                        'Key': 'Name',
                        'Value': generateTag("NAT Gateway","","")
                    }]
                }])
            nat_gateway_id = response['NatGateway']['NatGatewayId']

            # wait until the NAT gateway is available
            waitForNatCreation(nat_gateway_id)

        except exception.ClientError:
            logger.exception(f'Could not create the NAT gateway.')
            raise
        else:
            return response
    else:
        logger.info(f'No NAT Gateway is created for private subnets')


def createRouteTable(vpc_id,ig_id,visibility):
    if visibility.lower() == "public":
        vpc = vpc_resource.Vpc(vpc_id)
        route_table = vpc.create_route_table()
        route = route_table.create_route(
            DestinationCidrBlock = '0.0.0.0/0',
            GatewayId = ig_id
        )
        return route_table.id
    else:
        logger.info(f'Skipping private subnets........')
