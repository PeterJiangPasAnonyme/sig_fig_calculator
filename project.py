import sys
import math
import re
from webbrowser import get
from prettytable import PrettyTable


mode = ""


def main():
    """Get a mathematical formula from the user and calculate step by step with regard to significant figures"""
    # Print the instructions to the user
    print_instructions()

    # Attain mode of calculator from user
    print("Please select mode. To round at last step, type 'R'; to round every step, type 'SYY'.")
    while True:
        mode = input("Mode: ")
        if mode == "R" or mode == "SYY":
            break

    # Loop forever until the user terminates the program using Control + D
    while True:
        try:
            # Continue asking the user for a string until it passes basic tests of being a mathematical formula
            while True:
                formula = input("Formula: ")
                # Clear all spaces from the formula
                formula = formula.replace(" ", "")
                if is_valid(formula):
                    break
                else:
                    print("Invalid formula!")

            # Replace "pi" and "e" with strings of actual floats
            formula = formula.replace("pi", str(math.pi)).replace("e", str(math.e))

            # Add parentheses to parts of the formula to ensure it's processable by further algorithms
            formula_list = extract_steps(formula)

            # Calculate the formula and print the result
            if mode == "R":
                result = [d for d in round_to_sf("".join(calculate(formula_list)), get_sf(calculate(formula_list)))]
            else:
                result = calculate(formula_list)
            printed = PrettyTable()
            printed.field_names = ["".join(result)]
            print(printed)
        except EOFError:
            print()
            sys.exit()


def print_instructions():
    """Print the instructions for the user"""
    print("Please enter the formula to calculate.")
    # Parentheses are used to enclose parts of the formula to calculate first
    print("Please only use parentheses () to encapsulate parts of the formula.")
    # "pi" and "e" are used to replace respecitvely the ratio of a circle's circumference to its diameter and the natural number
    print("Supported symbols: . 0 1 2 3 4 5 6 7 8 9 e pi")
    # Square brackets ae used to enclose the arguments to a trigonometric or inverse trigonometric function
    print("Supported operations: + - * / ^ sin[x] cos[x] tan[x] asin[x] acos[x] atan[x]")
    # Trigonometric functions only take in values in radians as input; inverse trigonometric function returns values in radians as well
    print("Please enter an angle in radians to a trigonometric function!!!")
    print("Tip: If an angle in degrees is given, convert it to radians by angle * pi / 180.00000000")
    print("The program does not recognize exact numbers, please add as much trailing zeros as necessary to exact numbers to avoid diminishing the significant digits of the result")
    # Omission of multiplication signs will not be processable
    print("Tip: Please don't omit any multiplication signs!!!")
    print("Press Control + D to quit.")


def is_valid(formula):
    """Basic validity check of whether the argument is a mathematical formula"""
    # Check for characters that are not mathematical symbols, parentheses, brackets, trigonometric functions, "pi" or "e"
    for s in (
        formula.replace("asin", "")
        .replace("acos", "")
        .replace("atan", "")
        .replace("sin", "")
        .replace("cos", "")
        .replace("tan", "")
        .replace("pi", "")
        .replace("e", "")
    ):
        if (
            s not in ("+", "-", "*", "/", "^", "e", ".", "(", ")", "[", "]")
            and not s.isnumeric()
        ):
            return False

    # Check for opened parentheses and brackets that are not closed
    if (formula.count("(") != formula.count(")")) or (
        formula.count("[") != formula.count("]")
    ):
        return False

    # Check for impossible combinations of mathematical symbols, parentheses or brackets
    elif re.search(
        r"(\((\+|\*|/|\^|\.|\[|\])|(\+|-|\*|/|\^|\.|\[)\))", formula
    ) or re.search(r"((\+|-|\*|/|\^|\.)(\+|\*|/|\^|\.))|(\+|\.)-", formula):
        return False
    else:
        return True


def extract_steps(formula):
    """Add parentheses to parts of the formula to ensure it's processable by further algorithms"""
    char_list = [c for c in formula]
    char_list.insert(0, "(")
    char_list.append(")")
    return extract_trig_steps(extract_pow_steps(extract_addsub_steps(char_list)))


