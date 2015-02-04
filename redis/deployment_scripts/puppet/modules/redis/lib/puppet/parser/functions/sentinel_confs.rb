module Puppet::Parser::Functions
  newfunction(:sentinel_confs, :type => :rvalue) do |args|
    if args.length != 5
      raise "Wrong number of arguments"
    end
    nodes = args[0]
    quorum = args[1]
    parallel_syncs = args[2]
    down_after_milliseconds = args[3]
    failover_timeout = args[4]
    hash = {}

    nodes.each do |value|
      hash[value] = { 'monitor' => value + ' 6379 ' + quorum, 'down-after-milliseconds' => down_after_milliseconds, 'failover-timeout' => failover_timeout, 'parallel-syncs' => parallel_syncs }
    end

    hash
  end
end
