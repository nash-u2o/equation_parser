import re
from collections import deque

import numpy as np

# Constant values that can be typed into equation. In the current use of the parser, the variables are plugged into the equation before calling process_equation
# so this program does not deal directly with variables
constants = {
    "pi": np.pi,
    "e": np.e,
}

# PFEMDAS
precedence = {
    "^": 3,
    "*": 2,
    "/": 2,
    "%": 2,
    "+": 1,
    "-": 1,
}

associative = {
    "^": "right",
    "*": "left",
    "/": "left",
    "%": "left",
    "+": "left",
    "-": "left",
}

special_ops = ["(", ")"]  # , ","]

# When defining a function, put the name of it here so the program will recognize it. Define its behavior in _eval_function
functions = [
    "cos",
    "sec",
    "sin",
    "csc",
    "tan",
    "cot",
    "sqrt",
    "log",
    "log10",
]

# Regular expressions to identify input
# pattern = re.compile(r"\d*\.?\d+$|[^\w\s\.]|[\w\.]+")
# Match one or more any alphanumeric, non-whitespace character as well as no .
term = re.compile(r"^\-?\d*\.?\d+$|[\w\.]+")
# Match a real number. Can start with 0 or more integers, contain 0 or 1 .s in the middle, and ends with one or more integers
number = re.compile(r"^\d*\.?\d+$")
# same as above except for negative numbers
real_num = re.compile(r"^\-?\d*\.?\d+$")
# Match a ^ or match any non-alphanumeric, non-whitespace character that is not .
operator = re.compile(r"[^\w\s\.]")
# function_pattern = re.compile(r"\b(?:" + "|".join(functions) + r")\s*\(.*?\)")


def _handle_parenthesis(i, equation, block_tokens) -> int:
    """
    Handles nested parenthesis, adding their expression's contents to block_tokens

    Parameters
    ----------
    i: int
        The count tracking where we are in equation
    equation: str
        The equation
    block_tokens: list
        Holds the tokens within the current parenthesis block

    Returns
    -------
    int
        Returns what i was incremented to
    """
    try:
        left = 1
        right = 0
        while left != right:
            if equation[i] == "(":
                left += 1
                block_tokens.append(equation[i])
                i += 1
            elif equation[i] == ")":
                right += 1
                if right != left:
                    block_tokens.append(equation[i])
                i += 1
            else:
                block_tokens.append(equation[i])
                i += 1
        return i
    except:
        raise ValueError(
            "Error due to malformatted parenthesis near block " + str(block_tokens),
        )


def _parse_and_eval(equation: str) -> np.longdouble:
    """
    Parses the equation recursively and evaluates the results. The recursive results kick back replacing a parenthesis block with the result of the expression
    inside of it, fixing problems with parsing nested parenthesis

    x + (y - (z)))
    1. Evaluate z
    2. Evaluate y - z_results
    3. Evaluate x + y_z_results

    Parameters
    ----------
    equation: str
        The equation to be evaluated

    Returns
    -------
    np.longdouble
        The result of the equation
    """

    try:
        # Tokens to contribute to final evaluation
        tokens = []

        # Tokens inside a parenthesis block
        block_tokens = []
        func = ""
        i = 0
        while i < len(equation):
            # Handle the inside of a function
            if equation[i] in functions:
                func = equation[i]
                i += 1
                if equation[i] != "(":
                    raise ValueError("Unopened parenthsis at index " + i)

                # Inside of parenthesis block now
                i += 1
                i = _handle_parenthesis(i, equation, block_tokens)

                # Recursive call to evaluate inner contents of parenthesis before continuing
                parse_eval_res = _parse_and_eval(block_tokens)
                # Make the function string and then evaluate the function
                complete_func = func + "(" + str(parse_eval_res) + ")"
                eval_res = _eval_function(complete_func)

                block_tokens = []
                tokens.append(eval_res)
            # Handle the start of a parenthesis block
            elif equation[i] == "(":
                i += 1
                i = _handle_parenthesis(i, equation, block_tokens)

                # Recursive call to evaluate inner contents of parenthesis before continuing
                parse_eval_res = _parse_and_eval(block_tokens)
                block_tokens = []
                tokens.append(parse_eval_res)
            else:
                tokens.append(equation[i])
                i += 1

        # Replace variables with their constants for unary parse
        substitute_vars(tokens)

        tokens = _parse_unary(tokens)
        postfix_queue = construct_postfix_queue(tokens)
        res = eval_equation(postfix_queue)
        return res
    except:
        print("Tokens currently processed at error:", tokens)
        raise


