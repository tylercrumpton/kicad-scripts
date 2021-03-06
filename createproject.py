#!/usr/bin/env python3

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
import argparse

git_modules = [
    {
        "path": "hardware/includes/CrumpPrints.pretty",
        "url": "https://github.com/tylercrumpton/CrumpPrints.pretty.git",
    },
    {
        "path": "hardware/includes/CrumpSchemes",
        "url": "https://github.com/tylercrumpton/CrumpSchemes.git",
    },
    {
        "path": "hardware/includes/CrumpPrintSymbols.pretty",
        "url": "https://github.com/tylercrumpton/CrumpPrintSymbols.pretty.git",
    },
]


class cd:
    """Context manager for changing the current working directory"""

    def __init__(self, new_path):
        self.new_path = os.path.expanduser(new_path)

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


class ProjectAlreadyExistsError(Exception):
    pass


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
        self.has_started_creating_dirs = False

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):

        if etype is not None and self.has_started_creating_dirs:
            shutil.rmtree(self.project_path)
        return True

    def setup_git(self):
        # Make sure we're keeping the empty ProjectSpecific.pretty directory:
        open(os.path.join(self.project_specific_path, ".gitkeep"), "a").close()

        with cd(self.project_path):
            subprocess.run(["git", "init"])

            print("Adding CrumpLibs for schematic symbols and footprints")
            for module in git_modules:
                subprocess.run(
                    ["git", "submodule", "add", module["url"], module["path"]],
                    capture_output=True,
                )

            print("Staging files for Git commit")
            subprocess.run(["git", "add", "."])

    def setup_dirs(self):

        if os.path.isdir(self.project_path):
            error = f"ERROR: Directory {self.project_path + os.sep} already exists."
            print(error)
            raise ProjectAlreadyExistsError(error)

        self.has_started_creating_dirs

        print(f"Creating file structure in {self.project_path}")
        os.makedirs(self.project_path)
        os.makedirs(self.hardware_path)
        os.makedirs(self.include_path)
        os.makedirs(self.project_specific_path)

    def copy_project_template(self):

        print(f"Copying Git files to {self.project_path}")
        shutil.copy(
            os.path.join(self.template_path, "DOTgitignore"),
            os.path.join(self.project_path, ".gitignore"),
        ),

        print(f"Copying KiCad project template to {self.hardware_path}")
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
        shutil.copy(
            os.path.join(self.template_path, "fp-lib-table"), self.hardware_path
        )
        shutil.copy(
            os.path.join(self.template_path, "sym-lib-table"), self.hardware_path
        )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("name", help="name of the project to create")

    args = parser.parse_args()

    with ProjectCreator(args.name) as pc:
        pc.setup_dirs()
        pc.copy_project_template()
        pc.setup_git()


if __name__ == "__main__":
    main()
