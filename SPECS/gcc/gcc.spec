%global security_hardening nofortify
%define _use_internal_dependency_generator 0
Summary:        Contains the GNU compiler collection
Name:           gcc
Version:        9.1.0
Release:        7%{?dist}
License:        GPLv2+
URL:            https://gcc.gnu.org/
Group:          Development/Tools
Vendor:         Microsoft Corporation
Distribution:   Mariner
Source0:        https://ftp.gnu.org/gnu/gcc/%{name}-%{version}/%{name}-%{version}.tar.xz
Patch0:         090_all_pr55930-dependency-tracking.patch
# Only applies to the Power9 ISA
Patch1:         CVE-2019-15847.nopatch
Requires:       libstdc++-devel = %{version}-%{release}
Requires:       libgcc-devel = %{version}-%{release}
Requires:       libgomp-devel = %{version}-%{release}
Requires:       libgcc-atomic = %{version}-%{release}
Requires:       gmp
Requires:       libmpc
#%if %{with_check}
#BuildRequires:  autogen
#BuildRequires:  dejagnu
#%endif

%description
The GCC package contains the GNU compiler collection,
which includes the C and C++ compilers.

%package -n     gfortran
Summary:        GNU Fortran compiler.
Group:          Development/Tools
%description -n gfortran
The gfortran package contains GNU Fortran compiler.

%package -n     libgcc
Summary:    GNU C Library
Group:          System Environment/Libraries
%description -n libgcc
The libgcc package contains GCC shared libraries for gcc.

%package -n     libgcc-atomic
Summary:        GNU C Library for atomic counter updates
Group:          System Environment/Libraries
Requires:       libgcc = %{version}-%{release}
%description -n libgcc-atomic
The libgcc package contains GCC shared libraries for atomic counter updates.

%package -n     libgcc-devel
Summary:        GNU C Library
Group:          Development/Libraries
Requires:       libgcc = %{version}-%{release}
%description -n libgcc-devel
The libgcc package contains GCC shared libraries for gcc .
This package contains development headers and static library for libgcc.

%package -n     libstdc++
Summary:        GNU C Library
Group:          System Environment/Libraries
Requires:       libgcc = %{version}-%{release}
%description -n libstdc++
This package contains the GCC Standard C++ Library v3, an ongoing project to implement the ISO/IEC 14882:1998 Standard C++ library.

%package -n     libstdc++-devel
Summary:        GNU C Library
Group:          Development/Libraries
Requires:       libstdc++ = %{version}-%{release}
%description -n libstdc++-devel
This is the GNU implementation of the standard C++ libraries.
This package includes the headers files and libraries needed for C++ development.

%package -n     libgomp
Summary:        GNU C Library
Group:          System Environment/Libraries
%description -n libgomp
An implementation of OpenMP for the C, C++, and Fortran 95 compilers in the GNU Compiler Collection.

%package -n     libgomp-devel
Summary:        Development headers and static library for libgomp
Group:          Development/Libraries
Requires:       libgomp = %{version}-%{release}
%description -n libgomp-devel
An implementation of OpenMP for the C, C++, and Fortran 95 compilers in the GNU Compiler Collection.
This package contains development headers and static library for libgomp

%prep
%setup -q
%patch0 -p1
# disable no-pie for gcc binaries
sed -i '/^NO_PIE_CFLAGS = /s/@NO_PIE_CFLAGS@//' gcc/Makefile.in

%build
CFLAGS="`echo " %{build_cflags} " | sed 's/-Werror=format-security/-Wno-error=format-security/'`"
CXXFLAGS="`echo " %{build_cxxflags} " | sed 's/-Werror=format-security/-Wno-error=format-security/'`"
export CFLAGS
export CXXFLAGS

export glibcxx_cv_c99_math_cxx98=yes glibcxx_cv_c99_math_cxx11=yes
SED=sed \
%configure \
    --enable-shared \
    --enable-threads=posix \
    --enable-__cxa_atexit \
    --enable-clocale=gnu \
    --enable-languages=c,c++,fortran \
    --disable-multilib \
    --disable-bootstrap \
    --enable-linker-build-id \
    --enable-plugin \
    --enable-default-pie \
    --with-system-zlib
make %{?_smp_mflags}

