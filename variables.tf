variable "openstack_auth_url" {
	default = "https://cloud.netways.de:5000/v3/"
}

variable "openstack_tenant_name" {
	default = "2310-openstack-c3a60"
}

variable "openstack_credential_id" {
}

variable "openstack_credential_secret" {
}

variable "vm_network" {
	default = "icinga-testing-network"
}

variable "vm_keypair" {
	default = "aklimov"
}

variable "vm_prefix" {
	default = "aklimov-i2all-"
}
