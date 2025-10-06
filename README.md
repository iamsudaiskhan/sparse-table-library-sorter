# sparse-table-library-sorter
Efficient library book sorting system using Sparse Table data structure with circular buffer management, binary search insertion, and dynamic resizing for minimal data movement.

Sparse Table Library Sorting System
This project implements a complex library sorting solution using advanced data structures.
It was designed to efficiently handle sorted book insertion with minimal data movement,
leveraging a Sparse Table structure, circular buffers, and binary search insertion.
Features
Sparse Table Implementation
Optimized for fast access and minimal overhead in sorting operations.
Efficient Book Insertion
Binary search ensures books are inserted at the correct position quickly.
Circular Array Management
Handles data in a rotating buffer, reducing the need for shifting elements.
Dynamic Table Resizing
Automatically balances keys with even distribution for scalability.
Dummy & Genuine Key Handling
Maintains sorted order while supporting placeholder entries.
Requirements
Python 3.7+
No external libraries required (pure Python implementation).
Example (Conceptual Workflow)
A new book entry is requested.
The system locates the insertion index using binary search.
The circular buffer places the entry with minimal movement.
Sparse table ensures efficient queries on the sorted dataset.
Notes
This project was built as a data structures & algorithms exercise to demonstrate:
Advanced array manipulation techniques.
Practical usage of binary search, circular buffers, and sparse tables.
Scalability in environments requiring continuous insertions with sorted order maintained.

