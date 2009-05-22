from __future__ import with_statement

import logging
import re
import os
import os.path
import subprocess
from pkg_resources import get_distribution, ResourceManager

_INCLUDE_REGEX = re.compile(r"""^(\s*)include\(['"](.*)['"]\);\r?$""")
LOADED = {}

modularjslogger = logging.getLogger('modularjs')

def build(output_basename, input_modules):
    """ Creates a build of javascript files """

    distribution = get_distribution('modularjs')

    with open('%s.js' % output_basename, 'w') as output:
        output.write('var __build__ = true;\n');
        include('include', output)
        for input_module in input_modules:
            include(input_module, output)
        output.write('\nmodularjs.init();');

    modularjslogger.info('Wrote %s.js' % output_basename)

    with open('%s.compressed.js' % output_basename, 'w') as output:
        yui = os.path.join('lib', 'yuicompressor-2.4.2.jar')
        jar = distribution.get_resource_filename(ResourceManager(), yui)
        p = subprocess.Popen(['java', '-jar', jar,
                              '%s.js' % output_basename], stdout=output)

    modularjslogger.info('Wrote %s.compressed.js' % output_basename)


def include(module, output, indent=""):
    """ Process one module and writes to output """

    if module in LOADED:
        return

    try:
        lines = open(filename(module)).readlines()
    except IOError, e:
        modularjslogger.warning('Module %s not loaded: %s' % (module, e))
        return

    for line in open(filename(module)).readlines():
        include_module = _INCLUDE_REGEX.match(line)

        if include_module:
            include(include_module.group(2), output, indent + include_module.group(1))
        else:
            output.write(indent + line)

    output.write('\nmodularjs.loaded["%s"] = true;\n\n' % module)
    LOADED[module] = True
    modularjslogger.info('Module %s loaded' % module)


def filename(module):
    """
    This function should be equivalent to the javascript function modularjs.filename
    """

    return module.replace('.', os.sep) + '.js'



