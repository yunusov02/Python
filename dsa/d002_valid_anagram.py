
# D2 — Valid Anagram

# Given two strings `s` and `t`, return `true` if `t` is an anagram of `s` (same letters, same counts, any order).

# Example: `s = "anagram", t = "nagaram"` → `true`  ·  `s = "rat", t = "car"` → `false`



def valid_anagram(s: str, t: str) -> bool:

    length_s = len(s)
    length_t = len(t)

    if length_s != length_t:
        return False
    
    dict_s = dict()
    dict_t = dict()

    for el in s:
        dict_s[el] = dict_s.get(el, 0) + 1

    for el in t:
        dict_t[el] = dict_t.get(el, 0) + 1

    for char in dict_s.keys():
        if (dict_t.get(char) is None) or dict_t[char] != dict_s[char]:
            return False

    return True

    



def test_valid_anogram():

    s1 = "anagram"
    t1 = "nagaram"

    assert valid_anagram(s1, t1) == True

    s2 = "rat"
    t2 = "car"

    assert valid_anagram(s2, t2) == False

    s3 = "Listen"
    t3 = "Silent"

    assert valid_anagram(s3, t3) == False

    s4 = ""
    t4 = ""
    assert valid_anagram(s4, t4) == True




test_valid_anogram()