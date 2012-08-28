# We only compile with gcc, but other people may want other compilers.
# Set the compiler here.
%global opt_cc gcc
# Optional CFLAGS to use with the specific compiler...gcc doesn't need any,
# so uncomment and define to use
%global opt_cflags ${RPM_OPT_FLAGS/-D_FORTIFY_SOURCE=2/}
%global opt_cxx g++
#global opt_cxxflags
%global opt_fc pgf95 -noswitcherror
%global opt_fcflags -fastsse

%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
# Optional name suffix to use...we leave it off when compiling with gcc, but
# for other compiled versions to install side by side, it will need a
# suffix in order to keep the names from conflicting.
%global _cc_name_suffix -pgf
                                                                                   
#We don't want to be beholden to the proprietary libraries
%global    _use_internal_dependency_generator 0
%global    __find_requires %{nil}

#Useless debuginfo
%global debug_package %{nil}

Name:			openmpi161%{?_cc_name_suffix}
Version:		1.6.1
Release:		1%{?dist}
Summary:		Open Message Passing Interface
Group:			Development/Libraries
License:		BSD, MIT and Romio
URL:			http://www.open-mpi.org/

# We can't use %{name} here because of _cc_name_suffix
Source0:		http://www.open-mpi.org/software/ompi/v1.6/downloads/openmpi-%{version}.tar.bz2
Source1:		openmpi.module.in
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
#sparc 64 doesn't have valgrind
%ifnarch %{sparc}
BuildRequires:		valgrind-devel
%endif
BuildRequires:		libibverbs-devel >= 1.1.3, opensm-devel > 3.3.0
BuildRequires:		librdmacm-devel libibcm-devel
# EL6 hwloc is too old
%if 0%{?fedora}
BuildRequires:		hwloc-devel
%endif
BuildRequires:		python libtool-ltdl-devel
BuildRequires:		libesmtp-devel

Provides:		mpi
Requires:		environment-modules

# s390 is unlikely to have the hardware we want, and some of the -devel
# packages we require aren't available there.
ExcludeArch: s390 s390x

# Private openmpi libraries
%global __provides_exclude_from %{_libdir}/openmpi/lib/(lib(mca|o|v)|openmpi/).*.so
%global __requires_exclude lib(mca|o|v).*

%description
Open MPI is an open source, freely available implementation of both the 
MPI-1 and MPI-2 standards, combining technologies and resources from
several other projects (FT-MPI, LA-MPI, LAM/MPI, and PACX-MPI) in
order to build the best MPI library available.  A completely new MPI-2
compliant implementation, Open MPI offers advantages for system and
software vendors, application developers, and computer science
researchers. For more information, see http://www.open-mpi.org/ .


# When dealing with multilib installations, aka the ability to run either
# i386 or x86_64 binaries on x86_64 machines, we install the native i386
# openmpi libs/compilers and the native x86_64 libs/compilers.  Obviously,
# on i386 you can only run i386, so you don't really need the -m32 flag
# to gcc in order to force 32 bit mode.  However, since we use the native
# i386 package to support i386 operation on x86_64, and since on x86_64
# the default is x86_64, the i386 package needs to force i386 mode.  This
# is true of all the multilib arches, hence the non-default arch (aka i386
# on x86_64) must force the non-default mode (aka 32 bit compile) in it's
# native-arch package (aka, when built on i386) so that it will work
# properly on the non-native arch as a multilib package (aka i386 installed
# on x86_64).  Just to be safe, we also force the default mode (aka 64 bit)
# in default arch packages (aka, the x86_64 package).  There are, however,
# some arches that don't support forcing *any* mode, those we just leave
# undefined.
%ifarch %{ix86} ppc sparcv9
%global mode 32
%global modeflag -m32
%endif
%ifarch ia64
%global mode 64
%endif
%ifarch x86_64 ppc64 sparc64
%global mode 64
%global modeflag -m64
%endif