def extract_addsub_steps(char_list):
    """Put addends, minuends and subtrahends inside a pair of parentheses"""
    i = 0
    while True:
        # For each plus or minus sign in the argument, place parentheses around the addends, minuends and subtrahends before and after the sign
        if (char_list[i] == "+") or (
            char_list[i] == "-" and char_list[i - 1] not in ("(", "[")
        ):
            # When a plus or minus sign is found and the minus sign does not denote the negative of a number of formula
            # Open parentheses after the sign
            char_list.insert(i + 1, "(")

            # Make sure to have looped over the whole addend or subtrahend before closing the parentheses
            a = i + 2
            s = 0
            t = 0
            while True:
                if s == 0 and t == 0:
                    if char_list[a] in (")", "]", "+", "-"):
                        char_list.insert(a, ")")
                        break
                    elif a + 1 == len(char_list):
                        char_list.append(")")
                        break
                match char_list[a]:
                    case "(":
                        s += 1
                    case ")":
                        s -= 1
                    case "[":
                        t += 1
                    case "]":
                        t -= 1
                a += 1

            # Place right parenthesis before the sign
            char_list.insert(i, ")")

            # Make sure to have looped over the whole addend or minuend before placing the left parenthesis
            a = i - 1
            s = 0
            t = 0
            while True:
                if s == 0 and t == 0:
                    if char_list[a] in ("(", "[", "+", "-"):
                        char_list.insert(a + 1, "(")
                        break
                    elif a == 0:
                        char_list.insert(0, "(")
                        break
                match char_list[a]:
                    case "(":
                        s += 1
                    case ")":
                        s -= 1
                    case "[":
                        t += 1
                    case "]":
                        t -= 1
                a -= 1

            # Make up for the changed index of a value of the list due to adding parentheses
            i += 2

        elif char_list[i] == "-" and char_list[i - 1] in ("(", "["):
            # When a minus sign is found and the minus sign denotes the negative of a number of formula
            # Open parentheses after the sign
            char_list.insert(i + 1, "(")

            # Make sure to have looped over the whole addend or subtrahend before closing the parentheses
            a = i + 2
            s = 0
            t = 0
            while True:
                if s == 0 and t == 0:
                    if char_list[a] in (")", "]", "+", "-"):
                        char_list.insert(a, ")")
                        break
                    elif a + 1 == len(char_list):
                        char_list.append(")")
                        break
                match char_list[a]:
                    case "(":
                        s += 1
                    case ")":
                        s -= 1
                    case "[":
                        t += 1
                    case "]":
                        t -= 1
                a += 1

        i += 1

        # Break when the end of the list is reached
        if i == len(char_list):
            break

    return char_list


def extract_pow_steps(char_list):
    """Put the calculation of a power inside a pair of parentheses"""
    i = 0
    while True:
        # For each caret sign in the argument, place parentheses before the base and after the exponent
        if char_list[i] == "^":
            # When a caret sign is found
            if char_list[i + 1] == "(":
                # If the exponent is surrounded by parentheses
                # Iterate over the list until the end of the exponent to place the right parenthesis for the whole exponential calculation
                a = i + 1
                s = 0
                t = 0
                while True:
                    match char_list[a]:
                        case "(":
                            s += 1
                        case ")":
                            s -= 1
                        case "[":
                            t += 1
                        case "]":
                            t -= 1
                    if s == 0 and t == 0:
                        char_list.insert(a + 1, ")")
                        break
                    a += 1

            else:
                # If the exponent is not surrounded by parentheses
                # Iterate over the exponent number before placing the right parenthesis for the whole exponential calculation
                a = i + 1
                while True:
                    if not char_list[a].isnumeric() and char_list[a] != ".":
                        char_list.insert(a, ")")
                        break
                    a += 1

            if char_list[i - 1] == ")":
                # If the base is surrounded by parentheses
                # Iterate over the list until the beginning of the base to place the left parenthesis for the whole exponential calculation
                a = i - 1
                s = 0
                t = 0
                while True:
                    match char_list[a]:
                        case "(":
                            s += 1
                        case ")":
                            s -= 1
                        case "[":
                            t += 1
                        case "]":
                            t -= 1
                    if s == 0 and t == 0:
                        char_list.insert(a, "(")
                        break
                    a -= 1

                # Make up for the changed index of a value of the list due to adding parentheses
                i += 1

            else:
                # If the base is not surrounded by parentheses
                # Iterate over the base number before placing the left parenthesis for the whole exponential calculation
                a = i - 1
                while True:
                    if not char_list[a].isnumeric() and char_list[a] != ".":
                        char_list.insert(a + 1, "(")
                        break
                    a -= 1

                # Make up for the changed index of a value of the list due to adding parentheses
                i += 1

        i += 1

        # Break when the end of the list is reached
        if i == len(char_list):
            break

    return char_list


