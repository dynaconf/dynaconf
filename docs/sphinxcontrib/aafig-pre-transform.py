# -*- coding: utf-8 -*-
"""
    sphinxcontrib.aafig
    ~~~~~~~~~~~~~~~~~~~

    Allow embeded ASCII art to be rendered as nice looking images
    using the aafigure reStructuredText extension.

    See the README file for details.

    :copyright: Copyright 2009 by Leandro Lucarella <llucax@gmail.com> \
        (based on sphinxcontrib.mscgen).
    :license: BSD, see LICENSE for details.
"""

import posixpath
from os import path
try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

from docutils import nodes
from docutils.parsers.rst import directives

from sphinx.errors import SphinxError
from sphinx.util import ensuredir
from sphinx.util.compat import Directive

import aafigure


def merge_defaults(options, visitor):
    # merge default options
    for (k, v) in visitor.builder.config.aafig_default_options.items():
        if k not in options:
            options[k] = v
    return options


def get_basename(text, options, prefix='aafig'):
    options = options.copy()
    if 'format' in options:
        del options['format']
    hashkey = text.encode('utf-8') + str(options)
    id = sha(hashkey).hexdigest()
    return '%s-%s' % (prefix, id)


class AafigError(SphinxError):
    category = 'aafig error'


class aafig(nodes.General, nodes.Element):
    pass


class Aafig(directives.images.Image):
    """
    Directive to insert an ASCII art figure to be rendered by aafigure.
    """
    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    own_option_spec = dict(
        line_width   = float,
        background   = str,
        foreground   = str,
        fill         = str,
        aspect       = float,
        textual      = directives.flag,
        proportional = directives.flag,
    )
    option_spec = directives.images.Image.option_spec.copy()
    option_spec.update(own_option_spec)

    def run(self):
        text = '\n'.join(self.content)
        aafig_options = dict()
        image_attrs = dict()
        own_options_keys = self.own_option_spec.keys() + ['scale']
        for (k, v) in self.options.items():
            if k in own_options_keys:
                # convert flags to booleans
                if v is None:
                    v = True
                # convert percentage to float
                if k == 'scale':
                    v = float(v) / 100
                aafig_options[k] = v
                del self.options[k]
        # TODO/FIXME: en realidad los atributos de la imagen tienen que estar
        # en self.options, porque le estamos pasando self!
        self.arguments = [get_basename(text, aafig_options)]
        (image_node,) = directives.images.Image.run(self)
        if isinstance(image_node, nodes.system_message):
            return [image_node]
        aafig_node = aafig(text, image_node, **dict(options=aafig_options))
        return [aafig_node]


def render_aafigure(self, text, options):
    """
    Render an ASCII art figure into the requested format output file.
    """

    fname = get_basename(text, options)
    #fname = '%s.%s' % (get_basename(text, options), options['format'])
    if hasattr(self.builder, 'imgpath'):
        # HTML
        relfn = posixpath.join(self.builder.imgpath, fname)
        outfn = path.join(self.builder.outdir, '_images', fname)
    else:
        # LaTeX
        relfn = fname
        outfn = path.join(self.builder.outdir, fname)
    metadata_fname = '%s.aafig' % outfn

    try:
        if path.isfile(outfn):
            extra = None
            if options['format'].lower() == 'svg':
                f = None
                try:
                    try:
                        f = file(metadata_fname, 'r')
                        extra = f.read()
                    except:
                        raise AafigError()
                finally:
                    if f is not None:
                        f.close()
            return relfn, outfn, id, extra
    except AafigError:
        pass

    ensuredir(path.dirname(outfn))

    try:
        (visitor, output) = aafigure.render(text, outfn, options)
	output.close()
    except aafigure.UnsupportedFormatError, e:
        raise AafigError(str(e))

    extra = None
    if options['format'].lower() == 'svg':
        extra = visitor.get_size_attrs()
        f = file(metadata_fname, 'w')
        f.write(extra)
        f.close()

    return relfn, outfn, id, extra


def render_html(self, node, text, options, imgcls=None):
    try:
        options['format'] = self.builder.config.aafig_format['html']
        fname, outfn, id, extra = render_aafigure(self, text, options)
    except AafigError, exc:
        self.builder.warn('aafigure error: ' + str(exc))
        raise nodes.SkipNode

    self.body.append(self.starttag(node, 'p', CLASS='aafigure'))
    if fname is None:
        self.body.append(self.encode(text))
    else:
        imgcss = imgcls and 'class="%s"' % imgcls or ''
        if options['format'].lower() == 'svg':
            self.body.append('<object type="image/svg+xml" data="%s" %s %s />'
                    % (fname, extra, imgcss))
        else:
            self.body.append('<img src="%s" alt="%s" %s/>\n' %
                    (fname, self.encode(text).strip(), imgcss))
    self.body.append('</p>\n')
    raise nodes.SkipNode

def html_visit(self, node):
    #print node.attributes
    #merge_defaults(node['options'], self)
    #render_html(self, node, node['text'], node['options'])
    #return
    options = node['options'].copy()
    #merge_defaults(options, self)
    try:
        options['format'] = self.builder.config.aafig_format['html']
        fname, outfn, id, extra = render_aafigure(self, node.rawsource, options)
    except AafigError, exc:
        self.builder.warn('aafigure error: ' + str(exc))
        raise nodes.SkipNode
    image_node = node[0]
    image_node['src'] = fname # FIXME: no lo está tomando =/
    # TODO: improve image_node['alt']

def html_depart(self, node):
    pass

def render_latex(self, node, text, options):
    try:
        options['format'] = self.builder.config.aafig_format['latex']
        fname, outfn, id, extra = render_aafigure(self, text, options)
    except AafigError, exc:
        self.builder.warn('aafigure error: ' + str(exc))
        raise nodes.SkipNode

    if fname is not None:
        self.body.append('\\includegraphics[]{%s}' % fname)
    raise nodes.SkipNode


def latex_visit(self, node):
    raise nodes.SkipNode
    merge_defaults(node['options'], self)
    render_latex(self, node, node['text'], node['options'])


def setup(app):
    app.add_node(aafig, html=(html_visit, html_depart), latex=(latex_visit, None))
    app.add_directive('aafig', Aafig)
    app.add_config_value('aafig_format', dict(html='svg', latex='pdf'), 'html')
    app.add_config_value('aafig_default_options', dict(), 'html')

