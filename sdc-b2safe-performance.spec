Name:		sdc-b2safe-performance
Version:	0.1.1
Release:	1%{?dist}
Summary:	Nagios probe for SDC B2Safe Performance
License:	GPLv3+
Packager:	Angelos Tsalapatis <agelos.tsal@gmail.com>

Source:		%{name}-%{version}.tar.gz
BuildArch:	noarch
BuildRoot:	%{_tmppath}/%{name}-%{version}
AutoReqProv: no

%description
Nagios probe to check the Performance of B2Safe

%prep
%setup -q

%define _unpackaged_files_terminate_build 0 

%install

install -d %{buildroot}/%{_libexecdir}/argo-monitoring/probes/sdc-b2safe-performance
install -d %{buildroot}/%{_sysconfdir}/nagios/plugins/sdc-b2safe-performance
install -m 755 check_sdc_b2safe_performance.py %{buildroot}/%{_libexecdir}/argo-monitoring/probes/sdc-b2safe-performance/check_sdc_b2safe_performance.py

%files
%dir /%{_libexecdir}/argo-monitoring
%dir /%{_libexecdir}/argo-monitoring/probes/
%dir /%{_libexecdir}/argo-monitoring/probes/sdc-b2safe-performance

%attr(0755,root,root) /%{_libexecdir}/argo-monitoring/probes/sdc-b2safe-performance/check_sdc_b2safe_performance.py

%changelog
* Wed Aug 5 2020 Angelos Tsalapatis  <agelos.tsal@gmail.com> - 0.1-1
- Initial version of the package. 