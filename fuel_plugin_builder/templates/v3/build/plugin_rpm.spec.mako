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
Release:        1
BuildArch:      noarch
AutoReq:        no

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
    ${ uninstall_hook }
fi
% endif

%%files
/var/www/nailgun/plugins/${ name }
