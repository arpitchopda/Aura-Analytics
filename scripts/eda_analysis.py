import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda():
    cleaned_csv_path = "data/cleaned_customer_shopping.csv"
    plots_dir = "web/static/plots"
    
    print("Starting Exploratory Data Analysis (EDA)...")
    
    if not os.path.exists(cleaned_csv_path):
        raise FileNotFoundError(f"Cleaned CSV not found at {cleaned_csv_path}. Please run clean_and_load.py first.")
        
    # Ensure plots directory exists
    os.makedirs(plots_dir, exist_ok=True)
    
    # Load dataset
    df = pd.read_csv(cleaned_csv_path)
    
    # Configure matplotlib style
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.facecolor": "#0d0e12",  # Sleek dark mode background
        "axes.facecolor": "#171821",    # Dark panel color
        "text.color": "#f1f1f5",
        "axes.labelcolor": "#a5a6b7",
        "xtick.color": "#a5a6b7",
        "ytick.color": "#a5a6b7",
        "grid.color": "#2c2e3e",
        "font.family": "sans-serif"
    })
    
    # Palette colors (glassmorphic / modern tech style)
    accent_colors = ["#a15bf2", "#47a0ff", "#29cca3", "#ff6b8b", "#ffc107", "#795548"]
    
    # 1. Total Revenue by Product Category
    print("Generating Plot 1: Revenue by Category...")
    plt.figure(figsize=(10, 6))
    cat_sales = df.groupby("Category")["TotalRevenue"].sum().sort_values(ascending=False).reset_index()
    
    ax = sns.barplot(
        x="TotalRevenue", 
        y="Category", 
        data=cat_sales, 
        palette=accent_colors
    )
    plt.title("Total Sales Revenue by Product Category", fontsize=15, pad=20, color="#f1f1f5", weight="bold")
    plt.xlabel("Total Revenue ($)", fontsize=12, labelpad=10)
    plt.ylabel("Category", fontsize=12, labelpad=10)
    
    # Format x-axis with thousands separator
    import matplotlib.ticker as ticker
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}"))
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "category_sales.png"), dpi=200, facecolor="#0d0e12")
    plt.close()
    
    # 2. Age Distribution of Customers
    print("Generating Plot 2: Age Distribution...")
    plt.figure(figsize=(10, 6))
    # Fetch unique customer ages
    unique_custs = df.drop_duplicates(subset=["CustomerID"])
    
    sns.histplot(
        data=unique_custs, 
        x="Age", 
        kde=True, 
        color="#47a0ff", 
        bins=20,
        alpha=0.6,
        line_kws={"color": "#a15bf2", "linewidth": 2.5}
    )
    plt.title("Customer Age Demographic Distribution", fontsize=15, pad=20, color="#f1f1f5", weight="bold")
    plt.xlabel("Age", fontsize=12, labelpad=10)
    plt.ylabel("Number of Customers", fontsize=12, labelpad=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "age_distribution.png"), dpi=200, facecolor="#0d0e12")
    plt.close()
    
    # 3. Monthly Sales Seasonality Trend
    print("Generating Plot 3: Monthly Sales Trend...")
    plt.figure(figsize=(12, 6))
    # Parse Date
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["MonthYear"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    
    monthly_sales = df.groupby("MonthYear")["TotalRevenue"].sum().reset_index()
    
    ax = sns.lineplot(
        x="MonthYear", 
        y="TotalRevenue", 
        data=monthly_sales, 
        color="#29cca3", 
        marker="o", 
        linewidth=3, 
        markersize=8,
        markerfacecolor="#a15bf2",
        markeredgecolor="#f1f1f5"
    )
    plt.title("Monthly Sales Revenue Trend (2024 - 2025)", fontsize=15, pad=20, color="#f1f1f5", weight="bold")
    plt.xlabel("Month", fontsize=12, labelpad=10)
    plt.ylabel("Revenue ($)", fontsize=12, labelpad=10)
    plt.xticks(rotation=45)
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"${x:,.0f}"))
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "monthly_revenue_trend.png"), dpi=200, facecolor="#0d0e12")
    plt.close()
    
    # 4. Review Ratings by Category (Box Plot)
    print("Generating Plot 4: Ratings by Category...")
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        x="ReviewRating", 
        y="Category", 
        data=df, 
        palette=accent_colors,
        flierprops={"markerfacecolor": "#ff6b8b", "markeredgecolor": "none", "markersize": 4}
    )
    plt.title("Review Rating Distribution by Product Category", fontsize=15, pad=20, color="#f1f1f5", weight="bold")
    plt.xlabel("Review Rating (1.0 - 5.0)", fontsize=12, labelpad=10)
    plt.ylabel("Category", fontsize=12, labelpad=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "ratings_vs_category.png"), dpi=200, facecolor="#0d0e12")
    plt.close()

    # 5. Payment Method Share (Donut Chart)
    print("Generating Plot 5: Payment Method Share...")
    plt.figure(figsize=(8, 8))
    payment_share = df["PaymentMethod"].value_counts()
    
    plt.pie(
        payment_share, 
        labels=payment_share.index, 
        autopct="%1.1f%%", 
        startangle=140, 
        colors=["#a15bf2", "#47a0ff", "#29cca3", "#ff6b8b"],
        textprops={"color": "#f1f1f5", "fontsize": 11, "weight": "bold"},
        wedgeprops={"width": 0.4, "edgecolor": "#171821", "linewidth": 2} # Donut hole
    )
    plt.title("Transaction Volume by Payment Method", fontsize=15, pad=20, color="#f1f1f5", weight="bold")
    
    plt.tight_layout()
    plt.savefig(os.path.join(plots_dir, "payment_method_distribution.png"), dpi=200, facecolor="#0d0e12")
    plt.close()
    
    print("Exploratory Data Analysis completed! Visualizations saved to web/static/plots/")

if __name__ == "__main__":
    run_eda()
