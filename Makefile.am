ACLOCAL_AMFLAGS = -I m4

SUBDIRS = \
	2b \
	neutronhd \
	technohd

metadir = $(datadir)/meta
meta_DATA = index-enigma2-skins.xml
CLEANFILES = index-enigma2-skins.xml

index-enigma2-skins.xml: $(top_srcdir)/genmetaindex.py $(top_srcdir)/*/meta/skin_*.xml
	$(AM_V_GEN)$(PYTHON) $^ > $@
