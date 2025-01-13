AWS Secret rotation 
=====================================

Code to rotate AWS RDS secrets with the help of AWS Lambda Python

-----------------------------------------------------------------

Steps :

1. Create a Lambda layer and upload the zip file python.zip
2. Create a Lambda funtion and add the contents of the file lambda_function.py


Understanding the working of code - 

Python.zip contains the modules - 

PyYAML-6.0.2.dist-info					oauthlib
__pycache__						oauthlib-3.2.2.dist-info
_distutils_hack						pip
_mysql_connector.cpython-39-aarch64-linux-gnu.so	pip-22.0.4.dist-info
_yaml							pkg_resources
boto3							pyasn1
boto3-1.35.12.dist-info					pyasn1-0.6.0.dist-info
botocore						pyasn1_modules
botocore-1.35.12.dist-info				pyasn1_modules-0.4.0.dist-info
cachetools						python_dateutil-2.9.0.post0.dist-info
cachetools-5.5.0.dist-info				requests
certifi							requests-2.32.3.dist-info
certifi-2024.8.30.dist-info				requests_oauthlib
charset_normalizer					requests_oauthlib-2.0.0.dist-info
charset_normalizer-3.3.2.dist-info			rsa
dateutil						rsa-4.9.dist-info
distutils-precedence.pth				s3transfer
google							s3transfer-0.10.2.dist-info
google_auth-2.34.0.dist-info				setuptools
idna							setuptools-58.1.0.dist-info
idna-3.8.dist-info					six-1.16.0.dist-info
jmespath						six.py
jmespath-1.0.1.dist-info				urllib3
kubernetes						urllib3-1.26.20.dist-info
kubernetes-30.1.0.dist-info				websocket
mysql							websocket_client-1.8.0.dist-info
mysql_connector_python-9.0.0.dist-info			yaml


The code uses the following environment variables

Inputs
------
| Key | Description | Sample Value |
|------|-------------|--------|
| ADMIN_SECRET | Name of the secret which contains root credentials | master_secret |
| HOSTNAME_KEY | Mention the key which contains the hostname of RDS, which needs to be updated | RDS_HOSTNAME |
| PASSWORD_KEY | Mention the key which contains the password of RDS | RDS_PASSWORD |
| REGION | Region in which the secrets are present | ap-south-1 |
| SECRETS_WITH_KEYS_TO_UPDATE | This key refers to json value which will contain the secret name | {"arn:aws:secretsmanager:ap-south-1:123456789012:secret:prakash_test-abcdef":["SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_PRAKASH_TEST_SECRET_1","SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_PRAKASH_TEST_SECRET_2","SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_PRAKASH_TEST_SECRET_N"],"arn:aws:secretsmanager:ap-south-1:111111111111:secret:new_test-abcdef":["SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_NEW_TEST_SECRET_1","SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_NEW_TEST_SECRET_2","SECRET_KEY_VALUE_OF_WHICH_NEEDS_TO_BE_UPDATED_IN_NEW_TEST_SECRET_N"]}
| USERNAME_KEY | Mention the key which contains the admin username of RDS | ROOT_USER |
| ecs_services_to_force_deploy | JSON value which contains Cluster and Service names which you want to force deploy | {"cluster1":["service1","service2","servicen],"cluster2":["service10","service11","servicey"]} |
| eks_deployments_to_force_deploy | SON value which contains namespace and deployment names which you want to force deploy | {"namespace1":["deployment1","deployment2","deploymentn"],"namespace2":["deployment10","deployment20","deploymenty"]} |
| password_length | The password length that you want to set for the new password | 10 |
| user_name_password_update | The username, password of which you want to update | test_user |

Once the Lambda is created, it can be scheduled for auto rotation.
