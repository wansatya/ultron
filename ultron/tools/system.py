"""System tools for file operations and command execution"""

import asyncio
import os
from pathlib import Path
from typing import Dict, Any
from .base import Tool, ToolContext, ToolResult


class ExecTool(Tool):
    """Execute shell commands"""

    def __init__(self, sandbox: bool = False, allowed_commands: list = None):
        self.sandbox = sandbox
        self.allowed_commands = allowed_commands or []

    def name(self) -> str:
        return "system.exec"

    def description(self) -> str:
        return "Execute a shell command"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Execute a shell command"""
        valid, error = self.validate_params(params, ["command"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        command = params["command"]

        # Check if command is allowed (if whitelist is set)
        if self.allowed_commands:
            cmd_name = command.split()[0] if command.split() else ""
            if cmd_name not in self.allowed_commands:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command '{cmd_name}' not allowed"
                )

        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            output = stdout.decode() if stdout else ""
            error_output = stderr.decode() if stderr else ""

            if process.returncode == 0:
                return ToolResult(
                    success=True,
                    output=output,
                    metadata={"exit_code": process.returncode}
                )
            else:
                return ToolResult(
                    success=False,
                    output=output,
                    error=error_output,
                    metadata={"exit_code": process.returncode}
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to execute command: {str(e)}"
            )


class ReadFileTool(Tool):
    """Read file contents"""

    def name(self) -> str:
        return "system.read"

    def description(self) -> str:
        return "Read the contents of a file"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Read a file"""
        valid, error = self.validate_params(params, ["file_path"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        file_path = Path(params["file_path"])

        try:
            # Check if file exists
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {file_path}"
                )

            # Read file
            content = file_path.read_text()

            return ToolResult(
                success=True,
                output=content,
                metadata={"file_size": len(content), "path": str(file_path)}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to read file: {str(e)}"
            )


class WriteFileTool(Tool):
    """Write content to a file"""

    def name(self) -> str:
        return "system.write"

    def description(self) -> str:
        return "Write content to a file"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Write to a file"""
        valid, error = self.validate_params(params, ["file_path", "content"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        file_path = Path(params["file_path"])
        content = params["content"]

        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path.write_text(content)

            return ToolResult(
                success=True,
                output=f"Successfully wrote {len(content)} bytes to {file_path}",
                metadata={"bytes_written": len(content), "path": str(file_path)}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to write file: {str(e)}"
            )


class GlobTool(Tool):
    """Find files by pattern"""

    def name(self) -> str:
        return "system.glob"

    def description(self) -> str:
        return "Find files matching a pattern"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Find files matching a glob pattern"""
        valid, error = self.validate_params(params, ["pattern"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        pattern = params["pattern"]
        base_path = Path(params.get("base_path", "."))

        try:
            # Find matching files
            matches = list(base_path.glob(pattern))
            matches = [str(p) for p in matches]

            if matches:
                output = "\n".join(matches)
                return ToolResult(
                    success=True,
                    output=output,
                    metadata={"count": len(matches)}
                )
            else:
                return ToolResult(
                    success=True,
                    output="No files found matching pattern",
                    metadata={"count": 0}
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to search files: {str(e)}"
            )


class GrepTool(Tool):
    """Search file contents"""

    def name(self) -> str:
        return "system.grep"

    def description(self) -> str:
        return "Search for text in files"

    async def execute(self, params: Dict[str, Any], context: ToolContext) -> ToolResult:
        """Search for text in files"""
        valid, error = self.validate_params(params, ["pattern"])
        if not valid:
            return ToolResult(success=False, output="", error=error)

        pattern = params["pattern"]
        file_path = params.get("file_path", ".")

        try:
            # Use grep command
            process = await asyncio.create_subprocess_shell(
                f"grep -r '{pattern}' {file_path}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            output = stdout.decode() if stdout else ""

            if output:
                return ToolResult(
                    success=True,
                    output=output,
                    metadata={"pattern": pattern}
                )
            else:
                return ToolResult(
                    success=True,
                    output="No matches found",
                    metadata={"pattern": pattern}
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"Failed to search: {str(e)}"
            )
