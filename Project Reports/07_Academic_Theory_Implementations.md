# Academic Theory & Interactive Simulation Visualizers

## 1. Overview
A core requirement of the CSE 303 Lab curriculum is demonstrating mastery of foundational database theoretical concepts:
- **Task 3:** Hardware Data Redundancy & RAID-4 Fault Recovery.
- **Task 4:** Relational Data Normalization (1NF through 3NF).
- **Task 5:** Indexing Algorithms using B+ Tree Structures.

To make these abstract algorithms clear and interactive, we built a visualizer module (`templates/system_report.html`) into the web application.

---

## 2. RAID Level 4 Simulation (Task 3)

### 2.1 Theoretical Architecture
RAID-4 (Redundant Array of Independent Disks) uses block-level data striping across multiple Data Disks paired with a single dedicated **Parity Disk**. 

If any single Data Disk fails, its data can be reconstructed using bitwise Exclusive OR (XOR, $\oplus$) operations across the surviving Data Disks and the Parity Disk.

### 2.2 Mathematical Model & Equations
We model the system using **6 Data Disks ($D_1$ to $D_6$)** holding 4-bit binary blocks representing table data, plus **1 Parity Disk ($P$)**:

$$P = D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_5 \oplus D_6$$

#### Bitwise XOR Truth Table Mechanics
- $0 \oplus 0 = 0$
- $1 \oplus 1 = 0$
- $0 \oplus 1 = 1$
- $1 \oplus 0 = 1$

### 2.3 Simulated Disk State Matrix

| Disk Identifier | Assigned Database Entity Block | Binary Block Value |
| :--- | :--- | :--- |
| **Disk 1 ($D_1$)** | Customer Table Block | `1010` |
| **Disk 2 ($D_2$)** | Product Table Block | `1100` |
| **Disk 3 ($D_3$)** | Supplier Table Block | `0011` |
| **Disk 4 ($D_4$)** | Warehouse Table Block | `1111` |
| **Disk 5 ($D_5$)** | Order Table Block | `0011` |
| **Disk 6 ($D_6$)** | Payment Table Block | `1001` |
| **Disk 7 ($P$)** | **Calculated Parity Disk** | **`0101`** |

#### Step-by-Step Parity Calculation
$$\begin{aligned}
D_1 \oplus D_2 &= 1010 \oplus 1100 = 0110 \\
(D_1 \oplus D_2) \oplus D_3 &= 0110 \oplus 0011 = 0101 \\
((D_1 \oplus D_2 \oplus D_3)) \oplus D_4 &= 0101 \oplus 1111 = 1010 \\
(((D_1 \oplus \dots \oplus D_4))) \oplus D_5 &= 1010 \oplus 0011 = 1001 \\
P = (((D_1 \oplus \dots \oplus D_5))) \oplus D_6 &= 1001 \oplus 1001 = \mathbf{0101}
\end{aligned}$$

### 2.4 Simulated Disk Failure & Data Reconstruction
In the visualizer, the user can trigger a simulated failure of **Disk 5 ($D_5$)**, causing its contents to become corrupted (`????`).

#### Reconstruction Equation
To recover the data on lost Disk $D_5$, the system XORs all surviving Data Disks against the Parity Disk $P$:

$$D_5 = D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_6 \oplus P$$

#### Reconstruction Math Walkthrough
$$\begin{aligned}
D_1 \oplus D_2 \oplus D_3 \oplus D_4 \oplus D_6 &= 1010 \oplus 1100 \oplus 0011 \oplus 1111 \oplus 1001 = 1000 \\
D_5 = 1000 \oplus P (0101) &= \mathbf{0011}
\end{aligned}$$

The calculated result (`0011`) matches the original contents of Disk 5, demonstrating successful fault tolerance.

---

## 3. Relational Database Normalization (Task 4)

Normalization organizes database attributes to eliminate redundancy and prevent insertion, update, and deletion anomalies.

### 3.1 Unnormalized Form (UNF)
An initial raw transaction log contains repeating groups where a single order record stores multiple items and duplicate customer details:

```
UNF Table: Order_ID | Customer_Name | Customer_Address | Item_Names (Repeating) | Item_Prices (Repeating)
Order #5001 | Asiful Islam | Dhaka, BD | [Laptop, Mouse] | [1499.99, 29.99]
```

