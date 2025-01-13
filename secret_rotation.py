import boto3
from botocore.exceptions import ClientError
import secrets
import json
import os
import ast
from boto3.session import Session
import mysql.connector
from kubernetes import client, config
import datetime


def lambda_handler(event, context):
    region_name = os.environ.get("REGION","ap-south-1")
    admin_sm_secret_name = os.environ.get("ADMIN_SECRET")
    admin_sm_session = boto3.session.Session()
    admin_client = admin_sm_session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    admin_get_secret_value_response = admin_client.get_secret_value(
        SecretId=admin_sm_secret_name
    )
    admin_secret_keys = json.loads(admin_get_secret_value_response['SecretString'])
    admin_host_name = os.environ.get("HOSTNAME_KEY")
    admin_user_name = os.environ.get("USERNAME_KEY")
    admin_password = os.environ.get("PASSWORD_KEY")
    secrets_to_update = os.environ.get("SECRETS_WITH_KEYS_TO_UPDATE")
    user_password_update = os.environ.get("user_name_password_update")
    password_length = int(os.environ.get("password_length"))

    new_password = secrets.token_urlsafe(password_length)
    
    connection = mysql.connector.connect(
        host=admin_secret_keys[admin_host_name],
        user=admin_secret_keys[admin_user_name],
        password=admin_secret_keys[admin_password]
    )
    cursorObj = connection.cursor()
    cursorObj.execute(f"ALTER USER '{user_password_update}'@'%' IDENTIFIED BY '{new_password}'")
    cursorObj.close()
    connection.close()
    
    update_to_json = ast.literal_eval(secrets_to_update)
    list_of_secrets_to_update=update_to_json.keys()
    current_account_id = boto3.client('sts').get_caller_identity().get('Account')
    for secret_name, keys_to_update in update_to_json.items():
        print(secret_name)
        account_id = secret_name.split(':')[4]
        print(account_id)
        sm_session = boto3.session.Session()
        secret_manager_client = sm_session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        get_secret_value_response = secret_manager_client.get_secret_value(
            SecretId=secret_name
        )
        secret = get_secret_value_response['SecretString']
        secret_json = json.loads(secret)
        
        for keys in keys_to_update:
            secret_json[keys] = new_password
        secret_manager_client.update_secret(SecretId=secret_name,SecretString=json.dumps(secret_json))
        print(f"Secret {secret_name} updated with the new password")

    
    print("Force deploying EKS deployments")
    eks_response=eks_force_deploy()
    print(eks_response)
    
    print("Force deploying ECS services")
    ecs_response=ecs_force_deploy(region_name)
    print(ecs_response)

    return{"status":200}


def eks_force_deploy():
    kubeconfig_path = os.path.join(os.getcwd(), 'config')
    config.load_kube_config(kubeconfig_path)
    v1_apps = client.AppsV1Api()
    eks_details = os.environ.get('eks_deployments_to_force_deploy')
    try:
        for namespace,deployment_name in ast.literal_eval(eks_details).items():
            for deploymentname in deployment_name:
                print(f"Force deploying EKS deployment {deploymentname} in namespace {namespace}")
                deployment = v1_apps.read_namespaced_deployment(name=deploymentname, namespace=namespace)
                deployment.spec.template.metadata.annotations = {
                    'kubectl.kubernetes.io/restartedAt': str(datetime.datetime.now())
                }
                response = v1_apps.patch_namespaced_deployment(name=deploymentname, namespace=namespace, body=deployment)
                print(f"Deployment {deploymentname} successfully restarted.")
        return {
            'statusCode': 200
        }
    except Exception as e:
        print(f"Error updating the deployment: {e}")
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }

def ecs_force_deploy(region):
    session = boto3.session.Session(region_name = region)
    ecs = session.client('ecs')
    ecs_service_details = os.environ.get("ecs_services_to_force_deploy")
    for cluster_name,service_name in ast.literal_eval(ecs_service_details).items():
        for servicename in service_name:
            print(f"Force deploying service {servicename} in cluster {cluster_name}")
            ecs.update_service(cluster=cluster_name,service=servicename,forceNewDeployment = True)
    return {
            'statusCode': 200
        }
