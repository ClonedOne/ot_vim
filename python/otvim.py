from enum import Enum
import threading
import sched
import time
import vim

import doc_client

class OperationType(Enum):
    INSERT = 1
    DELETE = 2


class OTVim:
    def __init__(self, vim, autocmds=lambda: None):
        self._vim = vim
        self._autocmds = autocmds
        self.counter = 0


    def start(self, name, host, port):
        self._buffer = self._vim.current.buffer[:]
        self._cursor_pos = self._vim.current.window.cursor

        self._name = name
        self._ip =  host
        self._port = port

        self.logfile = open('logfile', 'w')


        print("Opening file: " + name + " on " +  host + ":" + port)

        self._still_alive = True

        self.dc = doc_client.DocClient(self._name, self._ip, int(self._port))

        self.listen_server_updates()

        #  set up event listeneres
        self._autocmds()


    def stop(self):
        self._still_alive = False


    def check_buffer(self):
        print("Check buffer test")
        #  print((self._vim.current.window.cursor))
        #  print([i for i in self._vim.current.buffer]) 
        #  print(test)
        new_buffer = self._vim.current.buffer[:]
        new_cursor = self._vim.current.window.cursor

        diff = find_difs(self._buffer, new_buffer, new_cursor)

        for d in diff:
            op = (d[2].value, ord(d[1]), d[0])
            self.logfile.write("called send_op: {}, {}, {}\n".format(*op))
            self.logfile.flush()
            self.dc.send_op(op)

        self._buffer = new_buffer
        self._cursor_pos = new_cursor

        #  print(new_cursor)


    def listen_server_updates(self):
        self.serv_conn = threading.Thread(target=self.server_connection)
        self.serv_conn.start()


    def server_connection(self):
        self.schedule = sched.scheduler(time.time, time.sleep)
        while(1):
            if not self._still_alive: exit(0)
            self.schedule.enter(0.05, 1, self.check_for_updates)
            self.schedule.run()


    def check_for_updates(self):
        #  print("counter:", self.counter)
        self.counter += 1
        #  self.insert_char('a', self.counter)
        #  if self.counter % 3 == 0:
        #      self.delete_char('a', len(self._vim.current.buffer[0]) - 1)
        inc_ops = self.dc.recv_ops()
        
        for inc_op in inc_ops:
            self.logfile.write("received op: {}, {}, {}\n".format(*inc_op))
            self.logfile.flush()
            if inc_op[0] == 1:
                self.insert_char(chr(inc_op[1]), inc_op[2])
            else:
                self.delete_char(chr(inc_op[1]), inc_op[2])


    def insert_char(self, char, pos):
        pos1d = 0
        for row in range(len(self._vim.current.buffer)):
            for col in range(len(self._vim.current.buffer[row])):
                if pos1d == pos:
                    if self._vim.current.buffer[row][col] == char: return
                    temp_string = self._vim.current.buffer[row]
                    new_str = temp_string[:col] + char + temp_string[col+1:]
                    self._vim.current.buffer[row] = new_str
                    self._vim.command(":redraw")
                    return
                pos1d+=1
            
        if pos >=  pos1d:
            if char == '\n':
                self._vim.current.buffer.append('')
                self._vim.command(":redraw")
            else:
                self._vim.current.buffer[row] += char
                self._vim.command(":redraw")


    def delete_char(self, char, pos):
        #  print(pos)
        pos1d = 0
        if pos <= 0:
            self._vim.current.buffer[0] = ""
            self._vim.command(":redraw")
            return

        for row in range(len(self._vim.current.buffer)):
            for col in range(len(self._vim.current.buffer[row])):
                if pos1d == pos:
                    if self._vim.current.buffer[row][pos] == char: return
                    #  if self._vim.current.buffer[row][pos] != char:
                        #  self.logfile.write('ERROR DELETE: Char different from specified\n')
                    
                    temp_string = self._vim.current.buffer[row]
                    new_str = temp_string[:col] + temp_string[col+1:]
                    
                    #  print(new_str)
                    self._vim.current.buffer[row] = new_str
                    self._vim.command(":redraw")

                pos1d+=1
            
        if pos > pos1d:
            print('Character not in the buffer')





def find_difs(b1, b2, cursor):
    """ Finds the position of the change in the buffer and returns the change.

    Returns a list of tuples (1D-POS, CHAR, OPERATION).

    """

    #  print (len(b1), b1)
    #  print (len(b2), b2)

    cursor_y = cursor[0] - 1
    cursor_x = cursor[1]

    lines_delta = len(b2) - len(b1)
    #  print('lines delta:', lines_delta)
    diff = []

    start = cursor_y - 1 if cursor_y - 1 > 0 else 0

    affected_lines = range(start, cursor_y + 1 + abs(lines_delta))
    #  print('Affected lines:', affected_lines)

    for line in affected_lines:
        #  print('line:', line)
        s1 = set()
        s2 = set()

        if (line < len(b1)):
            #  print('b1 line:', b1[line])
            s1 = set([(line, pos, b1[line][pos]) for pos in range(len(b1[line]))])
            if (line + 1 < len(b1)):
                s1.add((line, len(b1[line]), '\n'))

        if (line < len(b2)):
            #  print('b2 line:', b2[line])
            s2 = set([(line, pos, b2[line][pos]) for pos in range(len(b2[line]))])
            if (line + 1 < len(b2)):
                s2.add((line, len(b2[line]), '\n'))

        #  print('s1:', s1)
        #  print('s2:', s2)

        if (s1 == s2):
            continue

        else:
            sub_set = s1 - s2
            add_set = s2 - s1
            #  print('sub set:', sub_set)
            #  print('add set:', add_set)

        for r in sub_set:
            pos_1d = sum([(len(b1[line]) + 1) for line in range(r[0])]) + r[1]
            #  print(pos_1d)
            diff.append((pos_1d, r[2], OperationType.DELETE))

        for i in add_set:
            pos_1d = sum([(len(b2[line]) + 1) for line in range(i[0])]) + i[1]
            diff.append((pos_1d, i[2], OperationType.INSERT))

    return diff
