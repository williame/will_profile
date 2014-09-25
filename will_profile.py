import signal, time, traceback, threading, getopt, sys, os, json

def start(interval=0.1):
    global _interval, _samples
    _samples = []
    signal.signal(signal.SIGALRM,_sample)
    signal.setitimer(signal.ITIMER_REAL,interval,interval)
    
def stop():
    global _samples
    signal.setitimer(signal.ITIMER_REAL,0,0)
    samples, _samples = _samples, []
    samples.append((time.time(),None,None,[]))
    return samples
    
def _sample(signo,frame):
    thread = threading.current_thread()
    row = (time.time(),thread.ident,thread.name,traceback.extract_stack(frame))
    if not _samples or row[1:] != _samples[-1][1:]: # new stack since last sample?
        _samples.append(row)

if __name__=="__main__":
    opts, args = getopt.getopt(sys.argv[1:],"t:o:h")
    opts = dict(opts)
    if "h" in opts or not args:
        print >> sys.stderr, "Will's Python profiler:"
        print >> sys.stderr, "  * see http://williamedwardscoder.tumblr.com/post/35134924139/a-novel-profiler-for-python"
        print >> sys.stderr, "  * visualize traces at http://williame.github.io/will_profile/will_profile.html"
        print >> sys.stderr, "Options: {-t [int]} {-o [filename]} [script] {script args...}"
        print >> sys.stderr, "  -t int      number of sample tickss per second; default 10/sec"
        print >> sys.stderr, "  -o filename output profiling info to this file; default is [script].profile"
        print >> sys.stderr, "  -h          help"
    else:
        sys.argv = args
        progname = args[0]
        sys.path.insert(0, os.path.dirname(progname))
        with open(progname, "rb") as f:
            code = compile(f.read(), progname, "exec")
        start(1.0 / int(opts.get("-t", 10)))
        try:
            exec code in {
                    "__file__": progname,
                    "__name__": "__main__",
                    "__package__": None,
                }, None
        except SystemExit:
            pass
        finally:
            data = stop()
            json.dump(data, open(opts.get("-o", "%s.profile" % os.path.splitext(progname)[0]), "wb"))
            
