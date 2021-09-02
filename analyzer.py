from my_parser import Parser 
import re

# Класс для ошибок
class Error(Exception):
    def __init__(self, msg, pos, *args):
        self.pos = pos
        self.msg = msg
        self.args = args
    
    def __str__(self):
        return f'{self.msg} on line {self.pos}.'

# Класс анализатора
class Analyzer:

    '''
    1.	<program> ::= <start_prog> <main> | <main>
    2.	<start_prog> ::= <program_title> | <variables> | <program_title> <variables>
    3.	<program_title> ::= program <prog_name>; 
    4.	<prog_name> ::= <id>
    5.	<id> ::= <letter> | <id> <letter> | <id> <number>
    6.	<letter> ::= a | b | c | … | z | A | B | C | … | Z | _
    7.	<number> ::=  0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | <sign> <number>
    8.	<variables> ::= <def_const> <def_variables> | <def_const> | <def_variables> | <def_variables> <def_const>
    9.	<def_const> ::= <const> | <def_const>; <const>
    10.	<const> ::= const <c>;
    11.	<c> ::= <id> = <constant> | <c>; <id> = <constant>
    12.	 <constant> ::= <math_expr> 
    13.	 <math_expr> ::= <term> | <math_expr> + <term> | <math_expr> - <term> 
    14.	 <term> ::= <factor> | <term> * <factor> | <term> div <factor> 
    15.	 <factor> ::= <id> | <id>^ | <integer>
    16.	 <integer> ::= <id> | <number> | <sign> <number> | <integer> <number>
    17.	 <sign> ::= - | +
    18.	 <def_variables> ::= <var> | <def_variables>; <var>
    19.	 <var> ::= var <v>;
    20.	 <v> ::= <id_list>: <type> ; <v>; <id_list>: <type>
    21.	 <id_list> ::= <id> | <id_list>, <id>
    22.	 <type> ::= integer | boolean | ^integer | ^boolean 
    23.	 <main> ::= begin end. | begin <code> end.
    24.	 <code> ::= <stmt> | <code>; <stmt> | begin end | begin <code> end
    25.	 <stmt> ::= <assign> | <read> | <write> | <if> | <for>  
    26.	 <assign> ::= <id> := <expr>; | <id> := @<id>; | <id> := nil; | <id> := <id>^;
    27.	 <read> ::= read(<id_list>); | read();
    28.	 <write> ::= write(<id_list>); | write();  
    29.	 <for> ::= for <index_expr> do <body> 
    30.	 <index_expr> ::= <id> := <math_expr> to <math_expr> | <id> := <math_expr> downto <math_expr>   
    31.	 <body> ::= <stmt> | begin  <code> end;
    32.	 <if> ::= if <logic_expr> then <body> | if <logic_expr> then <body> else <body>
    33.	<logic_expr> ::= <simple_logic_expr> | not <simple_logic_expr> | <simple_logic_expr> <logic_operator> <simple_logic_expr>  | <math_expr> <relational_operators> <math_expr>
    34.	<logic_operator> ::= = | <> | < | <= | >= | > | or | and | xor
    35.	 <simple_logic_expr> ::= <id> | <id>^ | <boolean> | <integer> <relational_operators> <integer> | <boolean> <logic_operator> <boolean>
    36.	 <relational_operators> ::= = | <> | < | <= | >= | >
    37.	 <boolean> ::= <id> | true | false
    '''

    # program_text - текст исходной программы
    def __init__(self, program_text):
        self.program_text = program_text
        parser = Parser(program_text)
        self.program1 = parser.to_string_list1()
        self.program2 = parser.to_string_list2()
        self.cur_ind = 0
        self.error_ind = 0
        self.error_line = 0
        self.counter = 0 # счетчик скобок

        self.flag = False
    
    # Функция, которая выбрасывает ошибку и определяет строчку с ошибкой
    def __throw_error(self, cur_ind, msg, *args):
        self.error_ind = cur_ind 
        self.error_line = self.get_number_error_line()
        raise Error(msg, self.error_line, *args)
    
    # Выдает строку, на которой нашлась ошибка
    def get_number_error_line(self):
        line_number = 1
        ind = 0
        for word in self.program2:
            if word == '\n':
                line_number += 1
            else:
                if ind == self.error_ind:
                    return line_number
                ind += 1
        return 1

    # <id> ::= <letter> | <id> <letter> | <id> <number>
    # <letter> ::= a | b | c | … | z | A | B | C | … | Z | _
    # <number> ::=  0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 
    def __id(self, pointer=False, adr=False):

         if self.program1[self.cur_ind] in ['begin', 'end', 'program', 
                                            'const', 'var', 'integer', 
                                            'boolean', '^integer', '^boolean', 
                                            'pointer', 'nil', 'write', 
                                            'for', 'do', 'to', 
                                            'if', 'then', 'else', 'div', 'read']:
            return False
        
         if pointer and adr:
             pattern = re.compile('^([@]?[a-z_])+[0-9a-z_]*[\^]?$')
         elif pointer:
             pattern = re.compile('^[a-z_]+[0-9a-z_]*[\^]?$')
         elif adr:
             pattern = re.compile('^([@]?[a-z_])+[0-9a-z_]*$')
         else:
             pattern = re.compile('^[a-z_]+[0-9a-z_]*$')
        
         if pattern.match(self.program1[self.cur_ind]) is not None:
             return True
         else:
            return False

    # <prog_name> ::= <id>
    def __prog_name(self):
        return self.__id()

    # <program_title> ::= program <prog_name>; 
    def __program_title(self):
        
        if self.program1[self.cur_ind] == 'program':

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but identificator expected', 120)
        
            if self.__prog_name():

                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but \';\' expected', 126)
                
                if self.program1[self.cur_ind] != ";":
                    self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but \';\' expected', 129)
    
            else:
                self.__throw_error(self.cur_ind, 'Incorrect identificator', 132)

    # <integer> ::= <id> | <number> | <sign> <number> | <integer> <number>
    # <sign> ::= - | +
    def __integer(self):
        if re.match(r'[+-]*[0-9]+$', self.program1[self.cur_ind]) is not None:
            return True
        else:
            return False

    # <factor> ::= <id> | <id>^ | <integer>
    def __factor(self):
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 146)

        self.__check_brackets()

        if not self.__id(pointer=True) and not self.__integer():
            self.__throw_error(self.cur_ind, f'Incorrect expression', 149)

    # <term> ::= <factor> | <term> * <factor> | <term> div <factor>
    # Избавимся от левой рекурсии:
    # <term> ::= <factor>[*<factor>]* | <factor>[div <factor>]*
    def __term(self):

        self.__factor()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 159)
        
        self.__check_brackets()
        
        if self.program1[self.cur_ind] in ['*', 'div']:
            
            self.__factor()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 166)

            self.__check_brackets()
            
            if self.program1[self.cur_ind] in ['*', 'div']:
                self.__term()
            else:
                self.cur_ind -= 1

        else:
            self.cur_ind -= 1

    # Функция проверяет баланс скобок в выражении.
    def __check_brackets(self):
        if self.program1[self.cur_ind] == '(':
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 185)
            self.counter += 1
            while self.program1[self.cur_ind] == '(':
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 185)
                self.counter += 1
        elif self.program1[self.cur_ind] == ')':
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 185)
            self.counter -= 1
            while self.program1[self.cur_ind] == ')':
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 185)
                self.counter -= 1
    
    # <math_expr> ::= <term> | <math_expr> + <term> | <math_expr> - <term> 
    # Избавимся от левой рекурсии:
    # <math_expr> ::= <term>[-<term>]* | <term>[+<term>]*
    def __math_expr(self, log = False):
        
        self.__term()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 185)
        
        self.__check_brackets()
        
        if self.program1[self.cur_ind] in ['+', '-']:

            self.__term()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 192)
            
            self.__check_brackets()
            
            if self.program1[self.cur_ind] in ['+', '-']:
                self.__math_expr()
            else:  
                if self.counter != 0 and not log:
                    self.__throw_error(self.cur_ind, f'Incorrect expression', 185)
                self.cur_ind -= 1

        else:
            if self.counter != 0 and not log:
                self.__throw_error(self.cur_ind, f'Incorrect expression', 185)
            self.cur_ind -= 1

    # <constant> ::= <math_expr> 
    def __constant(self):
        self.__math_expr()

    # <c> ::= <id> = <constant>; | <c>; <id> = <constant>;
    # Избавимся от левой рекурсии:
    # <c> ::= [<id> = <constant>;]*
    def __c(self):

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected identificator', 213)

        if self.__id():

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but \'=\' expected', 219)
            if self.program1[self.cur_ind] != '=':
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but \'=\' expected', 221)
            
            self.__constant()
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but \';\' expected', 226)
            if self.program1[self.cur_ind] != ';':
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but \';\' expected', 228)  
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected identificator', 232)
            
            if self.__id():
                self.cur_ind -= 1
                self.__c()
            else:
                if self.program1[self.cur_ind] not in ['begin', 'const', 'var']:
                    self.__throw_error(self.cur_ind, 'Incorrect identificator', 239)
                self.cur_ind -= 1
        
        else:
            self.__throw_error(self.cur_ind, 'Incorrect identificator', 243)
        
    # <const> ::= const <c>
    def __const(self):
        if self.cur_ind == 0 and self.program1[self.cur_ind] == 'const':
            self.__c()
        elif self.cur_ind != 0:
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                if len(self.program1) == 1: return
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected begin', 252)

            if self.program1[self.cur_ind] == 'const':
                self.__c()
            else:
                self.cur_ind -= 1

    # <def_const> ::= <const> | <def_const> <const>
    # Избавимся от левой рекурсии:
    # <def_const> ::= <const> | <const> <def_const>
    def __def_const(self):
        self.__const()
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            if len(self.program1) == 1:
                self.cur_ind -= 1
                return
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected begin', 267)
    
        if self.program1[self.cur_ind] == 'const':
            self.cur_ind -= 1
            self.__def_const()
        elif self.program1[self.cur_ind] == 'var':
            self.cur_ind -= 1
            self.__def_variables()
        else:
            self.cur_ind -= 1
        
    # <id_list> ::= <id> | <id_list>, <id>
    def __id_list(self, pointer=False, adr=False, int=False):

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected identificator', 283)
        
        if self.__id(pointer, adr) or (int and self.__integer()):
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \':\'', 288)

            if self.program1[self.cur_ind] == ',':
                self.__id_list(pointer, adr, int)
            else:
                self.cur_ind -= 1
        else:
            self.__throw_error(self.cur_ind , f'Incorrect identificator', 295)

    # <type> ::= integer | boolean | ^integer | ^boolean 
    def __type(self):

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected type', 302)

        if self.program1[self.cur_ind] not in ['integer', 'boolean', '^integer', 'boolean']:
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected type', 305)

    # <v> ::= <id_list>: <type>; | <v>; <id_list>: <type>;
    # Избавимся от левой рекурсии:
    # <v> ::= [<id_list>: <type>;]*
    def __v(self):

        self.__id_list()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \':\'', 315)
        
        if self.program1[self.cur_ind] != ':':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \':\'', 318)
        
        self.__type()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but \';\' expected', 324)
        if self.program1[self.cur_ind] != ';':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but \';\' expected', 326)  
            
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected identificator', 330)
            
        if self.__id():
            self.cur_ind -= 1
            self.__v()
        else:
            if self.program1[self.cur_ind] not in ['begin', 'const', 'var']:
                    self.__throw_error(self.cur_ind, 'Incorrect identificator', 337)
            self.cur_ind -= 1

    # <var> ::= var <v>
    def __var(self):

        if self.cur_ind == 0 and self.program1[self.cur_ind] == 'var':
            self.__v()
        elif self.cur_ind != 0:
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                if len(self.program1) == 1: return
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected begin', 347)

            if self.program1[self.cur_ind] == 'var':
                self.__v()
            else:
                self.cur_ind -= 1

    # <def_variables> ::= <var> | <def_variables> <var>
    # Избавимся от левой рекурсии:
    # <def_variables> ::= <var> | <var> <def_variables> 
    def __def_variables(self):

        self.__var()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            if len(self.program1) == 1:
                self.cur_ind -= 1
                return
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected begin', 362)
    
        if self.program1[self.cur_ind] == 'var':
            self.cur_ind -= 1
            self.__def_variables()
        elif self.program1[self.cur_ind] == 'const':
            self.cur_ind -= 1
            self.__def_const()
        else:
            self.cur_ind -= 1

    # <variables> ::= <def_const> <def_variables> | <def_const> | <def_variables> | <def_variables> <def_const>
    def __variables(self):
        self.__def_const()
        self.__def_variables()
        self.__def_const()

    # <start_prog> ::= <program_title> | <variables> | <program_title> <variables>
    def __start_prog(self):
        self.__program_title()
        self.__variables()

    def __assign_address(self):
        tmp = self.cur_ind
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'expression\'', 400)
        if self.program1[self.cur_ind][0] == '@':
            if self.__id(adr=True):
                self.cur_ind += 1
                if self.cur_ind < len(self.program1):
                    if self.program1[self.cur_ind] == ';':
                        self.cur_ind -= 1
                        return True
        self.cur_ind = tmp
        return False

    # <assign> ::= <id> := <expr> | <id> := @<id> | <id> := nil | <id> := <id>^
    def __assign(self, if_stmt=False):
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \':=\'', 399)
        if self.program1[self.cur_ind] != ':=':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \':=\'', 401)
        
        if self.__assign_address():
            return

        self.__math_expr()
    
    def __empty_id_list(self):
        tmp = self.cur_ind
        tmp += 1
        if tmp < len(self.program1):
            if self.program1[tmp] == ')':
                self.cur_ind = tmp - 1
                return True
        return False

    # <read> ::= read(<id_list>) | read()
    def __read(self, if_stmt=False):
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'(\'', 403)
        if self.program1[self.cur_ind] != '(':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'(\'', 405)
        
        if not self.__empty_id_list():
            self.__id_list()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \')\'', 411)
        if self.program1[self.cur_ind] != ')':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \')\'', 405)

    # <write> ::= write(<id_list>) | write()
    def __write(self, if_stmt=False):
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'(\'', 420)
        if self.program1[self.cur_ind] != '(':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'(\'', 42)
        
        if not self.__empty_id_list():
            self.__id_list(True, True, True)

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \')\'', 428)
        if self.program1[self.cur_ind] != ')':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \')\'', 430)

    # <mult_op> ::= * | div | and
    def __mult_op(self):
        return self.program1[self.cur_ind] in ['*', 'div', 'and']
    
    # <add_op> ::= + | - | or | xor
    def __add_op(self):
        return self.program1[self.cur_ind] in ['+', '-', 'or', 'xor']

    # <rel_op> ::= = | <> | < | <= | >= | >
    def __rel_op(self):
        return self.program1[self.cur_ind] in ['=', '<>', '<', '<=', '>=', '>']

    # <simple_logic_expr> ::= <term2>[<adding_operator> <term2>]*
    def __simple_logic_expr(self):
        self.__term2()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 530)
        
        if self.__add_op():
            
            self.__term2()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 538)
            
            if self.__add_op():
                self.__simple_logic_expr()
            else:
                self.cur_ind -= 1

        else:
            self.cur_ind -= 1

    # <term2> ::= <factor2>[<mult_operator> <factor2>]*
    def __term2(self):
        self.__factor2()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 534)
        
        if self.__mult_op():

            self.__factor2()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 542)

            if self.__mult_op():
                self.__term2()
            else:
                self.cur_ind -= 1

        else:
            self.cur_ind -= 1

    # <factor2> ::= <id> | <integer> | <boolean> | ( <logic_expr> ) | not <factor2>
    def __factor2(self):
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 576)
        
        if self.program1[self.cur_ind] == '(':
            self.__logic_expr()
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \')\'', 582)
            if self.program1[self.cur_ind] != ')':
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \')\'', 582)
        elif self.program1[self.cur_ind] == 'not':
            self.__factor2()
        else:
            if not (self.__id(pointer=True) or self.__integer()):
                self.__throw_error(self.cur_ind, f'Incorrect expression', 589)

    # <logic_expr> ::= <simple_logic_expr>[<rel_op> <simple_logic_expr>]
    def __logic_expr(self):
        self.__simple_logic_expr()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 534)
        
        if self.__rel_op():

            self.log_fl = True
            
            self.__simple_logic_expr()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 542)
            
            if self.__rel_op():
                
                self.__logic_expr()
            else:
                self.cur_ind -= 1

        else:
            self.cur_ind -= 1

    # <if> ::= if <logic_expr> then <body> | if <logic_expr> then <body> else <body>
    def __if(self):
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 537)
        
        self.cur_ind -= 1
        self.__logic_expr()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'then\'', 543)
        if self.program1[self.cur_ind] != 'then':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'then\'', 543)
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected body of operator \'if\'', 549)
        if self.program1[self.cur_ind] == ';':
            self.cur_ind -= 1
            return
        elif self.program1[self.cur_ind] == 'else':
            self.cur_ind -= 1
            return
        else:
            self.flag = True
            self.cur_ind -= 1
            self.__body()
        
    def __else(self):

        if self.program1[self.cur_ind] != 'else':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected operator', 654)

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 537)
        
        if self.program1[self.cur_ind] == ';':
            return
        else:
            self.cur_ind -= 1
            self.__body()

    def __body(self):
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 672)
        
        if self.program1[self.cur_ind] == 'begin':
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 573)
  
            self.cur_ind = self.cur_ind - 1 
            self.__code()
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 467)
            if self.program1[self.cur_ind] != 'end':
                self.cur_ind -= 1
                self.__code()
            else:
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 481)  
        else:
            self.__stmt(if_stmt=True)

    # <index_expr> ::= <id> := <math_expr> to <math_expr> | <id> := <math_expr> downto <math_expr>  
    def __index_expr(self):
        
        if self.__id(pointer=True):
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \':=\'', 439)
            if self.program1[self.cur_ind] != ':=':
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \':=\'', 441)

            self.__math_expr()

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'to\downto\'', 447)
            if self.program1[self.cur_ind] not in ['to', 'downto']:
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'to\downto\'', 449)

            self.__math_expr()

        else:
            self.__throw_error(self.cur_ind, f'Incorrect identificator', 437)

    # <for> ::= for <index_expr> do <body>
    def __for(self):
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected expression', 442)
        
        self.__index_expr()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'do\'', 448)
        if self.program1[self.cur_ind] != 'do':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'do\'', 448)
        
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected body in cycle for', 536)
        if self.program1[self.cur_ind] == ';':
            self.cur_ind = self.cur_ind
        else:
            self.cur_ind -= 1
            self.__code() 

    # <stmt> ::= <assign>; | <read>; | <write>; | <if> | <for> 
    def __stmt(self, if_stmt=False):
        fl = False
        flag_of_else = False
        flag_of_if = False
        if self.__id():                              # assign
            self.__assign()
        elif self.program1[self.cur_ind] == 'read':  # read
            self.__read()
        elif self.program1[self.cur_ind] == 'write': # write
            self.__write()
        elif self.program1[self.cur_ind] == 'if':    # if
            flag_of_if = True
            self.__if()
        elif self.program1[self.cur_ind] == 'for':   # for
            fl = True
            self.__for()
        else: 
            self.__throw_error(self.cur_ind, f'Undefined operator', 454)
        if not flag_of_if:        
            self.cur_ind =  self.cur_ind + 1 if not fl else self.cur_ind
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 510)
            if self.program1[self.cur_ind] != ';' and if_stmt:
                self.__else()
                flag_of_else = True
            if self.program1[self.cur_ind] != ';' and not flag_of_else:
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \';\'', 512)
    
    def __check_begin_end(self):
        tmp = self.cur_ind
        if self.program1[tmp] == 'begin':
            tmp += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(tmp - 1, f'Found end of file but expected operator', 573)
            if self.program1[tmp] == 'end':
                tmp += 1
                if tmp >= len(self.program1):
                    self.__throw_error(tmp - 1, f'Found end of file but expected \';\'', 568)
                if self.program1[tmp] != ';':
                    self.__throw_error(tmp, f'Found \'{self.program1[tmp]}\' but expected \';\'', 571)
                else:
                    self.cur_ind = tmp
                    return True
        return False

    # <code> ::= <stmt> | <code> <stmt> | begin end; | begin <code> end;
    # Избавимся от левой рекурсии:
    # <code> ::= <stmt> | <stmt> <code> | begin end; | | begin end; <code> | begin <code> end;
    def __code(self, if_stmt=False):

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 565)
        
        self.cur_ind -= 1
        while True:
            self.cur_ind += 1
            if not self.__check_begin_end():
                break

        if self.program1[self.cur_ind] == 'begin':
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 573)
  
            self.cur_ind = self.cur_ind - 1 
            self.__code(if_stmt)
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 467)
            if self.program1[self.cur_ind] != 'end':
                self.cur_ind -= 1
                self.__code(if_stmt)
            else:
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \';\'', 473)
                if self.program1[self.cur_ind] != ';':
                    self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \';\'', 475)
        else:
            if self.program1[self.cur_ind] != 'end':
                self.__stmt(if_stmt)
            else:
                self.cur_ind -= 1
        
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 481)
            if self.program1[self.cur_ind] != 'end':
                self.cur_ind -= 1
                self.__code(if_stmt)
            else:
                self.cur_ind -= 1    

    # <main> ::= begin end. | begin <code> end.
    def __main(self):
        if self.program1[0] == 'begin':
            self.cur_ind = 0
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 492)
            
            # Внутри begin end может быть сколько угодно точек с запятой.
            if self.program1[self.cur_ind] == ';':
                while self.cur_ind < len(self.program1) and self.program1[self.cur_ind] == ';':
                    self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 501)

            tmp = self.cur_ind
            if self.program1[self.cur_ind] == 'end':
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'.\'', 498)
                if self.program1[self.cur_ind] != '.':
                    self.__throw_error(self.cur_ind - 1, f'Found \'{self.program1[self.cur_ind]}\' but expected \'.\'', 500)
                if self.program1[self.cur_ind] == '.':
                    return
            
            self.cur_ind = tmp - 1
            self.__code()
        
        else: 

            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected begin', 511) 
            
            if self.program1[self.cur_ind] != 'begin':
                self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected begin', 514)
            
            self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 518)
            
            # Внутри begin end может быть сколько угодно точек с запятой.
            if self.program1[self.cur_ind] == ';':
                while self.cur_ind < len(self.program1) and self.program1[self.cur_ind] == ';':
                    self.cur_ind += 1
            if self.cur_ind >= len(self.program1):
                self.__throw_error(self.cur_ind - 1, f'Found end of file but expected operator', 535)

            tmp = self.cur_ind
            if self.program1[self.cur_ind] == 'end':
                self.cur_ind += 1
                if self.cur_ind >= len(self.program1):
                    self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'.\'', 524)
                if self.program1[self.cur_ind] != '.':
                    self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'.\'', 526)
                if self.program1[self.cur_ind] == '.':
                    return
            
            self.cur_ind = tmp - 1
            self.__code()

        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'end\'', 535)
        if self.program1[self.cur_ind] != 'end':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'end\'', 537)
        self.cur_ind += 1
        if self.cur_ind >= len(self.program1):
            self.__throw_error(self.cur_ind - 1, f'Found end of file but expected \'.\'', 540)
        if self.program1[self.cur_ind] != '.':
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but expected \'.\'', 542) 

    # <program> ::= <start_prog> <main> | <main>
    def __program(self):
        if self.program1[self.cur_ind] not in ['program', 'var', 'const', 'begin']:
            self.__throw_error(self.cur_ind, f'Found \'{self.program1[self.cur_ind]}\' but declaration section or begin expected', 547)
        self.__start_prog()
        self.__main()
        if self.cur_ind + 1 < len(self.program1):
            self.__throw_error(self.cur_ind + 1, f'Found \'{self.program1[self.cur_ind + 1]}\' but expected end of file', 551)

    def check(self):
        if not self.program1: # пустой список
            self.error_line = 1
            self.__throw_error(self.error_line, f'Found end of file but declaration section or begin expected', 578)
        self.cur_ind = 0
        self.error_ind = 0
        self.error_line = 0
        self.__program()