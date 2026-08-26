"""
Given an integer array `nums`, return `true` if any value appears at least twice, and `false` if every element is distinct.

**Example:** `nums = [1,2,3,1]` → `true`  ·  `nums = [1,2,3,4]` → `false`

"""



def contain_duplicate(array: list[int]) -> bool:

    seen = set()

    for element in array:

        if element in seen:
            return True

        seen.add(element)

    return False



def tests():

    nums1 = [1, 2, 3, 1]
    assert contain_duplicate(nums1) == True

    nums2 = [1, 2, 3, 4]
    assert contain_duplicate(nums2) == False

    nums3 = []
    assert contain_duplicate(nums3) == False

    nums4 = [1]
    assert contain_duplicate(nums4) == False

    nums5 = [1, 2, True, False]
    assert contain_duplicate(nums5) == True

    print("All tests passed!")


tests()