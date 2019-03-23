License:        BSD
Vendor:         Otus
Group:          PD01
URL:            http://otus.ru/lessons/3/
Source0:        otus-%{current_datetime}.tar.gz
BuildRoot:      %{_tmppath}/otus-%{current_datetime}
Name:           ip2w
Version:        0.0.1
Release:        1
BuildArch:      noarch
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
BuildRequires: systemd
Requires: bash git
Summary:  Build rpm package for uwsgi daemon


%description
File description
Git version: %{git_version} (branch: %{git_branch})

%define __etcdir    /usr/local/etc
%define __logdir    /var/log/
%define __applog    /var/log/ip_weather.log
%define __bindir    /usr/local/ip2w/
%define __systemddir	/usr/lib/systemd/system/

%prep
%{__cp} /wsgi_daemon/.env %{buildroot}

%install
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}
%{__mkdir} -p %{buildroot}/%{__systemddir}
%{__install} -pD -m 644 /wsgi_daemon/uwsgi.service %{buildroot}%{__systemddir}%{name}.service
%{__mkdir} -p %{buildroot}/%{__logdir}
%{__mkdir} -p %{buildroot}/%{__bindir}
%{__mkdir} -p %{buildroot}/%{__etcdir}
touch %{buildroot}/%{__applog}

%post
%systemd_post %{name}.service
systemctl daemon-reload

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%clean
[ "%{buildroot}" != "/" ] && rm -fr %{buildroot}


%files
%{__logdir}
%{__bindir}
%{__systemddir}
%{__applog}
