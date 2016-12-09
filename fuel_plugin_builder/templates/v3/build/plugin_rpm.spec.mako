#
# The spec is generated automatically by Fuel Plugin Builder tool
# https://github.com/stackforge/fuel-plugins
#
# RPM spec file for package ${ name }
#
# Copyright (c) ${ year }, ${ license }, ${ vendor }
#

Name:           ${ name }
Version:        ${ version }
Url:            ${ homepage }
Summary:        ${ summary }
License:        ${ license }
Source0:        ${ name }.fp
Vendor:         ${ vendor }
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Group:          Development/Libraries
Release:        ${ build_version }
BuildArch:      noarch
AutoReq:        no

# This will allow arch binaries to be included as part of the plugin package
# otherwise the build of the plugin fails.
%%define _binaries_in_noarch_packages_terminate_build 0

%%description
${ description }

%%prep
rm -rf %{name}-%{version}
mkdir %{name}-%{version}

tar -vxf %{SOURCE0} -C %{name}-%{version}

%%install
cd %{name}-%{version}
mkdir -p %{buildroot}/var/www/nailgun/plugins/
cp -r ${ name } %{buildroot}/var/www/nailgun/plugins/

%%clean
rm -rf %{buildroot}

%%pre
${ preinstall_hook }

%%post
${ postinstall_hook }

%%preun
# Values of $1:
# install:      (N/A)
# upgrade:      1
# uninstall:    0
% if uninstall_hook:
if [ $1 -eq 0 ]; then
    # insert no-op to allow empty or comment-only uninstall hooks
    :
    ${ uninstall_hook }
fi
% endif

%%files
/var/www/nailgun/plugins/${ name }
