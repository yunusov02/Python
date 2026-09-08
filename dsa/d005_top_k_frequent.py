def top_k_frequent_element(nums: list[int], k: int) -> list[int]:
    
    frequency = {}
    
    for num in nums:
        if num in frequency:        
            frequency[num] += 1
        else:
            frequency[num] = 1
    
    
    max_freq = len(nums)
    
    buckets = [[] for _ in range(max_freq + 1)]
    
    for num, counts in frequency.items():
        buckets[counts].append(num)
     
    res = []
    
    i = max_freq    
    
    while i > 0 and len(res) < k:
        if buckets[i]:
            for num in buckets[i]:
                if len(res) == k:
                    return res
                res.append(num)
        i -= 1
        
    return res
 
def tests():
    nums1 = [1,1,1,2,2,3]
    k1 = 2
    
    assert top_k_frequent_element(nums1, k1) == [1, 2]
    
    nums2 = [1]
    k2 = 1
    assert top_k_frequent_element(nums2, k2) == [1]
    
    
    nums3 = [1,1,1,2,2,3]
    k3 = 1
    assert top_k_frequent_element(nums3, k3) == [1]
    
    
    nums4 = [1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]
    k4 = 2
    assert top_k_frequent_element(nums4, k4) == [1, 2]
    
    
    print("All tests passed")
    
tests()    
