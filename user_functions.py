import json

def calculate(expression: str) -> str:
    """
    Evaluates a mathematical expression and returns the result.

    :param expression: The mathematical expression to evaluate.
    :return: Result of the calculation as a JSON string.
    """
    try:
        # WARNING: Using eval can be dangerous; ensure to sanitize inputs in production.
        result = eval(expression)
        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})

# Set of user-defined functions
user_functions = {calculate}