# We set this to for convenience, since this is the unique dir we use for this
# particular package, version, compiler
%global mpidir openmpi%{?_cc_name_suffix}/%{version}-%{_arch}

%prep
%setup -q -n openmpi-%{version}
# Make sure we don't use the local libltdl library
rm -r opal/libltdl

%build
./configure --prefix=/opt/%{mpidir} \
	--with-openib=/usr \
	--with-sge \
%ifnarch %{sparc}
	--with-valgrind \
	--enable-memchecker \
%endif
	--with-esmtp \
%if 0%{?fedora}
	--with-hwloc=/usr \
%endif
	--with-libltdl=/usr \
	CC=%{opt_cc} CXX=%{opt_cxx} \
	F77="%{opt_fc}" \
	FC="%{opt_fc}" \
	LDFLAGS='-Wl,-z,noexecstack' \
	CFLAGS="%{?opt_cflags}" \
	CXXFLAGS="%{?opt_cxxflags}" \
	FFLAGS="%{?opt_fcflags}" \
	FCFLAGS="%{?opt_fcflags}" \
	AR="xiar"
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}
make install DESTDIR=${RPM_BUILD_ROOT}
find %{buildroot}/opt/%{mpidir}/lib -name \*.la | xargs rm

# Make the environment-modules file
mkdir -p %{buildroot}%{_sysconfdir}/modulefiles/mpi/`dirname %{mpidir}`
# Since we're doing our own substitution here, use our own definitions.
sed 's#@MPIDIR@#'%{mpidir}'#g' < %SOURCE1 > %{buildroot}%{_sysconfdir}/modulefiles/mpi/%{mpidir}


%clean
[ ! -z "${RPM_BUILD_ROOT}" ] && rm -rf ${RPM_BUILD_ROOT}


%files
%defattr(-,root,root,-)
%doc LICENSE README
%config(noreplace) %{_sysconfdir}/modulefiles/mpi/%{mpidir}
/opt/%{mpidir}


%changelog
* Thu Aug 23 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6.1-1.cora.1
- Upate to 1.6.1

* Wed Aug 22 2012 Orion Poplawski <orion@cora.nwra.com> - 1.6-1.cora.1
- Upate to 1.6
- icc/ifort 12.1.5
- Drop old mpi module dir

* Tue Feb 21 2012 Orion Poplawski <orion@cora.nwra.com> - 1.5.4-1.cora.1
- Update to 1.5.4
- ifort 12.1.3
- Update module dir and conflict

* Fri Apr 15 2011 Orion Poplawski <orion@cora.nwra.com> - 1.4.3-1.cora.2
- Compiled with ifort 2011.3.174
- Disable debuginfo generation

* Wed Oct 13 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.3-1
- Update to 1.4.3
- Compiled with ifort 11.1.073

* Fri Apr 13 2010 Orion Poplawski <orion@cora.nwra.com> - 1.4.1-1
- Update to 1.4.1
- Compiled with ifort 11.1.069

* Thu Sep 17 2009 Orion Poplawski <orion@cora.nwra.com> - 1.3.3-1
- Update to 1.3.3
- Compiled with ifort 11.1.046
- Compile dynamically, turn off dependencies

* Tue Apr 15 2008 Orion Poplawski <orion@cora.nwra.com> - 1.2.6-1
- Update to 1.2.6

* Fri Mar 14 2008 Orion Poplawski <orion@cora.nwra.com> - 1.2.5-1
- Update to 1.2.5

* Thu Jul 26 2007 Orion Poplawski <orion@cora.nwra.com> - 1.2.3-5
- Install then move libraries so --prefix works
- Move mode into mpidir
- No modeflag for ifort
- Have -devel Require -libs
- Allow for changing the Fortran compiler and package name

* Mon Jul 16 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-4
- Fix a directory permission problem on the base openmpi directories

* Thu Jul 12 2007 Florian La Roche <laroche@redhat.com> - 1.2.3-3
- requires alternatives for various sub-rpms

* Mon Jul 02 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-2
- Fix dangling symlink issue caused by a bad macro usage
- Resolves: bz246450

