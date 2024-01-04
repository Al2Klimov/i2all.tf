resource "openstack_compute_instance_v2" "master" {
	for_each = toset([for i in range(1, 3) : tostring(i)])
	name = "${var.vm_prefix}master-${each.value}"
	image_name = "Debian 12"
	flavor_name = "s1.xxlarge"
	network { name = "${var.vm_network}" }
	security_groups = [ "default" ]
	key_pair = "${var.vm_keypair}"
}
