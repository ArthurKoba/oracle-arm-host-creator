import datetime
import sys
from time import sleep
from typing import Tuple

import oci
from oci import Response
from oci.core.models import Image


def find_image(list_images_response: Response) -> Image:
    cloud_dev_images = []
    for i in list_images_response.data:
        if 'Canonical Ubuntu' in i.operating_system:
            cloud_dev_images.append(i)
    sorted_images = sorted(cloud_dev_images, key=lambda x: x.time_created)
    return sorted_images[-1]


def launch(config: dict, ssh_authorized_keys: str):
    comp_id = {'compartment_id': config['tenancy']}
    core_client = oci.core.ComputeClient(config)
    list_images_response = core_client.list_images(**comp_id)
    image = find_image(list_images_response)
    identity_client = oci.identity.IdentityClient(config)
    domains = identity_client.list_availability_domains(**comp_id)
    vnet_client = oci.core.VirtualNetworkClient(config)
    vnet_list = vnet_client.list_subnets(**comp_id)
    while True:
        try:
            launch_instance_details = oci.core.models.LaunchInstanceDetails(
                agent_config=oci.core.models.LaunchInstanceAgentConfigDetails(
                    is_monitoring_disabled=False,
                    is_management_disabled=False,
                    # are_all_plugins_disabled=False,
                    plugins_config=[
                        oci.core.models.InstanceAgentPluginConfigDetails(
                            name='Vulnerability Scanning',
                            desired_state='DISABLED'),
                        oci.core.models.InstanceAgentPluginConfigDetails(
                            name='Compute Instance Monitoring',
                            desired_state='ENABLED'),
                        oci.core.models.InstanceAgentPluginConfigDetails(
                            name='Bastion',
                            desired_state='DISABLED'),
                    ]
                ),
                availability_config=oci.core.models.LaunchInstanceAvailabilityConfigDetails(
                    recovery_action="RESTORE_INSTANCE"
                ),
                availability_domain=domains.data[0].name,
                compartment_id=comp_id['compartment_id'],
                display_name="koba-main-server",
                shape='VM.Standard.A1.Flex',
                create_vnic_details=oci.core.models.CreateVnicDetails(
                    assign_public_ip=True,
                    assign_private_dns_record=True,
                    subnet_id=vnet_list.data[0].id,
                ),
                # launch_options=oci.core.models.LaunchOptions(
                #     boot_volume_type='PARAVIRTUALIZED',
                #     firmware="UEFI_64",
                #     network_type='PARAVIRTUALIZED',
                #     remote_data_volume_type='PARAVIRTUALIZED',
                #     is_pv_encryption_in_transit_enabled=True,
                #     is_consistent_volume_naming_enabled=True
                # ),
                #
                instance_options=oci.core.models.InstanceOptions(
                    are_legacy_imds_endpoints_disabled=False
                ),
                metadata={
                    'ssh_authorized_keys': ssh_authorized_keys
                },
                shape_config=oci.core.models.LaunchInstanceShapeConfigDetails(
                    ocpus=4,
                    memory_in_gbs=24,
                ),
                source_details=oci.core.models.InstanceSourceViaImageDetails(
                    source_type="image",
                    image_id=image.id,
                    boot_volume_size_in_gbs=99
                ),
                is_pv_encryption_in_transit_enabled=True,
            )
            launch_instance_response = core_client.launch_instance(
                launch_instance_details=launch_instance_details
            )
            print(datetime.datetime.now().strftime('%d %b %Y %H:%M:%S'), 'Server Created!')
            break
        except oci.exceptions.ServiceError as e:
            print(f"{datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')} [{e.status}] - {e.message}")
            sleep(120)
            continue


def get_config() -> Tuple[dict, str]:
    if len(sys.argv) < 4:
        raise SystemExit("Usage: python -m app api.cfg api_key.pem server_public.key")
    else:
        cfg_content = []
        with open(sys.argv[1], 'r+') as f:
            for line in f:
                if 'key_file' in line:
                    line = f'key_file=./{sys.argv[2]}'
                cfg_content.append(line)
            f.seek(0)
            if not cfg_content:
                raise SystemExit("config_filename is empty")
            for line in cfg_content:
                f.write(line)
        with open(sys.argv[3], 'r') as f:
            ssh_authorized_keys = f.read()
            if ssh_authorized_keys[-1] == '\n':
                ssh_authorized_keys = ssh_authorized_keys[:-1]
            if not ssh_authorized_keys:
                raise SystemExit("server_public_key is empty")
    return oci.config.from_file(file_location=f"./{sys.argv[1]}"), ssh_authorized_keys

def main():
    configs, ssh_public_key = get_config()
    launch(configs, ssh_public_key)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"{datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')} Forced exit!")
