import sys


class Mod(object):
    def add_next(self, mod):
        self.next = mod


class InputMod(Mod):
    def __init__(self, src):
        self.src = src

    def start(self):
        while True:
            if self.src.has_trace():
                trc = self.src.read_trace()
            else:
                sys.exit()
            self.next.run(trc)


class ProcMod(Mod):
    def run(self, trc):
        self.do_job(trc)
        self.next.run(trc)

    def do_job(self, trc):
        pass
