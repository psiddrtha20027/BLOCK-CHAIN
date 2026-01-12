import tkinter as tk
from tkinter import messagebox
from web3 import Web3

# ------------------ Blockchain Setup ------------------

GANACHE_URL = "http://127.0.0.1:7545"

try:
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    connected = web3.is_connected()
except:
    connected = False

# Sample wallet (Ganache default account)
SAMPLE_ADDRESS = "0x0000000000000000000000000000000000000000"


# ------------------ Functions ------------------

def check_balance():
    if not connected:
        messagebox.showinfo("Simulation Mode",
                            "Blockchain not connected.\nSimulated Balance: 10 ETH")
        return

    try:
        balance_wei = web3.eth.get_balance(SAMPLE_ADDRESS)
        balance_eth = web3.from_wei(balance_wei, 'ether')
        messagebox.showinfo("Wallet Balance",
                            f"Wallet Address:\n{SAMPLE_ADDRESS}\n\nBalance: {balance_eth} ETH")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def simulate_transaction():
    tx_details = (
        "Transaction Simulation\n\n"
        "From: Your Wallet\n"
        "To: Receiver Wallet\n"
        "Amount: 1 ETH\n\n"
        "Note: This is only a simulation.\n"
        "No real transaction is performed."
    )
    messagebox.showinfo("Transaction", tx_details)


# ------------------ GUI Setup ------------------

root = tk.Tk()
root.title("Blockchain Wallet Simulator")
root.geometry("400x300")
root.resizable(False, False)

title_label = tk.Label(
    root,
    text="Blockchain Wallet (Python + Web3)",
    font=("Arial", 14, "bold")
)
title_label.pack(pady=15)

status_text = "Connected to Blockchain" if connected else "Simulation Mode (Offline)"
status_label = tk.Label(root, text=status_text, fg="green" if connected else "red")
status_label.pack(pady=5)

balance_btn = tk.Button(
    root,
    text="Check Wallet Balance",
    width=25,
    command=check_balance
)
balance_btn.pack(pady=10)

tx_btn = tk.Button(
    root,
    text="Simulate Transaction",
    width=25,
    command=simulate_transaction
)
tx_btn.pack(pady=10)

exit_btn = tk.Button(
    root,
    text="Exit",
    width=25,
    command=root.destroy
)
exit_btn.pack(pady=10)

root.mainloop()