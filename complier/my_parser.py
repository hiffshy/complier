class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def parse(self):
        try:
            self.parse_printf()
            if not self.at_end():
                self.raise_error("Ожидается конец выражения")
        except ParseError:
            pass
        return self.errors

    def parse_printf(self):
        self.consume('PRINTF', "Ожидается 'printf'")
        self.consume('LPAREN', "Ожидается '('")
        self.parse_format_string()
        self.parse_arguments()
        self.consume('RPAREN', "Ожидается ')'")
        self.consume('SEMICOLON', "Ожидается ';'")

    # def parse_format_string(self):
    #     self.consume('STRING', "Ожидается строка формата")
    def parse_format_string(self):
        token = self.consume('STRING', "Ожидается строка формата")
        if token:
            # Убираем внешние кавычки
            content = token.value[1:-1]
            allowed_specifiers = "disfcuoxp"
            index = 0
            while index < len(content):
                if content[index] == '%':
                    if index + 1 < len(content):
                        spec = content[index + 1]
                        if spec not in allowed_specifiers:
                            # Здесь вычисляем позицию ошибки.
                            # Если позиция токена хранится как позиция открывающей кавычки,
                            # то прибавляем смещение внутри содержимого.
                            col = token.position[1] + index
                            line = token.position[0]
                            error_msg = f"Строка {line}:{col} - Неверный спецификатор '%{spec}'"
                            self.errors.append(error_msg)
                            raise ParseError()
                        # Если спецификатор корректный – пропускаем оба символа
                        index += 2
                    else:
                        # Если после '%' нет символа – обрезанный спецификатор
                        col = token.position[1] + index
                        line = token.position[0]
                        error_msg = f"Строка {line}:{col} - Обрезанный спецификатор '%'"
                        self.errors.append(error_msg)
                        raise ParseError()
                else:
                    index += 1

    def parse_arguments(self):
        while self.match('COMMA'):
            self.parse_argument()

    def parse_argument(self):
        if not self.match('IDENT') and not self.match('NUMBER'):
            self.raise_error("Ожидается аргумент")

    def consume(self, token_type, error_msg):
        if self.current_token() is None:
            self.raise_error(f"{error_msg} (неожиданный конец файла)")
            return None

        if self.current_token().type == token_type:
            token = self.current_token()  # сохраняем токен
            self.advance()
            return token  # возвращаем его
        else:
            self.raise_error(error_msg)
            return None

        # def consume(self, token_type, error_msg):
    #     # Добавляем проверку на конец потока токенов
    #     if self.current_token() is None:
    #         self.raise_error(f"{error_msg} (неожиданный конец файла)")
    #         return

        if self.current_token().type == token_type:
            self.advance()
        else:
            self.raise_error(error_msg)

    def raise_error(self, message):
        # Обрабатываем случай отсутствия токена
        if self.current_token() is None:
            self.errors.append(f"Ошибка: {message} (в конце файла)")
            raise ParseError()

        token = self.current_token()
        error_text = (
            f"Строка {token.position[0]}:{token.position[1]} - {message}\n"
            f"Найден токен: '{token.value}' ({token.type})"
        )
        self.errors.append(error_text)
        raise ParseError()

    def advance(self):
        self.pos += 1

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def at_end(self):
        return self.pos >= len(self.tokens)

    def match(self, token_type):
        if self.current_token() and self.current_token().type == token_type:
            self.advance()
            return True
        return False