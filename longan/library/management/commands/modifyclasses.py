from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Modify model classes'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str, help="Name of file to process")
        parser.add_argument('--prefix', nargs='?', action='store', help="string to prefix to class name")
        parser.add_argument('--singularize', action='store_true', default=False, help="Convert names to singular")

    def handle(self, *args, **options):

        filename = options['filename'].pop(0)
        prefix = options.get('prefix', '')

        with open(filename) as fileobj:
            source = fileobj.read()

        source = self.modify(source, prefix=prefix, singularize=options['singularize'])

        self.stdout.write(source)

    def modify(self, source, prefix=None, singularize=False):

        import ast

        # import astunparse

        module = ast.parse(source)

        class_names = []

        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)

        # source = astunparse.unparse(module)

        # TODO: make changes via ast
        lines = []
        for line in source.split('\n'):

            for class_name in class_names:
                if any(expr in line for expr in [
                        'class %s' % class_name,
                        '\'%s\'' % class_name,
                        '(%s,' % class_name,
                        '(%s)' % class_name,                        
                ]):

                    if prefix is not None:
                        line = line.replace(class_name, prefix + class_name)
                        class_name = prefix + class_name

                    if singularize:
                        if class_name.endswith('s'):
                            line = line.replace(class_name, class_name[:-1])

            lines.append(line)

        return '\n'.join(lines)

    def apply_singularize(self, source):
        lines = []

        for line in source.split('\n'):

            if line.startswith('class'):

                _, string = line.split(' ', 1)
                class_name = string[:string.index('(')]

                if class_name.endswith('s'):
                    class_name = class_name[:-1]
                
                    line = 'class %s%s' % (class_name, string[string.index('('):])

            lines.append(line)

        return '\n'.join(lines)
