#
# T-603-THYD Compilers
# Project: Lexer Skeleton for ChocoPy 2022
#
from enum import Enum
from re import S
from typing import NamedTuple


# The token types the Lexer recognizes.
class Tokentype(Enum):
    EOI = 0  # end of input
    Unknown = 1  # unknown

    # Keywords
    KwNone = 2  # None
    KwPass = 3  # pass
    KwBreak = 4  # break
    KwContinue = 5  # continue
    KwImport = 6  # import
    KwFrom = 7  # from
    KwAs = 8  # as
    KwClass = 9  # class
    KwIf = 10  # if
    KwElif = 11  # elif
    KwElse = 12  # else
    KwFor = 13  # while
    KwWhile = 14  # while
    KwWith = 15  # while
    KwDef = 16  # def
    KwReturn = 17  # return
    KwDel = 18  # del
    KwAssert = 19  # assert
    KwGlobal = 20  # global
    KwNonLocal = 21  # nonlocal

    KwTry = 22  # try
    KwExcept = 23  # except
    KwRaise = 24  # raise
    KwFinally = 25  # finally

    KwAsync = 26  # async
    KwAwait = 27  # away
    KwYield = 28  # yield

    KwLambda = 29  # lambda

    # Operators
    OpOr = 30  # or
    OpAnd = 31  # and
    OpNot = 32  # not
    OpIs = 33  # is
    OpIn = 34  # in

    OpPlus = 35  # +
    OpMinus = 36  # -
    OpMultiply = 37  # *
    OpIntDivide = 38  # //
    OpModulus = 39  # %

    OpLt = 40  # <
    OpGt = 41  # >
    OpLtEq = 42  # <=
    OpGtEq = 43  # >=
    OpEq = 44  # ==
    OpNotEq = 45  # !=
    OpAssign = 46  # =

    # Punctuation marks
    ParenthesisL = 47  # (
    ParenthesisR = 48  # )
    BracketL = 49  # [
    BracketR = 50  # ]
    Comma = 51  # ,
    Colon = 52  # :
    Period = 53  # .
    Arrow = 54  # ->

    # Other
    BoolTrueLiteral = 55  # True
    BoolFalseLiteral = 56  # False
    IntegerLiteral = 57  # digits (see project description)
    StringLiteral = 58  # string literal (see project description)
    Identifier = 59  # name (see project description)
    Indent = 60  # indentation
    Dedent = 61  # dedentation
    Newline = 62  # newline


class Location(NamedTuple):
    line: int
    col: int


class Token(NamedTuple):
    type: Tokentype
    lexeme: str
    location: Location


class SyntaxErrorException(Exception):
    def __init__(self, message, loc):
        self.message = message
        self.location = loc


