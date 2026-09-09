# A6. Apache Hive Data Warehousing with Tez Execution Engine

**Source:** Apache Hive Documentation

Apache Hive is a data warehouse infrastructure built on top of Apache Hadoop. It provides a SQL-like language called HiveQL, which allows users to write queries that are automatically translated into MapReduce or Tez jobs for execution on the cluster.

Hive converts SQL queries into a directed acyclic graph (DAG) of tasks, which are then executed by the Tez execution engine. Tez improves performance over traditional MapReduce by reducing disk I/O and enabling more efficient task scheduling. The DAG model allows for complex query plans that can be optimized for better resource utilization and faster response times.

Hive stores its metadata in a relational database (such as MySQL or PostgreSQL) called the Hive Metastore. This metadata includes schema information, table locations, partition definitions, and statistics, which are essential for query optimization and execution planning.

Hive's integration with HDFS means that all data is stored in distributed blocks, and queries can leverage the full parallelism of the cluster. This makes Hive a popular choice for ad-hoc analytics and large-scale ETL pipelines.
