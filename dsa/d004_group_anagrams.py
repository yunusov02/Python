def char_profile(s: str) -> tuple[int, ...]:
    
    counts = [0] * 26
    for c in s:
        counts[ord(c) - ord('a')] += 1
    return tuple(counts)
    


def group_anagrams(strs: list[str]) -> list[list[str]]:

    anagrams = {}
    
    for s in strs:
        
        count_tuple = char_profile(s)
                
        if count_tuple in anagrams:
            anagrams[count_tuple].append(s)
        else:
            anagrams[count_tuple] = [s]
            
    return list(anagrams.values())





def tests():
    strs = ["eat","tea","tan","ate","nat","bat"]
    ans = [['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]


    res = sorted(sorted(g) for g in group_anagrams(strs))
    ans = sorted(sorted(g) for g in ans)
    
    assert len(ans) == len(res)

    for s, r in zip(ans, res):
        assert s == r
    
    
    print("All tests Passed")


tests()