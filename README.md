1. In OpenStack create an unrestricted Application Secret
2. Create an `.auto.tfvars` file from it like below
3. Run `terraform init`
4. Run `terraform apply`
5. Run `python3 tf2ansible.py < terraform.tfstate > inventory.txt`
6. Collect remote SSH keys:
   `ansible all -i inventory.txt -m ping --ssh-common-args="-o StrictHostKeyChecking=no -o UserKnownHostsFile=$(pwd)/known_hosts.txt"`
7. Provision the VMs:
   `ansible-playbook -i inventory.txt --ssh-common-args="-o UserKnownHostsFile=$(pwd)/known_hosts.txt" playbook.yml`

## .auto.tfvars

```
openstack_credential_id = "0123456789abcdef0123456789abcdef"
openstack_credential_secret = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
```

You may also want to override more of the variables listed in
[variables.tf](./variables.tf).
