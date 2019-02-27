#!/usr/bin/env python
#
# Copyright (c) 2014 Krzysztof Jusiak (krzysztof at jusiak dot net)
#
# Distributed under the Boost Software License, Version 1.0.
# (See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#
import os
import sys
from optparse import OptionParser
from clang.cindex import Index
from clang.cindex import TranslationUnit
from clang.cindex import Cursor
from clang.cindex import CursorKind
from clang.cindex import Config
from clang.cindex import Diagnostic
from clang.cindex import AccessSpecifier
import datetime

time_stamp = int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

if sys.version_info < (3, 0):
    import __builtin__
    def str(object, unused = None):
        return __builtin__.str(object)

    def bytes(object, unused = None):
        return __builtin__.bytes(object)


class Class:
    def __init__(self, node):
        self.__node = node
        self.__file = str(node.location.file.name)
        self.__parent_classes = []
        self.__pure_virtual_methods = []
        self.__parse_parent_classes()
        self.__parse_pure_virtual_methods()
        self.__namespace = self.__parse_name_space()
        self.__name = str(self.__node.displayname)
    
    def __parse_parent_classes(self):
        for node in self.__node.get_children():
            if node.kind == CursorKind.CXX_BASE_SPECIFIER:
                for sub_node in node.get_children():
                    if sub_node.kind is CursorKind.TYPE_REF: 
                        self.__parent_classes.append(Class(sub_node.get_definition()))
    
    def __parse_pure_virtual_methods(self):
        for node in self.__node.get_children():
            if node.kind == CursorKind.CXX_METHOD and node.access_specifier == AccessSpecifier.PUBLIC:
                if node.is_pure_virtual_method():
                    self.__pure_virtual_methods.append(node)
            
    def get_all_pure_virtual_methods(self):
        result = []
        result.extend(self.__pure_virtual_methods)
        for c in self.__parent_classes:
            result.extend(c.get_all_pure_virtual_methods())
        return result
    
    def get_all_pure_virtual_methods_as_strings(self):
        result = []
        for m in self.get_all_pure_virtual_methods():
            result.append(str(m.displayname))
        return result
    
    def __parse_name_space(self):
        result = []
        node = self.__node.semantic_parent
        while node is not None:
            if node.kind in [CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL, CursorKind.NAMESPACE]:
                result.append(node.displayname)
            node = node.semantic_parent
        return list(reversed(result))
    
    def get_name_space(self):
        return "::".join(self.__namespace)
    
    def get_file_name(self):
        return self.__file
    
    def get_expr(self):
        name_space = self.get_name_space()
        if name_space != "":
            return name_space + "::" + self.__name
        else:
            return self.__name 
    
class MockClass:
    def __init__(self, _class):
        self.__class = _class
        self.__mock_methods = self.__generate_mock_methods()
    
    def __get_result_type(self, tokens, name):
        result_type = []
        for token in tokens:
            if token in [name, 'operator']:
                break
            if token not in ['virtual', 'inline', 'volatile']:
                result_type.append(token)
            if token in ['const', 'volatile']:
                result_type.append(' ')
        return ''.join(result_type)
        
    def __generate_mock_methods(self):
        result = []
        for method in self.__class.get_all_pure_virtual_methods():
            spelling = str(method.spelling)
            name = str(method.displayname)
            tokens = [str(token.spelling) for token in method.get_tokens()]
            result.append(
                mock_method(
                    self.__get_result_type(tokens, spelling),
                    spelling,
                    method.is_const_method(),
                    False, # not template class
                    len(list(method.get_arguments())),
                    name[len(method.spelling) + 1 : -1]
                ))
        return result
     
    def get_mock_methods(self):
        return self.__mock_methods
    
    def get_source_class(self):
        return self.__class


