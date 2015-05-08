# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
    config.vm.box = "ubuntu/trusty64"
    config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
    config.vm.hostname = "trusty"

    # https://github.com/mitchellh/vagrant/issues/1673
    config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"
    config.vm.network :forwarded_port, guest: 8000, host: 8000 # Web App 1

    config.vm.provider :virtualbox do |v|
        # Allow symlinks to support virtualenvs inside /vagrant.
        v.customize([
            'setextradata',
            :id,
            'VBoxInternal2/SharedFoldersEnableSymlinksCreate/v-root',
            '1'
        ])

        v.customize ["modifyvm", :id,
            # Make the guest use the host for name resolution, so names on the VPN
            # will work (assuming they work on the host).
            "--natdnshostresolver1", "on",

            # Allow 1GB of RAM
            "--memory", "1024"]
    end

    config.vm.provision "shell" do |shell|
        shell.path = "provision.sh"
        shell.args = "true" # set DEV_ENV=true in provisioner script.
    end
end

