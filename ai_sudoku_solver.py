import numpy as np

# Load sudokus
sudoku = np.load("data/very_easy_puzzle.npy")
print("very_easy_puzzle.npy has been loaded into the variable sudoku")
print(f"sudoku.shape: {sudoku.shape}, sudoku[0].shape: {sudoku[0].shape}, sudoku.dtype: {sudoku.dtype}")

# Load solutions for demonstration
solutions = np.load("data/very_easy_solution.npy")
print()

# Print the first 9x9 sudoku...
print("First sudoku:")
print(sudoku[0], "\n")

# ...and its solution
print("Solution of first sudoku:")
print(solutions[0])


def sudoku_solver(sudoku):
    solved_sudoku = sudoku
    domain_arr = create_list_arr()
    multi_domain = False
    invalid_sudoku = False

    if check_duplicate_row(sudoku) is True or check_duplicate_col(sudoku) is True:
        solved_sudoku[solved_sudoku > -1] = -1
        invalid_sudoku = True
    else:
        for row in range(0, 9):
            for col in range(0, 9):
                if sudoku[row][col] == 0:
                    # for each empty cell on the board, finds the list of possible numbers based on
                    # the numbers that appear in its row, column and unit/square
                    current_domain_row = check_row(sudoku, row, [1, 2, 3, 4, 5, 6, 7, 8, 9])
                    current_domain_col = check_column(sudoku, col, [1, 2, 3, 4, 5, 6, 7, 8, 9])
                    current_domain_unit = check_unit(sudoku, row, col, [1, 2, 3, 4, 5, 6, 7, 8, 9])

                    # if only one element is left change empty cell to that value
                    if len(current_domain_row) == 1:
                        solved_sudoku[row][col] = current_domain_row[0]
                        # if value doesn't match up across the row, column and unit/square- invalid
                        if current_domain_row[0] not in (current_domain_col or current_domain_unit):
                            solved_sudoku[solved_sudoku > -1] = -1
                            invalid_sudoku = True
                        break
                    else:
                        current_domain_col = check_column(sudoku, col, current_domain_row)
                        # if only one element is left change current cell to domain value found
                        if len(current_domain_col) == 1 and current_domain_col == current_domain_row:
                            solved_sudoku[row][col] = current_domain_col[0]
                        else:
                            current_domain_unit = check_unit(sudoku, row, col, [1, 2, 3, 4, 5, 6, 7, 8, 9])
                            if len(current_domain_unit) == 1:
                                solved_sudoku[row][col] = current_domain_unit[0]
                            else:
                                # in the case that the "current domain" has multiple values:
                                domain_set \
                                    = set(current_domain_row).intersection(current_domain_col, current_domain_unit)
                                if len(domain_set) > 1:
                                    multi_domain = True
                                    # store domain set as a string, to be stored in a 2d array, for each qualifying
                                    # cell
                                    domain_list = list(domain_set)
                                    domain_str = ''.join(str(e) for e in domain_list)
                                    domain_arr[row][col] = domain_str
                                else:
                                    solved_sudoku[row][col] = list(domain_set)[0]

    # all other possible spaces filled, if there are many possible values for a cell:
    if multi_domain is True and invalid_sudoku is False:
        solved_sudoku = solve_multi_domain(solved_sudoku, domain_arr)

    return solved_sudoku


# checks if there's duplicate numbers in each row of the sudoku, if so, sudoku is invalid
def check_duplicate_row(puzzle):
    duplicate = False
    for row in range(0, 9):
        arr = puzzle[row]
        arr = [x for x in arr if x != 0]
        if len(arr) != len(set(arr)):
            duplicate = True
    return duplicate


# checks if there's duplicate numbers in each column of the sudoku, if so then sudoku is invalid
def check_duplicate_col(puzzle):
    duplicate = False
    for col in range(0, 9):
        arr = puzzle.T[col]
        arr = [x for x in arr if x != 0]
        if len(arr) != len(set(arr)):
            duplicate = True
    return duplicate


def check_column(puzzle, current_col, domain_list):
    # for each row in column of current square, check against domain list and remove number
    for row in puzzle.T[current_col]:
        if row in domain_list:
            domain_list.remove(row)
    return domain_list


def check_row(puzzle, current_row, domain_list):
    # for each column in row of current square, check against domain list and remove numbers from list
    for col in puzzle[current_row]:
        if col in domain_list:
            domain_list.remove(col)
    return domain_list