### 3.2 First Normal Form (1NF)
- **Rules:** Remove repeating groups; ensure all attribute values are atomic (indivisible); define a unique Primary Key.
- **Action:** Flatten the table so each row represents a single order line item.

```
1NF Relation: (Order_ID, Product_ID, Customer_Name, Customer_Address, Product_Name, Price, Quantity)
Key: (Order_ID, Product_ID)
```

### 3.3 Second Normal Form (2NF)
- **Rules:** Meet 1NF criteria; remove **Partial Functional Dependencies** (where an attribute depends on only part of a composite primary key).
- **Functional Dependencies:**
  - `(Order_ID, Product_ID) -> Quantity` (Full dependency)
  - `Product_ID -> Product_Name, Price` (Partial dependency on `Product_ID`)
  - `Order_ID -> Customer_Name, Customer_Address` (Partial dependency on `Order_ID`)
- **Action:** Split into 3 separate tables:

```
Order_Item (Order_ID [FK], Product_ID [FK], Quantity)
Product (Product_ID [PK], Product_Name, Price)
Order_Header (Order_ID [PK], Customer_Name, Customer_Address)
```

### 3.4 Third Normal Form (3NF)
- **Rules:** Meet 2NF criteria; remove **Transitive Functional Dependencies** (where a non-key attribute depends on another non-key attribute).
- **Transitive Dependency:**
  - In `Order_Header`: `Order_ID -> Customer_ID -> Customer_Name, Customer_Address`. `Customer_Address` depends transitively on `Order_ID` via `Customer_ID`.
- **Action:** Extract customer profile data into a dedicated `Customer` relation:

```
Customer (Customer_ID [PK], Customer_Name, Customer_Address)
Order (Order_ID [PK], Customer_ID [FK], Order_Date)
OrderDetail (Detail_ID [PK], Order_ID [FK], Product_ID [FK], Quantity, Unit_Price)
Product (Product_ID [PK], Product_Name, Price)
```

---

## 4. Order-3 B+ Tree Indexing Simulation (Task 5)

### 4.1 Structural Rules of Order-3 B+ Tree ($M = 3$)
1. Every internal node contains at most $M - 1 = 2$ keys and at most $M = 3$ child pointers.
2. Every internal node (except the root) contains at least $\lceil M/2 \rceil - 1 = 1$ key.
3. Leaf nodes are linked sequentially at the bottom level to allow range scans.
4. All search keys reside in the leaf nodes.

### 4.2 Insertion Trace (Product IDs 101 to 113)

1. **Insert 101, 102:** Leaf Node `[101 | 102]` (Node capacity full).
2. **Insert 103:** Overflow occurs `[101 | 102 | 103]`. Middle key `102` is promoted to create a root node:
   ```
            [ 102 ]
           /       \
      [ 101 ]     [ 102 | 103 ]
   ```
3. **Inserting 104 through 113:** Cascading leaf splits continue, maintaining a balanced tree height of $H = 2$.

### 4.3 Logarithmic Search Algorithm ($O(\log N)$)
- **Target Search Key:** `Product_ID = 108`
- **Step 1:** Compare `108` against Root Node `[106]`. Since $108 \ge 106$, follow the right child pointer.
- **Step 2:** Compare `108` against Internal Node `[109]`. Since $108 < 109$, follow the left branch pointer.
- **Step 3:** Land on Leaf Page `[106 | 107 | 108]`. Locate key `108` and fetch its database record pointer.
- **Complexity:** Resolves record location in 3 page reads ($O(\log_3 N)$) instead of scanning all 13 table rows ($O(N)$).

### 4.4 Deletion Rebalancing Traversal
- **Target Deletion Key:** `Product_ID = 105`
- **Step 1:** Traverse tree to Leaf Node `[104 | 105]`.
- **Step 2:** Remove key `105`. Remaining node state is `[104]`.
- **Step 3:** Verify node occupancy: Minimum required keys $= 1$. Since `[104]` retains 1 key, the node satisfies minimum occupancy rules. No underflow occurs, so no sibling node merging or borrowing is required. The tree remains balanced.
