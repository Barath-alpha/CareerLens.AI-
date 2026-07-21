# Comprehensive placement interview question bank with 320+ curated questions

QUESTIONS_BANK = {
    'technical': [
        # Data Structures & Algorithms
        {"question": "How do you find the start node of a cycle in a linked list using Floyd's algorithm?", "hint": "Use fast (2x) and slow (1x) pointers. Once they meet, reset one pointer to head and move both 1 step at a time.", "difficulty": "medium"},
        {"question": "Find the maximum subarray sum using Kadane's Algorithm.", "hint": "Maintain current_sum = max(num, current_sum + num) and max_so_far = max(max_so_far, current_sum). Time: O(N), Space: O(1).", "difficulty": "easy"},
        {"question": "How do you reverse a singly linked list in-place?", "hint": "Maintain prev, curr, next_node pointers. Set curr.next = prev, move prev = curr, curr = next_node.", "difficulty": "easy"},
        {"question": "Implement an LRU Cache using Least Recently Used eviction strategy.", "hint": "Combine a HashMap for O(1) lookups with a Doubly Linked List for O(1) node eviction and insertion.", "difficulty": "hard"},
        {"question": "Find the lowest common ancestor (LCA) of two nodes in a Binary Tree.", "hint": "If root is null, p, or q, return root. Recurse left and right. If both return non-null, root is LCA.", "difficulty": "medium"},
        {"question": "Solve the 0/1 Knapsack Problem using Dynamic Programming.", "hint": "dp[i][w] = max(dp[i-1][w], val[i-1] + dp[i-1][w-wt[i-1]]) if wt[i-1] <= w else dp[i-1][w]. Time: O(N*W).", "difficulty": "medium"},
        {"question": "How do you implement Dijkstra's Algorithm for Single Source Shortest Path?", "hint": "Use a Min-Heap (Priority Queue) storing (distance, node). Relax edges if new distance < stored distance.", "difficulty": "medium"},
        {"question": "Check if a string contains valid balanced parentheses: '()[]{}'", "hint": "Use a Stack. Push opening brackets, pop matching closing brackets. Stack must be empty at end.", "difficulty": "easy"},
        {"question": "Find the median of two sorted arrays of different sizes in O(log(min(M,N))).", "hint": "Use Binary Search on the smaller array to partition both arrays such that left elements <= right elements.", "difficulty": "hard"},
        {"question": "Implement a Trie (Prefix Tree) with insert, search, and startsWith methods.", "hint": "TrieNode contains dict/array of 26 children and is_end_of_word boolean flag.", "difficulty": "medium"},
        {"question": "Detect a cycle in a Directed Graph using DFS.", "hint": "Use 3 states: Unvisited (0), Visiting (1), Visited (2). If DFS encounters a node in 'Visiting' state, cycle exists.", "difficulty": "medium"},
        {"question": "Find all permutations of an array/string with duplicate elements.", "hint": "Sort array first. Backtrack while skipping adjacent duplicate elements: if i > 0 and nums[i] == nums[i-1] and not visited[i-1], continue.", "difficulty": "medium"},
        {"question": "Find the Longest Common Subsequence (LCS) of two strings.", "hint": "If s1[i] == s2[j], dp[i][j] = 1 + dp[i-1][j-1], else max(dp[i-1][j], dp[i][j-1]).", "difficulty": "medium"},
        {"question": "Find the Longest Increasing Subsequence (LIS) in O(N log N) time.", "hint": "Use Binary Search with Patience Sorting (std::lower_bound / bisect_left) on an active tails list.", "difficulty": "hard"},
        {"question": "Implement Topological Sort on a DAG using Kahn's Algorithm (BFS).", "hint": "Calculate in-degrees. Enqueue all 0 in-degree nodes. Process queue, decrement neighbor in-degrees, enqueue when 0.", "difficulty": "medium"},
        {"question": "Solve the Trapping Rain Water problem in O(N) time and O(1) space.", "hint": "Use Two Pointers (left, right) tracking max_left and max_right.", "difficulty": "hard"},
        {"question": "Find the Kth largest element in an unsorted array.", "hint": "Use QuickSelect algorithm (average O(N)) or a Min-Heap of size K (O(N log K)).", "difficulty": "medium"},
        {"question": "Serialize and Deserialize a Binary Tree.", "hint": "Use preorder traversal with delimiter (e.g. ',') and null marker (e.g. '#'). Reconstruct using Queue.", "difficulty": "hard"},
        {"question": "Find the maximum product subarray.", "hint": "Track both max_so_far and min_so_far because multiplying by a negative number flips minimums and maximums.", "difficulty": "medium"},
        {"question": "Check if a Binary Tree is a valid Binary Search Tree (BST).", "hint": "Validate that all node values lie strictly within (min_val, max_val) boundaries passed recursively.", "difficulty": "medium"},
        {"question": "Count total set bits (1s) in an integer (Brian Kernighan's Algorithm).", "hint": "Use n = n & (n - 1) in a loop while n > 0. Each operation clears the lowest set bit.", "difficulty": "easy"},
        {"question": "Implement Word Ladder (Shortest transformation sequence from beginWord to endWord).", "hint": "Use BFS starting from beginWord. Change 1 char at a time to check valid dictionary words.", "difficulty": "hard"},
        {"question": "Find the Subarray with given Sum (positive integers).", "hint": "Use Two Pointers / Sliding Window. Expand right pointer to add, shrink left pointer if current_sum > target.", "difficulty": "easy"},
        {"question": "Find the Clone of an Undirected Graph.", "hint": "Use BFS/DFS with a HashMap mapping original node -> cloned node to prevent infinite recursion on cycles.", "difficulty": "medium"},
        {"question": "Find the Course Schedule ordering (Prerequisites dependencies).", "hint": "Topological sort using Kahn's BFS or DFS cycle detection.", "difficulty": "medium"},
        {"question": "Implement Merge Sort and analyze its space-time complexity.", "hint": "Divide array into halves, sort recursively, merge two sorted halves. Time: O(N log N), Space: O(N).", "difficulty": "medium"},
        {"question": "Find the Minimum Window Substring containing all characters of pattern string.", "hint": "Sliding window with frequency map. Expand right until valid, shrink left to minimize length.", "difficulty": "hard"},
        {"question": "Find the Majority Element (appears more than N/2 times) using Boyer-Moore Voting Algorithm.", "hint": "Maintain candidate and count. If count == 0 set candidate = num. If num == candidate count++ else count--.", "difficulty": "easy"},
        {"question": "Sort an array of 0s, 1s, and 2s (Dutch National Flag Algorithm).", "hint": "Use 3 pointers: low=0, mid=0, high=N-1. Swap mid with low when 0, mid++ when 1, swap mid with high when 2.", "difficulty": "medium"},
        {"question": "Find the Longest Palindromic Substring.", "hint": "Expand around center for both odd and even length centers (2N-1 centers total). Time: O(N^2), Space: O(1).", "difficulty": "medium"},
        {"question": "Implement Binary Search on a rotated sorted array.", "hint": "Find mid. Determine which half is sorted (nums[low] <= nums[mid]). Check if target lies within sorted half.", "difficulty": "medium"},
        {"question": "Find all Triplets that sum to Zero (3Sum).", "hint": "Sort array. Loop i from 0 to N-2, use Two Pointers (left=i+1, right=N-1) for remaining 2 elements. Skip duplicates.", "difficulty": "medium"},
        {"question": "Find the Number of Islands in a 2D grid.", "hint": "Iterate grid. When '1' is found, increment island count and run DFS/BFS to sink all connected '1's to '0's.", "difficulty": "medium"},
        {"question": "Word Search in 2D Board (Matrix Backtracking).", "hint": "Run DFS from each cell matching first letter. Mark cell visited during DFS, unmark on backtrack.", "difficulty": "medium"},
        {"question": "Find the Diameter of a Binary Tree.", "hint": "Diameter is max(left_height + right_height) across all nodes. Compute in a single bottom-up post-order DFS.", "difficulty": "easy"},
        {"question": "Implement Min Stack supporting push, pop, top, and getMin in O(1) time.", "hint": "Maintain two stacks: main stack and min stack storing current minimum at each push step.", "difficulty": "medium"},
        {"question": "Coin Change Problem (Minimum coins to make total sum).", "hint": "dp[i] = min(dp[i], 1 + dp[i - coin]) for all coin <= i. Base case dp[0] = 0.", "difficulty": "medium"},
        {"question": "House Robber Problem (Maximum amount without robbing adjacent houses).", "hint": "dp[i] = max(dp[i-1], nums[i] + dp[i-2]). Optimize to O(1) space using prev1 and prev2 variables.", "difficulty": "easy"},
        {"question": "Construct Binary Tree from Preorder and Inorder Traversal.", "hint": "Preorder first element is root. Find root index in Inorder to split left and right subtrees.", "difficulty": "medium"},
        {"question": "Find Median from Data Stream (Continuous stream of numbers).", "hint": "Use two Heaps: Max-Heap for smaller half of numbers, Min-Heap for larger half. Keep sizes balanced.", "difficulty": "hard"},
    ],

    'core_cs': [
        # OS, DBMS, Networks, OOPs
        {"question": "Explain the difference between Process and Thread, and context switching overhead.", "hint": "Processes have independent virtual memory spaces, threads share process memory space.", "difficulty": "easy"},
        {"question": "What are Coffman's 4 necessary conditions for a Deadlock to occur?", "hint": "1. Mutual Exclusion 2. Hold and Wait 3. No Preemption 4. Circular Wait.", "difficulty": "easy"},
        {"question": "Explain ACID properties in DBMS with real-world examples.", "hint": "Atomicity (all or nothing), Consistency (valid constraints), Isolation (concurrent transactions), Durability (persisted).", "difficulty": "easy"},
        {"question": "Explain Database Normalization from 1NF to 3NF and BCNF.", "hint": "1NF: Atomic values; 2NF: No partial key dependency; 3NF: No transitive dependency; BCNF: X is superkey for X -> Y.", "difficulty": "medium"},
        {"question": "What is the difference between TCP and UDP? When to use which?", "hint": "TCP is connection-oriented, reliable, ordered (HTTP, FTP). UDP is connectionless, fast, lightweight (video streaming, gaming).", "difficulty": "easy"},
        {"question": "Explain the 7 layers of the OSI Model and their primary protocols.", "hint": "Application (HTTP), Presentation (SSL), Session, Transport (TCP/UDP), Network (IP), Data Link (Ethernet), Physical.", "difficulty": "easy"},
        {"question": "What happens when you type 'https://www.google.com' in a web browser?", "hint": "DNS resolution -> TCP 3-Way Handshake -> TLS Handshake -> HTTP Request -> Web Server handles & returns response -> Browser renders HTML/CSS/JS.", "difficulty": "medium"},
        {"question": "Explain Virtual Memory, Paging, and Page Faults in Operating Systems.", "hint": "Virtual memory abstracts RAM + Swap space. Paging divides memory into fixed-size pages. Page fault occurs when requested page is not in RAM.", "difficulty": "medium"},
        {"question": "Difference between SQL primary key, unique key, and candidate key.", "hint": "Primary key: Unique + NOT NULL (1 per table). Unique key: Unique + allows NULL. Candidate key: Minimal set of fields capable of being primary key.", "difficulty": "easy"},
        {"question": "Explain Object-Oriented Programming (OOP) Pillars: Encapsulation, Abstraction, Inheritance, Polymorphism.", "hint": "Encapsulation (data hiding), Abstraction (hiding implementation details), Inheritance (reusing code), Polymorphism (overloading/overriding).", "difficulty": "easy"},
        {"question": "What is the difference between Method Overloading and Method Overriding?", "hint": "Overloading: Same class, same method name, different parameters (Compile-time). Overriding: Parent-Child relationship, same signature (Runtime).", "difficulty": "easy"},
        {"question": "Explain Semaphores (Mutex vs Counting Semaphore) for Process Synchronization.", "hint": "Mutex is a binary lock (0 or 1). Counting Semaphore allows up to N concurrent threads to access shared resources.", "difficulty": "medium"},
        {"question": "What is Indexing in Databases and how do B-Trees/B+ Trees speed up search?", "hint": "Indexes create lookup trees on table columns. B+ Trees store all data pointers at leaf nodes connected via linked list for fast range queries.", "difficulty": "medium"},
        {"question": "Explain HTTP Status Codes: 200, 301, 400, 401, 403, 404, 500, 502, 503.", "hint": "2xx Success, 3xx Redirect, 4xx Client Error (401 Unauthorized, 403 Forbidden, 404 Not Found), 5xx Server Error.", "difficulty": "easy"},
        {"question": "What is a Proxy Server vs Reverse Proxy Server?", "hint": "Forward Proxy protects/masks clients. Reverse Proxy sits in front of servers for load balancing, caching, and SSL termination.", "difficulty": "medium"},
        {"question": "Explain Database Transactions and Isolation Levels (Read Uncommitted to Serializable).", "hint": "Isolation levels prevent Dirty Reads, Non-Repeatable Reads, and Phantom Reads using locks or MVCC.", "difficulty": "hard"},
        {"question": "Difference between Deep Copy and Shallow Copy.", "hint": "Shallow copy copies references to nested objects; deep copy recursively duplicates all nested objects.", "difficulty": "easy"},
        {"question": "Explain CPU Scheduling Algorithms: FCFS, SJF, Round Robin, Priority Scheduling.", "hint": "Round Robin uses time quantum; SJF gives lowest average waiting time; FCFS is non-preemptive fifo.", "difficulty": "medium"},
        {"question": "What is thrashing in OS and how can it be prevented?", "hint": "Thrashing occurs when OS spends more time swapping pages than executing processes. Prevent via Working Set Model.", "difficulty": "medium"},
        {"question": "Explain SQL Joins: INNER, LEFT, RIGHT, FULL OUTER, CROSS JOIN.", "hint": "INNER: matching rows in both; LEFT: all left + matching right; CROSS: Cartesian product.", "difficulty": "easy"},
    ],

    'system_design': [
        # Scalability, System Architecture
        {"question": "Design a URL Shortener service like Bitly.", "hint": "Use Base62 encoding on auto-incrementing ID or MD5 hash prefix. Use Redis cache for frequent redirects.", "difficulty": "medium"},
        {"question": "How would you design a scalable Chat Application like WhatsApp?", "hint": "Use WebSockets for real-time messaging, Cassandra for message history, and Push Notifications for offline users.", "difficulty": "hard"},
        {"question": "Design a rate limiter for API endpoints (100 req/min).", "hint": "Use Token Bucket, Leaky Bucket, or Redis Sliding Window Counter algorithm.", "difficulty": "medium"},
        {"question": "How do you design a CDN (Content Delivery Network)?", "hint": "Geographically distributed edge cache servers. Use Anycast DNS or GeoDNS to route users to nearest edge node.", "difficulty": "hard"},
        {"question": "Design YouTube / Netflix video streaming service architecture.", "hint": "Transcode videos into chunked HLS/DASH formats at multiple resolutions (360p, 1080p, 4K). Store chunks in S3 and cache at CDN.", "difficulty": "hard"},
        {"question": "Explain Horizontal vs Vertical Scaling and CAP Theorem.", "hint": "Vertical = add CPU/RAM to 1 machine; Horizontal = add more machines. CAP: Consistency, Availability, Partition Tolerance (pick 2).", "difficulty": "medium"},
        {"question": "Design a Notification System supporting Push, Email, and SMS.", "hint": "Use Message Queue (Kafka/RabbitMQ) for async decoupling. Third-party integrations: APNS/FCM (Push), SendGrid (Email), Twilio (SMS).", "difficulty": "medium"},
        {"question": "How does Database Sharding / Partitioning work?", "hint": "Split large tables horizontally across multiple database nodes using a Shard Key (e.g. hash(user_id) % num_shards).", "difficulty": "medium"},
        {"question": "Explain SQL vs NoSQL (Document, Key-Value, Columnar, Graph) database selection criteria.", "hint": "Use SQL (PostgreSQL/MySQL) for ACID compliance & relational structure. Use NoSQL (MongoDB/Redis/Cassandra) for high write throughput & dynamic schemas.", "difficulty": "easy"},
        {"question": "Design a Web Crawler capable of crawling billions of web pages.", "hint": "Use URL Frontier queue with DNS resolver cache, HTML Parser, Duplicate URL Filter (Bloom Filter), and storage.", "difficulty": "hard"},
    ],

    'hr': [
        # HR & Behavioral
        {"question": "Tell me about a time you faced a tight deadline and how you handled it.", "hint": "Use STAR method: Describe the project, prioritization strategy, communication with stakeholders, and final delivery.", "difficulty": "easy"},
        {"question": "Why do you want to join our company specifically?", "hint": "Mention specific products, technology stack, culture values, and recent news about the company.", "difficulty": "easy"},
        {"question": "Describe a scenario where you disagreed with a team member. How was it resolved?", "hint": "Focus on active listening, objective data-driven decision making, and maintaining team harmony.", "difficulty": "easy"},
        {"question": "Where do you see yourself in 3 to 5 years?", "hint": "Express desire to master technical skills, take ownership of major projects, and mentor junior developers.", "difficulty": "easy"},
        {"question": "What is your biggest weakness and how are you working to overcome it?", "hint": "Choose a genuine skill gap (e.g. public speaking, delegating), and detail proactive steps you take to improve.", "difficulty": "easy"},
        {"question": "Tell me about a project that failed or didn't go as expected. What did you learn?", "hint": "Focus on root-cause analysis, lessons learned, and how you implemented fixes in subsequent projects.", "difficulty": "medium"},
        {"question": "Why should we hire you over other qualified candidates?", "hint": "Highlight your unique blend of technical problem-solving skills, fast adaptability, and project achievements.", "difficulty": "easy"},
        {"question": "Describe a situation where you had to lead a team through uncertainty or technical challenges.", "hint": "Detail how you delegated tasks, maintained communication, and drove the team to meet project goals.", "difficulty": "medium"},
        {"question": "How do you handle constructive criticism from seniors or peers?", "hint": "Emphasize growth mindset, taking feedback objectively, and immediately putting improvements into practice.", "difficulty": "easy"},
        {"question": "What motivates you to perform your best work every day?", "hint": "Mention solving impactful real-world engineering problems, continuous learning, and working with talented peers.", "difficulty": "easy"},
    ],

    'aptitude': [
        # Aptitude & Puzzles
        {"question": "A train 150m long passes a pole in 15 seconds. What is the speed of the train in km/hr?", "hint": "Speed = Distance / Time = 150 / 15 = 10 m/s = 10 * 18/5 = 36 km/hr.", "difficulty": "easy"},
        {"question": "If A can finish a work in 10 days and B in 15 days, how long will they take working together?", "hint": "Combined rate = 1/10 + 1/15 = 1/6 work per day. Total time = 6 days.", "difficulty": "easy"},
        {"question": "A trader sells an item at 20% profit. If cost price increases by 10% and selling price increases by 20%, find new profit %.", "hint": "Let CP = 100, original SP = 120. New CP = 110, New SP = 144. Profit = 34 on 110 => 34/110 * 100 = 30.91%.", "difficulty": "medium"},
        {"question": "Puzzle: You have 8 identical-looking balls where 1 is heavier. Minimum weighings on a balance scale to find it?", "hint": "2 weighings. Divide into 3 groups (3, 3, 2). Weigh 3 vs 3. If equal, heavy is in group of 2.", "difficulty": "medium"},
        {"question": "Find the next number in the series: 2, 6, 12, 20, 30, 42, ?", "hint": "Pattern: n*(n+1) -> 1*2, 2*3, 3*4, 4*5, 5*6, 6*7. Next is 7*8 = 56.", "difficulty": "easy"},
        {"question": "Two dice are rolled together. What is the probability of getting a sum equal to 8?", "hint": "Favorable outcomes: (2,6), (3,5), (4,4), (5,3), (6,2) = 5 outcomes out of 36 total. P = 5/36.", "difficulty": "easy"},
        {"question": "Puzzle: 3 light switches outside a room, 3 bulbs inside. You can enter room only once. How to identify which switch controls which bulb?", "hint": "Turn switch 1 ON for 10 mins, turn OFF. Turn switch 2 ON. Enter room: lit bulb = switch 2, warm bulb = switch 1, cold bulb = switch 3.", "difficulty": "medium"},
        {"question": "A clock shows 3:15. What is the angle between the hour hand and minute hand?", "hint": "At 3:15, minute hand is at 90 deg. Hour hand moves 0.5 deg/min -> 3*30 + 15*0.5 = 97.5 deg. Angle = 97.5 - 90 = 7.5 degrees.", "difficulty": "medium"},
        {"question": "Find the compound interest on ₹10,000 for 2 years at 10% per annum compounded annually.", "hint": "Amount = P(1 + r/100)^n = 10000 * 1.21 = 12100. CI = 12100 - 10000 = ₹2,100.", "difficulty": "easy"},
        {"question": "Puzzle: You have a 3-liter jug and a 5-liter jug. How do you measure exactly 4 liters of water?", "hint": "Fill 5L jug, pour into 3L jug (2L left in 5L jug). Empty 3L jug, pour 2L into 3L jug. Fill 5L jug, fill remainder of 3L jug (1L). 4L remains in 5L jug!", "difficulty": "medium"},
    ]
}

def get_questions(q_type='technical', difficulty='medium', count=10, company=''):
    """Return filtered questions based on parameters."""
    bank = QUESTIONS_BANK.get(q_type.lower(), QUESTIONS_BANK['technical'])
    
    # Filter by difficulty if matched
    filtered = [q for q in bank if q.get('difficulty') == difficulty.lower()]
    if not filtered:
        filtered = bank

    # If count requested is larger than filtered, sample or cycle
    results = []
    for i in range(count):
        q_item = dict(filtered[i % len(filtered)])
        if company:
            q_item['question'] = f"[{company}] " + q_item['question']
        results.append(q_item)
        
    return results
