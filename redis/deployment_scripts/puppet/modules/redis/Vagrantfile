# -*- mode: ruby -*-
# vi: set ft=ruby :
#

if ENV['VAGRANT_HOME'].nil?
    ENV['VAGRANT_HOME'] = './'
end

redis = {
    :'centos5'  => { :memory => '120', :ip => '10.1.1.10', :box => 'puppetlabs/centos-5.11-64-puppet',  :domain => 'redis.local' },
    :'centos65' => { :memory => '120', :ip => '10.1.1.11', :box => 'puppetlabs/centos-6.5-64-puppet',   :domain => 'redis.local' },
    :'precise'  => { :memory => '120', :ip => '10.1.1.20', :box => 'puppetlabs/ubuntu-12.04-64-puppet', :domain => 'redis.local' },
    :'saucy'    => { :memory => '120', :ip => '10.1.1.21', :box => 'puppetlabs/ubuntu-13.10-64-puppet', :domain => 'redis.local' },
    :'trusty'   => { :memory => '240', :ip => '10.1.1.22', :box => 'puppetlabs/ubuntu-14.04-64-puppet', :domain => 'redis.local' },
    :'squeeze'  => { :memory => '120', :ip => '10.1.1.30', :box => 'puppetlabs/debian-6.0.9-64-puppet', :domain => 'redis.local' },
    :'wheezy'   => { :memory => '120', :ip => '10.1.1.31', :box => 'puppetlabs/debian-7.6-64-puppet',   :domain => 'redis.local' },
}

Vagrant::Config.run("2") do |config|
  config.vbguest.auto_update = true
  config.hostmanager.enabled = false

    redis.each_pair do |name, opts|
        config.vm.define name do |n|
            config.vm.provider :virtualbox do |vb|
                vb.customize ["modifyvm", :id, "--memory", opts[:memory] ]
            end
            n.vm.network "private_network", ip: opts[:ip]
            n.vm.box = opts[:box]
            n.vm.host_name = "#{name}" + "." + opts[:domain]
            n.vm.synced_folder "#{ENV['VAGRANT_HOME']}","/etc/puppet/modules/redis"
            n.vm.provision :shell, :inline => "gem install puppet facter --no-ri --no-rdoc" if name == "trusty"
            n.vm.provision :shell, :inline => "puppet module install thias-sysctl --force"
            n.vm.provision :puppet do |puppet|
                puppet.manifests_path = "tests"
                puppet.manifest_file  = "init.pp"
                #puppet.manifest_file  = "sentinel.pp"
                puppet.module_path = "./"
            end
        end
    end

end
