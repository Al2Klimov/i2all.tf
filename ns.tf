resource "openstack_compute_instance_v2" "ns" {
	name = "${var.vm_prefix}ns"
	image_name = "Centos 7"
	flavor_name = "s1.small"
	availability_zone = "${var.vm_avzone1}"
	network { name = "${var.vm_network}" }
	security_groups = [ "default" ]
	key_pair = "${var.vm_keypair}"
}
