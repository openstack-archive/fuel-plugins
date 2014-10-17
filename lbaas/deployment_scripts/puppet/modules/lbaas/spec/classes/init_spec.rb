require 'spec_helper'
describe 'lbaas' do

  context 'with defaults for all parameters' do
    it { should contain_class('lbaas') }
  end
end