def check_unit(puzzle, current_row, current_col, domain_list):
    # check each element of the current cell's unit/square and remove numbers from the domain list
    # unit square dimenions
    x = (current_col // 3) * 3  # change
    y = (current_row // 3) * 3  # change
    for a in range(0, 3):
        for b in range(0, 3):
            if puzzle[y + a][x + b] in domain_list:
                domain_list.remove(puzzle[y + a][x + b])
    return domain_list


def create_list_arr():
    array = np.empty([9, 9], dtype="<U9")
    array.fill("0")
    return array


def solve_multi_domain(solved_sudoku, domain_arr):
    # domain_arr is a 2d array storing strings (to be converted to int lists) containing a set of
    # possible values for each qualifying cell - the indices of the string corresponds to the
    # indices of the matching cell in the sudoku
    multi_multi_domain = False
    for a in range(0, 9):
        for b in range(0, 9):
            if domain_arr[a][b] != "0":
                domain_list = [int(s) for s in domain_arr[a][b]]
                # as more sudoku spaces have been filled, checks again
                domain_row = check_row(sudoku, a, domain_list)
                domain_col = check_column(sudoku, b, domain_list)
                domain_unit = check_unit(sudoku, a, b, domain_list)
                if len(domain_row) == 1:
                    solved_sudoku[a][b] = domain_row[0]
                    domain_arr[a][b] = "0"
                    # recursive call to go back to start of 2d array
                    solve_multi_domain(solved_sudoku, domain_arr)
                else:
                    if len(domain_col) == 1:
                        solved_sudoku[a][b] = domain_row[0]
                        domain_arr[a][b] = "0"
                        solve_multi_domain(solved_sudoku, domain_arr)
                    else:
                        if len(domain_unit) == 1:
                            solved_sudoku[a][b] = domain_row[0]
                            domain_arr[a][b] = "0"
                            solve_multi_domain(solved_sudoku, domain_arr)
                        else:
                            # checks for hidden singles in the sudoku, i.e. if there's only one
                            # possible candidate left for a cell based on the candidates of cells
                            # in its row, column and unit
                            multi_multi_domain = True
                            something = check_domains(domain_arr, a, b, domain_list)
                            if len(something) == 1:
                                solved_sudoku[a][b] = something
                                domain_arr[a][b] = "0"

    if multi_multi_domain is True:
        # in the case that backtracking is needed as there are multiple options for a cell
        if not recursive_domain(solved_sudoku, domain_arr, 0):
            # invalid sudoku
            solved_sudoku[solved_sudoku > -1] = -1

    return solved_sudoku


def is_valid(puzzle, row, col, num):
    # ensures that each possible candidate value is actually valid and doesn't
    # already exist in the cell's row, column or square
    counter = 0
    while counter < 9:
        if puzzle[row][counter] == num:
            return False
        if puzzle[counter][col] == num:
            return False
        counter += 1
    x = (col // 3) * 3
    y = (row // 3) * 3
    for a in range(0, 3):
        for b in range(0, 3):
            if puzzle[y + a][x + b] == num:
                return False
    return True


def check_domains(domain_matrix, row, col, domain_ele):
    for x in range(9):
        if domain_matrix[row][x] != "0":
            domain_ele = to_string(domain_ele, domain_matrix[row][x])
            if len(domain_ele) == 0:
                break

        if domain_matrix[x][col] != "0":
            domain_ele = to_string(domain_ele, domain_matrix[x][col])
            if len(domain_ele) == 0:
                break

        x = (col // 3) * 3
        y = (row // 3) * 3
        for a in range(0, 3):
            for b in range(0, 3):
                if domain_matrix[y + a][x + b] != '0':
                    domain_ele = to_string(domain_ele, domain_matrix[y + a][x + b])
                    if len(domain_ele) == 0:
                        break
    return domain_ele


def to_string(ele_1, ele_2):
    dom_set = set(ele_1).intersection(set(ele_2))
    domain_ele = "".join(map(str, set(ele_1) - dom_set))
    return domain_ele


def recursive_domain(puzzle, domain_arr, cell_num):
    # d_array --> domain array
    # recursive call to calculate new domains of constraints in domain arr
    # for each cell, calculate the domain set for its 3 constrains, if len == 1
    # replace, else call function again
    # for cell_num in range(81):
    while cell_num <= 80:
        row = int(cell_num / 9)
        col = cell_num % 9
        domain_list = [int(s) for s in domain_arr[row][col]]
        if puzzle[row][col] != 0:
            return recursive_domain(puzzle, domain_arr, cell_num + 1)
        for num in domain_list:
            if is_valid(puzzle, row, col, num) is True:
                puzzle[row][col] = num
                if recursive_domain(puzzle, domain_arr, cell_num + 1) is True:
                    return True
                puzzle[row][col] = 0
        return False
    return True


if __name__ == "__main__":

    SKIP_TESTS = False

    if not SKIP_TESTS:
        import time

        difficulties = ['very_easy', 'easy', 'medium', 'hard']

        for difficulty in difficulties:
            print(f"Testing {difficulty} sudokus")

            sudokus = np.load(f"data/{difficulty}_puzzle.npy")
            solutions = np.load(f"data/{difficulty}_solution.npy")

            count = 0
            for i in range(len(sudokus)):
                sudoku = sudokus[i].copy()
                print(f"This is {difficulty} sudoku number", i)
                print(sudoku)

                start_time = time.process_time()
                solution = sudoku_solver(sudoku)
                end_time = time.process_time()

                print(f"This is the solution for {difficulty} sudoku number", i)
                print(solution)

                print("Is the solution correct?")
                if np.array_equal(solution, solutions[i]):
                    print("Yes! Correct solution.")
                    count += 1
                else:
                    print("No, the correct solution is:")
                    print(solutions[i])

                print("This sudoku took", end_time - start_time, "seconds to solve.\n")

            print(f"{count}/{len(sudokus)} {difficulty} sudokus correct")
            if count < len(sudokus):
                break