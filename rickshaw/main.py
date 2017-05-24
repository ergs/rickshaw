"""Main entry point for rickshaw"""
try:
    from pprintpp import pprint
except ImportError:
    from pprint import pprint
import os
import subprocess
import json
import logging
import traceback
from argparse import ArgumentParser
from rickshaw import simspec
from rickshaw import generate
from rickshaw import server_scheduler


def main(args=None):
    p = ArgumentParser('rickshaw')
    p.add_argument('-n', dest='n', type=int, help='number of files to generate',
                   default=None)
    p.add_argument('-i', dest='i', type=str, help='name of input file', default=None)
    p.add_argument('-rs', dest='rs', action="store_true", help='runs the simulations after they have been generated')
    p.add_argument('-rh', dest='rh', action="store_true", help='runs the simulations after they have been generated')
    p.add_argument('-v', dest='v', action="store_true", help='verbose mode will pretty print generated files')
    p.add_argument('-o', dest='o', type=str, help='name of output file', default='rickshaw')
    p.add_argument('-s', dest='s', type=int, help='run in service mode with s sims', default=None)
    ns = p.parse_args(args=args)
    spec = {}
    if ns.i is not None:
        try:
            ext = os.path.splitext(ns.i)[1]
            if ext == '.json':
                with open(ns.i) as jf:
                    spec = json.load(jf)
                    for k,v in simspec['niche_links'].items():
                        spec['niche_links'][k] = set(v)
                    for k,v in simspec['archetypes'].items():
                        spec['archetypes'][k] = set(v)
            elif ext == '.py':
                with open(ns.i) as pf:
                    py_str = pf.read()
                    spec = eval(py_str)
        except:
            print('Failed to parse richshaw input file, please verify file format')
            pass
    if ns.s is not None:
        ss = server_scheduler.ServerScheduler()
        #i = 0        
        #while i < ss.ncpu:
        #    ss.start_rickshaw_service(ns.s, i)
        #    i+= 1
        ss.start_rickshaw_service(ns.s, 1)   
        return     
    if ns.n is not None:
        i = 0
        while i < ns.n:
            try:
                specific_spec = simspec.SimSpec(spec)
            except Exception:
                print('Simspec failed to build')
            try:            
                input_file = generate.generate(sim_spec=specific_spec)
                if ns.v:
                    pprint(input_file)
                jsonfile = str(i) + '.json'
                with open(jsonfile, 'w') as jf:
                    json.dump(input_file, jf, indent=4)
            except Exception as e:
                message = traceback.format_exc()
                logging.exception(message)
            i += 1
    else:
        specific_spec = simspec.SimSpec(spec)
        input_file = generate.generate(sim_spec=specific_spec)
        if ns.v:
            pprint(input_file)
        jsonfile = 'rickshaw' + '.json'
        with open(jsonfile, 'w') as jf:
            json.dump(input_file, jf, indent=4)   
    if ns.rs:
        p = os.popen('ls *.json').readlines()
        for i in range(len(p)):            
            subprocess.call(['cyclus', p[i].rstrip('\n'), '-o' +ns.o +'.sqlite'])
    if ns.rh:
        p = os.popen('ls *.json').readlines()
        for i in range(len(p)):            
            subprocess.call(['cyclus', p[i].rstrip('\n'), '-o' +ns.o +'.h5'])


if __name__ == '__main__':
    main()
