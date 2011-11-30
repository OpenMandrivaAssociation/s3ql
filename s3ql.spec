Name:               s3ql
Version:            1.7
Release:            1
Summary:            Full-Featured File System for Online Data Storage
Source:             http://s3ql.googlecode.com/files/s3ql-%{version}.tar.bz2
URL:                http://code.google.com/p/s3ql/
Group:              Networking/File transfer
License:            GPLv3
%py_requires -d
BuildRequires:      python-pyxml
BuildRequires:      python-distribute
BuildRequires:      python-liblzma >= 0.5.3
BuildRequires:      python-cryptopp
BuildRequires:      python-apsw >= 3.7.0
BuildRequires:      python-unittest2
BuildRequires:      python-paramiko
BuildRequires:      python-argparse
BuildRequires:      python-llfuse >= 0.31
BuildRequires:      gccxml
BuildRequires:      libattr-devel
BuildRequires:      fuse-devel
BuildRequires:      glibc-devel
BuildRequires:      sqlite3-devel
Requires:           fuse
Requires:           python-liblzma >= 0.5.3
Requires:           python-cryptopp
Requires:           python-apsw >= 3.7.0
Requires:           python-paramiko
Requires:           python-llfuse >= 0.31

%description
S3QL is a file system that stores all its data online using storage services
like Google Storage, Amazon S3 or OpenStack. S3QL effectively provides a hard
disk of dynamic, infinite capacity that can be accessed from any computer
with Internet access.

S3QL is a standard conforming, full featured UNIX file system that is
conceptually indistinguishable from any local file system. Furthermore, S3QL
has additional features like compression, encryption, data de-duplication,
immutable trees and snapshotting which make it especially suitable for on-line
backup and archival.

S3QL is designed to favor simplicity and elegance over performance and feature-
creep. Care has been taken to make the source code as readable and serviceable
as possible. Solid error detection and error handling have been included
from the very first line, and S3QL comes with extensive automated test cases
for all its components.

%prep
%setup -q

%build
%__python ./setup.py build

%check
# we can't test those, they use fuse and require the fuse
# kernel module to be loaded, which we cannot do from a
# chrooted package build environment where we don't run
# as root:
%__rm tests/t4* tests/t5*
%__python ./setup.py test

%install
%__python ./setup.py install \
    --prefix="%{_prefix}" \
    --root="%{buildroot}"

for x in contrib/*.py; do
    f="${x##*/}"
    case $f in
        *dummy*) continue ;;
        %{name}*) t="$f" ;;
        *) t="%{name}-$f" ;;
    esac
    t="${t%.py}"
    %__install -D -m0755 "$x" "%{buildroot}%{_bindir}/$t"
done
%__install -D -m0755 contrib/s3ql_backup.sh "%{buildroot}%{_bindir}/s3ql_backup"

find "%{buildroot}%{python_sitearch}" -type f -name '*.py' -exec %__chmod 0644 {} \;
# remove shebangs
find "%{buildroot}%{python_sitearch}" -type f -name '*.py' -exec %__sed -i -e '/^#!\//, 1d' {} \;
# recompile to fix mtimes
%__python -c 'import compileall; compileall.compile_dir("%{buildroot}%{python_sitearch}/",ddir="%{python_sitearch}/",force=True)'

%__perl -p -i -e 's,^(%{_mandir}/man\d/.+\.\d),${1}%{ext_man},' files.lst

%__rm -rf doc/html/man
%__rm doc/html/.buildinfo

%files
%defattr(-,root,root)
%doc doc/html
%doc Changes.txt
%{_bindir}/*
%{_mandir}/man1/*.xz
%{python_sitearch}/%{name}/*
%{python_sitearch}/%{name}-*.egg-info
