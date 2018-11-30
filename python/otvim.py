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

    lines_delta = len(b2) - len(b1)
    print('lines delta:', lines_delta)
    diff = []

    affected_lines = range(cursor_y, cursor_y + 1 + abs(lines_delta))
    print('Affected lines:', affected_lines)

    for line in affected_lines:
        print('line:', line)
        s1 = set()
        s2 = set()

        if (line < len(b1)):
            s1 = set(
                [
                    (line, pos, b1[line][pos])
                    if b1[line][pos] != ''
                    else (line, pos, '\n')
                    for pos in range(len(b1[line]))
                ]
            )

        if (line < len(b2)):
            s2 = set(
                [
                    (line, pos, b2[line][pos])
                    if b2[line][pos] != ''
                    else (line, pos, '\n')
                    for pos in range(len(b2[line]))
                ]
            )

        if (s1 == s2):
           continue

        else:
            diff_set = s1 - s2
            add_set = s2 - s1

        print('diff set:', diff_set)
        print('add set:', add_set)

