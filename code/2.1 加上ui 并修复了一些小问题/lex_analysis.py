# -*- coding: utf8 -*- 
import os
from ply import lex

# 保留字列表
reserved = (
    'main', 'int', 'char', 'if', 'else', 'do', 'while', 'repeat', 'until',
    'write', 'read', 'XOR', 'ODD', 'for', 'exit', 'continue', 'break',
    'switch', 'case', 'default', 'bool', 'and', 'or', 'not', 'const',
    'procedure', 'call'
)

# token名称列表
tokens = reserved + (
    'NUMBER', 'EQUAL', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN',
    'LBRACE', 'RBRACE', 'LSS', 'LEQ', 'GTR', 'GEQ', 'EQL', 'NEQ', 'SEMICOLON',
    'LBRACKET', 'RBRACKET', 'ID', 'SFPLUS', 'SFMINUS', 'MOD', 'COLON'
)

# 简单标记的正则表达式规则
t_EQUAL = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'{'
t_RBRACE = r'}'
t_LSS = r'<'
t_LEQ = r'<='
t_GTR = r'>'
t_GEQ = r'>='
t_EQL = r'=='
t_NEQ = r'!='
t_SEMICOLON = r';'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SFPLUS = r'\+\+'
t_SFMINUS = r'--'
t_NUMBER = r'\d+'
t_MOD = r'%'
t_COLON = r':'

# 忽略字符
t_ignore = ' \t\r'
t_ignore_COMMENT = r'\/\*(\s|.)*?\*\/'


# 带有操作代码的正则表达式规则
def t_ID(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    if t.value in reserved:
        t.type = t.value
    return t


# 记录行号，方便出错定位
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# 错误处理规则
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()

# file_name = input('Input x0 file?   ')
# fin = open('../test_files/' + file_name, 'r')
# data = fin.read()
# lexer.input(data)
# for tok in lexer:
#     print(tok)  # (tok.type, tok.value, tok.lineno, tok.lexpos)
# fin.close()