class Lexer:
    # Private map of reserved words.
    __reserved_words = {
        "None": Tokentype.KwNone,
        "pass": Tokentype.KwPass,
        "break": Tokentype.KwBreak,
        "continue": Tokentype.KwContinue,
        "import": Tokentype.KwImport,
        "from": Tokentype.KwFrom,
        "as": Tokentype.KwAs,
        "class": Tokentype.KwClass,
        "if": Tokentype.KwIf,
        "elif": Tokentype.KwElif,
        "else": Tokentype.KwElse,
        "for": Tokentype.KwFor,
        "while": Tokentype.KwWhile,
        "with": Tokentype.KwWith,
        "def": Tokentype.KwDef,
        "return": Tokentype.KwReturn,
        "del": Tokentype.KwDel,
        "assert": Tokentype.KwAssert,
        "global": Tokentype.KwGlobal,
        "nonlocal": Tokentype.KwNonLocal,
        "try": Tokentype.KwTry,
        "except": Tokentype.KwExcept,
        "raise": Tokentype.KwRaise,
        "finally": Tokentype.KwFinally,
        "async": Tokentype.KwAsync,
        "await": Tokentype.KwAwait,
        "yield": Tokentype.KwYield,
        "lambda": Tokentype.KwLambda,
        "or": Tokentype.OpOr,
        "and": Tokentype.OpAnd,
        "not": Tokentype.OpNot,
        "is": Tokentype.OpIs,
        "in": Tokentype.OpIn,
        "True": Tokentype.BoolTrueLiteral,
        "False": Tokentype.BoolFalseLiteral
    }

    def __read_next_char(self):
        """
        Private helper routine. Reads the next input character, while keeping
        track of its location within the input file.
        """
        if self.eof:
            self.ch = ''
            return

        if self.ch == '\n':
            self.line += 1
            self.col = 1
        else:
            self.col += 1

        self.ch = self.f.read(1)

        if not self.ch:  # eof
            self.ch = '\n'
            self.line += 1
            self.col = 1
            self.eof = True

    def __init__(self, f):
        """
        Constructor for the lexer.
        :param: f handle to the input file (from open('filename')).
        """
        self.f, self.ch, self.line, self.col = f, '', 1, 0
        self.legal_indent_levels = [1]
        self.beginning_of_logical_line = True
        self.eof = False
        self.__read_next_char()  # Read in the first input character (self.ch).        

    def remove_spaces_tabs_emptylines(self):
        # Remove spaces, tabs, comments, and "empty" lines, if any, before matching the next Tokentype.
        # skip character if space or tab
        while (self.ch == ' ' or self.ch == '\t'):
            self.__read_next_char()

    def ignore_comments(self):
        # When we see a comment start, skip that line: read characters until we see a newline character
        if self.ch == '#':
            while self.ch != '\n':
                self.__read_next_char()

    def check_indentation(self, loc):
        if loc.col > self.legal_indent_levels[-1]:
            self.legal_indent_levels.append(loc.col)
            token = Token(Tokentype.Indent, "INDENT", loc)
            return token
        else:
            while loc.col < self.legal_indent_levels[-1]:
                self.legal_indent_levels.pop()

            if loc.col != self.legal_indent_levels[-1]:
                raise SyntaxErrorException("Non matching indentation", loc)
            else:
                token = Token(Tokentype.Dedent, "DEDENT", loc)
                return token
    
    def match_lexeme(self, loc): # TODO: needs fix asap
        if self.ch == '':
            token = Token(Tokentype.EOI, '', loc)
            return token
        
        elif self.ch == '+':
            token = Token(Tokentype.OpPlus, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '-':
            self.__read_next_char()
            if self.ch == '>':
                token = Token(Tokentype.Arrow, self.ch, loc)
                self.__read_next_char()
                return token
            else:
                token = Token(Tokentype.OpMinus, self.ch, loc) # TODO: why there was no "read next char" in here? Did I made a 
                self.__read_next_char()                        # mistake by adding it, or there was a reason? Was the same for almost
                return token                                   # all the other symbols that needed a check with an if
        
        elif self.ch == '*':
            token = Token(Tokentype.OpMultiply, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '%':
            token = Token(Tokentype.OpModulus, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '/':
            self.__read_next_char()
            if self.ch == '/':
                token = Token(Tokentype.OpIntDivide, "//", loc)
                self.__read_next_char()
                return token
            else:
                # TODO: check for single slash?
                ...
        
        elif self.ch == '=':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpEq, "==", loc)
                self.__read_next_char()
                return token
            else:
                token = Token(Tokentype.OpAssign, "=", loc)
                self.__read_next_char()
                return token
        
        elif self.ch == '!':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpNotEq, "!=", loc)
                self.__read_next_char()
                return token
            else:
                token = Token(Tokentype.Unknown, self.ch, loc) # TODO: check if ! does anything
                self.__read_next_char()
                return token
        
        elif self.ch == '<':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpLtEq, '<=', loc)
                self.__read_next_char()
                return token
            else:
                token = Token(Tokentype.OpLt, '<', loc)
                self.__read_next_char()
                return token
        
        elif self.ch == '>':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpGtEq, ">=", loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpGt, '>', loc) 
                self.__read_next_char()
                return token
        
        elif self.ch == ')':
            token = Token(Tokentype.ParenthesisR, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '(':
            token = Token(Tokentype.ParenthesisL, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == ']':
            token = Token(Tokentype.BracketR, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '[':
            token = Token(Tokentype.BracketL, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '.':
            token = Token(Tokentype.Period, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == ':':
            token = Token(Tokentype.Colon, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == ',':
            token = Token(Tokentype.Comma, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '\n':
            token = Token(Tokentype.Newline, self.ch, loc)
            self.__read_next_char()
            return token
        
        elif self.ch == '"': # TODO: Check for escaped characters
            # Check for a string literal. Raise "Unterminated string"
            # syntax error exception if the string doesn't close on the line.
            self.__read_next_char()
            while self.ch != '"':
                if self.ch == '\n': 
                    raise SyntaxErrorException("Unterminated string", loc)              
                if self.ch == '\\': # TODO: check for possible errors. Too tired rn to think about that
                    self.__read_next_char() # Are we sure that we want to ignore everything that comes after a \ ?
                    pass
                self.__read_next_char()
            
            token = Token(Tokentype.StringLiteral, "?", loc) # Why the question mark is the identifier?
            self.__read_next_char()
            return token

        else:   # Check for identifiers/reserved words.
            if ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_'):  # Match an identifier.
                chars = [self.ch]
                while ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_'):
                    self.__read_next_char()
                    chars.append(self.ch)

                joined_str = ''.join(chars)
                if joined_str in self.__reserved_words.keys():
                    token = Token(self.__reserved_words.get(joined_str), joined_str, loc)
                    self.__read_next_char()
                    return token
                else:
                    token = Token(Tokentype.Identifier, joined_str, loc)
                    self.__read_next_char()
                    return token
            
            elif self.ch.isdigit(): # Match a number literal.
                chars = [self.ch]
                while self.ch.isdigit():
                    self.__read_next_char()
                    chars.append(self.ch)
            
                token = Token(Tokentype.IntegerLiteral, ''.join(chars), loc) # TODO: shouldn't we check for doubles too?
                self.__read_next_char()
                return token
            
            else:
                # Return Unknown if no other known token is matched.
                token = Token(Tokentype.Unknown, self.ch, loc)
                self.__read_next_char()
                return token
        

    def next(self):
        """
        Match the next token in input.
        :return: Token with information about the matched Tokentype.
        """
        self.remove_spaces_tabs_emptylines()
        self.ignore_comments()

        # Record the start location of the lexeme we're matching.
        loc = Location(self.line, self.col)
        
        # Ensure indentation is correct, emitting (returning) an INDENT/DEDENT token if called for.
        if self.beginning_of_logical_line:
            if loc.col == self.legal_indent_levels[-1]:         # TODO: SOLID principles violation detected, please fix this 
                pass
            else:
                return self.check_indentation(loc)
            
            
        # token = self.match_lexeme(loc)

        # Now, try to match a lexeme.
        if self.ch == '':
            token = Token(Tokentype.EOI, '', loc)
        
        elif self.ch == '+':
            token = Token(Tokentype.OpPlus, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '-':
            self.__read_next_char()
            if self.ch == '>':
                token = Token(Tokentype.Arrow, self.ch, loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpMinus, self.ch, loc)
        
        elif self.ch == '*':
            token = Token(Tokentype.OpMultiply, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '%':
            token = Token(Tokentype.OpModulus, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '/':
            self.__read_next_char()
            if self.ch == '/':
                token = Token(Tokentype.OpIntDivide, "//", loc)
                self.__read_next_char()
            else:
                # TODO: check for single slash?
                ...
        
        elif self.ch == '=':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpEq, "==", loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpAssign, "=", loc)
        
        elif self.ch == '!':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpNotEq, "!=", loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.Unknown, self.ch, loc) # TODO: check if ! does anything
                self.__read_next_char()
        
        elif self.ch == '<':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpLtEq, '<=', loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpLt, '<', loc)
        
        elif self.ch == '>':
            self.__read_next_char()
            if self.ch == '=':
                token = Token(Tokentype.OpGtEq, ">=", loc)
                self.__read_next_char()
            else:
                token = Token(Tokentype.OpGt, '>', loc)
        
        elif self.ch == ')':
            token = Token(Tokentype.ParenthesisR, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '(':
            token = Token(Tokentype.ParenthesisL, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == ']':
            token = Token(Tokentype.BracketR, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '[':
            token = Token(Tokentype.BracketL, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '.':
            token = Token(Tokentype.Period, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == ':':
            token = Token(Tokentype.Colon, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == ',':
            token = Token(Tokentype.Comma, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '\n':
            token = Token(Tokentype.Newline, self.ch, loc)
            self.__read_next_char()
        
        elif self.ch == '"': # TODO: Check for escaped characters
            # Check for a string literal. Raise "Unterminated string"
            # syntax error exception if the string doesn't close on the line.
            self.__read_next_char()
            while self.ch != '"':
                if self.ch == '\n': 
                    raise SyntaxErrorException("Unterminated string", loc)              
                if self.ch == '\\': # TODO: check for possible errors. Too tired rn to think about that
                    self.__read_next_char() # Are we sure that we want to ignore everything that comes after a \ ?
                    pass
                self.__read_next_char()
            
            token = Token(Tokentype.StringLiteral, "?", loc) # Why the question mark is the identifier?
            self.__read_next_char()

        else:   # Check for identifiers/reserved words.
            if ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_'):  # Match an identifier.
                chars = [self.ch]
                while ('a' <= self.ch <= 'z') or ('A' <= self.ch <= 'Z') or (self.ch == '_'):
                    self.__read_next_char()
                    chars.append(self.ch)

                joined_str = ''.join(chars)
                if joined_str in self.__reserved_words.keys():
                    token = Token(self.__reserved_words.get(joined_str), joined_str, loc)
                else:
                    token = Token(Tokentype.Identifier, joined_str, loc)
            
            elif self.ch.isdigit(): # Match a number literal.
                chars = [self.ch]
                while self.ch.isdigit():
                    self.__read_next_char()
                    chars.append(self.ch)
            
                token = Token(Tokentype.IntegerLiteral, ''.join(chars), loc) # TODO: shouldn't we check for doubles too?
            
            else:
                # Return Unknown if no other known token is matched.
                token = Token(Tokentype.Unknown, self.ch, loc)
                self.__read_next_char()

        self.beginning_of_logical_line = token.type == Tokentype.Newline

        return token



# Questions for the teacher:
# Do we need to check escaped literals?
# One dedentation or multiple?
# What kind of tests?
# What about single slash / ?
# Lexemes for indent, dedent, tabs, string literals, why question mark for literal...?