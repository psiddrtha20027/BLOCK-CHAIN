import tkinter as tk
from tkinter import messagebox, filedialog

# ---------------- ERC20 Solidity Template ---------------- #
def generate_erc20(name, symbol, amount):
    contract_name = name.replace(" ", "")
    return f'''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract {contract_name}Token {{

    string public name = "{name}";
    string public symbol = "{symbol}";
    uint8 public decimals = 18;

    uint256 public INITIAL_SUPPLY = {amount};
    uint256 public totalSupply;

    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor() {{
        totalSupply = INITIAL_SUPPLY * (10 ** uint256(decimals));
        balanceOf[msg.sender] = totalSupply;
        emit Transfer(address(0), msg.sender, totalSupply);
    }}

    function transfer(address to, uint256 value) public returns (bool) {{
        require(balanceOf[msg.sender] >= value, "Insufficient balance");
        balanceOf[msg.sender] -= value;
        balanceOf[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }}

    function approve(address spender, uint256 value) public returns (bool) {{
        allowance[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }}

    function transferFrom(address from, address to, uint256 value) public returns (bool) {{
        require(balanceOf[from] >= value, "Insufficient balance");
        require(allowance[from][msg.sender] >= value, "Allowance exceeded");

        balanceOf[from] -= value;
        balanceOf[to] += value;
        allowance[from][msg.sender] -= value;

        emit Transfer(from, to, value);
        return true;
    }}
}}
'''

# ---------------- GUI Logic ---------------- #
def create_contract():
    name = name_entry.get()
    symbol = symbol_entry.get()
    amount = amount_entry.get()

    if not name or not symbol or not amount:
        messagebox.showerror("Error", "All fields are required")
        return

    if not amount.isdigit():
        messagebox.showerror("Error", "Total Amount must be a number")
        return

    contract_code = generate_erc20(name, symbol, amount)

    file_path = filedialog.asksaveasfilename(
        defaultextension=".sol",
        filetypes=[("Solidity Files", "*.sol")]
    )

    if file_path:
        with open(file_path, "w") as f:
            f.write(contract_code)
        messagebox.showinfo("Success", "ERC20 Smart Contract Generated Successfully!")

# ---------------- Tkinter UI ---------------- #
root = tk.Tk()
root.title("ERC20 Token Generator")
root.geometry("400x320")

tk.Label(root, text="ERC20 Token Generator", font=("Arial", 16)).pack(pady=10)

tk.Label(root, text="Token Name").pack()
name_entry = tk.Entry(root)
name_entry.pack()

tk.Label(root, text="Token Symbol").pack()
symbol_entry = tk.Entry(root)
symbol_entry.pack()

tk.Label(root, text="Total Token Amount").pack()
amount_entry = tk.Entry(root)
amount_entry.pack()

tk.Button(
    root,
    text="Generate Smart Contract",
    command=create_contract,
    bg="green",
    fg="white"
).pack(pady=20)

root.mainloop()
