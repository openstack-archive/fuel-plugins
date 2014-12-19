require 'facter'

fencing_settings_path = ['/etc/pcs_fencing.yaml']

fencing_settings_path.each do |fencing_file|
  if File.exist?(fencing_file)
    Facter.add('fencing_settings_file') do
      setcode { fencing_file }
    end
    Facter.add('fencing_settings_yaml') do
      setcode { File.read(fencing_file) }
    end
    break
  end
end
