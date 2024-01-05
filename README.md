1. In OpenStack create an unrestricted Application Secret
2. Create an `.auto.tfvars` file from it like below
3. Run `terraform init`
4. Run `terraform apply`
5. Run `python3 tf2ansible.py < terraform.tfstate > inventory.txt`

## .auto.tfvars

```
openstack_credential_id = "0123456789abcdef0123456789abcdef"
openstack_credential_secret = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"
```

You may also want to override more of the variables listed in
[variables.tf](./variables.tf).