* Wed Jun 27 2007 Doug Ledford <dledford@redhat.com> - 1.2.3-1
- Update to latest upstream version
- Fix file ownership on -libs package
- Take a swing at solving the multi-install compatibility issues

* Mon Feb 19 2007 Doug Ledford <dledford@redhat.com> - 1.1.1-7
- Bump version to be at least as high as the RHEL4U5 openmpi
- Integrate fixes made in RHEL4 openmpi into RHEL5 (fix a multilib conflict
  for the openmpi.module file by moving from _datadir to _libdir, make sure
  all sed replacements have the g flag so they replace all instances of
  the marker per line, not just the first, and add a %defattr tag to the
  files section of the -libs package to avoid install errors about
  brewbuilder not being a user or group)
- Resolves: bz229298

* Wed Jan 17 2007 Doug Ledford <dledford@redhat.com> - 1.1.1-5
- Remove the FORTIFY_SOURCE and stack protect options
- Related: bz213075

* Fri Oct 20 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-4
- Bump and build against the final openib-1.1 package

* Wed Oct 18 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-3
- Fix an snprintf length bug in opal/util/cmd_line.c
- RESOLVES: rhbz#210714

* Wed Oct 18 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-2
- Bump and build against openib-1.1-0.pre1.1 instead of 1.0

* Tue Oct 17 2006 Doug Ledford <dledford@redhat.com> - 1.1.1-1
- Update to upstream 1.1.1 version

* Fri Oct 13 2006 Doug Ledford <dledford@redhat.com> - 1.1-7
- ia64 can't take -m64 on the gcc command line, so don't set it there

* Wed Oct 11 2006 Doug Ledford <dledford@redhat.com> - 1.1-6
- Bump rev to match fc6 rev
- Fixup some issue with alternatives support
- Split the 32bit and 64bit libs ld.so.conf.d files into two files so
  multilib or single lib installs both work properly
- Put libs into their own package
- Add symlinks to /usr/share/openmpi/bin%{mode} so that opal_wrapper-%{mode}
  can be called even if it isn't the currently selected default method in
  the alternatives setup (opal_wrapper needs to be called by mpicc, mpic++,
  etc. in order to determine compile mode from argv[0]).

* Sun Aug 27 2006 Doug Ledford <dledford@redhat.com> - 1.1-4
- Make sure the post/preun scripts only add/remove alternatives on initial
  install and final removal, otherwise don't touch.

* Fri Aug 25 2006 Doug Ledford <dledford@redhat.com> - 1.1-3
- Don't ghost the mpi.conf file as that means it will get removed when
  you remove 1 out of a number of alternatives based packages
- Put the .mod file in -devel

* Mon Aug  7 2006 Doug Ledford <dledford@redhat.com> - 1.1-2
- Various lint cleanups
- Switch to using the standard alternatives mechanism instead of a home
  grown one

* Wed Aug  2 2006 Doug Ledford <dledford@redhat.com> - 1.1-1
- Upgrade to 1.1
- Build with Infiniband support via openib

* Mon Jun 12 2006 Jason Vas Dias <jvdias@redhat.com> - 1.0.2-1
- Upgrade to 1.0.2

* Wed Feb 15 2006 Jason Vas Dias <jvdias@redhat.com> - 1.0.1-1
- Import into Fedora Core
- Resolve LAM clashes 

* Wed Jan 25 2006 Orion Poplawski <orion@cora.nwra.com> - 1.0.1-2
- Use configure options to install includes and libraries
- Add ld.so.conf.d file to find libraries
- Add -fPIC for x86_64

* Tue Jan 24 2006 Orion Poplawski <orion@cora.nwra.com> - 1.0.1-1
- 1.0.1
- Use alternatives

* Sat Nov 19 2005 Ed Hill <ed@eh3.com> - 1.0-2
- fix lam conflicts

* Fri Nov 18 2005 Ed Hill <ed@eh3.com> - 1.0-1
- initial specfile created

