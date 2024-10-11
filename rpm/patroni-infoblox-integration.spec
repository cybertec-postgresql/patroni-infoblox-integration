%define VERSION        1.3

%define        ENVNAME  patroni-infoblox-integration
%define        INSTALLPATH /opt/app/patroni-infoblox-integration
%define debug_package %{nil}
# remove build-id files that conflict with system python
%define _build_id_links none

# Fetch remote sources
%undefine _disable_source_fetch

Name:          patroni-infoblox-integration
Version:       %{VERSION}
Release:       1%{dist}
License:       MIT
Summary:       PostgreSQL high-availability manager
Source:        https://github.com/cybertec-postgresql/patroni-infoblox-integration/archive/refs/tags/%{version}.tar.gz
BuildRoot:     %{_tmppath}/%{buildprefix}-buildroot
Requires:      python3
BuildRequires: python3-virtualenv

%global __python %{__python3}

%description
Packaged version of Patroni HA manager.

%prep
%setup

%build

%install
mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}
virtualenv --system-site-packages $RPM_BUILD_ROOT%{INSTALLPATH}
$RPM_BUILD_ROOT%{INSTALLPATH}/bin/pip3 install .

# remove pycache files that reference the build root
find $RPM_BUILD_ROOT -name __pycache__ | xargs -r rm -rf
# fix references to build root in shell scripts
sed -i "s#$RPM_BUILD_ROOT##" $RPM_BUILD_ROOT%{INSTALLPATH}/bin/*

%clean
rm -rf $RPM_BUILD_ROOT

%post
%{_sbindir}/update-alternatives --install %{_bindir}/infoblox-callback.py \
  infoblox-callback.py %{INSTALLPATH}/bin/infoblox-callback.py 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove infoblox-callback.py %{INSTALLPATH}/bin/infoblox-callback.py
fi

%files
%defattr(-,root,root)
/opt/app/patroni-infoblox-integration

%changelog
* Tue May 12 2020 Ants Aasma 1.1-1.rhel7
- Initial packaging with a separate virtualenv

