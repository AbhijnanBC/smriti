# A9. Apache Spark RDD Persistence and Fault Tolerance

**Source:** Apache Spark Documentation

Users can ask Spark to persist an RDD in memory or on disk using the `persist()` or `cache()` methods. Persistence options include:

- `MEMORY_ONLY`: Store RDD as deserialized Java objects in the JVM heap. If the RDD does not fit in memory, some partitions may be recomputed on the fly.
- `MEMORY_AND_DISK`: Store partitions in memory; if they do not fit, spill to disk.
- `MEMORY_ONLY_SER`: Store RDD as serialized bytes (more memory-efficient but requires deserialization on access).
- `DISK_ONLY`: Store partitions only on disk.

Persistence improves performance when the same RDD is used in multiple actions. Spark's fault-tolerance mechanism relies on lineage: if a partition is lost, Spark recomputes it using the transformations that created it. For data that cannot be recomputed (e.g., after `repartition`), Spark can also replicate partitions across nodes.

By default, Spark persists RDDs in memory with the `MEMORY_ONLY` level, which offers the best performance when there is enough memory.
