resource "openstack_compute_instance_v2" "agent" {
	for_each = toset([for i in range(1, 33) : tostring(i)])
	name = "${var.vm_prefix}agent-${each.value}"
	image_name = "Centos 7"
	flavor_name = "s1.small"
	availability_zone = "${var.vm_avzone2}"
	network { name = "${var.vm_network}" }
	security_groups = [ "default" ]
	key_pair = "${var.vm_keypair}"
}
