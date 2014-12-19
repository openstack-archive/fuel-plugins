require 'spec_helper'

describe 'pcs_fencing::fencing_primitives' do

  let :params do
    {
      :fence_primitives => {
        'ipmi_off' => {
          'agent_type' => 'fence_ipmilan',
          'operations' => false,
          'meta'       => false,
          'parameters' => false
        }
      },
      :fence_topology => {
        'node-1.foo.bar' => {
          '1' => [ 'ipmi_off' ]
        }
      },
      :nodes => [
        {
          'fqdn' => 'node-1.foo.bar',
          'name' => 'node-1',
          'role' => 'primary-controller'
        }
      ]
    }
  end
  let(:names) { [ 'node-1.foo.bar' ] }
  let(:facts) {{ :osfamily => 'RedHat' }}

  context 'then configuring fencing' do

    it 'should install fence-agents' do
      should contain_package('fence-agents')
    end

    it 'should contain its class' do
      should contain_class('pcs_fencing::fencing_primitives').with(params)
    end

    it 'should create fencing primitives' do
      should contain_pcs_fencing__fencing('ipmi_off').with(
        params[:fence_primitives]['ipmi_off']
      )
    end

    it 'should enable fencing' do
      should contain_cs_property('stonith-enabled')
    end

    it 'should update cluster recheck interval' do
      should contain_cs_property('cluster-recheck-interval')
    end

    it 'should create a topology' do
      should contain_cs_fencetopo('fencing_topology').with(
        {
          :ensure         => 'present',
          :fence_topology => params[:fence_topology],
          :nodes          => names,
        }
      )
    end
  end
end
