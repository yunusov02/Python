def two_sum(nums, target):

    num_dict = {}

    for i, num in enumerate(nums):

        complement = target - num

        if complement in num_dict:
            return [num_dict[complement], i]

        num_dict[num] = i

def tests():
    assert two_sum([2, 7, 11, 15], 9) == [0, 1]
    assert two_sum([3, 2, 4], 6) == [1, 2]
    assert two_sum([3, 3], 6) == [0, 1]
    assert two_sum([1, 2, 3], 5) == [1, 2]
    assert two_sum([1, 2, 3], 7) is None

    print("All tests passed!")


tests()
