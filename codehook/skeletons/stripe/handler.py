handler_logic = """
numbers = [2, 3, 7, 4, 8]

even_numbers = [number for number in numbers if number % 2 == 0]
squares = [number**2 for number in even_numbers]
result = sum(squares)

print("Original data:", numbers)
print("Even numbers:", even_numbers)
print("Square values:", squares)
print("Sum of squares:", result)
"""