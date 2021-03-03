import time
import functools

import pandas

def timeit(f):
    @functools.wraps(f)
    def timeit_wrapper(*args, **kwargs):
        ts       = time.perf_counter_ns()
        response = f(*args, **kwargs)
        te       = time.perf_counter_ns()

        args[0].records = args[0].records.append(
            pandas.DataFrame({
                'function' : [f.__name__],
                'proc_time': (te - ts) / 1000
            })
        )

        args[0].records.to_csv('{}.csv'.format(
            args[0].account
        ))
            
        print('{} {:.2f} us'.format(
            f.__name__, (te - ts) / 1000
        ))
        return response
    return timeit_wrapper