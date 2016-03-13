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
%%define        DST_DIR /var/www/nailgun/plugins/${ name }

%%description
${ description }

%%prep
rm -rf %{name}-%{version}
mkdir %{name}-%{version}
%%define        SESSION_ID $(echo %{name}-%{version} | md5sum | cut -d" " -f1)

tar -vxf %{SOURCE0} -C %{name}-%{version}

%%install
cd %{name}-%{version}
mkdir -p %{buildroot}/var/www/nailgun/plugins/
cp -r ${ name } %{buildroot}/var/www/nailgun/plugins/

%%clean
rm -rf %{buildroot}

%%pre
export RPM_SESSION_ID=%{SESSION_ID}
${ preinstall_hook }

%%post
export RPM_SESSION_ID=%{SESSION_ID}
export DST_DIR=%{DST_DIR}
${ postinstall_hook }

%%preun
${ uninstall_hook }

%%files
%%{DST_DIR}
