import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import subprocess
import os
import threading
import json
from datetime import datetime

class TruffleIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Truffle Suite: Solidity Unit Tester")
        self.root.geometry("1200x850")
        self.root.minsize(900, 700)
        
        # Project Directory
        self.project_dir = "TruffleProject"
        self.test_running = False
        self.process = None
        
        # Configure styles
        self.configure_styles()
        
        # Setup UI
        self.setup_ui()
        
        # Pre-fill Code
        self.set_default_code()
        
        # Bind cleanup on close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_styles(self):
        """Configure ttk styles for better appearance."""
        style = ttk.Style()
        
        # Try to use 'clam' theme if available
        try:
            style.theme_use('clam')
        except:
            pass  # Use default theme if 'clam' is not available
        
        # Configure colors
        self.bg_dark = "#1e1e1e"
        self.fg_light = "#ffffff"
        self.success = "#4CAF50"
        self.error = "#f44336"
        self.warning = "#ff9800"
        self.info = "#4FC3F7"
        
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Title.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 9))

    def setup_ui(self):
        """Setup the user interface."""
        # Configure root background
        self.root.configure(bg=self.bg_dark)
        
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Top Frame: Code Editors
        top_frame = ttk.Frame(main_container)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Left: Solidity Editor
        left_panel = ttk.LabelFrame(top_frame, text="Solidity Contract (SimpleStorage.sol)", style="Title.TLabel")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(left_panel, text="", font=("Arial", 1)).pack()  # Spacer
        self.solidity_text = scrolledtext.ScrolledText(
            left_panel,
            height=20,
            bg="#2d2d2d",
            fg=self.fg_light,
            insertbackground="white",
            font=("Consolas", 10),
            wrap=tk.WORD,
            undo=True
        )
        self.solidity_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right: Test Editor
        right_panel = ttk.LabelFrame(top_frame, text="Truffle Unit Test (test.js)", style="Title.TLabel")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(right_panel, text="", font=("Arial", 1)).pack()  # Spacer
        self.test_text = scrolledtext.ScrolledText(
            right_panel,
            height=20,
            bg="#1e1e3f",
            fg=self.fg_light,
            insertbackground="white",
            font=("Consolas", 10),
            wrap=tk.WORD,
            undo=True
        )
        self.test_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control Panel
        control_frame = ttk.Frame(main_container)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left side buttons
        btn_container = ttk.Frame(control_frame)
        btn_container.pack(side=tk.LEFT)
        
        self.btn_init = ttk.Button(btn_container, text="Initialize Project", 
                                   command=self.init_project_structure)
        self.btn_init.pack(side=tk.LEFT, padx=2)
        
        self.btn_run = ttk.Button(btn_container, text="Run Tests", 
                                  command=self.start_test_thread, state=tk.DISABLED)
        self.btn_run.pack(side=tk.LEFT, padx=2)
        
        self.btn_stop = ttk.Button(btn_container, text="Stop", 
                                   command=self.stop_tests, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=2)
        
        self.btn_clear = ttk.Button(btn_container, text="Clear Console", 
                                    command=self.clear_console)
        self.btn_clear.pack(side=tk.LEFT, padx=2)
        
        # Right side status
        status_container = ttk.Frame(control_frame)
        status_container.pack(side=tk.RIGHT)
        
        self.status_lbl = ttk.Label(status_container, text="Status: Ready", 
                                    style="Status.TLabel", foreground="blue")
        self.status_lbl.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_container, mode='indeterminate', length=100)
        self.progress.pack(side=tk.LEFT, padx=5)
        
        # Bottom Frame: Console Output
        bottom_frame = ttk.LabelFrame(main_container, text="Console Output", style="Title.TLabel")
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(bottom_frame, text="", font=("Arial", 1)).pack()  # Spacer
        self.console_log = scrolledtext.ScrolledText(
            bottom_frame, 
            height=15, 
            bg="black", 
            fg="#00ff00",
            insertbackground="white",
            font=("Consolas", 10),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.console_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def set_default_code(self):
        """Pre-fills the editors with a working example."""
        sol_code = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleStorage {
    uint256 public storedData;

    function set(uint256 x) public {
        storedData = x;
    }

    function get() public view returns (uint256) {
        return storedData;
    }
}
"""
        test_code = """const SimpleStorage = artifacts.require("SimpleStorage");

contract("SimpleStorage", accounts => {
  it("should store the value 89.", async () => {
    const storage = await SimpleStorage.deployed();

    // Set value of 89
    await storage.set(89, { from: accounts[0] });

    // Get stored value
    const storedData = await storage.get.call();

    assert.equal(storedData, 89, "The value 89 was not stored.");
  });
});
"""
        self.solidity_text.insert(tk.END, sol_code)
        self.test_text.insert(tk.END, test_code)

    def log(self, message, level="INFO"):
        """Thread-safe logging to the console window with different levels."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "ERROR":
            color = self.error
            prefix = "[ERROR]"
        elif level == "WARNING":
            color = self.warning
            prefix = "[WARN] "
        elif level == "SUCCESS":
            color = self.success
            prefix = "[OK]   "
        else:
            color = self.info
            prefix = "[INFO] "
        
        formatted_message = f"{timestamp} {prefix} {message}\n"
        
        # Use after() to update UI from main thread
        self.root.after(0, self._update_log, formatted_message, color)

    def _update_log(self, message, color):
        """Update the console log from main thread."""
        self.console_log.config(state=tk.NORMAL)
        
        # Insert at the end
        end_position = self.console_log.index(tk.END)
        if end_position == "1.0":
            insert_position = "1.0"
        else:
            # Remove the trailing newline from END to avoid double newlines
            insert_position = self.console_log.index(tk.END + "-1c")
        
        self.console_log.insert(insert_position, message)
        
        # Apply color tag
        start_idx = insert_position
        end_idx = self.console_log.index(tk.END)
        self.console_log.tag_add(color, start_idx, end_idx)
        self.console_log.tag_config(color, foreground=color)
        
        self.console_log.see(tk.END)
        self.console_log.config(state=tk.DISABLED)

    def init_project_structure(self):
        """Creates the necessary folders and config files for Truffle."""
        try:
            self.log("Initializing project structure...", "INFO")
            
            # Check if project directory already exists
            if os.path.exists(self.project_dir):
                response = messagebox.askyesno(
                    "Project Exists", 
                    f"Project directory '{self.project_dir}' already exists.\nDo you want to overwrite it?"
                )
                if not response:
                    self.log("Project initialization cancelled by user.", "WARNING")
                    return
            
            # Create project directory
            if not os.path.exists(self.project_dir):
                os.makedirs(self.project_dir)
            
            # Create subfolders
            folders = ["contracts", "test", "migrations"]
            for folder in folders:
                folder_path = os.path.join(self.project_dir, folder)
                os.makedirs(folder_path, exist_ok=True)
                self.log(f"Created folder: {folder}", "INFO")

            # 1. Create truffle-config.js
            config_content = """module.exports = {
  networks: {
    development: {
      host: "127.0.0.1",
      port: 9545,
      network_id: "*",
    },
  },
  compilers: {
    solc: {
      version: "0.8.0",
    }
  }
};
"""
            config_path = os.path.join(self.project_dir, "truffle-config.js")
            with open(config_path, "w") as f:
                f.write(config_content)
            self.log("Created: truffle-config.js", "INFO")

            # 2. Create Migration Script
            migration_content = """const SimpleStorage = artifacts.require("SimpleStorage");

module.exports = function(deployer) {
  deployer.deploy(SimpleStorage);
};
"""
            migration_path = os.path.join(self.project_dir, "migrations", "1_deploy_contracts.js")
            with open(migration_path, "w") as f:
                f.write(migration_content)
            self.log("Created: 1_deploy_contracts.js", "INFO")

            self.log("Project structure initialized successfully!", "SUCCESS")
            self.log(f"Working directory: {os.path.abspath(self.project_dir)}", "INFO")
            
            # Enable run button, disable init button
            self.btn_run.config(state=tk.NORMAL)
            self.btn_init.config(state=tk.DISABLED)
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"Error initializing project: {error_msg}", "ERROR")
            messagebox.showerror("Initialization Error", f"Failed to initialize project:\n{error_msg}")

    def start_test_thread(self):
        """Runs the testing logic in a separate thread."""
        if self.test_running:
            messagebox.showwarning("Warning", "Tests are already running!")
            return
        
        self.test_running = True
        thread = threading.Thread(target=self.run_truffle_tests, daemon=True)
        thread.start()

    def run_truffle_tests(self):
        """Execute truffle tests."""
        # Update UI to show test is starting
        self.root.after(0, self._start_progress)
        
        try:
            # 1. Save files first
            self.save_files()
            
            # 2. Execute truffle test
            self.execute_truffle_test()
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"Unexpected error: {error_msg}", "ERROR")
        finally:
            # Always update UI when done
            self.root.after(0, self._stop_progress)
            self.test_running = False

    def save_files(self):
        """Save Solidity contract and test files."""
        try:
            # Get content from text widgets
            sol_content = self.solidity_text.get("1.0", tk.END).rstrip('\n')
            test_content = self.test_text.get("1.0", tk.END).rstrip('\n')

            # Check if project directory exists
            if not os.path.exists(self.project_dir):
                raise Exception(f"Project directory '{self.project_dir}' not found. Please initialize project first.")

            # Save Solidity contract
            sol_path = os.path.join(self.project_dir, "contracts", "SimpleStorage.sol")
            with open(sol_path, "w") as f:
                f.write(sol_content)
            self.log(f"Saved: {sol_path}", "INFO")

            # Save test file
            test_path = os.path.join(self.project_dir, "test", "test_storage.js")
            with open(test_path, "w") as f:
                f.write(test_content)
            self.log(f"Saved: {test_path}", "INFO")
            
            self.log("Files saved successfully", "SUCCESS")
            
        except Exception as e:
            raise Exception(f"Failed to save files: {str(e)}")

    def execute_truffle_test(self):
        """Execute truffle test command."""
        self.log("=" * 60, "INFO")
        self.log("Starting Truffle tests...", "INFO")
        self.log("=" * 60, "INFO")
        
        # Determine command based on OS
        is_windows = os.name == 'nt'
        cmd_name = "truffle.cmd" if is_windows else "truffle"
        
        try:
            # Check if truffle is installed
            if is_windows:
                test_cmd = "where" if is_windows else "which"
            else:
                test_cmd = "which"
                
            truffle_check = subprocess.run(
                [test_cmd, "truffle" if not is_windows else "truffle.cmd"],
                capture_output=True,
                text=True,
                shell=is_windows
            )
            
            if truffle_check.returncode != 0:
                raise FileNotFoundError("Truffle not found in PATH")
            
            # Start truffle test process
            self.process = subprocess.Popen(
                [cmd_name, "test"],
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=False
            )

            # Read output line by line
            while True:
                # Read stdout
                if self.process.stdout:
                    stdout_line = self.process.stdout.readline()
                    if stdout_line:
                        self.process_output(stdout_line.strip())
                
                # Read stderr
                if self.process.stderr:
                    stderr_line = self.process.stderr.readline()
                    if stderr_line:
                        self.process_output(stderr_line.strip(), is_error=True)
                
                # Check if process has finished
                if self.process.poll() is not None:
                    # Read any remaining output
                    remaining_stdout, remaining_stderr = self.process.communicate()
                    
                    if remaining_stdout:
                        for line in remaining_stdout.split('\n'):
                            if line.strip():
                                self.process_output(line.strip())
                    
                    if remaining_stderr:
                        for line in remaining_stderr.split('\n'):
                            if line.strip():
                                self.process_output(line.strip(), is_error=True)
                    
                    break

            # Check result
            if self.process.returncode == 0:
                self.log("All tests passed successfully!", "SUCCESS")
                self.root.after(0, lambda: self.status_lbl.config(text="Status: Success", foreground=self.success))
            else:
                self.log("Tests failed", "ERROR")
                self.root.after(0, lambda: self.status_lbl.config(text="Status: Failed", foreground=self.error))

        except FileNotFoundError:
            self.log("Truffle not found. Please install with: npm install -g truffle", "ERROR")
            self.root.after(0, lambda: messagebox.showerror(
                "Truffle Not Found",
                "Truffle is not installed or not in PATH.\n\n"
                "Please install it:\n"
                "1. Install Node.js from https://nodejs.org\n"
                "2. Run: npm install -g truffle\n"
                "3. Verify installation with: truffle version"
            ))
        except Exception as e:
            self.log(f"Error executing tests: {str(e)}", "ERROR")
        finally:
            self.process = None
            self.root.after(0, self._enable_buttons_after_test)

    def process_output(self, line, is_error=False):
        """Process a line of output from truffle."""
        if not line:
            return
        
        # Determine log level based on content
        if is_error:
            level = "ERROR"
        elif "✓" in line or "passing" in line.lower():
            level = "SUCCESS"
        elif "✗" in line or "failing" in line.lower():
            level = "ERROR"
        elif "warning" in line.lower():
            level = "WARNING"
        else:
            level = "INFO"
        
        self.log(line, level)

    def stop_tests(self):
        """Stop the currently running test process."""
        if self.process and self.process.poll() is None:
            self.log("Stopping tests...", "WARNING")
            self.process.terminate()
            
            # Wait a bit for process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            
            self.log("Tests stopped by user", "WARNING")
            self.root.after(0, lambda: self.status_lbl.config(text="Status: Stopped", foreground=self.warning))
            self.test_running = False
            self.root.after(0, self._enable_buttons_after_test)

    def _start_progress(self):
        """Start progress animation and update UI for test start."""
        self.status_lbl.config(text="Status: Running...", foreground=self.warning)
        self.btn_run.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_init.config(state=tk.DISABLED)
        self.progress.start(10)

    def _stop_progress(self):
        """Stop progress animation."""
        self.progress.stop()

    def _enable_buttons_after_test(self):
        """Enable/disable buttons after test completion."""
        self.btn_run.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self.btn_init.config(state=tk.NORMAL)

    def clear_console(self):
        """Clear the console output."""
        self.console_log.config(state=tk.NORMAL)
        self.console_log.delete(1.0, tk.END)
        self.console_log.config(state=tk.DISABLED)
        self.log("Console cleared", "INFO")

    def on_closing(self):
        """Handle application closing."""
        if self.test_running:
            if messagebox.askyesno("Quit", "Tests are running. Are you sure you want to quit?"):
                self.stop_tests()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = TruffleIDE(root)
    
    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()