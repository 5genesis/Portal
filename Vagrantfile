# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/bionic64"
  config.vm.network "forwarded_port", guest: 80, host: 80

  config.vm.provider "virtualbox" do |v|
    v.name = "5genesis-portal"
    v.memory = 2048
  end

  # All bootstrapping command should be in this external shell file
  # so it can be used on stand-alone installations
  config.vm.provision :shell, privileged: false, path: "bootstrap.sh", args: "'vagrant'"

  config.vm.post_up_message = <<-MESSAGE
    5Genesis Portal should be accessible at localhost (port 80)
  MESSAGE
end
