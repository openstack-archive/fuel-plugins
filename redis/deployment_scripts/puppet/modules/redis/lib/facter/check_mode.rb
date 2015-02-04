Facter.add('cluster_mode') do
  setcode do
    Facter::Util::Resolution.exec("cat /etc/astute.yaml | grep deployment_mode | awk '{print $2}'")
  end
end
