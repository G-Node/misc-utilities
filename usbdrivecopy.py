#!/usr/bin/env python
import shutil
import sys
import os
import multiprocessing as mp
import traceback
from gi.repository import Gio
import time
__author__ = 'gicmo'

class CopyWorker(mp.Process):
    def __init__(self, mount, source_dir):
        path = mount.get_root().get_path()
        drive_id = os.path.basename(path)
        worker_name = "CopyWorker.%s" % drive_id
        mp.Process.__init__(self, args=(mount, source_dir), name=worker_name)
        self._mount = mount
        self._source_dir = source_dir

    def run(self):
        try:
            mount = self._mount
            path = mount.get_root().get_path()
            dst = os.path.join (path, 'Winter Course 2012')
            print "%s -> %s" % (self._source_dir, path)
            start = time.time()
            shutil.copytree (self._source_dir, dst)
            end = time.time()
            dur = end - start
            print "%s done! [%f sec]" % (self.name, dur)
        except:
            print traceback.print_exc()
            sys.exit(1)
        sys.exit(0)

def main(argv):

    source_dir = sys.argv[1]

    monitor = Gio.VolumeMonitor.get()
    mounts = monitor.get_mounts()
    udrives = [m for m in mounts if m.get_drive() != None and m.get_drive().get_name() == 'General USB Flash Disk']


    print "Found %d usb drives:" % len(udrives)
    for mount in udrives:
        mount_name = mount.get_name()
        volume = mount.get_volume()
        volume_id = volume.get_identifier('uuid')
        drive_name = mount.get_drive().get_name()
        print '\t%s %s (%s)' % (volume_id, mount_name,  drive_name)

    do_cont = raw_input("Continue y(es)/N(no) [No]: ")

    if do_cont is None or do_cont[0] != 'y':
        print "Aborted"
        return 1

    jobs = []
    for mount in udrives:
        p = CopyWorker(mount, source_dir)
        jobs.append (p)
        p.start()

    res = 0
    for j in jobs:
        j.join()
        res += j.exitcode
        print '%s.exitcode = %s' % (j.name, j.exitcode)

    if res != 0:
        print "WARNING! Non-zero exit code(s) from worker(s)! [%d]" % res
        return res



    return res

if __name__ == '__main__':
    res = main (sys.argv)
    sys.exit (res)
