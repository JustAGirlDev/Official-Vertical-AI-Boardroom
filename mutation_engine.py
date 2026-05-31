import os
import subprocess
import ast
import astor  # Requires: pip install astor

class CodeMutator:
    def __init__(self, repo_path="."):
        self.repo_path = repo_path

    def _run_cmd(self, cmd):
        """Helper to run shell commands safely within the repo."""
        result = subprocess.run(cmd, shell=True, cwd=self.repo_path, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    def _vcs_prepare(self, branch_name):
        """Creates an isolated git branch for the mutation attempt."""
        self._run_cmd("git checkout main")
        code, _, _ = self._run_cmd(f"git checkout -b {branch_name}")
        return code == 0

    def _vcs_finalize(self, branch_name, success, commit_msg="Swarm self-optimization"):
        """Merges change if successful, rolls back completely if failed."""
        if success:
            self._run_cmd(f"git add .")
            self._run_cmd(f'git commit -m "{commit_msg}"')
            self._run_cmd("git checkout main")
            self._run_cmd(f"git merge {branch_name}")
            self._run_cmd(f"git branch -d {branch_name}")
            return True
        else:
            # Absolute rollback
            self._run_cmd("git reset --hard HEAD")
            self._run_cmd("git checkout main")
            self._run_cmd(f"git branch -D {branch_name}")
            return False

    def mutate_function_ast(self, file_path, target_func_name, new_body_source):
        """
        WISDOM CHOICE: Replaces a specific function's body safely using AST.
        """
        mutation_id = f"ast-{int(os.times().elapsed)}"
        if not self._vcs_prepare(mutation_id):
            return False, "Failed to initialize git mutation branch."

        full_path = os.path.join(self.repo_path, file_path)
        
        try:
            with open(full_path, "r") as f:
                source = f.read()
            
            tree = ast.parse(source)
            new_body_ast = ast.parse(new_body_source).body

            # Walk the tree to find the target function
            modified = False
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == target_func_name:
                    node.body = new_body_ast
                    modified = True
                    break

            if not modified:
                raise ValueError(f"Function '{target_func_name}' not found in AST.")

            # Write back the perfectly formatted code
            with open(full_path, "w") as f:
                f.write(astor.to_source(tree))

            # Validate syntax & verify via compilation
            code, _, err = self._run_cmd(f"python3 -m py_compile {file_path}")
            if code != 0:
                raise SyntaxError(f"AST mutation introduced syntax errors: {err}")

            # Finalize git merge
            self._vcs_finalize(mutation_id, success=True, commit_msg=f"Optimized function: {target_func_name}")
            return True, f"Successfully mutated {target_func_name}."

        except Exception as e:
            self._vcs_finalize(mutation_id, success=False)
            return False, f"AST Mutation failed: {str(e)}"

    def mutate_sed_fallback(self, file_path, old_pattern, new_pattern):
        """
        FALLBACK CHOICE: Uses sed line replacement for quick configurations or simple strings.
        """
        mutation_id = f"sed-{int(os.times().elapsed)}"
        if not self._vcs_prepare(mutation_id):
            return False, "Failed to initialize git mutation branch."

        # Escaping patterns for standard sed usage
        escaped_old = old_pattern.replace("/", "\\/")
        escaped_new = new_pattern.replace("/", "\\/")
        
        sed_cmd = f"sed -i 's/{escaped_old}/{escaped_new}/g' {file_path}"
        code, _, err = self._run_cmd(sed_cmd)

        if code == 0:
            # Check syntax post-sed to make sure we didn't break Python parsing
            check_code, _, _ = self._run_cmd(f"python3 -m py_compile {file_path}")
            if check_code == 0:
                self._vcs_finalize(mutation_id, success=True, commit_msg=f"Sed tweak: {old_pattern} -> {new_pattern}")
                return True, "Sed adjustment applied and verified."
        
        # If anything failed, revert
        self._vcs_finalize(mutation_id, success=False)
        return False, f"Sed mutation failed or caused syntax corruption: {err}"