def extract_trig_steps(char_list):
    """Put the calculation of a trigonometric or inverse trigonometric function inside a pair of parentheses"""
    i = 0
    while True:
        # For each value in the list
        if "".join(char_list[i : i + 4]) in ("acos", "asin", "atan"):
            # If it corresponds to the beginning of a trigonometric calculation, add parentheses around the calculation
            a = i
            s = 0
            while True:
                if char_list[a] == "[":
                    s += 1
                elif char_list[a] == "]":
                    s -= 1
                if s == 0 and a >= i + 4:
                    char_list.insert(a + 1, ")")
                    break
                a += 1
            char_list.insert(i, "(")
            i += 1

        elif (
            "".join(char_list[i : i + 3]) in ("cos", "sin", "tan")
            and char_list[i - 1] != "a"
        ):
            # If it corresponds to the beginning of an inverse trigonometric calculation, add parentheses around the calculation
            a = i
            s = 0
            while True:
                if char_list[a] == "[":
                    s += 1
                elif char_list[a] == "]":
                    s -= 1
                if s == 0 and a >= i + 3:
                    char_list.insert(a + 1, ")")
                    break
                a += 1
            char_list.insert(i, "(")
            i += 1

        i += 1

        # Break when the end of the list is reached
        if i == len(char_list):
            break

    return char_list


def calculate(formula):
    """A function that recursively "peels off" parentheses and calculates the formula in the argument step by step"""
    global mode
    
    # Peel of the parentheses
    formula.pop(0)
    formula.pop(-1)

    if formula[0] in ("a", "s", "c", "t"):
        # If the formula is a trigonometric or inverse trigonometric function
        for i in range(len(formula)):
            if formula[i] == "[":
                # Extract the arguments of the function
                extracted = formula[i + 1 : -1]
                extracted.append(")")
                extracted.insert(0, "(")

                # Pass the arguments to the function itself and handle error, and replace the argument with the calculated result
                calculated_1 = calculate(extracted)
                if calculated_1 == "Error":
                    return "Error"
                formula[i + 1 : -1] = calculated_1

                # After calculating the argument, pass the calculation of the function to trig_operate()
                if mode == "SYY":
                    calculated_2 = syy_trig_operate(formula)
                else:
                    calculated_2 = r_trig_operate(formula)
                if calculated_2 == "Error":
                    return "Error"
                return calculated_2

    else:
        i = 0
        while True:
            # Iterate over the formula to handle each pair of parentheses right under the current string of the formula
            if formula[i] == "(":
                j = i
                s = 0
                while True:
                    if formula[j] == "(":
                        s += 1
                    elif formula[j] == ")":
                        s -= 1
                    if s == 0:
                        break
                    j += 1

                # For each pair of parentheses
                # Pass the insides to the function itself and handle error, and replace it with the calculated result
                calculated_1 = calculate(formula[i : j + 1])
                if calculated_1 == "Error":
                    return "Error"
                formula[i : j + 1] = calculated_1
                i += len(calculated_1)

                # Break when the end of the list is reached
                if i >= len(formula):
                    break
            else:
                i += 1

                # Break when the end of the list is reached
                if i >= len(formula):
                    break

        # After calculating the insides of each pair of sub-parentheses, pass the calculation of the formula to reg_operate()
        if mode == "SYY":
            calculated_2 = syy_reg_operate(formula)
        else:
            calculated_2 = r_reg_operate(formula)
        if calculated_2 == "Error":
            return "Error"
        return calculated_2


