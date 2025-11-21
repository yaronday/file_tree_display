# Benchmarks

The measurements were carried out on unfiltered folders containing multiple files und subdirectories, using SSD.   
Avg. time was measured over 20 runs per configuration, using `timeit` decorator I've implemented in this package. 

Comparing FileTreeDisplay (FTD) with
[win_tree_wrapper](https://github.com/yaronday/file_tree_display/blob/master/benchmark/win_tree_wrapper.py) 
(Windows [tree](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/tree) 
wrapper which I've implemented for this purpose).    
[Benchtest code](https://github.com/yaronday/file_tree_display/blob/master/benchmark/benchtest.py)  

### Performance Comparison — FTD vs.`tree`

<table>
<tr><th>Test Context </th><th>Results</th></tr>
<tr><td>

| Metric               | Test1  | Test2      |
|:---------------------|:-------|:-----------|
| **Files**            | 10553  | 138492     |
| **Folders**          | 1235   | 20428      |
| **Wrapper Overhead** | ~30 ms | negligible |

</td><td>

| Tool     | T1 (s) | T2 (s) | Relative Speed |
|:---------|:------:|:------:|:--------------:|
| **FTD**  | 0.196  | 2.900* |       —        |
| **tree** | 0.390  | 5.018  |   ~2x slower   |

</td></tr> </table>

***Without sorting** FTD takes 162 ms and 2.338 s for Test1 and Test2, respectively.  
FTD is roughly **1.7x–2.4x faster** than the native `tree` binary across both datasets.  

---

### Brief Analysis

### I. Linear scaling as a function of entries 
FTD performance scales almost perfectly linearly with total entries:

* **T1:** 10 k files → 0.2 s
* **T2:** 138 k files → 2.9 s
  → ~14x more files → ~15x more runtime => expected by linearity.

### II. Figuring out why `tree` is nearly 2 times slower than my FTD    
Although `tree` is implemented in C, it incurs more I/O work:  
* Performs full `lstat()` on each entry (permissions, timestamps, etc.).  
* Prints incrementally to `stdout` → many system calls (syscalls).  
* Handles color / formatting output.  

My FTD avoids this by:  

* Using `os.scandir()` (caching stat info).
* Filtering and sorting in-memory.
* Buffering output before optional print/write.

Result: lower syscall count and fewer I/O stalls.

### III. Python overhead is clearly negligible
Even at 2.9 s for ~160K entries, throughput ~55K entries/s — close to filesystem limits on SSDs.
Measured wrapper overhead (~30 ms) is < 1 % of total runtime.

### Key Insights

| Observation                    | Explanation                                         |
|:-------------------------------|:----------------------------------------------------|
| **FTD ~2x faster than `tree`** | Avoids per-file printing and redundant stats.       |
| **I/O-bound execution**        | Filesystem metadata fetch dominates total time.     |
| **Linear runtime scaling**     | Recursive generator design adds no hidden overhead. |
| **Stable memory footprint**    | Uses streaming generators and `StringIO` buffering. |

### Conclusions 

* **FTD outperforms `tree` by roughly 2x** on both moderate and large datasets.  
* **Runtime scales linearly** with total directory entries.  
* **Python layer overhead is negligible** — performance is bounded by kernel I/O.

---