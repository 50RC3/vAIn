import ast
import astor
import git
from typing import List, Dict, Any
import numpy as np
from .reinforcement_learning.agent import RLAgent

class CodeEvolution:
    """Manages self-modifying code capabilities through genetic programming and RL"""
    
    def __init__(self, repo_path: str, backup_branch: str = "backup"):
        self.repo_path = repo_path
        self.repo = git.Repo(repo_path)
        self.backup_branch = backup_branch
        self.mutation_rate = 0.1
        self.population_size = 20
        self.rl_agent = RLAgent(
            state_size=128,  # Code embedding size
            action_size=10,  # Number of possible code transformations
            algorithm='PPO'
        )
        self.successful_mutations = {}
        
    def optimize_code(self, filepath: str, performance_metric: callable) -> bool:
        """Optimize code using genetic programming and RL"""
        # Create backup
        self._create_backup()
        
        try:
            # Parse source code
            with open(filepath, 'r') as f:
                source = f.read()
            tree = ast.parse(source)
            
            # Generate initial population
            population = self._generate_mutations(tree)
            
            # Evaluate and evolve
            best_code = None
            best_performance = float('-inf')
            
            for generation in range(10):
                for variant in population:
                    try:
                        # Convert AST back to source
                        mutated_source = astor.to_source(variant)
                        
                        # Safely test mutation
                        with self._safe_code_env():
                            performance = performance_metric(mutated_source)
                            
                        if performance > best_performance:
                            best_performance = performance
                            best_code = mutated_source
                            self._store_successful_mutation(filepath, mutated_source, performance)
                    except:
                        continue
                
                # Generate next generation
                population = self._evolve_population(population, performance_metric)
            
            if best_code:
                # Commit optimization
                self._safe_commit(filepath, best_code)
                return True
                
        except Exception as e:
            self._restore_backup()
            raise e
            
        return False
        
    def _generate_mutations(self, tree: ast.AST) -> List[ast.AST]:
        """Generate code mutations using genetic programming"""
        mutations = []
        for _ in range(self.population_size):
            mutated = self._mutate_ast(tree.copy())
            mutations.append(mutated)
        return mutations
        
    def _mutate_ast(self, tree: ast.AST) -> ast.AST:
        """Apply random mutations to AST"""
        for node in ast.walk(tree):
            if random.random() < self.mutation_rate:
                # Apply RL-selected transformation
                state = self._encode_node(node)
                action = self.rl_agent.act(state)
                tree = self._apply_transformation(tree, node, action)
        return tree
        
    def _evolve_population(self, population: List[ast.AST], 
                          fitness_fn: callable) -> List[ast.AST]:
        """Evolve code population using genetic algorithms"""
        # Calculate fitness
        fitness_scores = []
        for variant in population:
            try:
                source = astor.to_source(variant)
                score = fitness_fn(source)
            except:
                score = float('-inf')
            fitness_scores.append(score)
            
        # Select parents
        parents = self._select_parents(population, fitness_scores)
        
        # Create next generation
        next_gen = []
        while len(next_gen) < self.population_size:
            p1, p2 = random.sample(parents, 2)
            child = self._crossover(p1, p2)
            child = self._mutate_ast(child)
            next_gen.append(child)
            
        return next_gen
        
    def _safe_code_env(self):
        """Create safe environment for testing code mutations"""
        # Implement sandbox/container for safe code execution
        pass
        
    def _store_successful_mutation(self, filepath: str, code: str, 
                                 performance: float):
        """Store successful code mutations"""
        if filepath not in self.successful_mutations:
            self.successful_mutations[filepath] = []
        self.successful_mutations[filepath].append({
            'code': code,
            'performance': performance,
            'timestamp': time.time()
        })
        
    def _create_backup(self):
        """Create backup branch"""
        current = self.repo.active_branch
        new_branch = self.repo.create_head(self.backup_branch)
        new_branch.checkout()
        return current
        
    def _restore_backup(self):
        """Restore from backup branch"""
        self.repo.heads[self.backup_branch].checkout()
        
    def _safe_commit(self, filepath: str, code: str):
        """Safely commit code changes"""
        with open(filepath, 'w') as f:
            f.write(code)
        self.repo.index.add([filepath])
        self.repo.index.commit("Automated code optimization")
