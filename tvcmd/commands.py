import argparse
from . import manager, io, cons, errors

import logging
def log(): return logging.getLogger(__name__)

# manager singleton instance shortcut
m = manager.instance

class Base(argparse.ArgumentParser):
    
    def _print_message(self, message, file=None):
        if message:
            io.msg(message)
    
    def _complete(self, text, options, elist):
        _options = [ opt for opt in options if opt.startswith(text) ]
        _episodes = elist.complete_text(text)
        
        return _options + _episodes
    
    def _mark(self, elist, status):
        io.msg("Marking %d episode(s) as %s"%(len(elist), cons.ENUM_EPISODE_STATUS[status]["text"]))
        if len(elist): self.modified = True
        
        for e in elist:
            e.status = status
            io.msg(e.print_str())
    
    def do(self):
        pass
    
    def complete(self):
        pass

def Reload(Base):
    
    def __init__(self):
        super().__init__(self, prog="reload", description="Reload episodes list and status", epilog="example: reload")
    
    def do(self, line):
        try: args = self.parse_args(line.split())
        except SystemExit: return
        
        if m.modified:
            answer = io.ask_yn("Status database has been modified. Are you sure you want to reload?")
            if not answer: return
        
        try:
            m.load()
        except errors.ConfigError as ex:
            io.msg("Error loading: %s" % (ex))
            
def Update(Base):
    
    def __init__(self):
        super().__init__(self, prog="update", description="Updates episodes from source", epilog="example: upload")
    
    def do(self, line):
        args = self.parse_args(line.split())
        
        for show in m.shows:
            io.msg("Tracking show %s ... "%(show.name), end="")
            try:
                l = m.track(show.name)
                io.msg("OK: %d episodes found"%(len(l)))
            except Exception as ex:
                io.msg("FAIL: (%s)"%(ex))
        
        try:
            io.msg("Saving cache ... ", end="")
            self.save_cache()
            io.msg("OK")
        except Exception as ex:
            io.msg("FAIL: (%s)"%(ex))

def Save(Base):
    
    def __init__(self):
        super().__init__(self, prog="save", description="Save episodes status DB and cache", epilog="example: save")
        
    def do(self, line):
        try:
            io.msg("Saving ... ", end="")
            m.save_status()
            io.msg("OK")
        except errors.ConfigError as ex:
            io.msg("FAIL: (%s)"%(ex))
            
def Shows(Base):
    
    def __init__(self):
        super().__init__(self, prog="save", description="Save episodes status DB and cache", epilog="example: save")
    
    def do(self, line):
        args = self.parse_args(line.split())
        
        l = m.shows
        io.msg(l.print_str())

def Search(Base):
    
    def __init__(self):
        super().__init__(self, prog="save", description="Save episodes status DB and cache", epilog="example: save")
        self.add_argument("filter", metavar="SHOW", help="show name or part, ex: the offi")
    
    def do(self, line):
        args = self.parse_args([line])
        
        io.msg("Searching [%s] ... "%(args.filter), end="")
        try:
            l = m.search_shows(args.filter)
            io.msg("OK: %d shows found"%(len(l)))
            if (len(l)): io.msg("\n"+l.print_str())
        except Exception as ex:
            io.msg("FAIL: (%s)"%(ex))

def New(Base):
    
    def __init__(self):
        super().__init__(self, prog="new", description="Mark episodes as NEW", epilog="example: new lost.s01* lost.s02*")
        self.add_argument("filters", metavar="EPISODE", nargs="*", default=["*"], help="episode name or filter, ex: lost.s01e0*")
    
    def do(self, line):
        args = self.parse_args(line.split())
        
        l = episode.List()
        for pattern in args.filters:
            l.extend(m.episodes.filter(lambda e: e.match(pattern) and not e.future() and e.status in [cons.ADQUIRED, cons.SEEN]))
        
        self._mark(l, cons.NEW)
    
    def complete(self, text, line, start_index, end_index):
        return self._complete(text, ["-h", "--help"], m.episodes.filter(lambda e: not e.future() and e.status in [cons.ADQUIRED, cons.SEEN]))

