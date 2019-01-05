# -*- coding: utf8 -*-
from ply import yacc
from lex_analysis import tokens

precedence = (
    ('left', 'and', 'or', 'XOR'),
    ('left', 'EQL', 'NEQ'),
    ('left', 'LSS', 'LEQ', 'GTR', 'GEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'SFPLUS', 'SFMINUS', 'not')
)
# 'and', 'or', 'XOR', '==', '!=', '<', '<=', '>', '>=', 'ODD'在语法定义里处于同一级，注意加括号决定优先顺序

table_max_num = 100  # 符号表容量
ID_max_length = 10  # 标识符最大长度
address_max = 2048  # 地址上界
code_max_num = 200  # 最多的虚拟机代码数
stack_max_num = 700  # 运行时数据栈元素最大数量

table = []  # table = [{'name': ID, 'kind': ,'type': , 'value': , 'address': , 'size': }] 符号表
instruction = []  # instruction = [{'f': char, 'l': int, 'a': int}] 存放虚拟机代码

cx = 0  # 虚拟机代码索引
tx = 0  # 符号表当前尾指针
local_address = 3  # 局部变量地址
error_list = []  # 出错列表
loop_adr_list = []  # 存放每次循环语句循环的开始地址
ex3_adr_list = []  # 存放for循环表达式3的开始地址
for_start_adr = []  # 存放for循环的开始地址
isbreak_list = []  # 是否在循环中使用了break语句，1为是，空为否，每层增加一个元素
switch_start_adr = []  # 存放switch分支结构的开始地址


def p_program(p):
    'program : main LBRACE declaration_list gen_ini statement_list RBRACE'
    p[0] = ('program', p[3], p[4], p[5])
    gen('opr', 0, 0)

def p_gen_ini(p):
    'gen_ini : '
    p[0] = ('gen_ini')
    gen('ini', 0, local_address)

def p_declaration_list(p):
    '''declaration_list : declaration_list declaration_stat
                        | declaration_stat
                        | '''
    if len(p) == 3:
        p[0] = ('declaration_list', p[1], p[2])
    elif len(p) == 2:
        p[0] = ('declaration_list', p[1])
    else:
        p[0] = ('declaration_list', '')

def p_declaration_stat(p):
    '''declaration_stat : type ID SEMICOLON
                        | type ID LBRACKET NUMBER RBRACKET SEMICOLON
                        | const type ID EQUAL NUMBER SEMICOLON'''
    global local_address
    if len(p) == 4:
        p[0] = ('declaration_stat', p[1], p[2])
        enter(p[2], 'variable', p[1][1], -1, local_address, 1)
        local_address += 1
    else:
        if p[1] == 'const':
            p[0] = ('declaration_stat', p[2], p[3], p[5])
            enter(p[3], 'constant', p[2][1], int(p[5]), -1, -1)
        else:
            p[0] = ('declaration_stat', p[1], p[2], p[4])
            enter(p[2], 'variable', p[1][1], -1, local_address, int(p[4]))
            local_address += int(p[4])

def p_type(p):
    '''type : int
            | char
            | bool'''
    p[0] = ('type', p[1])

def p_var(p):
    '''var : ID
           | ID LBRACKET expression RBRACKET'''
    isDefined = 0
    for example in table:
        if example['name'] == p[1]:
            isDefined = 1
            break
    if isDefined == 0:
        print("Syntax error at '%s'!" % p[1])
        error_list.append('ID %s undefined!' % p[1])
    if len(p) == 2:
        p[0] = ('var', p[1])
    else:
        p[0] = ('var', p[1], p[3])

def p_statement_list(p):
    '''statement_list : statement_list statement
                      | '''
    if len(p) == 3:
        p[0] = ('statement_list', p[1], [2])
    else:
        p[0] = ('statement_list', '')

def p_statement(p):
    '''statement : if_stat
                 | while_stat
                 | read_stat
                 | write_stat
                 | compound_stat
                 | expression_stat
                 | repeat_stat
                 | do_while_stat
                 | for_stat
                 | exit_stat
                 | continue_stat
                 | break_stat
                 | switch_case_stat'''
    p[0] = ('statement', p[1])

def p_gen_jpc_back(p):
    'gen_jpc_back : '
    p[0] = ('gen_jpc_back')
    for example in reversed(instruction):
        if example['f'] == 'jpc' and example['a'] == 0:
            example['a'] = cx + 1
            break

def p_gen_jpc(p):
    'gen_jpc : '
    p[0] = ('gen_jpc')
    gen('jpc', 0, 0)

def p_gen_jmp(p):
    'gen_jmp : '
    p[0] = ('gen_jmp')
    gen('jmp', 0, 0)

def p_if_stat(p):
    '''if_stat : if LPAREN expression RPAREN gen_jpc statement
               | if LPAREN expression RPAREN gen_jpc statement else gen_jpc_back gen_jmp statement'''
    if len(p) == 7:
        p[0] = ('if_stat', p[3], p[5], p[6])
        for example in reversed(instruction):
            if example['f'] == 'jpc' and example['a'] == 0:
                example['a'] = cx
                break
    else:
        p[0] = ('if_stat', p[3], p[5], p[6], p[8], p[9], p[10])
        for example in reversed(instruction):
            if example['f'] == 'jmp' and example['a'] == 0:
                example['a'] = cx
                break

def p_rec_loop_adr(p):
    'rec_loop_adr : '
    p[0] = ('rec_loop_adr')
    loop_adr_list.append(cx)

def p_while_stat(p):
    'while_stat : while rec_loop_adr LPAREN expression RPAREN gen_jpc statement'
    p[0] = ('while_stat', p[2], p[4], p[6], p[7])
    gen('jmp', 0, loop_adr_list[-1])
    for example in reversed(instruction):
        if example['f'] == 'jpc' and example['a'] == 0:
            example['a'] = cx
            break
    if len(isbreak_list) != 0:
        tmp_cx = cx - 1
        while tmp_cx >= loop_adr_list[-1]:
            if instruction[tmp_cx]['f'] == 'jmp' and instruction[tmp_cx]['a'] == 0:
                instruction[tmp_cx]['a'] = cx
            tmp_cx -= 1
        isbreak_list.pop()
    loop_adr_list.pop()

def p_repeat_stat(p):
    'repeat_stat : repeat rec_loop_adr statement until LPAREN expression RPAREN'
    p[0] = ('repeat_stat', p[2], p[3], p[6])
    gen('jpc', 0, loop_adr_list[-1])
    if len(isbreak_list) != 0:
        tmp_cx = cx - 1
        while tmp_cx >= loop_adr_list[-1]:
            if instruction[tmp_cx]['f'] == 'jmp' and instruction[tmp_cx]['a'] == 0:
                instruction[tmp_cx]['a'] = cx
            tmp_cx -= 1
        isbreak_list.pop()
    loop_adr_list.pop()

def p_do_while_stat(p):
    'do_while_stat : do rec_loop_adr statement while LPAREN expression RPAREN'
    p[0] = ('do_while_stat', p[2], p[3], p[6])
    gen('jnc', 0, loop_adr_list[-1])
    if len(isbreak_list) != 0:
        tmp_cx = cx - 1
        while tmp_cx >= loop_adr_list[-1]:
            if instruction[tmp_cx]['f'] == 'jmp' and instruction[tmp_cx]['a'] == 0:
                instruction[tmp_cx]['a'] = cx
            tmp_cx -= 1
        isbreak_list.pop()
    loop_adr_list.pop()

def p_rec_ex3_adr(p):
    'rec_ex3_adr : '
    p[0] = ('rec_ex3_adr')
    ex3_adr_list.append(cx)

def p_gen_jmp_back(p):
    'gen_jmp_back : '
    p[0] = ('gen_jmp_back')
    for example in reversed(instruction):
        if example['f'] == 'jmp' and example['a'] == 0:
            example['a'] = cx
            break

def p_gen_jmp_condition(p):
    'gen_jmp_condition : '
    global for_start_adr
    p[0] = ('gen_jmp_condition')
    gen('jmp', 0, loop_adr_list[-1])
    for_start_adr.append(loop_adr_list[-1])
    loop_adr_list.pop()

def p_for_stat(p):
    '''for_stat : for LPAREN expression SEMICOLON rec_loop_adr expression SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr expression RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN SEMICOLON rec_loop_adr expression SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr expression RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN expression SEMICOLON rec_loop_adr SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr expression RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN expression SEMICOLON rec_loop_adr expression SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN SEMICOLON rec_loop_adr SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr expression RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN SEMICOLON rec_loop_adr expression SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN expression SEMICOLON rec_loop_adr SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr RPAREN gen_jmp_condition gen_jmp_back statement
                | for LPAREN SEMICOLON rec_loop_adr SEMICOLON gen_jpc gen_jmp \
                    rec_ex3_adr RPAREN gen_jmp_condition gen_jmp_back statement'''
    if len(p) == 16:
        p[0] = ('for_stat', p[3], p[5], p[6], p[8], p[9], p[10], p[11], p[13], p[14], p[15])
    elif len(p) == 15:
        if p[3] == ';':
            p[0] = ('for_stat', p[4], p[5], p[7], p[8], p[9], p[10], p[12], p[13], p[14])
        elif p[6] == ';':
            p[0] = ('for_stat', p[3], p[5], p[7], p[8], p[9], p[10], p[12], p[13], p[14])
        else:
            p[0] = ('for_stat', p[3], p[5], p[6], p[8], p[9], p[10], p[12], p[13], p[14])
    elif len(p) == 14:
        if p[3] == ';' and p[5] == ';':
            p[0] = ('for_stat', p[4], p[6], p[7], p[8], p[9], p[11], p[12], p[13])
        elif p[3] == ';' and p[6] == ';':
            p[0] = ('for_stat', p[4], p[5], p[7], p[8], p[9], p[11], p[12], p[13])
        else:
            p[0] = ('for_stat', p[3], p[5], p[7], p[8], p[9], p[11], p[12], p[13])
    else:
        p[0] = ('for_stat', p[4], p[6], p[7], p[8], p[10], p[11], p[12])

    for example in reversed(instruction):
        if example['f'] == 'jpc' and example['a'] == 0:
            example['a'] = cx + 1
            break
    gen('jmp', 0, ex3_adr_list[-1])
    ex3_adr_list.pop()
    if len(isbreak_list) != 0:
        tmp_cx = cx - 1
        while tmp_cx >= for_start_adr[-1]:
            if instruction[tmp_cx]['f'] == 'jmp' and instruction[tmp_cx]['a'] == 0:
                instruction[tmp_cx]['a'] = cx
            tmp_cx -= 1
        isbreak_list.pop()
    for_start_adr.pop()

def p_exit_stat(p):
    'exit_stat : exit LPAREN RPAREN SEMICOLON'
    p[0] = ('exit_stat')
    gen('opr', 0, 0)

def p_continue_stat(p):
    'continue_stat : continue SEMICOLON'
    p[0] = ('continue_stat')
    if len(loop_adr_list) == 0 and len(for_start_adr) == 0:
        print("'continue' is used in loops!")
        error_list.append("'continue' is used in loops!")
    elif len(for_start_adr) != 0:
        gen('jmp', 0, for_start_adr[-1])
    else:
        gen('jmp', 0, loop_adr_list[-1])

def p_break_stat(p):
    'break_stat : break SEMICOLON'
    p[0] = ('break_stat')
    if len(loop_adr_list) == 0 and len(for_start_adr) == 0:
        print("'break' is used in loops or the end of every case statement!")
        error_list.append("'break' is used in loops or the end of every case statement!")
    else:
        gen('jmp', 0, 0)
        isbreak_list.append(1)

def p_rec_switch_adr(p):
    'rec_switch_adr : '
    p[0] = ('rec_switch_adr')
    switch_start_adr.append(cx)

def p_switch_case_stat(p):
    '''switch_case_stat : switch LPAREN expression RPAREN LBRACE rec_switch_adr case_list default COLON statement RBRACE
                        | switch LPAREN expression RPAREN LBRACE rec_switch_adr case_list RBRACE'''
    if len(p) == 11:
        p[0] = ('switch_case_stat', p[3], p[6], p[7], p[10])
    else:
        p[0] = ('switch_case_stat', p[3], p[6], p[7])
    tmp_cx = cx - 1
    while tmp_cx >= switch_start_adr[-1]:
        if instruction[tmp_cx]['f'] == 'jmp' and instruction[tmp_cx]['a'] == 0:
            instruction[tmp_cx]['a'] = cx
        tmp_cx -= 1
    switch_start_adr.pop()

def p_case_list(p):
    '''case_list : case_list case_stat
                 | case_stat'''
    if len(p) == 3:
        p[0] = ('case_list', p[1], p[2])
    else:
        p[0] = ('case_list', p[1])

def p_gen_opr_switch(p):
    'gen_opr_switch : '
    p[0] = ('gen_opr_switch')
    gen('opr', 0, 23)

def p_case_stat(p):
    '''case_stat : case expression COLON gen_opr_switch gen_jpc statement break SEMICOLON'''
    p[0] = ('case_stat', p[2], p[4], p[5], p[6])
    for example in reversed(instruction):
        if example['f'] == 'jpc' and example['a'] == 0:
            example['a'] = cx + 1
            break
    gen('jmp', 0, 0)

def p_read_stat(p):
    'read_stat : read var SEMICOLON'
    p[0] = ('read_stat', p[2])
    gen('opr', 0, 16)
    for example in table:
        if example['name'] == p[2][1]:
            if example['size'] == 1:
                # p[2] = ('var', ID)
                gen('sto', 0, example['address'])
            else:
                # p[2] = ('var', ID, ('expression', ('simple_expr', ('additive_expr', ('term', (
                #         'self_operating', ('factor', NUM)))))))
                gen('sto', 0, example['address'] + int(p[2][2][1][1][1][1][1][1]))
            break

def p_write_stat(p):
    'write_stat : write expression SEMICOLON'
    p[0] = ('write_stat', p[2])
    if len(p[2][1][1][1][1][1][1]) == 2:
        if p[2][1][1][1][1][1][1][0] == 'var':
            # p[2] = ('expression', ('simple_expr', ('additive_expr', ('term', ('self_operating', (
            #         'factor', ('var', ID))))))))
            for example in table:
                if example['name'] == p[2][1][1][1][1][1][1][1]:
                    if example['address'] == -1 and example['size'] == -1:
                        # 输出一个常量值
                        gen('opr', 0, 14)
                    elif example['size'] == 1:
                        # 输出一个变量值
                        gen('opr', 0, 14)
                    else:
                        # 输出整个数组
                        for i in range(example['size']):
                            gen('lod', 0, example['address'] + i)
                            gen('opr', 0, 14)
                    break
        else:
            # 输出表达式
            gen('opr', 0, 14)
    else:
        # 输出常数
        gen('opr', 0, 14)

def p_compound_stat(p):
    'compound_stat : LBRACE statement_list RBRACE'
    p[0] = ('compound_stat', p[2])

def p_expression_stat(p):
    '''expression_stat : expression SEMICOLON
                       | SEMICOLON'''
    if len(p) == 3:
        p[0] = ('expression_stat', p[1])
    else:
        p[0] = ('expression_stat', '')

def p_expression(p):
    '''expression : var EQUAL expression
                  | simple_expr'''
    if len(p) == 4:
        p[0] = ('expression', p[1], p[3])
        for example in table:
            if example['name'] == p[1][1]:
                if len(p[1]) == 2:
                    # p[1] = ('var', ID)
                    gen('sto', 0, example['address'])
                else:
                    try:
                        # 等号左边是数组，指令中地址用负值表示
                        tmp = int(p[1][2][1][1][1][1][1][1]) + 1
                        gen('sto', 0, example['address'] + int(p[1][2][1][1][1][1][1][1]))
                    except:
                        gen('sto', 0, -example['address'])
                break
    else:
        p[0] = ('expression', p[1])

def p_simple_expr(p):
    '''simple_expr : additive_expr
                   | additive_expr LSS additive_expr
                   | additive_expr LEQ additive_expr
                   | additive_expr GTR additive_expr
                   | additive_expr GEQ additive_expr
                   | additive_expr EQL additive_expr
                   | additive_expr NEQ additive_expr
                   | additive_expr XOR additive_expr
                   | ODD additive_expr
                   | additive_expr and additive_expr
                   | additive_expr or additive_expr'''
    if len(p) == 2:
        p[0] = ('simple_expr', p[1])
    elif len(p) == 4:
        p[0] = ('simple_expr', p[2], p[1], p[3])
        if p[2] == '<':
            gen('opr', 0, 10)
        elif p[2] == '<=':
            gen('opr', 0, 13)
        elif p[2] == '>':
            gen('opr', 0, 12)
        elif p[2] == '>=':
            gen('opr', 0, 11)
        elif p[2] == '==':
            gen('opr', 0, 8)
        elif p[2] == '!=':
            gen('opr', 0, 9)
        elif p[2] == 'XOR':
            gen('opr', 0, 22)
        elif p[2] == 'and':
            gen('opr', 0, 24)
        elif p[2] == 'or':
            gen('opr', 0, 25)
    else:
        p[0] = ('simple_expr', p[2])
        gen('opr', 0, 6)

def p_additive_expr(p):
    '''additive_expr : term
                     | term PLUS additive_expr
                     | term MINUS additive_expr'''
    if len(p) == 2:
        p[0] = ('additive_expr', p[1])
    else:
        p[0] = ('additive_expr', p[2], p[1], p[3])
        if p[2] == '+':
            gen('opr', 0, 2)
        else:
            gen('opr', 0, 3)

def p_term(p):
    '''term : self_operating
            | self_operating TIMES term
            | self_operating DIVIDE term
            | self_operating MOD term'''
    if len(p) == 2:
        p[0] = ('term', p[1])
    else:
        p[0] = ('term', p[2], p[1], p[3])
        if p[2] == '*':
            gen('opr', 0, 4)
        elif p[2] == '/':
            gen('opr', 0, 5)
        elif p[2] == '%':
            gen('opr', 0, 21)

def p_self_operating(p):
    '''self_operating : factor
                      | LPAREN SFPLUS factor RPAREN
                      | LPAREN SFMINUS factor RPAREN
                      | LPAREN factor SFPLUS RPAREN
                      | LPAREN factor SFMINUS RPAREN
                      | not factor'''
    if len(p) == 2:
        p[0] = ('self_operating', p[1])
    elif len(p) == 5:
        if p[2] == '++':
            p[0] = ('self_operating', 'operator_front', p[2], p[3])
            gen('opr', 0, 17)
        elif p[2] == '--':
            p[0] = ('self_operating', 'operator_front', p[2], p[3])
            gen('opr', 0, 18)
        elif p[3] == '++':
            p[0] = ('self_operating', 'operator_back', p[3], p[2])
            gen('opr', 0, 19)
        elif p[3] == '--':
            p[0] = ('self_operating', 'operator_back', p[3], p[2])
            gen('opr', 0, 20)
    else:
        p[0] = ('self_operating', p[2])
        gen('opr', 0, 26)

def p_factor(p):
    '''factor : LPAREN expression RPAREN
              | var
              | NUMBER'''
    if len(p) == 4:
        p[0] = ('factor', p[2])
    else:
        p[0] = ('factor', p[1])
        if p[1][0] == 'var':
            for example in table:
                if example['name'] == p[1][1]:
                    if len(p[1]) == 2:
                        # p[1] = ('var', ID)
                        if example['kind'] == 'variable':
                            gen('lod', 0, example['address'])
                        elif example['kind'] == 'constant':
                            gen('lit', 0, example['value'])
                    else:
                        try:
                            # 数组索引为常数
                            tmp = int(p[1][2][1][1][1][1][1][1]) + 1
                            if tmp - 1 >= example['size']:
                                print('Array index out of range!')
                                error_list.append('Array index out of range!')
                                return
                            gen('lod', 0, example['address'] + int(p[1][2][1][1][1][1][1][1]))
                        except:
                            gen('lod', 0, -example['address'])
                    break
        else:
            gen('lit', 0, int(p[1]))

def p_error(p):
    if p:
        print("Syntax error at '%s' at the line %d" % (p.value, p.lineno))
        error_list.append("Syntax error at '%s' at the line %d" % (p.value, p.lineno))
    else:
        print('Syntax error in input!')
        error_list.append('Syntax error in input!')

def enter(name, kind, type, value, address, size):
    global tx
    if tx >= table_max_num:
        print('Too many identifiers!')
        return
    new_ID = {}
    new_ID['name'] = name
    new_ID['kind'] = kind
    new_ID['type'] = type
    new_ID['value'] = value
    new_ID['address'] = address
    new_ID['size'] = size
    table.append(new_ID)
    tx += 1

def gen(f, l, a):
    global cx
    if cx >= code_max_num:
        print('Program is too long!') # 生成的虚拟机代码程序过长
        return
    if a >= address_max:
        print('Displacement address is too big!') # 地址偏移越界
        return
    new_code = {}
    new_code['f'] = f
    new_code['l'] = l
    new_code['a'] = a
    instruction.append(new_code)
    cx += 1

# 通过过程基址求上l层过程的基址
def base(l, s, b):
    b1 = b
    while l > 0:
        b1 = s[b1]
        l -= 1
    return b1

def interpret():
    p = 0  # 指令指针
    b = 1  # 指令基址
    t = 0  # 栈顶指针
    s = [0, 0, 0, 0]  # 栈
    for i in range(stack_max_num - 4):
        s.append(-999)

    print('\n===fresult.txt===\n')
    fresult = open('../result_files/fresult.txt', 'w')
    print('Start x0')
    fresult.write('Start x0\n')

    while p != cx:
        current_code = instruction[p]
        p += 1

        if current_code['f'] == 'ini':
            t += current_code['a']

        elif current_code['f'] == 'lit':
            t += 1
            s[t] = current_code['a']

        elif current_code['f'] == 'lod':
            t += 1
            if current_code['a'] < 0:
                tmp = s[base(current_code['l'], s, b) - current_code['a'] + s[t - 1]]
            else:
                tmp = s[base(current_code['l'], s, b) + current_code['a']]
            if tmp == -999:
                print('Array or variable not assigned!')
                error_list.append('Array or variable not assigned!')
                return
            else:
                for example in table:
                    if (example['address'] <= current_code['a'] and
                        current_code['a'] <= example['address'] + example['size'] - 1) \
                            or example['address'] == -current_code['a']:
                        if example['type'] == 'int':
                            if tmp >= -2147483648 and tmp <= 2147483647:
                                s[t] = tmp
                            else:
                                print("The range of type 'int' is -2147483648 ~ 2147483647!")
                                error_list.append("The range of type 'int' is -2147483648 ~ 2147483647!")
                        elif example['type'] == 'char':
                            if tmp >= -128 and tmp <= 127:
                                s[t] = tmp
                            else:
                                print("The range of type 'char' is -128 ~ 127!")
                                error_list.append("The range of type 'char' is -128 ~ 127!")
                        elif example['type'] == 'bool':
                            if tmp == 0 or tmp == 1:
                                s[t] = tmp
                            else:
                                print("The range of type 'bool' is 0 ~ 1!")
                                error_list.append("The range of type 'bool' is 0 ~ 1!")
                        break

        elif current_code['f'] == 'sto':
            if current_code['a'] < 0 :
                s[base(current_code['l'], s, b) - current_code['a'] + s[t - 1]] = s[t]
            else:
                s[base(current_code['l'], s, b) + current_code['a']] = s[t]
                # 这里的连续赋值只考虑了等号再讲栈顶值赋值给变量，没有考虑再赋值给数组，再赋值给数组的情况比较复杂
                for code in instruction[p:]:
                    if code['f'] == 'sto':
                        s[base(instruction[p]['l'], s, b) + instruction[p]['a']] = s[t]
                        p += 1
                    else:
                        break
            t -= 1

        elif current_code['f'] == 'cal':
            s[t + 1] = base(current_code['l'], s, b)
            s[t + 2] = b
            s[t + 3] = p
            b = t + 1
            p = current_code['a']

        elif current_code['f'] == 'jmp':
            p = current_code['a']

        elif current_code['f'] == 'jpc':
            if s[t] == 0:
                p = current_code['a']
            t -= 1

        elif current_code['f'] == 'jnc':
            if s[t] != 0:
                p = current_code['a']
            t -= 1

        elif current_code['f'] == 'opr':
            if current_code['a'] == 0:
                t = b - 1
                p = s[t + 3]
                b = s[t + 2]
                break
            elif current_code['a'] == 1:
                s[t] = -s[t]
            elif current_code['a'] == 2:
                t -= 1
                s[t] += s[t + 1]
            elif current_code['a'] == 3:
                t -= 1
                s[t] -= s[t + 1]
            elif current_code['a'] == 4:
                t -= 1
                s[t] *= s[t + 1]
            elif current_code['a'] == 5:
                t -= 1
                s[t] /= s[t + 1]
            elif current_code['a'] == 6:
                s[t] = s[t] % 2
            elif current_code['a'] == 8:
                t -= 1
                s[t] = (s[t] == s[t + 1])
            elif current_code['a'] == 9:
                t -= 1
                s[t] = (s[t] != s[t + 1])
            elif current_code['a'] == 10:
                t -= 1
                s[t] = (s[t] < s[t + 1])
            elif current_code['a'] == 11:
                t -= 1
                s[t] = (s[t] >= s[t + 1])
            elif current_code['a'] == 12:
                t -= 1
                s[t] = (s[t] > s[t + 1])
            elif current_code['a'] == 13:
                t -= 1
                s[t] = (s[t] <= s[t + 1])
            elif current_code['a'] == 14:
                if instruction[p - 2]['f'] == 'opr' or instruction[p - 2]['f'] == 'lit':
                    # 输出表达式或常数的值
                    print(s[t])
                    fresult.write(str(s[t]) + '\n')
                else:
                    for example in table:
                        if (example['address'] <= instruction[p - 2]['a'] and
                            instruction[p - 2]['a'] <= example['address'] + example['size'] - 1) \
                                or example['address'] == -instruction[p - 2]['a']:
                            # 输出变量、索引为常数的数组、索引为表达式的数组的值
                            if example['type'] == 'int':
                                if s[t] >= -2147483648 and s[t] <= 2147483647:
                                    print(s[t])
                                    fresult.write(str(s[t]) + '\n')
                            elif example['type'] == 'bool':
                                if s[t] == 1:
                                    print('true')
                                    fresult.write('true\n')
                                elif s[t] == 0:
                                    print('false')
                                    fresult.write('false\n')
                            else:
                                if s[t] >= -128 and s[t] <= 127:
                                    print(chr(s[t]))
                                    fresult.write(str(chr(s[t])) + '\n')
                            break
                t -= 1
            elif current_code['a'] == 15:
                print()
                fresult.write('\n')
            elif current_code['a'] == 16:
                t += 1
                s[t] = int(input('Input?    '))
                fresult.write('Input?    ' + str(s[t]) + '\n')
            elif current_code['a'] == 17:
                s[t] += 1
                s[base(instruction[p - 2]['l'], s, b) + instruction[p - 2]['a']] += 1
            elif current_code['a'] == 18:
                s[t] -= 1
                s[base(instruction[p - 2]['l'], s, b) + instruction[p - 2]['a']] -= 1
            elif current_code['a'] == 19:
                s[base(instruction[p - 2]['l'], s, b) + instruction[p - 2]['a']] += 1
            elif current_code['a'] == 20:
                s[base(instruction[p - 2]['l'], s, b) + instruction[p - 2]['a']] -= 1
            elif current_code['a'] == 21:
                t -= 1
                s[t] = s[t] % s[t + 1]
            elif current_code['a'] == 22:
                t -= 1
                if s[t] == s[t + 1]:
                    s[t] = 0
                else:
                    s[t] = 1
            elif current_code['a'] == 23:
                if s[t] == s[t - 1]:
                    s[t - 1] = 1
                    t -= 1
                else:
                    s[t] = 0
            elif current_code['a'] == 24:
                t -= 1
                if s[t] != 0 and s[t + 1] != 0:
                    s[t] = 1
                else:
                    s[t] = 0
            elif current_code['a'] == 25:
                t -= 1
                if s[t] == 0 and s[t + 1] == 0:
                    s[t] = 0
                else:
                    s[t] = 1
            elif current_code['a'] == 26:
                if s[t] == 0:
                    s[t] = 1
                else:
                    s[t] = 0


    print('End x0')
    fresult.write('End x0\n')
    fresult.close()


if __name__ == '__main__':
    file_name = input('Input x0 file?   ')
    fin = open('../test_files/' + file_name, 'r')
    data = fin.read()

    foutput = open('../result_files/foutput.txt', 'w')
    ftable = open('../result_files/ftable.txt', 'w')
    fcode = open('../result_files/fcode.txt', 'w')

    table = []
    instruction = []
    cx = 0
    tx = 0
    local_address = 3
    isbreak_list = []
    error_list = []
    loop_adr_list = []
    ex3_adr_list = []
    for_start_adr = []
    switch_start_adr = []

    gen('jmp', 0, 1)
    parser = yacc.yacc(start='program')
    parser.parse(data)

    if len(error_list) == 0:

        print('\n===ftable.txt===\n')
        for i in range(len(table)):
            if table[i]['kind'] == 'constant':
                ftable.write(str(i + 1) + '\t' + table[i]['name'] + '\t' + table[i]['kind'] + '\t' + table[i]['type']
                            + '\tvalue = ' + str(table[i]['value']) + '\taddress =  \tsize =  \n')
                print(str(i + 1), '\t', table[i]['name'], '\t', table[i]['kind'], '\t', table[i]['type'],
                    '\tvalue =', table[i]['value'], '\taddress =  \tsize =  ')
            elif table[i]['kind'] == 'variable':
                ftable.write(str(i + 1) + '\t' + table[i]['name'] + '\t' + table[i]['kind'] + '\t' + table[i]['type']
                             + '\tvalue =  \taddress = ' + str(table[i]['address']) + '\tsize = '
                             + str(table[i]['size']) + '\n')
                print(str(i + 1), '\t', table[i]['name'], '\t', table[i]['kind'], '\t', table[i]['type'],
                      '\tvalue =  \taddress =', table[i]['address'], '\tsize =', table[i]['size'])

        print('\n===fcode.txt===\n')
        for i in range(len(instruction)):
            fcode.write(str(i) + '\t' + instruction[i]['f'] + ' ' + str(instruction[i]['l']) + ', '
                        + str(instruction[i]['a']) + '\n')
            print(str(i), '\t', instruction[i]['f'], str(instruction[i]['l']) + ',', instruction[i]['a'])

        interpret()
    else:
        print('%d errors in x0 program' % len(error_list))
        foutput.write(str(len(error_list)) + ' errors in x0 program\n\n')
        for err in error_list:
            foutput.write(err + '\n')

    print('\n===foutput.txt===\n')
    if len(error_list) == 0:
        print('\n===Parsing success!===\n')
        foutput.write('\n===Parsing success!===\n')
    else:
        print('%d errors in x0 program' % len(error_list))
        foutput.write(str(len(error_list)) + ' errors in x0 program\n\n')
        for err in error_list:
            print(err)
            foutput.write(err + '\n')

    fin.close()
    foutput.close()
    ftable.close()
    fcode.close()