def syy_reg_operate(formula):
    """Carry out operations of addition and subtraction, multiplication and division, exponentiation on the formula passed in as argument"""
    # Clear out all parentheses
    i = 0
    while True:
        if i >= len(formula):
            break
        elif formula[i] == "(" or formula[i] == ")":
            formula.pop(i)
        else:
            i += 1

    # Join the list of the characters of the formula into a string
    formula_str = "".join(formula)

    if (
        "+" not in formula
        and "-" not in formula[1:]
        and "*" not in formula
        and "/" not in formula
        and "^" not in formula
    ):
        # If the argument is already a calculated number, return itself
        return formula

    elif (
        ("+" in formula or "-" in formula)
        and "*" not in formula
        and "/" not in formula
        and "^" not in formula
    ):
        # If the argument comprises of addition and/or subtraction
        dec_places = []
        sum = 0
        if formula[0] != "-":
            formula.insert(0, "+")
        i = 0
        while True:
            # Loop over the passed in list
            if formula[i] == "+":
                # Identify each addition sign and the following addend, and add the number of decimal points of the addend to the list dec_places
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("+", "-"):
                        dec_places.append(get_dp("".join(formula[i + 1 : j + 1])))

                        # Add the addend to the overall sum
                        sum += float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1

            elif formula[i] == "-":
                # Identify each subtraction sign and the following subtrahend, and add the number of decimal points of the subtrahend to the list dec_places
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("+", "-"):
                        dec_places.append(get_dp("".join(formula[i + 1 : j + 1])))

                        # Subtract the subtrahend from the overall sum
                        sum -= float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1
            else:
                i += 1

            # Break when the end of the list is reached
            if i >= len(formula):
                break

        # The number of decimal places to round the sum to is the smallest value of the list dec_places
        dp_f = min(dec_places)
        if dp_f <= 0:
            # Handle cases where the sum is an integer, add trailing zeros if necessary
            sum = int(round(sum, dp_f))
            if str(sum).count("0") > -dp_f:
                exp = len(str(sum).lstrip("-")) - 1
                sum = (
                    "("
                    + str(round(sum, dp_f) / math.pow(10, exp))
                    + (str(round(sum, dp_f)).count("0") + dp_f) * "0"
                    + f"*(10.000000000000000^{exp}))"
                )
        else:
            # Handle cases where the sum has decimal places, add trailing zeros if necessary
            sum = str(round(sum, dp_f)) + "0" * (dp_f - get_dp(round(sum, dp_f)))

        return [d for d in str(sum)]

    elif (
        ("+" not in formula or "-" not in formula)
        and ("*" in formula or "/" in formula)
        and "^" not in formula
    ):
        # If the argument comprises of multiplication and/or division
        sfs = []
        product = 1
        if formula[0] != "/":
            formula.insert(0, "*")
        i = 0
        while True:
            # Loop over the passed in list
            if formula[i] == "*":
                # Identify each multiplication sign and the following multiplier, and add the number of significant figures of the multiplier to the list sfs
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("*", "/"):
                        sfs.append(get_sf("".join(formula[i + 1 : j + 1])))

                        # Multiply to the overall product
                        product *= float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1
            elif formula[i] == "/":
                # Identify each division sign and the following divisor, and add the number of significant figures of the divisor to the list sfs
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("*", "/"):
                        sfs.append(get_sf("".join(formula[i + 1 : j + 1])))

                        try:
                            # Divide from the overall product
                            product /= float("".join(formula[i + 1 : j + 1]))
                        except ZeroDivisionError:
                            # Handle ZeroDivisionError
                            return "Error"
                        i = j
                        break
                    j += 1
            else:
                i += 1

            # Break when the end of the list is reached
            if i >= len(formula):
                break

        # Use the round_to_sf() function to round the overall product to the minimum number of significant figures in the list sfs
        product = round_to_sf(str(product), min(sfs))

        return [d for d in product]

    elif (
        ("+" not in formula or "-" in formula)
        and "*" not in formula
        and "/" not in formula
        and "^" in formula
    ):
        # If the argument comprises of exponentiation
        # Extract the base and exponent
        base_str = formula_str.rpartition("^")[0]
        exp_str = formula_str.rpartition("^")[2]

        if base_str == "10":
            # If the base is 10, assume that it's part of a scientific notation, and give as much significant figures to the results as possible to avoid diminishing the number of significant figures in the result
            result = round_to_sf(str(math.pow(10, float(exp_str))), 16)
        else:
            try:
                # Round the results according the the number of significant figures of the base
                result = round_to_sf(
                    str(math.pow(float(base_str), float(exp_str))), get_sf(base_str)
                )
            except RecursionError:
                # Handle the case where "0^0" is passed in as argument
                return "Error"

        return [d for d in result]

    else:
        # Other cases are handled as errors
        return "Error"


