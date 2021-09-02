class Parser:

    # program_text - текст исходной программы
    def __init__(self, program_text):
        self.program_text = program_text

    # Преобразование в массив строк без переносов строки
    def to_string_list1(self):
        words = []
        word = ''
        text = self.program_text.lower()
        text = text.replace(':=', '$')
        text = text.replace('<>', '?')
        text = text.replace('>=', '!')
        text = text.replace('<=', '%')
        counter = 0
        sign = ''
        for i, letter in enumerate(text):
            if letter.isdigit() or letter.isalpha() or letter == '@' or letter == '^' or letter in ['+', '-']:
                if letter in ['+', '-']:
                    counter += 1
                    if counter == 1:
                        sign += letter
                    else:
                        word += letter
                else:
                    word += letter
            else:
                if counter == 1:
                    words.append(sign + word)
                    sign = ''
                else:
                    words.append(sign)
                    sign = ''
                if counter != 1:
                    words.append(word)
                if letter:
                    words.append(letter)
                word = ''
        words = list(filter(lambda item: item != '\t' and item != '\n' and item != '' and item != ' ', [':=' if x == '$' else x for x in words]))
        
        for i, item in enumerate(words):
            if item == '?': words[i] = '<>'
            if item == '!': words[i] = '>='
            if item == '%': words[i] = '<='
        
        return words

    # Преобразование в массив строк с переносом строк
    def to_string_list2(self):
        words = []
        word = ''
        text = self.program_text.lower()
        text = text.replace(':=', '$')
        text = text.replace('<>', '?')
        text = text.replace('>=', '!')
        text = text.replace('<=', '%')
        counter = 0
        sign = ''
        for i, letter in enumerate(text):
            if letter.isdigit() or letter.isalpha() or letter == '@' or letter == '^' or letter in ['+', '-']:
                if letter in ['+', '-']:
                    counter += 1
                    if counter == 1:
                        sign += letter
                    else:
                        word += letter
                else:
                    word += letter
            else:
                if counter == 1:
                    words.append(sign + word)
                    sign = ''
                else:
                    words.append(sign)
                    sign = ''
                if counter != 1:
                    words.append(word)
                if letter:
                    words.append(letter)
                word = ''
        words = list(filter(lambda item: item != '\t' and item != '' and item != ' ', [':=' if x == '$' else x for x in words]))

        for i, item in enumerate(words):
            if item == '?': words[i] = '<>'
            if item == '!': words[i] = '>='
            if item == '%': words[i] = '<='
        
        return words
    
