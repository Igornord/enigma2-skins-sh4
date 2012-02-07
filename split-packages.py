#!/usr/bin/env python2

#install DEST_DIR
global pkgs_dir
pkgs_dir = ''

#where this script will build packages
global build_dir
build_dir = ''

bb_data = {}

def bb_set(var, val, *args):
	bb_data[var] = val

def bb_get(var, *args):
	try:
		return bb_data[var]
	except KeyError:
		return ""
		
import os
from shutil import copyfile
import bb

# bitbake/portage copyrighted (c)
def install_files(files, root):
	import glob, errno, re,os
	
	for file in files:
		if os.path.isabs(file):
			file = '.' + file
		if not os.path.islink(file):
			if os.path.isdir(file):
				newfiles =  [ os.path.join(file,x) for x in os.listdir(file) ]
				if newfiles:
					files += newfiles
					continue
		globbed = glob.glob(file)
		if globbed:
			if [ file ] != globbed:
				if not file in globbed:
					files += globbed
					continue
				else:
					globbed.remove(file)
					files += globbed
		if (not os.path.islink(file)) and (not os.path.exists(file)):
			continue
		if file[-4:] == '.pyc':
			continue
		if file in seen:
			continue
		seen.append(file)
		if os.path.isdir(file) and not os.path.islink(file):
			bb.mkdirhier(os.path.join(root,file))
			os.chmod(os.path.join(root,file), os.stat(file).st_mode)
			continue
		fpath = os.path.join(root,file)
		dpath = os.path.dirname(fpath)
		bb.mkdirhier(dpath)
		ret = bb.copyfile(file, fpath)
		if ret is False:
			raise("File population failed when copying %s to %s" % (file, fpath))

#Copied from bitbake (c)
#######################################################################
#######################################################################

def legitimize_package_name(s):
	"""
	Make sure package names are legitimate strings
	"""
	import re

	def fixutf(m):
		cp = m.group(1)
		if cp:
			return ('\u%s' % cp).decode('unicode_escape').encode('utf-8')

	# Handle unicode codepoints encoded as <U0123>, as in glibc locale files.
	s = re.sub('<U([0-9A-Fa-f]{1,4})>', fixutf, s)

	# Remaining package name validity fixes
	return s.lower().replace('_', '-').replace('@', '+').replace(',', '+').replace('/', '-')

def do_split_packages(d, root, file_regex, output_pattern, description, postinst=None, recursive=False, hook=None, extra_depends=None, aux_files_pattern=None, postrm=None, allow_dirs=False, prepend=False, match_path=False, aux_files_pattern_verbatim=None, allow_links=False):
	"""
	Used in .bb files to split up dynamically generated subpackages of a 
	given package, usually plugins or modules.
	"""

	dvar = pkgs_dir

	packages = []

	if not recursive:
		objs = os.listdir(dvar + root)
	else:
		objs = []
		for walkroot, dirs, files in os.walk(dvar + root):
			for file in files:
				relpath = os.path.join(walkroot, file).replace(dvar + root + '/', '', 1)
				if relpath:
					objs.append(relpath)
					
	for o in objs:
		import re, stat
		if match_path:
			m = re.match(file_regex, o)
		else:
			m = re.match(file_regex, os.path.basename(o))
		
		if not m:
			continue
		f = os.path.join(dvar + root, o)
		mode = os.lstat(f).st_mode
		if not (stat.S_ISREG(mode) or (allow_links and stat.S_ISLNK(mode)) or (allow_dirs and stat.S_ISDIR(mode))):
			continue
		on = legitimize_package_name(m.group(1))
		pkg = output_pattern % on
		if not pkg in packages:
			if prepend:
				packages = [pkg] + packages
			else:
				packages.append(pkg)
			the_files = [os.path.join(root, o)]
			if aux_files_pattern:
				if type(aux_files_pattern) is list:
					for fp in aux_files_pattern:
						the_files.append(fp % on)	
				else:
					the_files.append(aux_files_pattern % on)
			if aux_files_pattern_verbatim:
				if type(aux_files_pattern_verbatim) is list:
					for fp in aux_files_pattern_verbatim:
						the_files.append(fp % m.group(1))	
				else:
					the_files.append(aux_files_pattern_verbatim % m.group(1))
			
			bb_set('FILES_' + pkg, " ".join(the_files))
			
			if extra_depends != '':
				the_depends = bb_get('RDEPENDS_' + pkg, d, True)
				if the_depends:
					the_depends = '%s %s' % (the_depends, extra_depends)
				else:
					the_depends = extra_depends
				
				bb_set('RDEPENDS_' + pkg, the_depends, d)
			
			bb_set('DESCRIPTION_' + pkg, description % on, d)
			
			if postinst:
				bb_set('pkg_postinst_' + pkg, postinst, d)
			if postrm:
				bb_set('pkg_postrm_' + pkg, postrm, d)
		else:			
			oldfiles = bb_get('FILES_' + pkg, d, True)			
			if not oldfiles:
				raise("Package '%s' exists but has no files" % pkg)
			bb_set('FILES_' + pkg, oldfiles + " " + os.path.join(root, o), d)
		
		if callable(hook):
			hook(f, pkg, file_regex, output_pattern, m.group(1))

	bb_set('PACKAGES', ' '.join(packages), d)

