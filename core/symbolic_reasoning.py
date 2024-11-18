class PropositionalLogic:
    """
    A class to represent propositional logic and perform basic logical operations
    such as AND, OR, NOT, and implication. This is designed to integrate with vAIn 
    for AI-based reasoning and decision-making.
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

    def negation(self, var_name: str) -> bool:
        """
        Negates a logical variable.
        :param var_name: Name of the variable to negate
        :return: Negated value
        """
        self._check_variable_exists(var_name)
        return not self.variables[var_name]

    def conjunction(self, var_name1: str, var_name2: str) -> bool:
        """
        Performs logical AND operation between two variables.
        :param var_name1: First variable
        :param var_name2: Second variable
        :return: Result of AND operation
        """
        self._check_variables_exist(var_name1, var_name2)
        return self.variables[var_name1] and self.variables[var_name2]

    def disjunction(self, var_name1: str, var_name2: str) -> bool:
        """
        Performs logical OR operation between two variables.
        :param var_name1: First variable
        :param var_name2: Second variable
        :return: Result of OR operation
        """
        self._check_variables_exist(var_name1, var_name2)
        return self.variables[var_name1] or self.variables[var_name2]

    def implication(self, var_name1: str, var_name2: str) -> bool:
        """
        Performs logical implication (if var_name1 then var_name2).
        :param var_name1: Premise variable
        :param var_name2: Conclusion variable
        :return: Result of implication
        """
        self._check_variables_exist(var_name1, var_name2)
        return not self.variables[var_name1] or self.variables[var_name2]

    def evaluate_expression(self, expression: str) -> bool:
        """
        Evaluates a logical expression given as a string. Supports 'and', 'or', 'not', and '->' for implication.
        :param expression: A logical expression to evaluate (string)
        :return: Evaluated result (boolean)
        """
        tokens = expression.lower().split()
        if len(tokens) == 3:
            var_name1, operator, var_name2 = tokens
            if operator == 'and':
                return self.conjunction(var_name1, var_name2)
            elif operator == 'or':
                return self.disjunction(var_name1, var_name2)
            elif operator == '->':
                return self.implication(var_name1, var_name2)
            else:
                raise ValueError(f"Unsupported operator '{operator}' in expression.")
        elif len(tokens) == 2:
            operator, var_name = tokens
            if operator == 'not':
                return self.negation(var_name)
            else:
                raise ValueError(f"Unsupported operator '{operator}' in expression.")
        else:
            raise ValueError("Invalid expression format. Expected 'var operator var' or 'operator var'.")

    def _check_variable_exists(self, var_name: str) -> None:
        """Check if a variable exists in the logic system."""
        if var_name not in self.variables:
            raise ValueError(f"Variable '{var_name}' not found.")

    def _check_variables_exist(self, var_name1: str, var_name2: str) -> None:
        """Check if both variables exist in the logic system."""
        self._check_variable_exists(var_name1)
        self._check_variable_exists(var_name2)

    def __str__(self) -> str:
        """Return a string representation of all variables and their values."""
        return "\n".join(f"{var}: {val}" for var, val in self.variables.items())

# Example usage of the PropositionalLogic class tailored for vAIn
if __name__ == "__main__":
    logic_system = PropositionalLogic()
    
    # Add variables
    logic_system.add_variable("A", True)
    logic_system.add_variable("B", False)
    
    # Evaluate some expressions
    print(f"A AND B: {logic_system.conjunction('A', 'B')}")
    print(f"A OR B: {logic_system.disjunction('A', 'B')}")
    print(f"NOT A: {logic_system.negation('A')}")
    print(f"A -> B: {logic_system.implication('A', 'B')}")
    print(f"Evaluate 'A and not B': {logic_system.evaluate_expression('A and not B')}")

    # Display current state of variables
    print("\nCurrent Variables and their Values:")
    print(logic_system)
