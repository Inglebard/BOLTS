#!/usr/bin/env python
#BOLTS - Open Library of Technical Specifications
#Copyright (C) 2013 Johannes Reinhardt <jreinhardt@ist-dein-freund.de>
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Lesser General Public
#License as published by the Free Software Foundation; either
#version 2.1 of the License, or any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#Lesser General Public License for more details.
#
#You should have received a copy of the GNU Lesser General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

from bolttools.blt import BOLTSRepository
from bolttools.freecad import FreeCADData
from bolttools.openscad import OpenSCADData
from bolttools.drawings import DrawingsData
from bolttools.solidworks import SolidWorksData

from backends.license import LICENSES_SHORT

from os import getcwd
from shutil import make_archive, copyfile
import os.path
from subprocess import call, Popen
import argparse
from datetime import datetime


def export(args):
	#load data
	repo = BOLTSRepository(args.repo)
	openscad = OpenSCADData(args.repo)
	freecad = FreeCADData(args.repo)
	drawings = DrawingsData(args.repo)
	solidworks = SolidWorksData(args.repo)

	license = LICENSES_SHORT[args.license]

	out_path = os.path.join(repo.path,"output",args.target)
	if args.target == "openscad":
		from backends.openscad import OpenSCADExporter
		OpenSCADExporter(repo,openscad).write_output(out_path,license)
		copyfile(os.path.join(repo.path,"backends","licenses",args.license.strip("+")),
			os.path.join(out_path,"LICENSE"))
	elif args.target == "freecad":
		from backends.freecad import FreeCADExporter
		FreeCADExporter(repo,freecad).write_output(out_path,license)
		copyfile(os.path.join(repo.path,"backends","licenses",args.license.strip("+")),
			os.path.join(out_path,"BOLTS","LICENSE"))
	elif args.target == "html":
		from backends.html import HTMLExporter
		HTMLExporter(repo,freecad,openscad,drawings).write_output(out_path)
	elif args.target == "solidworks":
		from backends.solidworks import SolidWorksExporter
		SolidWorksExporter(repo,solidworks).write_output(out_path)

def test(args):
	exec_dir = os.path.join(args.repo,"output",args.target)
	if args.target == "freecad":
		freecad_process = Popen(["freecad","-M","."],cwd=exec_dir)
		freecad_process.wait()
	elif args.target == "openscad":
		freecad_process = Popen(["openscad"],cwd=exec_dir)
		freecad_process.wait()
#
#def release(args):
#	#check that there are no uncommited changes
#	if call(["git","diff","--exit-code","--quiet"]) == 1:
#		print "There are uncommited changes present in the git repository. Please take care of them before releasing"
#		exit(1)
#
#	if args.kind == "stable" and args.version is None:
#		print "Please specify a version using -v when releasing a stable version"
#		exit(2)
#	if args.kind == "development" and not args.version is None:
#		print "No explicit version can be given for development releases"
#		exit(2)
#	repo = blt_parser.BOLTSRepository(args.repo)
#
#	#export
#	html.HTMLExporter().write_output(repo)
#	for li_short in ["lgpl2.1+","gpl3"]:
#		license = LICENSES_SHORT[li_short]
#		openscad.OpenSCADExporter().write_output(repo,license)
#		copyfile(os.path.join(repo.path,"licenses",li_short.strip("+")),
#			os.path.join(repo.path,"output","openscad","LICENSE"))
#		freecad.FreeCADExporter().write_output(repo,license)
#		copyfile(os.path.join(repo.path,"licenses",li_short.strip("+")),
#			os.path.join(repo.path,"output","freecad","BOLTS","LICENSE"))
#
#		for backend,backend_name in zip(["freecad","openscad"],["FreeCAD","OpenSCAD"]):
#			#construct filename from date
#			if args.kind == "development":
#				date = datetime.now().strftime("%Y%m%d%H%M")
#				template = "BOLTS_%s_%s_%s" % (backend_name,date,li_short)
#			elif args.kind == "stable":
#				template = "BOLTS_%s_%s_%s" % (backend_name,args.version,li_short)
#
#			#create archives
#			root_dir = os.path.join(repo.path,"output",backend)
#			base_name = os.path.join(repo.downloads.out_root,"downloads",backend,template)
#			make_archive(base_name,"gztar",root_dir)
#			make_archive(base_name,"zip",root_dir)
#
#	#write html overview
#	downloads.DownloadsExporter().write_output(repo)


parser = argparse.ArgumentParser()
parser.add_argument("--repo",
	type=str,
	help="path of the BOLTS repository to work on",
	default=getcwd())

subparsers = parser.add_subparsers()
parser_export = subparsers.add_parser("export")
parser_export.add_argument("target",
	type=str,
	choices=["openscad","freecad","html","downloads","solidworks"],
	help="the distribution to create")
parser_export.add_argument("-l","--license",
	type=str,
	choices=["lgpl2.1","lgpl2.1+","lgpl3","lgpl3+","gpl3","gpl3+"],
	default="lgpl2.1",
	help="the license of the exported license")
parser_export.set_defaults(func=export)

parser_test = subparsers.add_parser("test")
parser_test.add_argument("target",
	type=str,
	choices=["openscad","freecad"],
	help="the backend to test")
parser_test.set_defaults(func=test)

#parser_release = subparsers.add_parser("release")
#parser_release.set_defaults(func=release)
#parser_release.add_argument("kind",
#	type=str,
#	choices=["development","stable"],
#	help="whether to create a development snapshot or a official relase",
#	default="development")
#parser_release.add_argument("-v","--version",type=str)


args = parser.parse_args()
args.func(args)
