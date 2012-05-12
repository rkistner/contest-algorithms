#!/usr/bin/env python2
#
# Copyright 2012 Ralf Kistner
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



#
# Usage:
#   ./test.py <source file> <input files>
# 
# Important: use quotes around the input files to allow new files to be detected automatically (see examples).
#
# Examples:
#   ./test.py a.py "a*.in"
# Shorter version of the above:
#   ./test.py a.py
# Java:
#   ./test.py a.java
# Only small input:
#   ./test.py a.java "A-small*.in"
#
# Dependencies:
#   Linux, Python 2.6 or 2.7, Pyinotify
#
# Adapted from https://github.com/seb-m/pyinotify/blob/master/python2/examples/autocompile.py
from __future__ import print_function

import subprocess
import sys, os
import pyinotify
from glob import glob
import fnmatch
import hashlib
import time
import shutil

def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.digest()
    
class OnWriteHandler(pyinotify.ProcessEvent):
    def my_init(self, app, input_files, inout):
        self.input_files = input_files
        self.app = app
        self.hashes = {}
        self.inout = inout
        self.name = app[:app.rindex('.')]

    def run(self, path):
        if not path.endswith(".in"):
            return
        run_path = path.replace(".in", ".run")
        expected_path = path.replace(".in", ".out")
        start = time.time()
        if not self.inout:
            infile = file(path, 'r')
            outfile = file(run_path, 'w')
            print("==> Testing input file %s..." % path)
            self.run_app(infile, outfile)
            infile.close()
            outfile.close()
        else:
            if path == self.name + ".in":
                return
            print("==> Testing input file %s..." % path)
            run_path = self.name + ".out"
            shutil.copyfile(path, self.name + ".in")
            self.run_app()
        
        
        end = time.time()
        tdiff = end - start

        print("==> Output vs expected output")
        run_output = file(run_path, 'r').readlines()
        try:
            expected_output = file(expected_path, 'r').readlines()
        except:
            expected_output = []
        N = max(len(run_output), len(expected_output))
        diff = False
        for i in range(N):
            if i < len(run_output):
                r = run_output[i].strip()
            else:
                r = ""
            if i < len(expected_output):
                e = expected_output[i].strip()
            else:
                e = ""
            if r == e:
                print("%2d:   %s" % (i + 1, r))
            else:
                diff = True
                print("%2d: ! %s ! %s !" % (i + 1, r, e))

        #subprocess.call(['diff', '-y', '-b', '-N', run_path, expected_path])
        
        if diff:
            print("Invalid output")
        else:
            print("Output matched")
        print("==> %.3fs ------------- %s ----------------" % (tdiff, path))

    def compile(self):
        if self.app.endswith(".java"):
            return subprocess.call(['javac', self.app])
        if self.app.endswith(".scala"):
            return subprocess.call(['scalac', self.app])
        return 0
    
    def run_app(self, stdin=None, stdout=None):
        if self.app.endswith(".py"):
            subprocess.call(['python', self.app], stdin=stdin, stdout=stdout)
        elif self.app.endswith(".java"):
            klass = self.app.replace(".java", "")
            subprocess.call(['java', klass], stdin=stdin, stdout=stdout)
        elif self.app.endswith(".scala"):
            klass = self.app.replace(".scala", "")
            subprocess.call(['scala', klass], stdin=stdin, stdout=stdout)
        else:
            print("Don't know how to run %s" % self.app)

    def run_all(self):
        result = self.compile()
        if result != 0:
            print("Compile failed with exit code %d" % result)
            return
            
        for g in self.input_files:
            files = glob(g)
            for f in files:
                self.run(f)
    
    def is_modified(self, path):
        # The following lines check the hash of the input file. This prevents double updates.
        f = open(path, 'rb')
        md5 = md5_for_file(f)
        f.close()
        if path in self.hashes and self.hashes[path] == md5:
            return False
        else:
            self.hashes[path] = md5
            return True
            
    def updated(self, path):
        cwd = os.getcwd() + "/"
        short_path = path.replace(cwd, '')
        if short_path == self.app:
            if self.is_modified(path):
                print('==> Source code modified for %s' % path)
                self.run_all()
        else:
            for g in self.input_files:
                if fnmatch.fnmatch(short_path, g):
                    if self.is_modified(path):
                        self.run(short_path)
                    
    def process_IN_CLOSE_WRITE(self, event):
        self.updated(event.pathname)
        
    
    def process_IN_MOVED_TO(self, event):
        self.updated(event.pathname)
            

def auto_compile(path, input_files, inout):
    wm = pyinotify.WatchManager()
    handler = OnWriteHandler(app=path, input_files=input_files, inout=inout)
    handler.run_all()
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(path, pyinotify.ALL_EVENTS, rec=False, auto_add=False)
    wm.add_watch('.', pyinotify.ALL_EVENTS, rec=True, auto_add=True)
    print('==> Start monitoring %s, %s (type c^c to exit)' % (path, input_files))
    notifier.loop()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s <source file> <input files>" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    # Required arguments
    path = sys.argv[1]
    input_files = sys.argv[2:]
    inout = False
    if input_files and input_files[0] == '-f':
        input_files = input_files[1:]
        inout = True
    if not input_files:
        base = path[:path.find('.')]
        input_files = ["%s*.in" % base]
        
    # Blocks monitoring
    auto_compile(path, input_files, inout)