#End of bitbake code
#######################################################################
#######################################################################

#Use tricky files staff from bitbake(portage based), it is usefull.
#But keep packaging simple

DATAS = [
	'PKGV',
	'PKGR',
	'DESCRIPTION',
	'SECTION',
	'PRIORITY',
	'MAINTAINER',
	'LICENSE',
	'PACKAGE_ARCH',
	'HOMEPAGE',
	'RDEPENDS',
	'RREPLACES',
	'RCONFLICTS',
	'SRC_URI']

def read_control_file(fname):
	src = open(fname).read()
	for line in src.split("\n"):
		if line.startswith('Package: '):
			full_package = line[9:]
		if line.startswith('Depends: '):
			bb_set('RDEPENDS_' + full_package, ' '.join(line[9:].split(', ')))
		if line.startswith('Description: '):
			bb_set('DESCRIPTION_' + full_package, line[13:])
		if line.startswith('Replaces: '):
			bb_set('RREPLACES_' + full_package, ' '.join(line[10:].split(', ')))
		if line.startswith('Conflicts: '):
			bb_set('RCONFLICTS_' + full_package, ' '.join(line[11:].split(', ')))
		if line.startswith('Maintainer: '):
			bb_set('MAINTAINER_' + full_package, line[12:])
		if line.startswith('Version: '):
			bb_set('PKGV_' + full_package, line[9:].split('-')[0])
			bb_set('PKGR_' + full_package, line[9:].split('-')[1])
		if line.startswith('Section: '):
			bb_set('SECTION_' + full_package, line[9:])
		if line.startswith('Priority: '):
			bb_set('PRIORITY_' + full_package, line[10:])
		if line.startswith('License: '):
			bb_set('LICENSE_' + full_package, line[9:])
		if line.startswith('Architecture: '):
			bb_set('PACKAGE_ARCH_' + full_package, line[14:])
		if line.startswith('Homepage: '):
			bb_set('HOMEPAGE_' + full_package, line[10:])
		if line.startswith('Source: '):
			bb_set('SRC_URI_' + full_package, line[8:])
	return full_package

def write_control_file(fname, full_package):
	s = "Package: %s\n" % full_package
	p = []
	p.append(["Version: %s-%s\n", ['PKGV', 'PKGR']])
	p.append(["Description: %s\n", ['DESCRIPTION']])
	p.append(["Section: %s\n", ['SECTION']])
	p.append(["Priority: %s\n", ['PRIORITY']])
	p.append(["Maintainer: %s\n", ['MAINTAINER']])
	p.append(["License: %s\n", ['LICENSE']])
	p.append(["Architecture: %s\n", ['PACKAGE_ARCH']])
	p.append(["Homepage: %s\n", ['HOMEPAGE']])
	p.append(["Depends: %s\n", ['RDEPENDS']])
	p.append(["Replaces: %s\n", ['RREPLACES']])
	p.append(["Conflicts: %s\n", ['RCONFLICTS']])
	p.append(["Source: %s\n", ['SRC_URI']])
	
	for l in p:
		def ext(param):
			return "%s_%s" % (param, full_package)
		var = map(bb_get, map(ext, l[1]))
		chck = 0
		for param in var:
			if not param:
				chck = 1
				break
		if chck: continue
		var = l[0] % tuple(var)
		s += var
	print 'Write control file to', fname
	open(fname, 'w').write(s)

def pjoin(*args):
	#TODO: make it more clean. remove '/' dublicates. Do it with re, it would be faster..
	return '/'.join(args)

if __name__ == "__main__":
	pkgs_dir = '/home/tech/tdt-amiko/tdt/tufsbox/ipk/'
	build_dir = '/home/tech/build_dir/'
	
	work_dir = os.getcwd()
	print "Building in", work_dir
	
	bb.mkdirhier(build_dir)
	
	enigma2_skindir = '/usr/local/share/enigma2'
	do_split_packages(bb_data, enigma2_skindir, '(.*?)/.*', 'enigma2-skin-%s', 'Enigma2 Skin: %s', recursive=True, match_path=True, prepend=True)
	
	os.chdir(pkgs_dir)
	
	global seen
	seen = []
	
	parent_pkg = read_control_file(pjoin(work_dir, 'CONTROL'))
	
	for p in bb_data['PACKAGES'].split(" "):
		print "Package: ", p
		print "Description: ", bb_data['DESCRIPTION_'+p]
		files = bb_data['FILES_'+p].split(" ")
		
		pack_dir = pjoin(build_dir,p)
		if not os.path.exists(pack_dir):
			os.mkdir(pack_dir)
		
		install_files(files, pack_dir)
		
		for data in DATAS:
			if not bb_get(data+'_'+p):
				bb_set(data+'_'+p, bb_get(data+'_'+parent_pkg))
		
		bb.mkdirhier(pjoin(pack_dir, 'CONTROL'))
		write_control_file(pjoin(pack_dir, 'CONTROL', 'control'), p)