def construct_postfix_queue(tokens) -> deque:
    """
    Constructs the postfix queue of the previously infix equation, allowing the program to execute the equation more easily.
    Uses the Shunting Yard Algorithm: https://en.wikipedia.org/wiki/Shunting_yard_algorithm

    Parameters
    ----------
    tokens:
        The characters making up the equation/section of the equation. At this point, unary operators should be recognized

    Returns
    -------
    deque
        Deque of tokens in postfix notation
    """
    stack = deque()
    queue = deque()
    for op in tokens:
        if isinstance(op, np.longdouble):
            queue.append(op)
        elif term.match(str(op)):
            if not real_num.match(str(op)):
                # If a function
                if any(element in op for element in functions):
                    queue.append(op)
                else:
                    try:
                        queue.append(np.longdouble(op))
                    except:
                        raise ValueError("Undefined variable: " + op)
            else:
                queue.append(op)
        elif operator.match(str(op)):
            if op not in special_ops:
                while (
                    len(stack) > 0
                    and stack[0] != "("
                    and (
                        precedence[stack[0]] > precedence[op]
                        or (
                            precedence[stack[0]] == precedence[op]
                            and associative[op] == "left"
                        )
                    )
                ):
                    queue.append(stack.popleft())
                stack.appendleft(op)
            elif op == ",":
                raise ValueError("Undefined operator " + op)
            elif op == "(":
                stack.appendleft(op)
            elif op == ")":
                if len(stack) == 0:
                    raise ValueError("Mismatched parenthesis")
                while stack[0] != "(":
                    if len(stack) == 0:
                        raise ValueError("Mismatched parenthesis")
                    queue.append(stack.popleft())
                if stack[0] != "(":
                    raise ValueError("Mismatched parenthesis")
                stack.popleft()
            else:
                raise ValueError("Error at: " + op)
        else:
            raise ValueError("Error at: " + op)

    while len(stack) > 0:
        if stack[0] == "(" or stack[0] == ")":
            raise ValueError("Mismatched parenthesis")
        queue.append(stack.popleft())
    return queue


# Looks at tokens and, if the token is a defined constant, subsitute its values (pi, euler's constant)
def substitute_vars(tokens):
    for i in range(len(tokens)):
        if tokens[i] in constants:
            tokens[i] = constants[tokens[i]]


def eval_equation(queue) -> np.longdouble:
    """
    Evaluate the postfix equation. All functions have been evaluated at this point

    Parameters
    ----------
    queue: deque
        Postfix queue of tokens

    Returns
    -------
    np.longdouble
        The result of the operation
    """
    operandStack = deque()
    for element in queue:
        try:
            operandStack.appendleft(np.longdouble(element))
        except:
            op2 = operandStack.popleft()
            op1 = operandStack.popleft()

            if element == "^":
                operandStack.appendleft(op1**op2)
            elif element == "*":
                operandStack.appendleft(op1 * op2)
            elif element == "/":
                operandStack.appendleft(op1 / op2)
            elif element == "%":
                operandStack.appendleft(op1 % op2)
            elif element == "+":
                operandStack.appendleft(op1 + op2)
            elif element == "-":
                operandStack.appendleft(op1 - op2)
            else:
                raise ValueError(element + " is undefined")

    # If residual stack has more than one entry, there's a problem with the user's equation
    if len(operandStack) > 1:
        raise ValueError("Malformatted Equation.")
    else:
        # The final result is left at the stop of the stack
        return operandStack[0]


