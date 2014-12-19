require 'spec_helper'

describe 'pcs_fencing::fencing', :type => :define do

  let (:title) { 'virsh_off' }
  let (:node)  { 'node-1' }
  let (:res_name) { "stonith__#{title}__#{node}" }
  let :params do
    {
      :agent_type => 'fence_virsh',
      :parameters => false,
      :operations => false,
      :meta => false
    }
  end
  let :primitive_params do
    {
      :ensure => 'present',
      :provided_by => 'pacemaker',
      :primitive_class => 'stonith',
      :primitive_type => params[:agent_type],
      :parameters => params[:parameters],
      :operations => params[:operations],
      :metadata => params[:meta]
    }
  end
  let :location_prohibit_params do
    {
      :node_name => node,
      :score => '-INFINITY',
      :primitive => res_name
    }
  end
  let :location_allow_params do
    {
      :primitive => res_name,
      :rules => [
        {
          'score'   => '100',
          'boolean' => '',
          'expressions' => [
            {'attribute'=>"#uname",'operation'=>'ne','value'=>node}
          ]
        }
      ]
    }
  end
  let(:facts) {{ :osfamily => 'Debian' }}
  let(:facts) {{ :pacemaker_hostname => node }}

  context 'then configuring STONITH primitive' do
    it 'should contain its definition' do
      should contain_pcs_fencing__fencing(title).with(params)
    end

    it 'should create a pacemaker primitive' do
      should contain_cs_resource(res_name).with(
        {
          'ensure' => primitive_params[:ensure],
          'primitive_class' => primitive_params[:primitive_class],
          'primitive_type' => primitive_params[:primitive_type],
          'provided_by' => primitive_params[:provided_by],
          'parameters' => primitive_params[:parameters],
          'operations' => primitive_params[:operations],
          'metadata' => primitive_params[:metadata]
        }
      )
    end
    it 'should create a prohibit location' do
      should contain_cs_location("location__prohibit__#{res_name}").with(
        {
          'node_name' => location_prohibit_params[:node_name],
          'node_score' => location_prohibit_params[:score],
          'primitive' => location_prohibit_params[:primitive]
        }
      )
    end
    it 'should create an allow location' do
      should contain_cs_location("location__allow__#{res_name}").with(
        {
          'primitive' => location_allow_params[:primitive],
          'rules' => location_allow_params[:rules]
        }
      )
    end
  end
end
