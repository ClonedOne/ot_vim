from enum import Enum
from pprint import pprint
import vim

class OperationType(Enum):
    INSERT = 1
    DELETE = 2


class OTVim:
    def __init__(self, vim, autocmds=lambda: None):
        self._vim = vim
        self._autocmds = autocmds


    def start(self):
        self._buffer = self._vim.current.buffer[:]
        self._cursor_pos = self._vim.current.window.cursor

        #  set up event listeneres
        self._autocmds()


    def stop(self):
        pass


    def check_buffer(self):
        #  print("Check buffer test")
        print((self._vim.current.window.cursor))
        #  pprint([i for i in self._vim.current.buffer])

        new_buffer = self._vim.current.buffer[:]
        new_cursor = self._vim.current.window.cursor

        diff = find_difs(self._buffer, new_buffer, new_cursor)

        self._buffer = new_buffer
        self._cursor_pos = new_cursor

        #  print(new_cursor)



def find_difs(b1, b2, cursor):
    """ Finds the position of the change in the buffer and returns the change.

    Returns a list of tuples (1D-POS, CHAR, OPERATION).

    """

    print (len(b1), b1)
    print (len(b2), b2)

    cursor_y = cursor[0] - 1
    cursor_x = cursor[1]

    lines_delta = len(b2) - len(b1)
    print('lines delta:', lines_delta)
    diff = []

    start = cursor_y - 1 if cursor_y - 1 > 0 else 0

    affected_lines = range(start, cursor_y + 1 + abs(lines_delta))
    print('Affected lines:', affected_lines)

    for line in affected_lines:
        print('line:', line)
        s1 = set()
        s2 = set()

        if (line < len(b1)):
            print('b1 line:', b1[line])
            s1 = set([(line, pos, b1[line][pos]) for pos in range(len(b1[line]))])
            if (line + 1 < len(b1)):
                s1.add((line, len(b1[line]), '\n'))

        if (line < len(b2)):
            print('b2 line:', b2[line])
            s2 = set([(line, pos, b2[line][pos]) for pos in range(len(b2[line]))])
            if (line + 1 < len(b2)):
                s2.add((line, len(b2[line]), '\n'))

        print('s1:', s1)
        print('s2:', s2)

        if (s1 == s2):
           continue

        else:
            sub_set = s1 - s2
            add_set = s2 - s1
            print('sub set:', sub_set)
            print('add set:', add_set)

        for r in sub_set:
            pos_1d = sum([(len(b1[line]) + 1) for line in range(r[0])]) + r[1]
            print(pos_1d)
            diff.append((pos_1d, r[2], OperationType.DELETE))

        for i in add_set:
            pos_1d = sum([(len(b2[line]) + 1) for line in range(i[0])]) + i[1]
            diff.append((pos_1d, i[2], OperationType.INSERT))

    return diff