%install
make %{?_smp_mflags} DESTDIR=%{buildroot} install
install -vdm 755 %{buildroot}/%_lib
ln -sv %{_bindir}/cpp %{buildroot}/%{_lib}
ln -sv gcc %{buildroot}%{_bindir}/cc
install -vdm 755 %{buildroot}%{_datarootdir}/gdb/auto-load%{_lib}
mv -v %{buildroot}%{_lib64dir}/*gdb.py %{buildroot}%{_datarootdir}/gdb/auto-load%{_lib}
chmod 755 %{buildroot}/%{_lib64dir}/libgcc_s.so.1
rm -rf %{buildroot}%{_infodir}
%find_lang %{name} --all-name

%check
ulimit -s 32768
# disable PCH tests is ASLR is on (due to bug in pch)
test `cat /proc/sys/kernel/randomize_va_space` -ne 0 && rm gcc/testsuite/gcc.dg/pch/pch.exp
# disable security hardening for tests
rm -f $(dirname $(gcc -print-libgcc-file-name))/../specs
# run only gcc tests
make %{?_smp_mflags} check-gcc
# Only 1 FAIL is OK
[ `grep ^FAIL testsuite/gcc/gcc.sum | wc -l` -ne 1 -o `grep ^XPASS testsuite/gcc/gcc.sum | wc -l` -ne 0 ] && exit 1 ||:
[ `grep "^FAIL: gcc.dg/cpp/trad/include.c (test for excess errors)" testsuite/gcc/gcc.sum | wc -l` -ne 1 ] && exit 1 ||:

%post   -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files -f %{name}.lang
%defattr(-,root,root)
%license COPYING
%{_lib}/cpp
#   Executables
%exclude %{_bindir}/*gfortran
%{_bindir}/*
#   Libraries
%{_lib64dir}/*
%exclude %{_libexecdir}/gcc/%{_arch}-%{_host_vendor}-linux-gnu/%{version}/f951
%{_libdir}/gcc/*
#   Library executables
%{_libexecdir}/gcc/*
#   Man pages
%{_mandir}/man1/gcov.1.gz
%{_mandir}/man1/gcov-dump.1.gz
%{_mandir}/man1/gcov-tool.1.gz
%{_mandir}/man1/gcc.1.gz
%{_mandir}/man1/g++.1.gz
%{_mandir}/man1/cpp.1.gz
%{_mandir}/man7/*.gz
%{_datadir}/gdb/*

%exclude %{_lib64dir}/libgcc*
%exclude %{_lib64dir}/libstdc++*
%exclude %{_lib64dir}/libgomp*

%files -n gfortran
%defattr(-,root,root)
%{_bindir}/*gfortran
%{_mandir}/man1/gfortran.1.gz
%{_libexecdir}/gcc/%{_arch}-%{_host_vendor}-linux-gnu/%{version}/f951

%files -n libgcc
%defattr(-,root,root)
%{_lib64dir}/libgcc_s.so.*

%files -n libgcc-atomic
%defattr(-,root,root)
%{_lib64dir}/libatomic.so*

%files -n libgcc-devel
%defattr(-,root,root)
%{_lib64dir}/libgcc_s.so
%{_lib}/libcc1.*

%files -n libstdc++
%defattr(-,root,root)
%{_lib64dir}/libstdc++.so.*
%dir %{_datarootdir}/gcc-%{version}/python/libstdcxx
%{_datarootdir}/gcc-%{version}/python/libstdcxx/*

%files -n libstdc++-devel
%defattr(-,root,root)
%{_lib64dir}/libstdc++.so
%{_lib64dir}/libstdc++.la
%{_lib64dir}/libstdc++.a
%{_lib64dir}/libstdc++fs.a

%{_includedir}/c++/*

%files -n libgomp
%defattr(-,root,root)
%{_lib64dir}/libgomp*.so.*

%files -n libgomp-devel
%defattr(-,root,root)
%{_lib64dir}/libgomp.a
%{_lib64dir}/libgomp.la
%{_lib64dir}/libgomp.so
%{_lib64dir}/libgomp.spec

%changelog
* Thu Sep 10 2020 Thomas Crain <thcrain@microsoft.com> - 9.1.0-7
- Ignore CVE-2019-15847, as it applies to an unsupported ISA

* Mon Jul 06 2020 Henry Beberman <henry.beberman@microsoft.com> - 9.1.0-6
- Comment out with_check BuildRequires to break circular dependency in build graph.

* Thu Jun 11 2020 Henry Beberman <henry.beberman@microsoft.com> - 9.1.0-5
- Disable -Werror=format-security to build with hardened cflags

* Sat May 09 00:21:12 PST 2020 Nick Samson <nisamson@microsoft.com> - 9.1.0-4
- Added %%license line automatically

* Thu Apr 30 2020 Emre Girgin <mrgirgin@microsoft.com> - 9.1.0-3
- Renaming mpc to libmpc

* Thu Apr 09 2020 Emre Girgin <mrgirgin@microsoft.com> - 9.1.0-2
- Add the "--enable-default-pie" flag in order to enforce ASLR-enabled binaries.

* Tue Mar 17 2020 Andrew Phelps <anphel@microsoft.com> - 9.1.0-1
- Update to version 9.1.0. License verified. Add libstdc++fs.a

* Tue Jan 21 2020 Andrew Phelps <anphel@microsoft.com> - 7.3.0-6
- Fixing build issues for multiple architectures

* Tue Sep 03 2019 Mateusz Malisz <mamalisz@microsoft.com> - 7.3.0-5
- Initial CBL-Mariner import from Photon (license: Apache2).

* Fri Nov 02 2018 Alexey Makhalov <amakhalov@vmware.com> - 7.3.0-4
- Use nofortify security_hardening instead of sed hacking
- Use %configure

* Wed Sep 19 2018 Alexey Makhalov <amakhalov@vmware.com> - 7.3.0-3
- Fix compilation issue for glibc-2.28

* Thu Aug 30 2018 Keerthana K <keerthanak@vmware.com> - 7.3.0-2
- Packaging .a files (libstdc++-static files).

* Wed Aug 01 2018 Srivatsa S. Bhat <srivatsa@csail.mit.edu> - 7.3.0-1
- Update to version 7.3.0 to get retpoline support.

* Tue Nov 14 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-7
- Aarch64 support

* Mon Oct 02 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-6
- Added smp_mflags for parallel build

* Mon Sep 25 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-5
- Enable elfdeps for libgcc_s to generate libgcc_s.so.1(*)(64bit) provides

* Mon Aug 28 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-4
- Fix makecheck

* Tue Aug 15 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-3
- Fix compilation issue for glibc-2.26

* Tue Aug 15 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-2
- Improve make check

* Thu Mar 9 2017 Alexey Makhalov <amakhalov@vmware.com> - 6.3.0-1
- Update version to 6.3

* Thu Mar 02 2017 Xiaolin Li <xiaolinl@vmware.com> - 5.3.0-6
- Enabled fortran.

* Wed Feb 22 2017 Alexey Makhalov <amakhalov@vmware.com> - 5.3.0-5
- Added new plugin entry point: PLUGIN_TYPE_CAST (.patch)

* Thu Sep  8 2016 Alexey Makhalov <amakhalov@vmware.com> - 5.3.0-4
- Enable plugins and linker build id.

* Tue May 24 2016 Priyesh Padmavilasom <ppadmavilasom@vmware.com> - 5.3.0-3
- GA - Bump release of all rpms

* Tue May 17 2016 Anish Swaminathan <anishs@vmware.com> - 5.3.0-2
- Change package dependencies

* Mon Mar 28 2016 Alexey Makhalov <amakhalov@vmware.com> - 5.3.0-1
- Update version to 5.3

* Tue Nov 10 2015 Xiaolin Li <xiaolinl@vmware.com> - 4.8.2-6
- Handled locale files with macro find_lang

* Mon Nov 02 2015 Vinay Kulkarni <kulkarniv@vmware.com> - 4.8.2-5
- Put libatomic.so into its own package.

* Wed May 20 2015 Touseef Liaqat <tliaqat@vmware.com> - 4.8.2-4
- Updated group.

* Mon May 18 2015 Touseef Liaqat <tliaqat@vmware.com> - 4.8.2-3
- Update according to UsrMove.

* Fri May 15 2015 Divya Thaluru <dthaluru@vmware.com> - 4.8.2-2
- Packaging .la files

* Tue Apr 01 2014 baho-utot <baho-utot@columbus.rr.com> - 4.8.2-1
- Initial build. First version
