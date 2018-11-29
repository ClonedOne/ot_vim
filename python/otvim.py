from enum import Enum
import vim

class OperationType(Enum):
    INSERT = 1
    DELETE = 2


class OTVim:
    def __init__(self, vim, autocmds=lambda: None):
        self._vim = vim
        self._autocmds = autocmds


    def start(self):
        self._buffer = self._vim.current.buffer
        self._cursor_pos = self._vim.current.window.cursor

        #  set up event listeneres
        self._autocmds()


    def stop(self):
        pass


    def check_buffer(self):
        #  print("Check buffer test")
        print(list(self._vim.current.window.cursor))
        #  print(len(self._vim.current.buffer))



def find_difs(b1, b2):
    """ Finds the position of the change in the buffer and returns the change.

    Returns a tuple (X (ROW), Y (COLUMN), CHAR, OPERATION).

    Vim beffer change event only return the new position of the cursor and the
    content of the entire buffer as a 2d array.  This method will identify the
    changed characters and the operation type.  The function should (hopefully)
    run in O(longest line modified * number of lines inserted/deleted).  Due to
    the limited information provided by Vim we will have to dinstinguish
    between different situations.


    LINE INSERT OPERATIONS:

    If it is an insert of a newline then the length of the new line will be 1
    and the first character will be ''.

    A line pasted will still have the cursor in position 0 but will have length
    > 0.


    LINE DELETE OPERATIONS:

    If a single char delete operation removed the newline character, the
    cursor_x will be equal to the length of the line above in the old buffer.
    The length of the above line in the new buffer will also be longer than
    what it was before.

    If a delete operation removed an entire line, cursor_x will be at position
    0 on the line above.  The length of the above line in the new buffer will
    not be changed


    IN-LINE INSERT/DELETE OPERATIONS:

    Transform the corresponding line of both (old and new) buffers into
    position-preserving sets and perfor set subraction to find differences.

    - old_buffer \ new_buffer in case of delete
    - new_buffer \ old_buffer in case of insert

    """

    cursor_y = cursor[0] - 1
    cursor_x = cursor[1]
    cur_line_len = len(b2[cursor_y])
#     old_line_len = len(b1[cursor_y])
    old_line_len = 0
    lines_delta = len(b2) - len(b1)
    diff = []

    if lines_delta > 0: # lines were added

#         if cur_line_len == 1 and b2[cursor_y][0] == '':
#             return [(cursor_y, 0, '\n', OperationType.INSERT)]

#         elif cursor_x == 0 and cur_line_len > 0:
#             for i in range(cursor_y, cursor_y + lines_delta):
#                 for j in b2[i]:
#                     j = j if j != '' else '\n'
#                     diff += (cursor_y, 0, j, OperationType.INSERT)
#             return diff

        for i in range(cursor_y, cursor_y + lines_delta):
            start = cursor_x if i == cursor_y else 0
            for j in range(start, len(b2[i])):
                if b2[i][j] == '': continue
                diff += [(i, j, b2[i][j], OperationType.INSERT)]
            diff += [(i, j+1, '\n', OperationType.INSERT)]
        return diff
#         else:
#             print("ERROR: INSERT NOT HANDLED")


    elif lines_delta < 0: # lines were removed

        if cursor_x == old_line_len and cur_line_len > old_line_len:
            return (cursor_y + 1, 0, '\n', OperationType.DELETE)

        elif cursor_x == 0 and cur_line_len == old_line_len:
        ## TODO: HANDLE MULTIPLE LINES
            return (cursor_y + 1, 0, b1[cursor_y + 1], OperationType.DELETE)

        else:
            print("ERROR: DELETE NOT HANDLED")


    else: # the operation is on the same line

        s1 = set([(cursor_y, pos, b1[cursor_y][pos]) for pos in range(old_line_len)])
        s2 = set([(cursor_y, pos, b2[cursor_y][pos]) for pos in range(cur_line_len)])

        if len(b1[cursor_y]) <= len(b2[cursor_y]): # insert or change operation
            diff = [(elem[0], elem[1], elem[2], OperationType.INSERT) for elem in s2 - s1]

        else: # delete operation
            diff = [(elem[0], elem[1], elem[2], OperationType.DELETE) for elem in s1 - s2]
