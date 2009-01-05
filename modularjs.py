#!/usr/bin/env python

from __future__ import with_statement

import sys
import os
import os.path
import subprocess
import shutil
import re
from optparse import OptionParser


LOADED = {}

def help():
    global parser
    print parser.format_help()
    exit(1)


def main():
    global parser
    name = sys.argv[0]
    usage = """\t%s init
\t%s build MODULE_NAME_1 [MODULE_NAME_1 ...] [-o OUTPUT_BASE_NAME]""" % (name, name)
    parser = OptionParser(usage=usage, version="%prog 0.1")
    parser.add_option("-o", "--output", dest="output",
                      help="Save output to OUTPUT_BASE_NAME", metavar="OUTPUT_BASE_NAME")
    options, input_modules = parser.parse_args()

    argc = len(sys.argv)

    if argc < 2:
        help()

    command = input_modules[0]
    input_modules = input_modules[1:]

    dirname = os.path.dirname(__file__)    

    if command == 'init':
        print 'Initializing...'
        filename = os.path.join(dirname, 'include.js')
        shutil.copy(filename, '.')
        print 'Done, file %s copied to current directory' % filename

    elif command == 'build':
        output_basename = options.output or '%s.build' % input_modules[0]
    
        with open('%s.js' % output_basename, 'w') as output:
            include("include", output)
            for input_module in input_modules:
                include(input_module, output)
    
        with open('%s.compressed.js' % output_basename, 'w') as output:
            jar = os.path.join(dirname, 'lib', 'yuicompressor-2.4.2.jar')
            p = subprocess.Popen(['java', '-jar', jar,
                                  '%s.js' % output_basename], stdout=output)

    else:
        help()


_INCLUDE_REGEX = re.compile(r"""^(\s*)include\(['"](.*)['"]\);$""")

def include(module, output, indent=""):
    """ Process one module and writes to output """

    if module in LOADED:
        return

    for line in open(filename(module)).readlines():
        include_module = _INCLUDE_REGEX.match(line)

        if include_module:
            include(include_module.group(2), output, indent + include_module.group(1))
        else:
            output.write(indent + line)

    output.write('\nmodularjs.loaded["%s"] = true;\n\n' % module)
    LOADED[module] = True
    print "Module %s loaded" % module


def filename(module):
    """
    This function should be equivalent to the javascript function modularjs.filename
    """

    return module.replace('.', os.sep) + '.js'


if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass

    main()