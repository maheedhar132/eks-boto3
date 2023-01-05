import boto3
import os
import logging

vpc_resource = boto3.resource("ec2", region_name="ap-south-1")


# logger config
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s: %(levelname)s: %(message)s')


def getAwsSecrets():
    access_id = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_KEY')
    return access_id,secret_key

def create_vpc(cidr):
    """
    Creates a custom VPC
    """
    try:
        response = vpc_resource.create_vpc(CidrBlock = cidr,
        InstanceTenancy = 'default',
        TagSpecifications=[{
                            'ResourceType':
                                'vpc',
                                'Tags': [{
                                    'Key':
                                    'Name',
                                    'Value':
                                    'hands-on-cloud-custom-vpc'
                                }]
                            }])
    except Exception as e:
        logger.exception('Couldn\'t create custom VPC')
        raise
    else:
        return response

if __name__ == '__main__':
    cidr = '192.168.0.0/16'
    logger.info('Creating custom VPC..')
    custom_vpc = create_vpc(cidr)
    logger.info(f'Custom VPC is created with VPC ID: {custom_vpc.id}')
