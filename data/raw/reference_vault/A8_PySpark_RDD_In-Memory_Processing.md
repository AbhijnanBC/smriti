# A8. PySpark RDD In-Memory Processing

**Source:** Apache Spark Documentation / IBM

A Resilient Distributed Dataset (RDD) is an immutable, fault-tolerant collection of elements that can be distributed across multiple cluster nodes and processed in parallel. RDDs are the fundamental building block of Apache Spark. They can be created from data stored in HDFS, local file systems, or by transforming existing RDDs.

Two types of operations can be performed on RDDs:

- **Transformations** (e.g., `map`, `filter`, `flatMap`) produce a new RDD from an existing one. Transformations are lazy; they are not executed immediately but are recorded as a lineage graph.
- **Actions** (e.g., `count`, `collect`, `saveAsTextFile`) trigger the execution of the transformation graph and return a result to the driver program or write data to storage.

Spark's ability to cache RDDs in memory is a key differentiator from MapReduce. Caching allows subsequent operations to reuse the data without recomputing it from disk, which can dramatically improve performance for iterative algorithms such as machine learning and graph processing.

RDDs are "resilient" because they remember their lineage (the set of transformations used to build them). If a partition is lost due to a node failure, Spark can recompute it from its lineage, ensuring fault tolerance without the overhead of replication.
