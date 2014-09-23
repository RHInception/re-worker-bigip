%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%global _pkg_name replugin
%global _src_name reworkerbigip

Name: re-worker-bigip
Summary: RE Worker which interacts with F5 BigIPs
Version: 0.0.1
Release: 6%{?Dist}

Group: Applications/System
License: AGPLv3
Source0: %{_src_name}-%{version}.tar.gz
Url: https://github.com/rhinception/re-worker-bigip

BuildArch: noarch
BuildRequires: python2-devel, python-setuptools
Requires: re-worker, python-setuptools, python-argparse, bigip

%description
A Release Engine Worker Plugin that will enable and disable nodes in
F5 BigIP load balancers, as well as configuration sync from active to
failover devices.

%prep
%setup -q -n %{_src_name}-%{version}

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install -O1 --root=$RPM_BUILD_ROOT --record=re-worker-bigip-files.txt

%files -f re-worker-bigip-files.txt
%doc README.md LICENSE AUTHORS
%dir %{python2_sitelib}/%{_pkg_name}
%exclude %{python2_sitelib}/%{_pkg_name}/__init__.py*

%changelog
* Tue Sep 23 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-6
- 'show' does not take any options

* Tue Sep 23 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-5
- Call the actual 'show' command

* Tue Sep 23 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-4
- Print results from calls to bigip api

* Thu Jun 26 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-3
- Add in logging statements

* Thu Jun 26 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-2
- Fix package description

* Tue Jun 24 2014 Tim Bielawa <tbielawa@redhat.com> - 0.0.1-1
- First package
