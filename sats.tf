resource "openstack_compute_instance_v2" "sat" {
	for_each = toset([for i in range(1, 9) : tostring(i)])
	name = "${var.vm_prefix}sat-${each.value}"
	image_name = "Debian 12"
	flavor_name = "s1.large"
	network { name = "${var.vm_network}" }
	security_groups = [ "default" ]
	key_pair = "${var.vm_keypair}"
}
