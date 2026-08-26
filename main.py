def create_multiplier(multiplier):

    def multiply(a):
        return a * multiplier

    return multiply


double = create_multiplier(2)
res = double(5)  # This will return 10


print(res)  # Output: 10