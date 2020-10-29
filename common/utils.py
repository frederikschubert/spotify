import multiprocessing as mp
import os

from tqdm import tqdm


def imap_progress(f, iterable):
    with mp.Pool(processes=os.cpu_count()) as pool:
        results = []
        for result in tqdm(pool.imap_unordered(f, iterable), total=len(iterable)):
            results.append(result)
    return results

