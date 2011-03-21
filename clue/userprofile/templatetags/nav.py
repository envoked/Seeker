from django.template import Library, Node, Variable
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse

register = Library()

class NavUrlNode(Node):

    def __init__(self, *args):
        self.name_var = Variable(args[0])
        self.args=[]
        for ii in range(1,args.__len__()):
            self.args.append(Variable(args[ii]))

    def render(self, context):
        name = self.name_var.resolve(context)
        print name
        args=[]
        for ii in range(self.args.__len__()):
            args.append(self.args[ii].resolve('profile_edit_' + context))
        return reverse('profile_edit_' + name, args=args)


@register.tag
def nav_url(parser, token):
    args = token.split_contents()
    return NavUrlNode(*args[1:])