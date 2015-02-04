module Puppet::Parser::Functions
  newfunction(:redis_backend_url, :type => :rvalue) do |args|
    nodes = args[0]
    timeout = args[1]

    backend_url="redis://" + nodes[0] + ":26379?sentinel=" + nodes[0]

    nodes.each do |value|
      if value != nodes[0]
        backend_url=backend_url + "&sentinel_fallback=" + value + ":26379?sentinel=" + value
      end
    end
    backend_url=backend_url + "&timeout=" + timeout

    backend_url
  end
end
