from sympy import symbols, And, Or, Not, Implies, Xor, Equivalent, simplify
from sympy.parsing.sympy_parser import parse_expr

class PropositionalLogic:
    """
    A class to represent propositional logic and perform advanced logical operations.
    Supports complex expression parsing, truth table generation, and additional operators.
    """

    def __init__(self):
        """Initialize the propositional logic system with no variables."""
        self.variables = {}

    def add_variable(self, var_name: str, value: bool = False) -> None:
        """
        Adds a logical variable with a default value.
        :param var_name: Name of the variable (string)
        :param value: Initial value of the variable (boolean)
        """
        self.variables[var_name] = value
        print(f"Variable added: {var_name} -> {value}")

    def set_variable(self, var_name: str, value: bool) -> None:
        """
        Updates the value of an existing variable.
        :param var_name: Name of the variable (string)
        :param value: New value of the variable (boolean)
        """
        self._check_variable_exists(var_name)
        self.variables[var_name] = value
        print(f"Variable updated: {var_name} -> {value}")

    def evaluate_expression(self, expression: str) -> bool:
        """
        Evaluates a logical expression using sympy.
        :param expression: A logical expression to evaluate (string)
        :return: Evaluated result (boolean)
        """
        expr = self._parse_expression(expression)
        return bool(expr.subs(self.variables))

    def generate_truth_table(self, expression: str) -> None:
        """
        Generates a truth table for a given logical expression.
        :param expression: A logical expression to evaluate (string)
        """
        expr = self._parse_expression(expression)
        variables = list(expr.free_symbols)
        print("Truth Table:")
        print(" | ".join(f"{str(v):^5}" for v in variables) + " | Result")
        print("-" * (7 * len(variables) + 9))

        for values in self._truth_table_combinations(len(variables)):
            subs = {var: val for var, val in zip(variables, values)}
            result = bool(expr.subs(subs))
            print(" | ".join(f"{int(v):^5}" for v in values) + f" | {int(result)}")

    def generate_truth_table_data(self, expression: str):
        """
        Generates the truth table as a list of dictionaries for programmatic use.
        :param expression: A logical expression to evaluate (string)
        :return: List of dictionaries containing the truth table data
        """
        expr = self._parse_expression(expression)
        variables = list(expr.free_symbols)
        table = []
        for values in self._truth_table_combinations(len(variables)):
            subs = {var: val for var, val in zip(variables, values)}
            result = bool(expr.subs(subs))
            table.append({str(var): val for var, val in subs.items()} | {"Result": result})
        return table

    def _parse_expression(self, expression: str):
        """
        Parses a logical expression into a sympy object.
        :param expression: Logical expression (string)
        :return: Parsed sympy object
        """
        # Replace user-friendly operators with SymPy compatible ones
        expression = expression.replace("Nand", "Not(And").replace(")", " )")
        try:
            return parse_expr(expression, local_dict=self._get_symbols())
        except Exception as e:
            raise ValueError(f"Error parsing expression: {expression}. Details: {e}")

    def _get_symbols(self):
        """Creates sympy symbols for all variables."""
        return {var: symbols(var) for var in self.variables}

    def _truth_table_combinations(self, num_vars: int):
        """Generates all combinations of truth values for a given number of variables."""
        from itertools import product
        return product([False, True], repeat=num_vars)

    def _check_variable_exists(self, var_name: str) -> None:
        """Check if a variable exists in the logic system."""
        if var_name not in self.variables:
            raise ValueError(f"Variable '{var_name}' not found.")

    def __str__(self) -> str:
        """Return a string representation of all variables and their values."""
        return "\n".join(f"{var} ({type(val).__name__}): {val}" for var, val in self.variables.items())

# Example usage
if __name__ == "__main__":
    logic_system = PropositionalLogic()

    # Add variables
    logic_system.add_variable("A", True)
    logic_system.add_variable("B", False)
    logic_system.add_variable("C", True)

    # Custom operator with parsing fix
    print(f"Nand(A, C): {logic_system.evaluate_expression('Nand(A, C)')}")

    # Truth table programmatic usage
    truth_table = logic_system.generate_truth_table_data("A and (B or C)")
    print("\nGenerated Truth Table Data:")
    print(truth_table)