def syy_trig_operate(formula):
    """Calculate trigonometric or inverse trigonometric function passed in as argument"""
    formula_str = "".join(formula)
    formula_str = "".join(formula)

    # Use regular expressions to see whether the argument matches a trigonometric or inverse trigonometric function with a number passed in as argument
    if matches := re.search(
        r"^(sin|cos|tan|asin|acos|atan)\[(-?\d+(\.\d+)?)\]$", formula_str
    ):
        sf = get_sf(matches.group(2))
        match matches.group(1):
            # Calculate the result if the argument matches an acceptable trigonometric or inverse trigonometric function
            case "sin":
                rounded = round_to_sf(str(math.sin(float(matches.group(2)))), sf)
            case "cos":
                rounded = round_to_sf(str(math.cos(float(matches.group(2)))), sf)
            # Since arguments are limited by significant figures, they will not be treated exactly as points where the tangent function approaches infinity, and there is no concern of the argument being outside its domain
            case "tan":
                rounded = round_to_sf(str(math.tan(float(matches.group(2)))), sf)
            # For inverse sine and inverse cosine functions arguments outside the domain are handled
            case "asin":
                try:
                    rounded = round_to_sf(str(math.asin(float(matches.group(2)))), sf)
                except ValueError:
                    return "Error"
            case "acos":
                try:
                    rounded = round_to_sf(str(math.acos(float(matches.group(2)))), sf)
                except ValueError:
                    return "Error"
            case "atan":
                rounded = round_to_sf(str(math.atan(float(matches.group(2)))), sf)
        return [d for d in rounded]
    # Other cases are handled as errors
    else:
        return "Error"


def r_reg_operate(formula):
    """Carry out operations of addition and subtraction, multiplication and division, exponentiation on the formula passed in as argument"""
    # Clear out all parentheses
    i = 0
    while True:
        if i >= len(formula):
            break
        elif formula[i] == "(" or formula[i] == ")":
            formula.pop(i)
        else:
            i += 1

    # Join the list of the characters of the formula into a string
    formula_str = "".join(formula)

    if (
        "+" not in formula
        and "-" not in formula[1:]
        and "*" not in formula
        and "/" not in formula
        and "^" not in formula
    ):
        # If the argument is already a calculated number, return itself
        return formula

    elif (
        ("+" in formula or "-" in formula)
        and "*" not in formula
        and "/" not in formula
        and "^" not in formula
    ):
        # If the argument comprises of addition and/or subtraction
        sum = 0
        if formula[0] != "-":
            formula.insert(0, "+")
        i = 0
        while True:
            # Loop over the passed in list
            if formula[i] == "+":
                # Identify each addition sign and the following addend, and add the number of decimal points of the addend to the list dec_places
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("+", "-"):
                        # Add the addend to the overall sum
                        sum += float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1

            elif formula[i] == "-":
                # Identify each subtraction sign and the following subtrahend, and add the number of decimal points of the subtrahend to the list dec_places
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("+", "-"):
                        # Subtract the subtrahend from the overall sum
                        sum -= float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1
            else:
                i += 1

            # Break when the end of the list is reached
            if i >= len(formula):
                break

        return [d for d in str(sum)]

    elif (
        ("+" not in formula or "-" not in formula)
        and ("*" in formula or "/" in formula)
        and "^" not in formula
    ):
        # If the argument comprises of multiplication and/or division
        product = 1
        if formula[0] != "/":
            formula.insert(0, "*")
        i = 0
        while True:
            # Loop over the passed in list
            if formula[i] == "*":
                # Identify each multiplication sign and the following multiplier, and add the number of significant figures of the multiplier to the list sfs
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("*", "/"):
                        # Multiply to the overall product
                        product *= float("".join(formula[i + 1 : j + 1]))
                        i = j
                        break
                    j += 1
            elif formula[i] == "/":
                # Identify each division sign and the following divisor, and add the number of significant figures of the divisor to the list sfs
                j = i + 1
                while True:
                    if j == len(formula) - 1 or formula[j + 1] in ("*", "/"):
                        try:
                            # Divide from the overall product
                            product /= float("".join(formula[i + 1 : j + 1]))
                        except ZeroDivisionError:
                            # Handle ZeroDivisionError
                            return "Error"
                        i = j
                        break
                    j += 1
            else:
                i += 1

            # Break when the end of the list is reached
            if i >= len(formula):
                break

        return [d for d in product]

    elif (
        ("+" not in formula or "-" in formula)
        and "*" not in formula
        and "/" not in formula
        and "^" in formula
    ):
        # If the argument comprises of exponentiation
        # Extract the base and exponent
        base_str = formula_str.rpartition("^")[0]
        exp_str = formula_str.rpartition("^")[2]

        try:
            # Round the results according the the number of significant figures of the base
            result = str(math.pow(float(base_str), float(exp_str)))
        except RecursionError:
            # Handle the case where "0^0" is passed in as argument
            return "Error"

        return [d for d in result]

    else:
        # Other cases are handled as errors
        return "Error"


