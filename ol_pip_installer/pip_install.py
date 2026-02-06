from odoo import models, fields, _
from odoo.exceptions import UserError
import subprocess
import sys


class PipInstallWizard(models.TransientModel):
    _name = 'pip.install.wizard'
    _description = 'Pip Install Wizard'

    name = fields.Char(string="Command", required=True, help="Enter the pip command to execute, e.g., 'pip install <package>'")

    def action_install_now(self):
        command = self.name.strip()
        if not command:
            raise UserError(_("Please enter a valid pip command."))

        # Split the command into arguments
        command_parts = command.split(' ')
        if command_parts[0].lower() != 'pip':
            raise UserError(_("The command must start with 'pip'."))

        try:
            # Execute the pip command
            result = subprocess.run(
                [sys.executable, "-m"] + command_parts,
                capture_output=True,
                text=True
            )
            # Raise an error if the command failed
            if result.returncode != 0:
                raise UserError(_("Command failed:\n%s") % result.stderr)

            # Return the output on success
            raise UserError(_("Command succeeded:\n%s") % result.stdout)

        except Exception as e:
            raise UserError(_("An error occurred:\n%s") % str(e))