class ClassCollector:
    def __init__(self, file_name, clang_args):
        self.__file_name = os.path.abspath(file_name)
        self.__clang_args = clang_args
        self.encode = 'utf-8'
        self.expr = ''
        self.__classes = []
        self.__parse()
        
    def __recursive_parse(self, node):
        if node.kind in [CursorKind.CLASS_TEMPLATE, CursorKind.STRUCT_DECL, CursorKind.CLASS_DECL]:
            file = str(node.location.file.name, self.encode)
            if os.path.abspath(file) != self.__file_name:
                return
            self.__classes.append(Class(node=node))
        else:
            [self.__recursive_parse(c) for c in node.get_children()]
    
    def __parse(self):
        index = Index.create(excludeDecls = True).parse(
            path = self.__file_name
          , args = self.__clang_args
          , options = TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE
        )
        abort = False
        for d in index.diagnostics:
            print d
            if d.severity >= Diagnostic.Error:
                abort = True
        if abort:
            exit(1)
        self.__recursive_parse(index.cursor)
    
    def get_classes(self):
        return self.__classes                 


class mock_method:
    operators = {
        'operator,'   : 'comma_operator',
        'operator!'   : 'logical_not_operator',
        'operator!='  : 'inequality_operator',
        'operator%'   : 'modulus_operator',
        'operator%='  : 'modulus_assignment_operator',
        'operator&'   : 'address_of_or_bitwise_and_operator',
        'operator&&'  : 'logical_and_operator',
        'operator&='  : 'bitwise_and_assignment_operator',
        'operator()'  : 'function_call_or_cast_operator',
        'operator*'   : 'multiplication_or_dereference_operator',
        'operator*='  : 'multiplication_assignment_operator',
        'operator+'   : 'addition_or_unary_plus_operator',
        'operator++'  : 'increment1_operator',
        'operator+='  : 'addition_assignment_operator',
        'operator-'   : 'subtraction_or_unary_negation_operator',
        'operator--'  : 'decrement1_operator',
        'operator-='  : 'subtraction_assignment_operator',
        'operator->'  : 'member_selection_operator',
        'operator->*' : 'pointer_to_member_selection_operator',
        'operator/'   : 'division_operator',
        'operator/='  : 'division_assignment_operator',
        'operator<'   : 'less_than_operator',
        'operator<<'  : 'left_shift_operator',
        'operator<<=' : 'left_shift_assignment_operator',
        'operator<='  : 'less_than_or_equal_to_operator',
        'operator='   : 'assignment_operator',
        'operator=='  : 'equality_operator',
        'operator>'   : 'greater_than_operator',
        'operator>='  : 'greater_than_or_equal_to_operator',
        'operator>>'  : 'right_shift_operator',
        'operator>>=' : 'right_shift_assignment_operator',
        'operator[]'  : 'array_subscript_operator',
        'operator^'   : 'exclusive_or_operator',
        'operator^='  : 'exclusive_or_assignment_operator',
        'operator|'   : 'bitwise_inclusive_or_operator',
        'operator|='  : 'bitwise_inclusive_or_assignment_operator',
        'operator||'  : 'logical_or_operator',
        'operator~'   : 'complement_operator'
    }

    def __init__(self, result_type, name, is_const, is_template, args_size, args, args_prefix = 'arg'):
        self.result_type = result_type
        self.name = name
        self.is_const = is_const
        self.is_template = is_template
        self.args_size = args_size
        self.args = args
        self.args_prefix = args_prefix

    def __named_args(self):
        result = []
        for i in range(0, self.args_size):
            i and result.append(', ')
            result.append(self.args_prefix + str(i))
        return ''.join(result)

    def __named_args_with_types(self):
        if (self.args == ''):
            return ''
        result = []
        in_type = False
        i = 0
        for c in self.args:
            if c in ['<', '(']:
                in_type = True
            elif c in ['>', ')']:
                in_type = False
            if not in_type and c == ',':
                result.append(' ' + self.args_prefix + str(i))
                i+=1
            result.append(c)
        result.append(' ' + self.args_prefix + str(i))
        return ''.join(result)

    def __str__(self):
        return "{}".format(self.name)
    
    def to_string(self, gap = '    '):
        mock = []
        name = self.name
        if self.name in self.operators:
            mock.append(gap)
            mock.append(
                "virtual %(result_type)s %(name)s(%(args)s) %(const)s{ %(return)s %(body)s; }\n" % {
                    'result_type' : self.result_type,
                    'name' : self.name,
                    'args' : self.__named_args_with_types(),
                    'const' : self.is_const and 'const ' or '',
                    'return' : self.result_type.strip() != 'void' and 'return' or '',
                    'body' : self.operators[self.name] + "(" + self.__named_args() + ")"
                }
            )
            name = self.operators[self.name]

        mock.append(gap)
        mock.append(
            "MOCK_%(const)sMETHOD%(nr)s%(template)s(%(name)s, %(result_type)s(%(args)s));" % {
            'const' : self.is_const and 'CONST_' or '',
            'nr' : self.args_size,
            'template' : self.is_template and '_T' or '',
            'name' : name,
            'result_type' : self.result_type,
            'args' : self.args
        })

        return ''.join(mock)


