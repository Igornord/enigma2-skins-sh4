AC_INIT([enigma2-plugins],[3.2.0],[enigma2-devel@lists.elitedvb.net])
AM_INIT_AUTOMAKE([dist-bzip2 foreign no-define tar-pax])
AC_CONFIG_HEADERS([enigma2-plugins-config.h])

# Silent rules are available since 1.11, but older versions
# are still in use. So don't use them unconditionally.
m4_ifdef([AM_SILENT_RULES], [AM_SILENT_RULES([yes])])

AC_USE_SYSTEM_EXTENSIONS
AC_SYS_LARGEFILE

AC_PROG_CC
AC_PROG_CXX
m4_ifdef([LT_INIT], [LT_INIT], [AC_PROG_LIBTOOL])
AC_CONFIG_MACRO_DIR([m4])

AC_PATH_PROG(MSGFMT, msgfmt, AC_MSG_ERROR(Could not find msgfmt))

AM_PATH_PYTHON
AX_PYTHON_DEVEL
AX_PTHREAD

TUXBOX_APPS_DVB

PKG_CHECK_MODULES(ENIGMA2, enigma2)
AC_ARG_ENABLE(libeplayer3,
	[  --enable-libeplayer3          enable TDT libeplayer3 as player engine supportt],
	[AC_DEFINE(ENABLE_LIBEPLAYER3,1,[enable TDT libeplayer3 as player engine support])])

PKG_CHECK_MODULES(LIBCRYPTO, libcrypto)
PKG_CHECK_MODULES(SIGC,sigc++-1.2)

AC_ARG_WITH(tpm,
	AS_HELP_STRING([--with-tpm], [enable plugins that require a TPM]),
	[with_tpm="$withval"],[with_tpm="no"])
if test "$with_tpm" = "yes"; then
	AC_DEFINE([HAVE_TPM],[1],[Define to 1 to enable plugins that require a TPM])
fi
AM_CONDITIONAL(TPM, test "$with_tpm" = "yes")

AC_ARG_WITH(debug,
	AS_HELP_STRING([--without-debug],[disable debugging code]),
	[with_debug="$withval"],[with_debug="yes"])
if test "$with_debug" = "yes"; then
	DEBUG_CFLAGS="-ggdb3"
	AC_DEFINE([DEBUG],[1],[Define to 1 to enable debugging code])
fi
AC_SUBST(DEBUG_CFLAGS)

AC_ARG_WITH(po,
	AS_HELP_STRING([--with-po],[enable updating of po files]),
	[with_po="$withval"],[with_po="no"])
if test "$with_po" = "yes"; then
	AC_PATH_PROG(MSGINIT, msginit)
	AC_PATH_PROG(MSGMERGE, msgmerge)
	AC_PATH_PROG(MSGUNIQ, msguniq)
	AC_PATH_PROG(XGETTEXT, xgettext)
	if test -z "$MSGINIT" -o -z "$MSGMERGE" -o -z "$MSGUNIQ" -o -z "$XGETTEXT"; then
		AC_MSG_ERROR([Could not find required gettext tools])
	fi
fi
AM_CONDITIONAL(UPDATE_PO, test "$with_po" = "yes")

AC_CONFIG_FILES([
Makefile
2b/Makefile
2b/meta/Makefile
2b/src/Makefile
2b/src/buttons/Makefile
2b/src/epg/Makefile
2b/src/fonts/Makefile
2b/src/icons/Makefile
2b/src/line/Makefile
2b/src/sel/Makefile
2b/src/skin_default/Makefile
2b/src/skin_default/buttons/Makefile
2b/src/skin_default/icons/Makefile

neutronhd/Makefile
neutronhd/meta/Makefile
neutronhd/po/Makefile
neutronhd/src_plugin/Makefile
neutronhd/src_skin/Makefile
neutronhd/src_skin/buttons/Makefile
neutronhd/src_skin/epg/Makefile
neutronhd/src_skin/fonts/Makefile
neutronhd/src_skin/icons/Makefile
neutronhd/src_skin/menu/Makefile
neutronhd/src_skin/pixmap/Makefile
neutronhd/src_skin/starsbar/Makefile
neutronhd/src_skin/style/Makefile

sd/Makefile
sd/meta/Makefile
sd/src/Makefile
sd/src/bs1/Makefile
sd/src/buttons/Makefile
sd/src/icons/Makefile
sd/src/menu/Makefile
sd/src/skin_default/Makefile
sd/src/skin_default/buttons/Makefile
sd/src/skin_default/icons/Makefile
sd/src/skin_default/menu/Makefile
sd/src/skin_default/spinner/Makefile
sd/src_conv/Makefile
sd/src_rend/Makefile

technohd/Makefile
technohd/meta/Makefile
technohd/po/Makefile
technohd/src_plugin/Makefile
technohd/src_skin/Makefile
technohd/src_skin/buttons/Makefile
technohd/src_skin/epg/Makefile
technohd/src_skin/fonts/Makefile
technohd/src_skin/icons/Makefile
technohd/src_skin/menu/Makefile
technohd/src_skin/style/Makefile

])
AC_OUTPUT