def r_trig_operate(formula):
    """Calculate trigonometric or inverse trigonometric function passed in as argument"""
    formula_str = "".join(formula)

    # Use regular expressions to see whether the argument matches a trigonometric or inverse trigonometric function with a number passed in as argument
    if matches := re.search(
        r"^(sin|cos|tan|asin|acos|atan)\[(-?\d+(\.\d+)?)\]$", formula_str
    ):
        sf = get_sf(matches.group(2))
        match matches.group(1):
            # Calculate the result if the argument matches an acceptable trigonometric or inverse trigonometric function
            case "sin":
                rounded = str(math.sin(float(matches.group(2))))
            case "cos":
                rounded = str(math.cos(float(matches.group(2))))
            # Since arguments are limited by significant figures, they will not be treated exactly as points where the tangent function approaches infinity, and there is no concern of the argument being outside its domain
            case "tan":
                rounded = str(math.tan(float(matches.group(2))))
            # For inverse sine and inverse cosine functions arguments outside the domain are handled
            case "asin":
                try:
                    rounded = str(math.asin(float(matches.group(2))))
                except ValueError:
                    return "Error"
            case "acos":
                try:
                    rounded = str(math.acos(float(matches.group(2))))
                except ValueError:
                    return "Error"
            case "atan":
                rounded = str(math.atan(float(matches.group(2))))
        return [d for d in rounded]

    # Other cases are handled as errors
    else:
        return "Error"


def get_sf(number):
    """Returns the number of significant figures of the number in the argument"""
    if str(number).find(".") == -1:
        # If the number is an integer, all digits except the trailing zeros are significant
        return len([d for d in str(number).rstrip("0") if d.isnumeric()])
    elif str(number).startswith("0.") or str(number).startswith("-0."):
        # If the number is a float whose absolute value is smaller than 1, all digits except leading zeros are significant
        return len(str(number).lstrip("-0."))
    elif str(number).startswith("-"):
        # For floats with an absolute value greater than 1, all digits are significant
        return len(str(number)) - 2
    else:
        return len(str(number)) - 1


def get_dp(number):
    """Returns the digit to round to when adding or subtracting numbers"""
    if str(number).find(".") == -1:
        # Return a non-positive value if the number is an integer
        i = 1
        while True:
            if number[0 - i] == "0":
                i += 1
            else:
                return 1 - i
    else:
        # Return the number of decimal places if the number is a float
        return len(str(number).rpartition(".")[2])


def round_to_sf(number, sf_f):
    """Round a number to an intended number of significant figures"""
    # Original number of significant figures
    sf_i = get_sf(number)

    # Number of decimal places
    dec_places = get_dp(number)

    # Number of digits before decimal point
    if dec_places >= sf_i:
        int_places = 0
    else:
        int_places = sf_i - dec_places

    # Total number of digits
    digits = len(number) - number.count("-") - number.count(".")

    if number.find(".") == -1:
        # If the number is an integer
        if sf_f <= sf_i:
            return str(int(round(int(number), sf_f - digits)))

        elif sf_f <= digits:
            # Handle case where rounding makes the number of significant figures ambiguous
            return (
                "("
                + round_to_sf(str(float(number) / math.pow(10, digits - 1)), sf_f)
                + f"*(10.000000000000000^{digits - 1}))"
            )

        else:
            # Handle case where trailing zeros should be added
            return number + "." + (sf_f - digits) * "0"
    else:
        # If the number is a float
        if sf_f <= int_places:
            # Handle case where the number is rounded to an integer
            if number.removeprefix("-")[sf_f - 1] == "0":
                # Handle case where rounding makes the number of significant figures ambiguous
                return (
                    "("
                    + round_to_sf(str(float(number) / math.pow(10, int_places - 1)), sf_f)
                    + f"*(10.000000000000000^{int_places - 1}))"
                )

            else:
                return str(int(round(float(number), sf_f - int_places)))

        else:
            # Handle case where the number is still rounded as a float and add trailing zeros if necessary
            return (
                str(round(float(number), sf_f - sf_i + dec_places))
                + (sf_f - get_sf(round(float(number), sf_f - sf_i + dec_places))) * "0"
            )


if __name__ == "__main__":
    main()