class mock_generator:
    def __is_template_class(self, expr):
        return '<' in expr

    def __get_result_type(self, tokens, name):
        result_type = []
        for token in tokens:
            if token in [name, 'operator']:
                break
            if token not in ['virtual', 'inline', 'volatile']:
                result_type.append(token)
            if token in ['const', 'volatile']:
                result_type.append(' ')
        return ''.join(result_type)

    def __pretty_template(self, expr):
        first = False
        typename = []
        typenames = []
        for token in expr.split("::")[-1]:
            if token == '<':
                first = True
            elif token == ',':
                typenames.append(''.join(typename))
                typename = []
            elif token == '>':
                typenames.append(''.join(typename))
                typename = []
            elif token == ' ':
                continue
            elif first:
                typename.append(token)

        result = []
        if len(typenames) > 0:
            result.append("template<")
            for i, t in enumerate(typenames):
                i != 0 and result.append(", ")
                result.append("typename ")
                result.append(t)
            result.append(">")
            result.append("\n")

        return ''.join(result)

    def __pretty_mock_methods(self, mock_methods):
        result = []
        for i, mock_method in enumerate(mock_methods):
            i and result.append('\n')
            result.append(mock_method.to_string())
            first = False
        return ''.join(result)

    def __pretty_namespaces_begin(self, expr):
        result = []
        for i, namespace in enumerate(expr.split("::")[0 : -1]):
            i and result.append('\n')
            result.append("namespace " + namespace + " {")
        return ''.join(result)

    def __pretty_namespaces_end(self, expr):
        result = []
        for i, namespace in enumerate(expr.split("::")[0 : -1]):
            i and result.append('\n')
            result.append("} // namespace " + namespace)
        return ''.join(result)

    def __get_interface(self, expr):
        result = []
        ignore = False
        for token in expr.split("::")[-1]:
            if token == '<':
                ignore = True
            if not ignore:
                result.append(token)
            if token == '>':
                ignore = False
        return ''.join(result)
    
    def __get_mock_methods(self, node, mock_methods, name_space = ""):
        self.__recursive_traverse(node, mock_methods, name_space, False)

    def __generate_file(self, mock_class, file_type, file_template_type):
        source_class = mock_class.get_source_class()
        expr = source_class.get_expr()
        interface = self.__get_interface(expr)
        mock_file = {
            'hpp' : self.mock_file_hpp % { 'interface' : interface },
            'cpp' : self.mock_file_cpp % { 'interface' : interface },
        }
        path = self.path + "/" + mock_file[file_type]
        print "Generating {}".format(path)
        source_file_name = source_class.get_file_name()
        not os.path.exists(os.path.dirname(path)) and os.makedirs(os.path.dirname(path))
        content = file_template_type % {
            'mock_file_hpp' : mock_file['hpp'],
            'mock_file_cpp' : mock_file['cpp'],
            'generated_dir' : self.path,
            'guard' : "__{:X}".format(time_stamp) + "_"+ mock_file[file_type].replace('.', '_').upper(),
            'dir' : os.path.dirname(source_file_name),
            'file' : os.path.basename(source_file_name),
            'namespaces_begin' : self.__pretty_namespaces_begin(expr),
            'interface' : interface,
            'template_interface' : expr.split("::")[-1],
            'template' : self.__pretty_template(expr),
            'mock_methods' : self.__pretty_mock_methods(mock_class.get_mock_methods()),
            'namespaces_end' : self.__pretty_namespaces_end(expr)
            }
        with open(path, 'w') as file:
            file.write(content)


    def __init__(self, file_name, args, expr, path, mock_file_hpp, file_template_hpp, mock_file_cpp, file_template_cpp, encode = "utf-8"):
        self.expr = expr
        self.path = path
        self.clang_args = args
        self.mock_file_hpp = mock_file_hpp
        self.file_template_hpp = file_template_hpp
        self.mock_file_cpp = mock_file_cpp
        self.file_template_cpp = file_template_cpp
        self.encode = encode
        self.file_name = os.path.abspath(file_name)
        self.input_file_name = file_name

    def generate(self):
        classes = ClassCollector(file_name=self.input_file_name, clang_args=self.clang_args).get_classes()
        self.__mock_classes = [MockClass(c) for c in classes]
        for mock_class in self.__mock_classes:
            if len(mock_class.get_mock_methods()) > 0:
                source_class = mock_class.get_source_class()
                print "Found Class '{}' with following pure virtual methods: [{}]".format(source_class.get_expr(), "; ".join(source_class.get_all_pure_virtual_methods_as_strings()))
                self.file_template_hpp != "" and self.__generate_file(mock_class, "hpp", self.file_template_hpp)
                self.file_template_cpp != "" and self.__generate_file(mock_class, "cpp", self.file_template_cpp)
        return 0

