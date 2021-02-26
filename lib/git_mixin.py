import os

from . import util

class GitMixin:
    def git_command(self, command, repo=None):
        """Executes a git command. Expects an array as command argument,
        with each subcommand, option, argument being a own element.

        The repo argument can be used to specify the folder in which the
        command should be executed."""
        return util.execute_command(
            ["git"] + command,
            working_dir=repo
        )

    def determine_git_repo(self, file_name):
        working_dir = None
        if file_name:
            # Remove the traling filename, we just need the folder
            working_dir = os.path.dirname(file_name)

        # Get git top-level folder
        if working_dir:
            working_dir = self.git_command(
                ["rev-parse", "--show-toplevel"],
                repo=working_dir)

        return working_dir
