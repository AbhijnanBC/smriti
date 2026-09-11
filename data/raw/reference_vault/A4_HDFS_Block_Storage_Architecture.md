# A4. HDFS Block Storage Architecture

**Source:** Apache Hadoop Documentation

The Hadoop Distributed File System (HDFS) is designed to store very large data sets reliably and to stream those data sets at high bandwidth to user applications. HDFS has two main layers:

- **Namespace:** Manages directories, files, and blocks. It supports all namespace-related file system operations such as creating, deleting, moving, and renaming files and directories.
- **Block Storage Service:** Consists of two parts:
  - **Block Management:** Performed by the Namenode, which tracks Datanode cluster membership, processes block reports, and manages replica placement policies.
  - **Storage:** Provided by Datanodes, which store blocks on the local file system and serve read/write requests from clients.

In the classic HDFS architecture, there is a single Namespace for the entire cluster. This can become a bottleneck as the cluster grows. HDFS Federation addresses this limitation by adding support for multiple Namenodes and namespaces. Each Namespace and its associated block pool form a Namespace Volume, which is a self-contained unit of management. Datanodes store blocks for all block pools in the cluster, providing a unified storage layer.

This design enables horizontal scaling of the Namenode layer and improves overall system throughput.
