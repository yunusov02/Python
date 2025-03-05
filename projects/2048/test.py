def right(array):
    """
    Example
    2 4 4 8 -> 0 2 8 8
    0 0 2 0 -> 0 0 0 2
    2 2 2 2 -> 0 0 4 4
    0 0 0 0 -> 0 0 0 0
    """
        
    for i in range(4):

        new_row = [num for num in array[i] if num != 0]

        while len(new_row) < 4:
            new_row.insert(0, 0)
        
        for j in range(3, 0, -1):
            if new_row[j] == new_row[j-1] and new_row[j-1] != 0:
                new_row[j] += new_row[j-1]
                new_row[j-1] = 0

        final_row = [num for num in new_row if num != 0]
        while len(final_row) < 4:
            final_row.insert(0, 0)


        array[i] = final_row    


        # for j in range(4 - 1, 0, -1):
        #     if array[i][j] == array[i][j-1] or array[i][j] == 0 or array[i][j-1] == 0:
        #         array[i][j] += array[i][j-1]
                
        #         temp = j - 1
        #         while temp > 0:
        #             array[i][temp] = array[i][temp-1]
        #             temp -= 1

        #         array[i][temp] = 0

    return array

    
array = [
    [2, 4, 4, 8],
    [0, 0, 2, 2],
    [2, 2, 2, 4],
    [0, 2, 0, 0]
]

array = right(array)

for i in range(4):
    print(array[i])
