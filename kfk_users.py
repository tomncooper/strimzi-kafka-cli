import click
import os
import yaml

from kfk import kfk
from option_extensions import NotRequiredIf, RequiredIf
from commons import print_missing_options_for_command, download_strimzi_if_not_exists
from constants import *


@click.option('-n', '--namespace', help='Namespace to use', required=True)
@click.option('-c', '--cluster', help='Cluster to use', required=True)
@click.option('--delete', help='Delete a user.', is_flag=True)
@click.option('-o', '--output',
              help='Output format. One of: json|yaml|name|go-template|go-template-file|template|templatefile|jsonpath|jsonpath-file.')
@click.option('--describe', help='List details for the given user.', is_flag=True)
@click.option('--authentication-type', type=click.Choice(['tls', 'scram-sha-512'], case_sensitive=True), cls=RequiredIf,
              required_if='create')
@click.option('--create', help='Create a new user.', is_flag=True)
@click.option('--list', help='List all available users.', is_flag=True)
@click.option('--user', help='User Name', required=True, cls=NotRequiredIf, not_required_if='list')
@kfk.command()
def users(user, list, create, authentication_type, describe, output, delete, cluster, namespace):
    """The kafka user(s) to be created, altered or described."""
    if list:
        os.system('kubectl get kafkausers -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                                 namespace=namespace))
    elif create:
        download_strimzi_if_not_exists()

        with open(r'{strimzi_path}/examples/user/kafka-user.yaml'.format(strimzi_path=STRIMZI_PATH).format(
                version=STRIMZI_VERSION)) as file:
            topic_dict = yaml.full_load(file)

            topic_dict["metadata"]["name"] = user
            topic_dict["spec"]["authentication"]["type"] = authentication_type
            del topic_dict["spec"]["authorization"]

            topic_yaml = yaml.dump(topic_dict)
            os.system(
                'echo "{topic_yaml}" | kubectl create -f - -n {namespace}'.format(strimzi_path=STRIMZI_PATH,
                                                                                  topic_yaml=topic_yaml,
                                                                                  namespace=namespace))

    elif describe:
        if output is not None:
            os.system(
                'kubectl get kafkausers -l strimzi.io/cluster={cluster} -n {namespace} -o {output}'.format(
                    cluster=cluster,
                    namespace=namespace, output=output))
        else:
            user_exists = user in os.popen(
                'kubectl get kafkausers -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                               namespace=namespace)).read()
            if user_exists:
                os.system(
                    'kubectl describe kafkausers {user} -n {namespace}'.format(user=user, namespace=namespace))
    elif delete:
        user_exists = user in os.popen(
            'kubectl get kafkausers -l strimzi.io/cluster={cluster} -n {namespace}'.format(cluster=cluster,
                                                                                           namespace=namespace)).read()
        if user_exists:
            os.system(
                'kubectl delete kafkausers {user} -n {namespace}'.format(user=user, namespace=namespace))
    else:
        print_missing_options_for_command("users")