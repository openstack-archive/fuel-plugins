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

%%files
/var/www/nailgun/plugins/${ name }