def Adquire(Base):
    
    def __init__(self):
        super().__init__(self, prog="adquire", description="Mark episodes as ADQUIRED", epilog="example: adquire lost.s01* lost.s02*")
        self.add_argument("filters", metavar="EPISODE", nargs="*", default=["*"], help="episode name or filter, ex: lost.s01e0*")
    
    def do(self, line):
        args = self.parse_args(line.split())
        
        l = episode.List()
        for pattern in args.filters:
            l.extend(m.episodes.filter(lambda e: e.match(pattern) and not e.future() and e.status in [cons.NEW]))
        
        self._mark(l, cons.ADQUIRED)
    
    def complete(self, text, line, start_index, end_index):
        return self._complete(text, ["-h", "--help"], m.episodes.filter(lambda e: not e.future() and e.status in [cons.NEW]))

def See(Base):
    
    def __init__(self):
        super().__init__(self, prog="see", description="Mark episodes as SEEN", epilog="example: see lost.s01* lost.s02*")
        self.add_argument("filters", metavar="EPISODE", nargs="*", default=["*"], help="episode name or filter, ex: lost.s01e0*")
    
    def do(self, line):
        args = self.parse_args(line.split())
        
        l = episode.List()
        for pattern in args.filters:
            l.extend(m.episodes.filter(lambda e: e.match(pattern) and not e.future() and e.status in [cons.NEW, cons.ADQUIRED]))
        
        self._mark(l, cons.SEEN)
    
    def complete(self, text, line, start_index, end_index):
        return self._complete(text, ["-h", "--help"], m.episodes.filter(lambda e: not e.future() and e.status in [cons.NEW, cons.ADQUIRED]))

def Format(Base):
    
    def __init__(self):
        super().__init__(self, prog="format", description="print episodes with given formats", epilog="example: format lost*")
        self.add_argument("filters", metavar="EPISODE", nargs="*", default=["*"], help="episode name or filter, ex: lost.s01e0*")

    def do(self, line):
        args = self.parse_args(line.split())
        
        l = episode.List()
        for pattern in args.filters:
            l.extend(m.episodes.filter(lambda e: e.match(pattern) and not e.future() and e.status in [cons.NEW]))
        
        if len(m.formats) == 0:
            io.msg("no formats defined, please check your config")
            return
        
        for e in l:
            for fmt in m.formats:
                io.msg(e.format(fmt))
    
    def complete(self, text, line, start_index, end_index):
        return self._complete(text, ["-h", "--help"], m.episodes.filter(lambda e: not e.future() and e.status in [cons.NEW]))

def Ls(Base):
    
    def __init__(self):
        super().__init__(self, prog="ls", description="Show episodes information", epilog="example: ls -as lost*")
        self.add_argument("-n", "--new", action="store_true", help="list NEW episodes (default)")
        self.add_argument("-a", "--adquired", action="store_true", help="list ADQUIRED episodes (default)")
        self.add_argument("-s", "--seen", action="store_true", help="list SEEN episodes")
        self.add_argument("-f", "--future", action="store_true", help="list episodes not aired to date, implies -nas")
        self.add_argument("filters", metavar="EPISODE", nargs="*", default=["*"], help="episode name or filter, ex: lost.s01e0*")

    def do(self, line):
        args = self.parse_args(line.split())
        
        l = episode.List()
        for pattern in args.filters:
            l.extend(m.episodes.filter(lambda e: e.match(pattern)))
        
        # defaults: NEW and ADQUIRED
        if not (args.new or args.adquired or args.seen or args.future):
            args.new = args.adquired = True
        
        if args.future:
            l = l.filter(lambda e: e.future())
            # future implies every other status
            args.new = args.adquired = args.seen = True
        else:
            l = l.filter(lambda e: not e.future())
        
        if not args.new: l = l.filter(lambda e: e.status != cons.NEW)
        if not args.adquired: l = l.filter(lambda e: e.status != cons.ADQUIRED)
        if not args.seen: l = l.filter(lambda e: e.status != cons.SEEN)
        
        l.sort(key=lambda e: e.date, reverse = True)
        
        io.msg(l.print_str())
        
    def complete(self, text, line, start_index, end_index):
        return self._complete(text, ["-n", "--new", "-a", "--adquired", "-s", "--seen", "-f", "--future"], m.episodes)