def _eval_function(func) -> np.longdouble:
    """
    Evaluate a function

    NOTE: To add new functions, define their behavior here and put their string in the functions array near the top of this file

    Parameters
    ----------
    func: str
        String of function and its argument. Ex: sin(x)

    Returns
    -------
    np.longdouble
        The result of the operation
    """
    # Find the function's name
    elem_func = func[: func.find("(")]
    # Pull out the function's arguments
    elem_arg = func[func.find("(") + 1 : func.find(")")]

    try:
        if elem_func == "cos":
            return np.cos(np.longdouble(elem_arg))
        elif elem_func == "sec":
            return 1 / np.cos(np.longdouble(elem_arg))
        elif elem_func == "sin":
            return np.sin(np.longdouble(elem_arg))
        elif elem_func == "csc":
            return 1 / np.sin(np.longdouble(elem_arg))
        elif elem_func == "tan":
            return np.tan(np.longdouble(elem_arg))
        elif elem_func == "cot":
            return 1 / np.tan(np.longdouble(elem_arg))
        elif elem_func == "sqrt":
            return np.sqrt(np.longdouble(elem_arg))
        elif elem_func == "log":
            return np.log(np.longdouble(elem_arg))
        elif elem_func == "log10":
            return np.log10(np.longdouble(elem_arg))
        else:
            raise ValueError("Undefined function: " + func)
    except:
        raise ValueError(f"Error with function: {func}")


def _parse_unary(list) -> list:
    """
    Examine the different cases where a - can occur, and determine if it is subtraction or a negative sign

    Parameters
    ----------
    list: list
        List of tokens

    Returns
    -------
    List of tokens modified to allow the parser to handle negtive numbers
    """
    # The final array that holds the modifications
    res = []
    i = 0
    while i < len(list):
        if list[i] == "-":  # or list[i] == "+":  unary + implementation
            if i + 1 < len(list):
                if i == 0:
                    res.append("0")
                    res.append("-")
                    i += 1
                else:
                    # If a "-" is surrounded by two numbers, or if there is a number on the left and an operator on the right, just add the negative sign
                    if (
                        real_num.match(str(list[i - 1]))
                        and real_num.match(str(list[i + 1]))
                    ) or (
                        real_num.match(str(list[i - 1]))
                        and operator.match(str(list[i + 1]))
                    ):
                        res.append(list[i])
                        i += 1
                    # If a "-" has a "(" on the left, or has an operator on the left and a number on the right multiple the number by -1 to flip its sign and append the number
                    elif list[i - 1] == "(" or (
                        operator.match(str(list[i - 1]))
                        and real_num.match(str(list[i + 1]))
                    ):
                        i += 1
                        res.append(-1 * np.longdouble(list[i]))
                        i += 1
                    else:
                        raise ValueError(
                            "Unsupported operation: "
                            + str(list[i - 1])
                            + str(list[i])
                            + str(list[i + 1])
                        )
            else:
                raise ValueError("Error with: -")
        else:
            res.append(list[i])
            i += 1
    return res


def _separate_equation(equation):
    # Add space between all operators and operands
    equation = re.sub(r"([^\w\.])", r" \1 ", equation)
    # Get rid of any extra spaces
    equation = re.sub(r"\s+", " ", equation).strip()
    print(equation)
    return equation


def process_equation(equation):
    """
    Call this method and pass an equation to evaluate it

    Parameters
    ----------
    equation: str
        Equation to be evaluated
    """
    if len(equation) == 0:
        print("Error: Empty Equation")
        return None

    spaced_equation = _separate_equation(equation)
    try:
        ans = _parse_and_eval(list(spaced_equation.split(" ")))
        ans = np.round(ans, decimals=15)
        print("Result: " + str(ans))
        return ans
    except Exception as e:
        print(e.args)


if __name__ == "__main__":
    # equation = "1 + sqrt(1) - 1 -- 1"
    ans = process_equation("6 ^^3 3")
    # eval("(()) 1 + - 2")
    pass