def main(args):
    clang_args = None
    args_split = [i for i, arg in enumerate(args) if arg == "--"]
    if args_split:
        args, clang_args = args[:args_split[0]], args[args_split[0] + 1:]

    default_config = os.path.dirname(args[0]) + "/gmock.conf"

    parser = OptionParser(usage="usage: %prog [options] files...")
    parser.add_option("-c", "--config", dest="config", default=default_config, help="config FILE (default='gmock.conf')", metavar="FILE")
    parser.add_option("-d", "--dir", dest="path", default=".", help="dir for generated mocks (default='.')", metavar="DIR")
    parser.add_option("-e", "--expr", dest="expr", default="", help="limit to interfaces within expression (default='')", metavar="LIMIT")
    parser.add_option("-l", "--libclang", dest="libclang", default=None, help="path to libclang.so (default=None)", metavar="LIBCLANG")
    parser.add_option
    (options, args) = parser.parse_args(args)

    if len(args) < 2:
        parser.error("at least one file has to be given")

    config = {}
    with open(options.config, 'r') as file:
        exec(file.read(), config)

    if options.libclang:
      Config.set_library_file(options.libclang)

    for file_name in args[1:]:
        if not os.path.exists(file_name):
            sys.stdout.write("{} does not exist\n".format(file_name))
            return 1 
        result = mock_generator(
            file_name = file_name,
            args = clang_args,
            expr = options.expr,
            path = options.path,
            mock_file_hpp = config['mock_file_hpp'],
            file_template_hpp = config['file_template_hpp'],
            mock_file_cpp = config['mock_file_cpp'],
            file_template_cpp = config['file_template_cpp']
            ).generate()
        if (result != 0):
            return result
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))

