require 'spec_helper'
describe 'vpnaas' do

  context 'with defaults for all parameters' do
    it { should contain_class('vpnaas') }
  end
end
