"""Creates a project with my common structure and includes.

Directory structure of the new project will be created in the
current directory and will look like:

    {projectname}/
    ├── hardware/
    │   ├── includes/
    │   │   ├── CrumpPrints.pretty/
    │   │   ├── CrumpPrintsSymbols.pretty/
    │   │   └── CrumpSchemes/
    │   ├── {projectname}.kicad_pcb
    │   ├── {projectname}.pro
    │   └── {projectname}.sch
    ├── .gitignore
    └── .gitmodules
"""
import os
import shutil
import subprocess


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class ProjectCreator(object):
    def __init__(self, project_name):
        self.project_name = project_name
        self.current_path = os.getcwd()
        self.project_path = os.path.join(self.current_path, self.project_name)
        self.hardware_path = os.path.join(self.project_path, "hardware")
        self.include_path = os.path.join(self.hardware_path, "includes")
        self.project_specific_path = os.path.join(
            self.include_path, "ProjectSpecific.pretty"
        )
        self.template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates", "createproject"
        )

    def setup_git(self):
        # Make sure we're keeping the empty ProjectSpecific.pretty directory:
        open(os.path.join(self.project_specific_path, ".gitkeep"), "a").close()

        # Init git and stage all files for initial commit:
        with cd(self.project_path):
            subprocess.run(["git", "init"])
            subprocess.run(["git", "add", "."])

    def setup_dirs(self):

        if os.path.isdir(self.project_path):
            print(f"ERROR: Directory {self.project_path + os.sep} already exists.")
            exit(1)

        print(f"Creating file structure in {self.project_path}")
        os.makedirs(self.project_path)
        os.makedirs(self.hardware_path)
        os.makedirs(self.include_path)
        os.makedirs(self.project_specific_path)

    def copy_project_template(self):

        shutil.copy(os.path.join(self.template_path, ".gitignore"), self.project_path)
        shutil.copy(os.path.join(self.template_path, ".gitmodules"), self.project_path)
        shutil.copy(
            os.path.join(self.template_path, "projectname.kicad_pcb"),
            os.path.join(self.hardware_path, f"{self.project_name}.kicad_pcb"),
        )
        shutil.copy(
            os.path.join(self.template_path, "projectname.pro"),
            os.path.join(self.hardware_path, f"{self.project_name}.pro"),
        )
        shutil.copy(
            os.path.join(self.template_path, "projectname.sch"),
            os.path.join(self.hardware_path, f"{self.project_name}.sch"),
        )


def main():
    pc = ProjectCreator("test")
    pc.setup_dirs()
    pc.copy_project_template()
    pc.setup_git()


if __name__ == "__main__":
    main()
