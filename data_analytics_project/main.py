import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from data_entry import get_amount, get_category, get_date, get_description
from rich.console import Console
from rich.table import Table

console = Console()

class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        if not os.path.exists(cls.CSV_FILE):
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = CSV.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)
        console.print("Entry added successfully", style="bold green")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            console.print("No transactions found in the given date range.", style="bold red")
        else:
            console.print(f"Transactions from {start_date.strftime(CSV.FORMAT)} to {end_date.strftime(CSV.FORMAT)}")
            table = Table(title="Transactions Summary")
            table.add_column("Date", justify="center", style="cyan")
            table.add_column("Amount ($)", justify="center", style="magenta")
            table.add_column("Category", justify="center", style="green")
            table.add_column("Description", justify="center", style="yellow")

            for index, row in filtered_df.iterrows():
                table.add_row(
                    row["date"].strftime(CSV.FORMAT),
                    f"{row['amount']:.2f}",
                    row["category"],
                    row["description"]
                )
            console.print(table)

            # Summary Statistics
            total_income = filtered_df[filtered_df["category"] == "Income"]["amount"].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"]["amount"].sum()
            net_savings = total_income - total_expense
            
            console.print("\nSummary:", style="bold blue")
            console.print(f"Total Income: ${total_income:.2f}", style="bold green")
            console.print(f"Total Expense: ${total_expense:.2f}", style="bold red")
            console.print(f"Net Savings: ${net_savings:.2f}", style="bold yellow")

        return filtered_df


def add():
    CSV.initialize_csv()
    date = get_date("Enter the date of the transaction (dd-mm-yyyy) or enter for today's date: ", allow_default=True)
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def plot_dashboard(df):
    # Set Seaborn style
    sns.set_theme(style="whitegrid")
    
    # Prepare data
    df.set_index("date", inplace=True)

    # Resample Income and Expenses
    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )
    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    # Create a figure with subplots, increasing the size
    fig, axs = plt.subplots(2, 2, figsize=(20, 12), gridspec_kw={'height_ratios': [2, 1]})
    plt.subplots_adjust(hspace=0.3, wspace=0.3)  # Adjust spacing between subplots

    # Plotting Income and Expenses
    axs[0, 0].plot(income_df.index, income_df['amount'], label='Income', color='#28a745', marker='o', markersize=6, linestyle='-', linewidth=2)
    axs[0, 0].plot(expense_df.index, expense_df['amount'], label='Expenses', color='#dc3545', marker='x', markersize=6, linestyle='--', linewidth=2)

    # Adding titles and labels for the line plot
    axs[0, 0].set_title('Income and Expenses Over Time', fontsize=22, fontweight='bold', color='#333')
    axs[0, 0].set_xlabel('Date', fontsize=16, fontweight='bold', color='#555')
    axs[0, 0].set_ylabel('Amount ($)', fontsize=16, fontweight='bold', color='#555')
    axs[0, 0].legend(fontsize=14, loc='upper left')
    axs[0, 0].grid(True)

    # Pie chart for income/expense breakdown
    axs[0, 1].pie([income_df['amount'].sum(), expense_df['amount'].sum()], 
                   labels=['Income', 'Expenses'], autopct='%1.1f%%', 
                   startangle=90, colors=['#28a745', '#dc3545'], shadow=True)
    axs[0, 1].set_title('Income vs. Expenses', fontsize=22, fontweight='bold', color='#333')

    # Bar chart for income and expenses in the lower right subplot (1, 1)
    category_summary = df.groupby('category')['amount'].sum().reset_index()
    bars = axs[1, 1].bar(category_summary['category'], category_summary['amount'], color=['#28a745', '#dc3545'])
    
    # Adding data labels on the bar chart
    for bar in bars:
        yval = bar.get_height()
        axs[1, 1].text(bar.get_x() + bar.get_width()/2, yval + 0.5, f"${yval:.2f}", ha='center', va='bottom', fontsize=12)

    axs[1, 1].set_title('Total Amount by Category', fontsize=22, fontweight='bold', color='#333')
    axs[1, 1].set_ylabel('Amount ($)', fontsize=16, fontweight='bold', color='#555')
    axs[1, 1].set_xlabel('Category', fontsize=16, fontweight='bold', color='#555')

    # Customizing tick labels
    axs[1, 1].tick_params(axis='x', rotation=45)

    # Hide the empty subplot (1, 0)
    axs[1, 0].axis('off')

    # Global aesthetics
    plt.suptitle('Financial Dashboard', fontsize=26, fontweight='bold', color='#333')
    plt.show()

    # Exporting the dashboard image
    save_dashboard = input("Do you want to save the dashboard as an image? (y/n): ").lower()
    if save_dashboard == 'y':
        file_name = input("Enter the file name (without extension): ")
        plt.savefig(f"{file_name}.png", dpi=300)
        console.print(f"Dashboard saved as {file_name}.png", style="bold blue")


def main():
    while True:
        console.print("\n1. Add a new transaction", style="bold")
        console.print("2. View transactions and summary within a date range", style="bold")
        console.print("3. Plot transactions", style="bold")
        console.print("4. Exit", style="bold")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            add()
        elif choice == "2":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
        elif choice == "3":
            start_date = get_date("Enter the start date (dd-mm-yyyy): ")
            end_date = get_date("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if not df.empty:
                plot_dashboard(df)
        elif choice == "4":
            console.print("Exiting the program. Goodbye!", style="bold red")
            break
        else:
            console.print("Invalid choice. Please select a valid option.", style="bold red")


if __name__ == "__main__":
    main()
