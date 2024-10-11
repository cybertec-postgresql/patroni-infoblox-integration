%define VERSION        1.2

%define        ENVNAME  patroni-infoblox-integration
%define        INSTALLPATH /opt/app/patroni-infoblox-integration
%define debug_package %{nil}

# Fetch remote sources
%undefine _disable_source_fetch

Name:          patroni-infoblox-integration
Version:       %{VERSION}
Release:       1.rhel7
License:       MIT
Summary:       PostgreSQL high-availability manager
Source:        %{name}-%{version}.tar.gz
BuildRoot:     %{_tmppath}/%{buildprefix}-buildroot
Requires:      python3

#%global __requires_exclude_from ^%{INSTALLPATH}/lib/python3.6/site-packages/(psycopg2/|_cffi_backend.so|_cffi_backend.cpython-36m-x86_64-linux-gnu.so|.libs_cffi_backend/libffi-.*.so.6.0.4)
#%global __provides_exclude_from ^%{INSTALLPATH}/lib/python3.6/

%global __python %{__python3}

%description
Packaged version of Patroni HA manager.

%prep
%setup

%build

%install
mkdir -p $RPM_BUILD_ROOT%{INSTALLPATH}
virtualenv-3 --distribute --system-site-packages $RPM_BUILD_ROOT%{INSTALLPATH}
$RPM_BUILD_ROOT%{INSTALLPATH}/bin/pip3 install .

virtualenv-3.6 --relocatable $RPM_BUILD_ROOT%{INSTALLPATH}
sed -i "s#$RPM_BUILD_ROOT##" $RPM_BUILD_ROOT%{INSTALLPATH}/bin/activate*

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

