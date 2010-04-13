###############################################################################
# Recurse dictionary template tag for Django v1.1
# Copyright (C) 2008 Lucas Murray, (C) 2010 Stefan Praszalowicz
# http://www.undefinedfire.com 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
###############################################################################

from django import template

register = template.Library()

class RecurseDictNode(template.Node):
    def __init__(self, var, nodeList):
        self.var = var
        self.nodeList = nodeList

    def __repr__(self):
        return '<RecurseDictNode>'

    def renderCallback(self, context, vals, level):
        if len(vals) == 0:
            return ''

        output = []

        if 'loop' in self.nodeList:
            output.append(self.nodeList['loop'].render(context))

        for k, v in vals:
            context.push()
            
            context['level'] = level
            context['key'] = k
            
            if 'value' in self.nodeList:
                output.append(self.nodeList['value'].render(context))
                
                if type(v) == list or type(v) == tuple:
                    child_items = [ (None, x) for x in v ]
                    output.append(self.renderCallback(context, child_items, level + 1))
                else:
                    try:
                        child_items = v.items()
                        output.append(self.renderCallback(context, child_items, level + 1))
                    except:
                        output.append(unicode(v))
            
            if 'endloop' in self.nodeList:
                output.append(self.nodeList['endloop'].render(context))
            else:
                output.append(self.nodeList['endrecursedict'].render(context))
            
            context.pop()

        if 'endloop' in self.nodeList:
            output.append(self.nodeList['endrecursedict'].render(context))

        return ''.join(output)

    def render(self, context):
        vals = self.var.resolve(context).items()
        output = self.renderCallback(context, vals, 1)
        return output

def recursedict_tag(parser, token):
    bits = list(token.split_contents())
    if len(bits) != 2 and bits[0] != 'recursedict':
        raise template.TemplateSyntaxError, "Invalid tag syxtax expected '{% recursedict [dictVar] %}'"

    var = parser.compile_filter(bits[1])
    nodeList = {}
    while len(nodeList) < 4:
        temp = parser.parse(('value','loop','endloop','endrecursedict'))
        tag = parser.tokens[0].contents
        nodeList[tag] = temp
        parser.delete_first_token()
        if tag == 'endrecursedict':
            break

    return RecurseDictNode(var, nodeList)

recursedict_tag = register.tag('recursedict', recursedict_tag)