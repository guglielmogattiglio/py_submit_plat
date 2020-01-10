class MyExc(Exception):
    def __init__(self, line_num, exc_message):
        self.line_num = line_num
        self.exc_message = exc_message


def get_n_line(s, n):
    c = 0
    start = -1
    for i in range(len(s)):
        if s[i] == '\n':
            c += 1
            if c == n:
                start = i
            if c == n + 1:
                return s[start:i]
