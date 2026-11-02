
from pathlib import Path
import html

import pandas as pd
import streamlit as st
import plotly.express as px


# ==========================================================
# RETAILPULSE - RETAIL ANALYTICS DASHBOARD
# Run: streamlit run app.py
# Keep style.css and the data folder beside app.py
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CSS_PATH = PROJECT_ROOT / "style.css"

st.set_page_config(
    page_title="RetailPulse | Analytics",
    page_icon="\U0001F4CA",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------- CSS LOADER --------------------

if CSS_PATH.exists():
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True,
        )
    except OSError:
        st.warning("CSS file could not be loaded.")
else:
    st.info("Create style.css beside app.py to apply the custom theme.")


# -------------------- DATA FILES --------------------

FILES = {
    "monthly_sales": "monthly_sales_summary.csv",
    "products": "top_products_summary.csv",
    "countries": "top_countries_summary.csv",
    "rfm": "customer_rfm_segments.csv",
    "churn": "customer_churn_predictions.csv",
    "forecast": "sales_forecast.csv",
    "forecast_test": "forecast_test_results.csv",
    "inventory": "inventory_recommendations.csv",
}


# -------------------- COLUMN ALIASES --------------------

ALIASES = {
    "date": [
        "YearMonth", "InvoiceDate", "Date", "Month",
        "Period", "ds", "date", "month"
    ],
    "sales": [
        "TotalSales", "Total Sales", "Revenue", "Sales",
        "Monetary", "PredictedSales", "Forecast",
        "Predicted", "yhat"
    ],
    "quantity": [
        "Quantity", "UnitsSold", "Units Sold",
        "TotalQuantity", "Units_Sold"
    ],
    "product": [
        "Description", "Product Name", "ProductName",
        "product_name", "Product_Name", "Product",
        "ItemName", "Item Name", "StockCode",
        "Stock Code", "product", "name"
    ],
    "country": ["Country", "Region", "country", "region"],
    "segment": [
        "Customer_Segment", "Customer Segment",
        "Segment", "CustomerSegment", "RFM_Segment"
    ],
    "customer": [
        "Customer ID", "CustomerID", "Customer_ID",
        "customer_id", "Customer"
    ],
    "probability": [
        "Churn_Probability", "Churn Probability",
        "ChurnProbability", "Probability",
        "churn_probability", "Churn_Risk"
    ],
    "status": [
        "Churn_Status", "Churn Status", "Status",
        "Prediction", "Churn", "Customer_Status"
    ],
    "inventory": [
        "Inventory_Level", "Inventory Level",
        "Current_Stock", "Stock", "Inventory"
    ],
    "recommended": [
        "Recommended_Order", "Recommended Order",
        "Order_Quantity", "Suggested_Order",
        "Units_Ordered", "Units Ordered"
    ],
}


# -------------------- HELPER FUNCTIONS --------------------

@st.cache_data(show_spinner=False)
def load_csv(filename):
    """Load a CSV safely. Missing or unreadable files return empty data."""
    path = DATA_DIR / filename

    if not path.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(path, low_memory=False)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        st.warning(f"Could not load {filename}: {exc}")
        return pd.DataFrame()


def find_col(df, kind):
    """Find a column using flexible aliases."""
    if df.empty:
        return None

    candidates = ALIASES.get(kind, [])
    normalized = {
        str(column).strip().lower().replace("_", " "): column
        for column in df.columns
    }

    # First try exact matches.
    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ")
        if key in normalized:
            return normalized[key]

    # Then try partial matches.
    for candidate in candidates:
        key = candidate.strip().lower().replace("_", " ")
        for normalized_name, original_name in normalized.items():
            if key and (
                key in normalized_name
                or normalized_name in key
            ):
                return original_name

    return None


def find_numeric_col(df, preferred=None):
    """Find a numeric column without assuming a fixed schema."""
    if df.empty:
        return None

    if preferred:
        for candidate in preferred:
            for column in df.columns:
                if str(column).strip().lower().replace("_", " ") == (
                    candidate.lower().replace("_", " ")
                ):
                    values = pd.to_numeric(
                        df[column], errors="coerce"
                    )
                    if values.notna().any():
                        return column

    for column in df.columns:
        values = pd.to_numeric(df[column], errors="coerce")
        if values.notna().any():
            return column

    return None


def to_numeric(series):
    return pd.to_numeric(series, errors="coerce")


def format_money(value):
    try:
        return f"GBP {float(value):,.2f}"
    except (ValueError, TypeError):
        return "-"


def format_number(value):
    try:
        return f"{float(value):,.0f}"
    except (ValueError, TypeError):
        return "-"


def section(title, subtitle=None):
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)


def metric_card(label, value):
    st.metric(label=label, value=value)




def page_title(title, subtitle):
    st.markdown(
        f'<div class="hero-title">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="hero-subtitle">{html.escape(subtitle)}</div>',
        unsafe_allow_html=True,
    )


def show_table(df, title=None, max_rows=500):
    """Display readable tables without hiding product names."""
    if title:
        section(title)

    if df is None or df.empty:
        st.info("No records available for this section.")
        return

    view = df.head(max_rows).copy()

    # Make headings easier to read.
    view.columns = [
        str(column).replace("_", " ").strip()
        for column in view.columns
    ]

    # Display every column, including product descriptions.
    st.dataframe(
        view,
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    if len(df) > max_rows:
        st.caption(
            f"Showing {max_rows:,} of {len(df):,} records."
        )


def download_csv(df, filename):
    if df is not None and not df.empty:
        st.download_button(
            label=" Download CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=filename,
            mime="text/csv",
        )


def styled_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            color="#f5f0fa",
            family="Arial, sans-serif",
        ),
        margin=dict(l=15, r=15, t=55, b=15),
        title_font_size=18,
    )
    fig.update_xaxes(showgrid=False, automargin=True)
    fig.update_yaxes(
        gridcolor="rgba(255,255,255,0.10)",
        automargin=True,
    )
    return fig



def show_chart(fig):
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": True},
    )




def get_chart_data(df, kind="sales"):
    if df.empty:
        return None, None, None

    x_col = find_col(df, "date")
    y_col = find_col(df, kind)

    if y_col is None:
        y_col = find_numeric_col(df)

    if x_col is None:
        non_numeric = [
            col for col in df.columns
            if not pd.api.types.is_numeric_dtype(df[col])
        ]
        if non_numeric:
            x_col = non_numeric[0]

    if x_col is None or y_col is None:
        return None, x_col, y_col

    view = df[[x_col, y_col]].copy()
    view[y_col] = to_numeric(view[y_col])
    view = view.dropna(subset=[y_col])

    return view, x_col, y_col


def show_product_chart(df, title="Top Products"):
    if df.empty:
        st.info("Product data is unavailable.")
        return

    product_col = find_col(df, "product")
    value_col = (
        find_col(df, "sales")
        or find_col(df, "quantity")
        or find_numeric_col(df)
    )

    if product_col is None:
        st.warning(
            "No product description/name column was found. "
            "Check whether the CSV contains Description or Product Name."
        )
        return

    if value_col is None:
        st.warning("No numeric sales/value column was found.")
        return

    view = df[[product_col, value_col]].copy()
    view[value_col] = to_numeric(view[value_col])
    view = view.dropna(subset=[value_col])
    view = view.sort_values(value_col, ascending=False).head(15)

    if view.empty:
        st.info("No product records are available to plot.")
        return

    fig = px.bar(
        view.sort_values(value_col),
        x=value_col,
        y=product_col,
        orientation="h",
        title=title,
        labels={
            product_col: "Product",
            value_col: "Sales / Value",
        },
    )
    show_chart(fig)


# -------------------- LOAD ALL DATA --------------------

monthly = load_csv(FILES["monthly_sales"])
products = load_csv(FILES["products"])
countries = load_csv(FILES["countries"])
rfm = load_csv(FILES["rfm"])
churn = load_csv(FILES["churn"])
forecast = load_csv(FILES["forecast"])
forecast_test = load_csv(FILES["forecast_test"])
inventory = load_csv(FILES["inventory"])


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown(
        '<div class="brand-mark"> RetailPulse</div>',
        unsafe_allow_html=True,
    )
    st.caption("Retail Intelligence Dashboard")

    page = st.radio(
        "NAVIGATION",
        [
            " Home",
            " Executive Dashboard",
            " Sales Analytics",
            " Customer Analytics",
            " Customer Segmentation",
            " Customer Churn",
            " Inventory",
            " Country Analysis",
            " Product Analytics",
            " Demand Forecast",
            " Business Insights",
            " CSV Data Explorer"
        ],
    )

    st.markdown("---")
    st.caption("RetailPulse  Analytics Suite")


# ==========================================================
# PAGE 1 - HOME | RETAILPULSE
# ==========================================================

if page == " Home":

    # Load the detailed sales dataset for Home KPIs
    sales_home = load_csv("featured_sales.csv")

    # ---------- EXPLORE WORKSPACE ----------
    st.markdown(
        '<div class="home-eyebrow">RETAIL INTELLIGENCE PLATFORM</div>'
        '<div class="home-heading">Explore <span>Workspace</span></div>'
        '<div class="home-subtitle">'
        'Your retail business, understood through data.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Revenue
    sales_col = find_col(sales_home, "sales")
    if sales_col and not sales_home.empty:
        total_revenue = to_numeric(
            sales_home[sales_col]
        ).fillna(0).sum()
    else:
        monthly_sales_col = find_col(monthly, "sales")
        total_revenue = (
            to_numeric(monthly[monthly_sales_col]).fillna(0).sum()
            if monthly_sales_col and not monthly.empty
            else 0
        )

    # Orders
    invoice_col = next(
        (c for c in sales_home.columns
         if str(c).strip().lower() in ["invoice", "invoiceno", "invoice no"]),
        None,
    )
    total_orders = (
        sales_home[invoice_col].nunique()
        if invoice_col and not sales_home.empty
        else 0
    )

    # Customers
    customer_col = find_col(sales_home, "customer")
    total_customers = (
        sales_home[customer_col].nunique()
        if customer_col and not sales_home.empty
        else (
            rfm[find_col(rfm, "customer")].nunique()
            if not rfm.empty and find_col(rfm, "customer")
            else len(rfm)
        )
    )

    # Products
    product_col = find_col(sales_home, "product")
    total_products = (
        sales_home[product_col].nunique()
        if product_col and not sales_home.empty
        else len(products)
    )

    # Countries
    country_col = find_col(sales_home, "country")
    total_countries = (
        sales_home[country_col].nunique()
        if country_col and not sales_home.empty
        else len(countries)
    )

    processed_datasets = len(list(DATA_DIR.glob("*.csv")))

    kpis = [
        ("", "Total Revenue", format_money(total_revenue), "Recorded sales"),
        ("", "Total Orders", format_number(total_orders), "Unique invoices"),
        ("", "Total Customers", format_number(total_customers), "Unique customers"),
        ("", "Products", format_number(total_products), "Product records"),
        ("", "Countries Served", format_number(total_countries), "Countries / regions"),
        ("", "ML Models", "3", "Forecast  Segmentation  Churn"),
        ("", "Dashboard Pages", "12", "Including Home"),
        ("", "Processed Datasets", format_number(processed_datasets), "CSV files available"),
    ]

    for row_start in range(0, len(kpis), 4):
        metric_cols = st.columns(4)

        for col, item in zip(metric_cols, kpis[row_start:row_start + 4]):
            icon, label, value, note = item

            with col:
                st.markdown(
                    f"""
                    <div class="rp-kpi">
                        <div class="rp-kpi-top">
                            <span class="rp-kpi-icon">{icon}</span>
                            <span class="rp-kpi-dot"></span>
                        </div>
                        <div class="rp-kpi-label">{html.escape(label)}</div>
                        <div class="rp-kpi-value">{html.escape(str(value))}</div>
                        <div class="rp-kpi-note">{html.escape(note)}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="rp-section-gap"></div>', unsafe_allow_html=True)

    # ---------- QUICK NAVIGATION ----------
    st.markdown(
        '<div class="rp-section-heading"> Quick Navigation</div>'
        '<div class="rp-section-subtitle">'
        'Jump straight into the insights you need.'
        '</div>',
        unsafe_allow_html=True,
    )

    quick_pages = [
        ("", " Executive Dashboard", "Business KPIs and performance"),
        ("", " Sales Analytics", "Revenue and sales trends"),
        ("", " Customer Analytics", "Customer behaviour and value"),
        ("", " Customer Segmentation", "Explore RFM customer groups"),
        ("", " Customer Churn", "Find customers at risk"),
        ("", " Inventory", "Stock and reorder insights"),
        ("", " Country Analysis", "Compare country performance"),
        ("", " Product Analytics", "Discover top-performing products"),
        ("", " Demand Forecast", "Explore predicted sales"),
        ("", " Business Insights", "Understand business opportunities"),
    ]

    for row_start in range(0, len(quick_pages), 3):
        nav_cols = st.columns(3)

        for col, item in zip(
            nav_cols, quick_pages[row_start:row_start + 3]
        ):
            icon, name, description = item

            with col:
                with st.container(border=True):
                    st.markdown(
                        f"""
                        <div class="rp-nav-icon">{icon}</div>
                        <div class="rp-nav-title">{html.escape(name)}</div>
                        <div class="rp-nav-description">
                            {html.escape(description)}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )


    # ---------- ABOUT THIS PROJECT ----------
    st.markdown('<div class="rp-section-gap"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="rp-about">
            <div class="rp-about-label">ABOUT THE PROJECT</div>
            <div class="rp-about-title">What is <span>RetailPulse?</span></div>
            <div class="rp-about-text">
                RetailPulse is a retail analytics and business intelligence
                project that transforms sales and customer data into useful
                business insights. It brings sales performance, customer
                segmentation, churn risk, demand forecasting and inventory
                analysis together in one interactive workspace.
            </div>
            <div class="rp-about-pills">
                <span>Sales Analytics</span>
                <span>Customer Intelligence</span>
                <span>Machine Learning</span>
                <span>Inventory Insights</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- TECHNOLOGY STACK ----------
    st.markdown(
        '<div class="rp-section-heading"> Technology Stack</div>'
        '<div class="rp-section-subtitle">'
        'Tools used to build the RetailPulse analytics experience.'
        '</div>',
        unsafe_allow_html=True,
    )

    tech_stack = [
        ("PY", "Python", "Data processing and analytics"),
        ("PD", "Pandas", "Data cleaning and transformation"),
        ("ST", "Streamlit", "Interactive dashboard"),
        ("PX", "Plotly", "Interactive charts"),
        ("ML", "Scikit-learn", "Machine learning workflows"),
        ("CSV", "CSV / Excel", "Dataset storage and exchange"),
    ]

    tech_cols = st.columns(3)

    for i, (symbol, name, description) in enumerate(tech_stack):
        with tech_cols[i % 3]:
            st.markdown(
                f"""
                <div class="rp-tech">
                    <div class="rp-tech-symbol">{symbol}</div>
                    <div class="rp-tech-name">{html.escape(name)}</div>
                    <div class="rp-tech-description">
                        {html.escape(description)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )



# ==========================================================
# PAGE 2 - EXECUTIVE DASHBOARD
# ==========================================================

if page == " Executive Dashboard":
    page_title(
        "Executive Dashboard",
        "Retail performance, customer behaviour and business health at a glance.",
    )

    # ---------------- KPI DATA ----------------
    sales_col = find_col(monthly, "sales") or find_numeric_col(monthly)
    customer_col = find_col(rfm, "customer")
    segment_col = find_col(rfm, "segment")

    total_sales = (
        to_numeric(monthly[sales_col]).sum()
        if sales_col and not monthly.empty
        else 0
    )

    customer_count = (
        rfm[customer_col].nunique()
        if customer_col and not rfm.empty
        else 0
    )

    # ---------------- KPI CARDS ----------------
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card("Total Revenue", format_money(total_sales))

    with col2:
        metric_card("Unique Customers", format_number(customer_count))

    with col3:
        metric_card("Churn Records", format_number(len(churn)))

    with col4:
        metric_card("Inventory Items", format_number(len(inventory)))

    st.markdown("---")

    # ---------------- MAIN CHARTS ----------------
    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Revenue Performance")

        chart_df, x_col, y_col = get_chart_data(monthly)

        if chart_df is not None and not chart_df.empty:
            fig = px.line(
                chart_df,
                x=x_col,
                y=y_col,
                markers=True,
                title="Monthly Sales Trend",
                template="plotly_dark",
                color_discrete_sequence=["#2DD4BF"],
            )
            fig.update_layout(
                paper_bgcolor="#111C2F",
                plot_bgcolor="#111C2F",
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis_title="Period",
                yaxis_title="Sales",
                hovermode="x unified",
            )
            show_chart(fig)
        else:
            st.info("Monthly sales chart is unavailable.")

    with right:
        st.subheader("Customer Overview")

        if not rfm.empty and segment_col:
            counts = (
                rfm[segment_col]
                .fillna("Unknown")
                .astype(str)
                .str.strip()
                .value_counts()
                .rename_axis("Segment")
                .reset_index(name="Customers")
            )

            fig = px.pie(
                counts,
                names="Segment",
                values="Customers",
                hole=0.58,
                title="Customer Segment Distribution",
                template="plotly_dark",
                color_discrete_sequence=[
                    "#2DD4BF",
                    "#60A5FA",
                    "#A78BFA",
                    "#FBBF24",
                    "#FB7185",
                ],
            )
            fig.update_layout(
                paper_bgcolor="#111C2F",
                plot_bgcolor="#111C2F",
                margin=dict(l=15, r=15, t=60, b=15),
                legend_title_text="Segment",
            )
            show_chart(fig)
        else:
            st.info("Customer segment data is unavailable.")

    st.markdown("---")

    # ---------------- PRODUCT & COUNTRY CHARTS ----------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Product Performance")
        show_product_chart(products, "Top Products")

    with col2:
        st.subheader("Geographic Performance")

        country_col = find_col(countries, "country")
        country_value = (
            find_col(countries, "sales")
            or find_numeric_col(countries)
        )

        if country_col and country_value and not countries.empty:
            view = countries[[country_col, country_value]].copy()
            view[country_value] = to_numeric(view[country_value])
            view = view.dropna().sort_values(
                country_value, ascending=False
            ).head(10)

            view = view.sort_values(country_value, ascending=True)

            fig = px.bar(
                view,
                x=country_value,
                y=country_col,
                orientation="h",
                title="Top 10 Countries by Sales",
                template="plotly_dark",
                color_discrete_sequence=["#2DD4BF"],
            )
            fig.update_layout(
                paper_bgcolor="#111C2F",
                plot_bgcolor="#111C2F",
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis_title="Sales",
                yaxis_title="Country",
            )
            show_chart(fig)
        else:
            st.info("Country summary is unavailable.")

# ==========================================================
# PAGE 3 - SALES ANALYTICS
# ==========================================================


elif page == " Sales Analytics":
    page_title(
        "Sales Analytics",
        "Explore revenue trends, products, countries and transaction performance.",
    )

    sales_df = load_csv("featured_sales.csv")
    monthly_df = load_csv("monthly_sales_summary.csv")
    products_df = load_csv("top_products_summary.csv")
    countries_df = load_csv("top_countries_summary.csv")

    # Normalize missing data
    if sales_df is None:
        sales_df = pd.DataFrame()
    if monthly_df is None:
        monthly_df = pd.DataFrame()
    if products_df is None:
        products_df = pd.DataFrame()
    if countries_df is None:
        countries_df = pd.DataFrame()

    sales_df = sales_df.copy()

    # Identify columns
    date_col = next(
        (c for c in ["InvoiceDate", "Date", "Invoice_Date"]
         if c in sales_df.columns),
        None,
    )
    revenue_col = next(
        (c for c in ["TotalSales", "Revenue", "Sales", "Amount"]
         if c in sales_df.columns),
        None,
    )
    quantity_col = next(
        (c for c in ["Quantity", "Units Sold", "UnitsSold"]
         if c in sales_df.columns),
        None,
    )
    invoice_col = next(
        (c for c in ["Invoice", "InvoiceNo", "Invoice No"]
         if c in sales_df.columns),
        None,
    )
    customer_col = next(
        (c for c in ["Customer ID", "CustomerID", "Customer Id"]
         if c in sales_df.columns),
        None,
    )
    country_col = next(
        (c for c in ["Country", "country"]
         if c in sales_df.columns),
        None,
    )
    product_col = next(
        (c for c in ["Description", "Product", "StockCode", "Product ID"]
         if c in sales_df.columns),
        None,
    )

    # Prepare numeric columns
    if revenue_col:
        sales_df[revenue_col] = pd.to_numeric(
            sales_df[revenue_col], errors="coerce"
        )

    if quantity_col:
        sales_df[quantity_col] = pd.to_numeric(
            sales_df[quantity_col], errors="coerce"
        )

    if date_col:
        sales_df[date_col] = pd.to_datetime(
            sales_df[date_col], errors="coerce"
        )

    # ---------------- FILTERS ----------------
    st.subheader("Filters")

    filtered = sales_df.copy()

    if not filtered.empty:
        f1, f2 = st.columns(2)

        with f1:
            if date_col:
                valid_dates = filtered[date_col].dropna()

                if not valid_dates.empty:
                    min_date = valid_dates.min().date()
                    max_date = valid_dates.max().date()

                    date_range = st.date_input(
                        "Select date range",
                        value=(min_date, max_date),
                        min_value=min_date,
                        max_value=max_date,
                        key="sales_date_range",
                    )

                    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                        start_date, end_date = date_range
                        filtered = filtered[
                            filtered[date_col].dt.date.between(
                                start_date, end_date
                            )
                        ]

        with f2:
            if country_col:
                country_options = sorted(
                    filtered[country_col].dropna().astype(str).unique()
                )
                selected_countries = st.multiselect(
                    "Filter by country",
                    country_options,
                    default=country_options,
                    key="sales_country_filter",
                )
                filtered = filtered[
                    filtered[country_col].astype(str).isin(selected_countries)
                ]

    # ---------------- KPI METRICS ----------------
    st.subheader("Sales Performance")

    revenue = (
        filtered[revenue_col].fillna(0).sum()
        if revenue_col else 0
    )
    units = (
        filtered[quantity_col].fillna(0).sum()
        if quantity_col else 0
    )
    invoices = (
        filtered[invoice_col].nunique()
        if invoice_col else 0
    )
    customers = (
        filtered[customer_col].nunique()
        if customer_col else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Total Revenue", format_money(revenue))
    with c2:
        metric_card("Units Sold", format_number(units))
    with c3:
        metric_card("Invoices", format_number(invoices))
    with c4:
        metric_card("Unique Customers", format_number(customers))

    st.caption(f"Showing {len(filtered):,} transaction rows after filters.")

    if not filtered.empty and revenue_col:
        # ---------------- REVENUE TREND ----------------
        st.divider()
        st.subheader("Monthly Revenue Trend")

        if date_col:
            trend = filtered.dropna(subset=[date_col]).copy()

            if not trend.empty:
                trend["Month"] = trend[date_col].dt.to_period("M").astype(str)
                trend = (
                    trend.groupby("Month", as_index=False)[revenue_col]
                    .sum()
                    .sort_values("Month")
                )

                fig = px.line(
                    trend,
                    x="Month",
                    y=revenue_col,
                    markers=True,
                    title="Revenue Over Time",
                    template="plotly_dark",
                    color_discrete_sequence=["#2DD4BF"],
                )
                fig.update_layout(
                    paper_bgcolor="#111C2F",
                    plot_bgcolor="#111C2F",
                    xaxis_title="Month",
                    yaxis_title="Revenue",
                    hovermode="x unified",
                )
                show_chart(fig)
            else:
                st.info("No valid dates available for the revenue trend.")
        else:
            st.info("A date column is required to show the revenue trend.")

        # ---------------- PRODUCT AND COUNTRY ----------------
        st.divider()
        left, right = st.columns(2)

        with left:
            st.subheader("Top Products")

            if product_col:
                product_view = filtered.dropna(subset=[product_col]).copy()
                product_view[product_col] = product_view[product_col].astype(str)

                product_sales = (
                    product_view.groupby(product_col, as_index=False)[revenue_col]
                    .sum()
                    .sort_values(revenue_col, ascending=False)
                    .head(10)
                    .sort_values(revenue_col, ascending=True)
                )

                if not product_sales.empty:
                    fig = px.bar(
                        product_sales,
                        x=revenue_col,
                        y=product_col,
                        orientation="h",
                        title="Top 10 Products by Revenue",
                        template="plotly_dark",
                        color_discrete_sequence=["#60A5FA"],
                    )
                    fig.update_layout(
                        paper_bgcolor="#111C2F",
                        plot_bgcolor="#111C2F",
                        xaxis_title="Revenue",
                        yaxis_title="Product",
                    )
                    show_chart(fig)
                else:
                    st.info("No product data available.")
            else:
                st.info("No product name or product ID column found.")

        with right:
            st.subheader("Country Performance")

            if country_col:
                country_sales = (
                    filtered.dropna(subset=[country_col])
                    .groupby(country_col, as_index=False)[revenue_col]
                    .sum()
                    .sort_values(revenue_col, ascending=False)
                    .head(10)
                    .sort_values(revenue_col, ascending=True)
                )

                if not country_sales.empty:
                    fig = px.bar(
                        country_sales,
                        x=revenue_col,
                        y=country_col,
                        orientation="h",
                        title="Top 10 Countries by Revenue",
                        template="plotly_dark",
                        color_discrete_sequence=["#A78BFA"],
                    )
                    fig.update_layout(
                        paper_bgcolor="#111C2F",
                        plot_bgcolor="#111C2F",
                        xaxis_title="Revenue",
                        yaxis_title="Country",
                    )
                    show_chart(fig)
                else:
                    st.info("No country data available.")
            else:
                st.info("Country column not found in sales data.")

        # ---------------- DOWNLOAD ----------------
        st.divider()
        st.subheader("Export Filtered Sales Data")

        csv_data = filtered.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download filtered sales CSV",
            data=csv_data,
            file_name="retailpulse_filtered_sales.csv",
            mime="text/csv",
            key="download_filtered_sales",
        )

    elif sales_df.empty:
        st.warning(
            "Sales transaction data is unavailable. "
            "Check that data/featured_sales.csv exists."
        )
    else:
        st.warning(
            "The revenue column was not detected. "
            f"Available columns: {sales_df.columns.tolist()}"
        )


    # -------------------------------
    # 3. TOP 10 PRODUCTS
    # -------------------------------
    st.subheader(" Top 10 Products by Revenue")

    if products_df is not None and not products_df.empty:
        products_df = products_df.copy()

        if {"Description", "TotalSales"}.issubset(products_df.columns):
            products_df["TotalSales"] = pd.to_numeric(
                products_df["TotalSales"], errors="coerce"
            )
            products_df = products_df.dropna(
                subset=["Description", "TotalSales"]
            )

            top_products = (
                products_df.sort_values("TotalSales", ascending=False)
                .head(10)
                .sort_values("TotalSales", ascending=True)
            )

            if not top_products.empty:
                fig = px.bar(
                    top_products,
                    x="TotalSales",
                    y="Description",
                    orientation="h",
                    title="Top 10 Products",
                    labels={
                        "TotalSales": "Revenue",
                        "Description": "Product",
                    },
                    text="TotalSales",
                )
                fig.update_traces(
                    marker_color="#a887ce",
                    texttemplate="%{x:,.0f}",
                    textposition="outside",
                    cliponaxis=False,
                )
                fig.update_layout(
                    template="plotly_dark",
                    yaxis_title="",
                    xaxis_title="Revenue",
                )
                show_chart(fig)
            else:
                st.info("No valid product sales records found.")
        else:
            st.warning(
                "Product CSV needs Description and TotalSales columns."
            )
    else:
        st.info("Top products summary is unavailable.")

    st.divider()

    # -------------------------------
    # 4. COUNTRY-WISE SALES
    # -------------------------------
    st.subheader(" Country-wise Sales")

    if countries_df is not None and not countries_df.empty:
        countries_df = countries_df.copy()

        if {"Country", "TotalSales"}.issubset(countries_df.columns):
            countries_df["TotalSales"] = pd.to_numeric(
                countries_df["TotalSales"], errors="coerce"
            )
            countries_df = countries_df.dropna(
                subset=["Country", "TotalSales"]
            )

            top_countries = countries_df.nlargest(10, "TotalSales")

            if not top_countries.empty:
                fig = px.bar(
                    top_countries,
                    x="Country",
                    y="TotalSales",
                    title="Top 10 Countries by Revenue",
                    labels={
                        "Country": "Country",
                        "TotalSales": "Revenue",
                    },
                )
                fig.update_traces(marker_color="#9c526d")
                fig.update_layout(
                    template="plotly_dark",
                    xaxis_tickangle=-35,
                    yaxis_title="Revenue",
                )
                show_chart(fig)
            else:
                st.info("No valid country sales records found.")
        else:
            st.warning(
                "Country CSV needs Country and TotalSales columns."
            )
    else:
        st.info("Country sales summary is unavailable.")

    # -------------------------------
    # 5. DATA TABLES AND DOWNLOADS
    # -------------------------------

elif page == " Customer Analytics":
    page_title(
        "Customer Analytics",
        "Understand customer value and purchasing behavior.",
    )

    if rfm.empty:
        st.info("Customer RFM data is unavailable.")

    else:
        customer_col = find_col(rfm, "customer")

        monetary_col = next(
            (
                c for c in rfm.columns
                if str(c).strip().lower().replace("_", " ")
                in ["monetary", "monetary value", "total spend", "totalspend"]
            ),
            None,
        )

        frequency_col = next(
            (
                c for c in rfm.columns
                if str(c).strip().lower().replace("_", " ")
                in ["frequency", "purchase frequency", "orders"]
            ),
            None,
        )

        recency_col = next(
            (
                c for c in rfm.columns
                if str(c).strip().lower().replace("_", " ")
                in ["recency", "recency days", "days since last purchase"]
            ),
            None,
        )

        # KPI metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            total_customers = (
                rfm[customer_col].nunique()
                if customer_col
                else len(rfm)
            )
            metric_card(
                "Total Customers",
                format_number(total_customers),
            )

        with col2:
            average_spend = (
                to_numeric(rfm[monetary_col]).mean()
                if monetary_col
                else None
            )
            metric_card(
                "Average Monetary Value",
                format_money(average_spend),
            )

        with col3:
            average_frequency = (
                to_numeric(rfm[frequency_col]).mean()
                if frequency_col
                else None
            )
            metric_card(
                "Average Frequency",
                f"{average_frequency:.1f}"
                if pd.notna(average_frequency)
                else "-",
            )

        st.divider()

        # Recency vs spending analysis
        if recency_col and monetary_col:
            view = rfm[[recency_col, monetary_col]].copy()

            view[recency_col] = to_numeric(view[recency_col])
            view[monetary_col] = to_numeric(view[monetary_col])
            view = view.dropna()

            if not view.empty:
                fig = px.scatter(
                    view,
                    x=recency_col,
                    y=monetary_col,
                    title="Customer Recency vs Monetary Value",
                    labels={
                        recency_col: "Days Since Last Purchase",
                        monetary_col: "Customer Spending",
                    },
                    opacity=0.65,
                )

                fig.update_layout(
                    template="plotly_dark",
                    xaxis_title="Recency (Days)",
                    yaxis_title="Monetary Value",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )
        else:
            st.info(
                "Recency or Monetary columns were not found, "
                "so the scatter chart cannot be displayed."
            )

        # Top customers by spending
        if customer_col and monetary_col:
            top_customers = rfm[
                [customer_col, monetary_col]
            ].copy()

            top_customers[monetary_col] = to_numeric(
                top_customers[monetary_col]
            )

            top_customers = (
                top_customers.dropna()
                .sort_values(monetary_col, ascending=False)
                .head(10)
            )

            if not top_customers.empty:
                fig = px.bar(
                    top_customers.sort_values(
                        monetary_col, ascending=True
                    ),
                    x=monetary_col,
                    y=customer_col,
                    orientation="h",
                    title="Top 10 Customers by Spending",
                    labels={
                        customer_col: "Customer ID",
                        monetary_col: "Monetary Value",
                    },
                )

                fig.update_layout(template="plotly_dark")

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                )

        # Full customer records
        st.subheader("Customer Records")
        show_table(rfm, "Customer Records")
        download_csv(rfm, FILES["rfm"])


# ==========================================================
# PAGE 5 - CUSTOMER SEGMENTATION
# ==========================================================

elif page == " Customer Segmentation":
    page_title(
        "Customer Segmentation",
        "Analyze customer groups, spending, and business value.",
    )

    segment_col = find_col(rfm, "segment")
    customer_col = find_col(rfm, "customer")

    monetary_col = next(
        (
            c for c in rfm.columns
            if str(c).strip().lower().replace("_", " ")
            in ["monetary", "monetary value", "total spend", "totalspend"]
        ),
        None,
    )

    if rfm.empty or segment_col is None:
        st.warning(
            "Customer segment data is unavailable. "
            "Check customer_rfm_segments.csv."
        )
        show_table(rfm, "RFM Data Preview")

    else:
        data = rfm.copy()

        data[segment_col] = (
            data[segment_col]
            .fillna("Unknown")
            .astype(str)
            .str.strip()
            .replace("", "Unknown")
        )

        counts = (
            data[segment_col]
            .value_counts()
            .rename_axis("Segment")
            .reset_index(name="Customers")
        )

        total_customers = (
            data[customer_col].nunique()
            if customer_col
            else len(data)
        )

        total_segments = data[segment_col].nunique()
        largest_segment = counts.iloc[0]["Segment"]
        largest_count = int(counts.iloc[0]["Customers"])

        # KPI cards
        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card(
                "Total Customers",
                format_number(total_customers),
            )

        with col2:
            metric_card(
                "Customer Segments",
                format_number(total_segments),
            )

        with col3:
            metric_card(
                "Largest Segment",
                str(largest_segment),
            )
            st.caption(
                f"{format_number(largest_count)} customers"
            )

        st.divider()

        # Segment filters
        selected_segments = st.multiselect(
            "Filter customer segments",
            options=counts["Segment"].tolist(),
            default=counts["Segment"].tolist(),
        )

        filtered = data[
            data[segment_col].isin(selected_segments)
        ].copy()

        if filtered.empty:
            st.info("Select at least one customer segment to view charts.")

        else:
            filtered_counts = (
                filtered[segment_col]
                .value_counts()
                .rename_axis("Segment")
                .reset_index(name="Customers")
            )

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                fig = px.bar(
                    filtered_counts.sort_values("Customers"),
                    x="Customers",
                    y="Segment",
                    orientation="h",
                    text="Customers",
                    title="Customers by Segment",
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

            with chart_col2:
                fig = px.pie(
                    filtered_counts,
                    names="Segment",
                    values="Customers",
                    hole=0.55,
                    title="Customer Segment Distribution",
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

            # Spending comparison
            if monetary_col:
                filtered[monetary_col] = to_numeric(
                    filtered[monetary_col]
                )

                spending = (
                    filtered.groupby(segment_col, dropna=False)
                    [monetary_col]
                    .agg(["mean", "sum"])
                    .reset_index()
                )

                spending.columns = [
                    "Segment",
                    "Average Spending",
                    "Total Spending",
                ]

                fig = px.bar(
                    spending.sort_values("Average Spending"),
                    x="Average Spending",
                    y="Segment",
                    orientation="h",
                    title="Average Spending by Segment",
                    labels={
                        "Average Spending": "Average Monetary Value",
                    },
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

                show_table(spending, "Segment Spending Summary")

            show_table(
                filtered_counts,
                "Segment Customer Counts",
            )

            st.subheader("Customer-Level Segmentation")
            show_table(filtered, "Customer-Level Segmentation")

            download_csv(
                filtered,
                FILES["rfm"],
            )

# ==========================================================
# PAGE 6 - churn
# ==========================================================
elif page == " Customer Churn":
    page_title(
        "Customer Churn",
        "Identify at-risk customers and prioritize retention campaigns.",
    )

    if churn.empty:
        st.info("Customer churn predictions are unavailable.")

    else:
        probability_col = find_col(churn, "probability")
        status_col = find_col(churn, "status")
        customer_col = find_col(churn, "customer")

        view = churn.copy()

        # Convert probability to numeric
        if probability_col:
            view[probability_col] = to_numeric(
                view[probability_col]
            )

            # Support probability values from 0-1 or 0-100
            max_probability = view[probability_col].max()

            if pd.notna(max_probability) and max_probability > 1:
                view[probability_col] = (
                    view[probability_col] / 100
                )

            view = view.dropna(
                subset=[probability_col]
            )

            view[probability_col] = view[
                probability_col
            ].clip(0, 1)

            # Categorize risk
            def classify_risk(prob):
                if prob >= 0.7:
                    return "High Risk"
                elif prob >= 0.4:
                    return "Medium Risk"
                return "Low Risk"

            view["Risk Level"] = view[
                probability_col
            ].apply(classify_risk)

            high_risk_count = int(
                (view["Risk Level"] == "High Risk").sum()
            )
            medium_risk_count = int(
                (view["Risk Level"] == "Medium Risk").sum()
            )
            low_risk_count = int(
                (view["Risk Level"] == "Low Risk").sum()
            )
            avg_probability = (
                view[probability_col].mean() * 100
                if not view.empty
                else None
            )

        else:
            high_risk_count = 0
            medium_risk_count = 0
            low_risk_count = 0
            avg_probability = None

        unique_customers = (
            view[customer_col].nunique()
            if customer_col and not view.empty
            else len(view)
        )

        # KPI cards
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card(
                "Customers Scored",
                format_number(unique_customers),
            )

        with col2:
            metric_card(
                "High-Risk Customers",
                format_number(high_risk_count),
            )

        with col3:
            metric_card(
                "Medium-Risk Customers",
                format_number(medium_risk_count),
            )

        with col4:
            metric_card(
                "Average Churn Probability",
                (
                    f"{avg_probability:.1f}%"
                    if avg_probability is not None
                    else "N/A"
                ),
            )

        st.divider()

        # Status distribution
        if status_col:
            counts = (
                view[status_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
                .rename_axis("Status")
                .reset_index(name="Customers")
            )

            show_chart(
                px.pie(
                    counts,
                    names="Status",
                    values="Customers",
                    hole=0.5,
                    title="Customer Prediction Status",
                )
            )

        if probability_col and not view.empty:
            chart_col1, chart_col2 = st.columns(2)

            # Probability distribution
            with chart_col1:
                fig = px.histogram(
                    view,
                    x=probability_col,
                    nbins=20,
                    title="Churn Probability Distribution",
                    labels={
                        probability_col: "Churn Probability",
                    },
                )
                fig.update_layout(
                    template="plotly_dark",
                    xaxis=dict(tickformat=".0%"),
                )
                show_chart(fig)

            # Risk category distribution
            with chart_col2:
                risk_counts = (
                    view["Risk Level"]
                    .value_counts()
                    .reindex(
                        ["High Risk", "Medium Risk", "Low Risk"],
                        fill_value=0,
                    )
                    .rename_axis("Risk Level")
                    .reset_index(name="Customers")
                )

                fig = px.bar(
                    risk_counts,
                    x="Risk Level",
                    y="Customers",
                    title="Customers by Risk Level",
                    text="Customers",
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)
                st.write("Risk Level Counts:")
                st.write(view["Risk Level"].value_counts())

            # Filter customers by risk
            selected_risks = st.multiselect(
                "Filter by Risk Level",
                options=["High Risk", "Medium Risk", "Low Risk"],
                default=["High Risk"],
            )

            filtered = view[
                view["Risk Level"].isin(selected_risks)
            ].copy()

            filtered = filtered.sort_values(
                probability_col,
                ascending=False,
            )

            st.subheader("Customer Retention Priority")
            st.caption(
                "Higher predicted probability indicates higher model-estimated churn risk."
            )

            show_table(
                filtered.head(25),
                "Highest-Priority Customers",
                max_rows=25,
            )

            download_csv(
                filtered,
                FILES["churn"],
            )

        else:
            st.warning(
                "A numeric churn probability column was not found. "
                "Showing available prediction records instead."
            )
            show_table(churn, "Churn Prediction Records")
            download_csv(churn, FILES["churn"])

# ==========================================================
# PAGE 7 - INVENTORY
# ==========================================================

elif page == " Inventory":
    page_title(
        "Inventory Analytics",
        "Monitor stock levels and review recommended replenishment.",
    )

    if inventory.empty:
        st.info("Inventory recommendations are unavailable.")

    else:
        stock_col = find_col(inventory, "inventory")
        order_col = find_col(inventory, "recommended")

        # Detect optional product/category columns
        product_col = find_col(inventory, "product")
        category_col = find_col(inventory, "category")

        view = inventory.copy()

        if stock_col:
            view[stock_col] = to_numeric(view[stock_col])

        if order_col:
            view[order_col] = to_numeric(view[order_col])

        # KPI metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card(
                "Inventory Records",
                format_number(len(view)),
            )

        with col2:
            metric_card(
                "Total Recorded Stock",
                (
                    format_number(view[stock_col].sum())
                    if stock_col else "-"
                ),
            )

        with col3:
            metric_card(
                "Suggested Order Units",
                (
                    format_number(view[order_col].sum())
                    if order_col else "-"
                ),
            )

        with col4:
            if stock_col:
                low_stock_count = int(
                    (view[stock_col] <= 10).sum()
                )
                metric_card(
                    "Low-Stock Records",
                    format_number(low_stock_count),
                )
            else:
                metric_card("Low-Stock Records", "-")

        st.divider()

        # Stock and recommended order analysis
        if stock_col and order_col:
            chart_data = view[
                [stock_col, order_col]
            ].dropna()

            if not chart_data.empty:
                fig = px.scatter(
                    chart_data,
                    x=stock_col,
                    y=order_col,
                    title="Current Stock vs Suggested Orders",
                    labels={
                        stock_col: "Current Inventory",
                        order_col: "Recommended Order Quantity",
                    },
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

                # Compare total stock and order quantities
                comparison = pd.DataFrame({
                    "Metric": [
                        "Current Stock",
                        "Suggested Orders",
                    ],
                    "Units": [
                        chart_data[stock_col].sum(),
                        chart_data[order_col].sum(),
                    ],
                })

                fig = px.bar(
                    comparison,
                    x="Metric",
                    y="Units",
                    text="Units",
                    title="Stock and Replenishment Summary",
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

        # Category-wise stock summary, when available
        if category_col and stock_col:
            category_summary = (
                view.groupby(category_col, dropna=False)[stock_col]
                .sum()
                .reset_index()
                .sort_values(stock_col, ascending=False)
            )

            fig = px.bar(
                category_summary,
                x=category_col,
                y=stock_col,
                title="Total Inventory by Category",
            )
            fig.update_layout(template="plotly_dark")
            show_chart(fig)

        # Inventory records

        show_table(view, "Inventory Recommendation Records")
        download_csv(view, FILES["inventory"])


# ==========================================================
# PAGE 8 - COUNTRY ANALYSIS
# ==========================================================

elif page == " Country Analysis":
    page_title(
        "Country Analysis",
        "Compare sales performance across countries and regions.",
    )

    country_col = find_col(countries, "country")
    value_col = (
        find_col(countries, "sales")
        or find_col(countries, "revenue")
        or find_col(countries, "quantity")
        or find_numeric_col(countries)
    )

    if countries.empty or country_col is None or value_col is None:
        st.info(
            "Country analysis needs a country column and a numeric sales or quantity column."
        )
        show_table(countries, "Country Data Preview")

    else:
        view = countries[[country_col, value_col]].copy()
        view[value_col] = to_numeric(view[value_col])
        view = view.dropna(subset=[country_col, value_col])

        view[country_col] = (
            view[country_col].astype(str).str.strip()
        )
        view = view[view[country_col] != ""]

        view = (
            view.groupby(country_col, as_index=False)[value_col]
            .sum()
            .sort_values(value_col, ascending=False)
        )

        if view.empty:
            st.info("No valid country records are available.")

        else:
            total_countries = view[country_col].nunique()
            total_value = view[value_col].sum()
            top_country = view.iloc[0][country_col]
            top_value = view.iloc[0][value_col]

            # KPI cards
            col1, col2, col3 = st.columns(3)

            with col1:
                metric_card(
                    "Countries / Regions",
                    format_number(total_countries),
                )

            with col2:
                metric_card(
                    "Total Recorded Value",
                    format_money(total_value),
                )

            with col3:
                metric_card(
                    "Top Country",
                    str(top_country),
                )
                st.caption(format_money(top_value))

            st.divider()

            # Country filter
            selected_countries = st.multiselect(
                "Select countries",
                options=view[country_col].tolist(),
                default=view[country_col].head(10).tolist(),
            )

            filtered = view[
                view[country_col].isin(selected_countries)
            ].copy()

            if filtered.empty:
                st.info("Select at least one country to display charts.")

            else:
                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    fig = px.bar(
                        filtered.sort_values(value_col).tail(20),
                        x=value_col,
                        y=country_col,
                        orientation="h",
                        title="Country Performance",
                        labels={
                            country_col: "Country",
                            value_col: "Recorded Sales / Value",
                        },
                    )
                    fig.update_layout(template="plotly_dark")
                    show_chart(fig)

                with chart_col2:
                    pie_data = filtered.head(8)

                    fig = px.pie(
                        pie_data,
                        names=country_col,
                        values=value_col,
                        hole=0.5,
                        title="Share of Selected Countries",
                    )
                    fig.update_layout(template="plotly_dark")
                    show_chart(fig)

                show_table(filtered, "Country Summary")
                download_csv(filtered, FILES["countries"])

# ==========================================================
# PAGE 9 - PRODUCT ANALYTICS
# ==========================================================

elif page == " Product Analytics":
    page_title(
        "Product Analytics",
        "Analyze product performance and identify top-selling products.",
    )

    if products.empty:
        st.info("Top-products summary is unavailable.")

    else:
        product_col = find_col(products, "product")
        value_col = (
            find_col(products, "sales")
            or find_col(products, "revenue")
            or find_col(products, "quantity")
            or find_numeric_col(products)
        )

        if product_col is None:
            st.warning(
                "Product name or description column was not detected."
            )
            show_table(products, "Product Records")

        elif value_col is None:
            st.warning("No numeric product value column was detected.")
            show_table(products, "Product Records")

        else:
            view = products.copy()
            view[value_col] = to_numeric(view[value_col])
            view = view.dropna(subset=[value_col])

            view[product_col] = view[product_col].astype(str)

            # Search products
            search = st.text_input(
                "Search product",
                placeholder="Enter product name or stock code",
            )

            if search.strip():
                view = view[
                    view[product_col].str.contains(
                        search.strip(),
                        case=False,
                        na=False,
                    )
                ]

            if view.empty:
                st.info("No product matches your search.")

            else:
                # KPI metrics
                total_products = view[product_col].nunique()
                total_value = view[value_col].sum()

                top_product_row = view.loc[
                    view[value_col].idxmax()
                ]
                top_product_name = top_product_row[product_col]
                top_product_value = top_product_row[value_col]

                col1, col2, col3 = st.columns(3)

                with col1:
                    metric_card(
                        "Products Found",
                        format_number(total_products),
                    )

                with col2:
                    metric_card(
                        "Total Recorded Value",
                        format_money(total_value),
                    )

                with col3:
                    metric_card(
                        "Top Product",
                        str(top_product_name)[:35],
                    )
                    st.caption(format_money(top_product_value))

                st.divider()

                # Top product chart
                top = (
                    view.sort_values(value_col, ascending=False)
                    .head(20)
                )

                fig = px.bar(
                    top.sort_values(value_col),
                    x=value_col,
                    y=product_col,
                    orientation="h",
                    title="Top 20 Products by Value",
                    labels={
                        product_col: "Product",
                        value_col: "Recorded Sales / Value",
                    },
                )
                fig.update_layout(template="plotly_dark")
                show_chart(fig)

                # Product records
                ordered_columns = [product_col] + [
                    column for column in view.columns
                    if column != product_col
                ]

                show_table(
                    view[ordered_columns],
                    "Product Records",
                )

                download_csv(
                    view,
                    "filtered_product_analytics.csv",
                )


# ==========================================================
# PAGE 10 - DEMAND FORECAST
# ==========================================================

elif page == " Demand Forecast":
    page_title(
        "Demand Forecast",
        "Explore forecast trends, prediction metrics, and test results.",
    )

    chart_df, x_col, y_col = get_chart_data(forecast)

    if forecast.empty:
        st.info("Forecast data is unavailable. Check sales_forecast.csv.")

    else:
        # Forecast KPIs
        numeric_cols = forecast.select_dtypes(
            include="number"
        ).columns.tolist()

        forecast_value_col = (
            y_col if y_col in forecast.columns
            else numeric_cols[0] if numeric_cols
            else None
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            metric_card(
                "Forecast Records",
                format_number(len(forecast)),
            )

        with col2:
            metric_card(
                "Forecast Total",
                (
                    format_money(
                        to_numeric(forecast[forecast_value_col]).sum()
                    )
                    if forecast_value_col else "-"
                ),
            )

        with col3:
            metric_card(
                "Average Forecast",
                (
                    format_money(
                        to_numeric(forecast[forecast_value_col]).mean()
                    )
                    if forecast_value_col else "-"
                ),
            )

        st.divider()

        # Forecast trend
        if chart_df is not None and not chart_df.empty:
            fig = px.line(
                chart_df,
                x=x_col,
                y=y_col,
                markers=True,
                title="Sales / Demand Forecast Trend",
                labels={
                    x_col: "Date / Period",
                    y_col: "Forecast Value",
                },
            )
            fig.update_layout(template="plotly_dark")
            show_chart(fig)
        else:
            st.info(
                "Forecast chart needs a date/period column "
                "and a numeric forecast column."
            )

        show_table(forecast, "Forecast Records")
        download_csv(forecast, FILES["forecast"])

    # Test results
    if not forecast_test.empty:
        st.divider()
        page_title(
            "Forecast Model Evaluation",
            "Review available forecast test results.",
        )

        # Display test results without assuming particular metric columns
        show_table(forecast_test, "Forecast Test Results")
        download_csv(
            forecast_test,
            FILES["forecast_test"],
        )


# ==========================================================
# PAGE 11 - BUSINESS INSIGHTS
# ==========================================================

# ==========================================================
# BUSINESS INSIGHTS
# ==========================================================

elif page == " Business Insights":

    page_title(
        "Business Insights",
        "Key observations from sales, customers, churn and inventory data.",
    )

    insights = []

    # ------------------------------------------------------
    # 1. SALES INSIGHTS
    # ------------------------------------------------------

    if not monthly.empty:

        value_col = (
            find_col(monthly, "sales")
            or find_col(monthly, "revenue")
            or find_numeric_col(monthly)
        )

        date_col = (
            find_col(monthly, "yearmonth")
            or find_col(monthly, "date")
            or find_col(monthly, "month")
        )

        if value_col:

            values = to_numeric(monthly[value_col])
            valid = values.dropna()

            if not valid.empty:

                best_idx = valid.idxmax()
                best_value = valid.loc[best_idx]

                period = (
                    str(monthly.loc[best_idx, date_col])
                    if date_col
                    else f"record {best_idx}"
                )

                insights.append(
                    (
                        "Sales Performance",
                        f"Highest sales value is "
                        f"{format_money(best_value)} during {period}.",
                    )
                )

                insights.append(
                    (
                        "Total Sales",
                        f"Total sales across available summary "
                        f"records: {format_money(valid.sum())}.",
                    )
                )

    # ------------------------------------------------------
    # 2. PRODUCT INSIGHTS
    # ------------------------------------------------------

    if not products.empty:

        product_col = (
            find_col(products, "description")
            or find_col(products, "product")
            or find_col(products, "stockcode")
        )

        value_col = (
            find_col(products, "sales")
            or find_col(products, "revenue")
            or find_col(products, "quantity")
            or find_col(products, "unitssold")
            or find_numeric_col(products)
        )

        if product_col and value_col:

            view = products.copy()
            view[value_col] = to_numeric(view[value_col])

            view = view.dropna(subset=[value_col]).sort_values(
                value_col,
                ascending=False,
            )

            if not view.empty:

                top_product = str(view.iloc[0][product_col])

                insights.append(
                    (
                        "Top Product",
                        f"Top product in the available summary: "
                        f"{top_product}.",
                    )
                )

    # ------------------------------------------------------
    # 3. CUSTOMER SEGMENTATION
    # ------------------------------------------------------

    if not rfm.empty:

        segment_col = find_col(rfm, "segment")

        if segment_col:

            counts = (
                rfm[segment_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
            )

            if not counts.empty:

                insights.append(
                    (
                        "Customer Segmentation",
                        f"Largest segment: {counts.index[0]} "
                        f"({counts.iloc[0]:,} customer records).",
                    )
                )

    # ------------------------------------------------------
    # 4. CHURN INSIGHTS
    # ------------------------------------------------------

    if not churn.empty:

        probability_col = (
            find_col(churn, "churnriskprobability")
            or find_col(churn, "probability")
        )

        risk_col = find_col(churn, "churnrisk")

        if probability_col:

            probabilities = to_numeric(
                churn[probability_col]
            ).dropna()

            if not probabilities.empty:

                high_risk_count = int(
                    (probabilities >= 0.7).sum()
                )

                insights.append(
                    (
                        "Customer Retention",
                        f"{high_risk_count:,} customers have a "
                        f"model-estimated churn probability of "
                        f"70% or higher. This is a prediction, "
                        f"not a confirmed churn outcome.",
                    )
                )

        elif risk_col:

            risks = churn[risk_col].astype(str)
            high_risk_count = int((risks == "High").sum())

            insights.append(
                (
                    "Customer Retention",
                    f"{high_risk_count:,} customers are classified "
                    f"as High Risk by the model.",
                )
            )

    # ------------------------------------------------------
    # 5. INVENTORY INSIGHTS
    # ------------------------------------------------------

    if not inventory.empty:

        demand_col = find_col(inventory, "demandcategory")

        reorder_col = (
            find_col(inventory, "suggestedreorderlevel")
            or find_col(inventory, "reorderlevel")
        )

        if demand_col:

            categories = (
                inventory[demand_col]
                .fillna("Unknown")
                .astype(str)
                .value_counts()
            )

            high_demand_count = int(
                categories.get("High Demand", 0)
            )

            insights.append(
                (
                    "Product Demand",
                    f"{high_demand_count:,} products are labelled "
                    f"High Demand in the inventory analysis.",
                )
            )

        if reorder_col:

            reorder_values = to_numeric(
                inventory[reorder_col]
            ).dropna()

            if not reorder_values.empty:

                median_reorder = reorder_values.median()

                insights.append(
                    (
                        "Inventory Planning",
                        f"Median suggested reorder level: "
                        f"{median_reorder:,.0f} units. This is an "
                        f"estimate based on assumed demand coverage, "
                        f"not actual stock on hand.",
                    )
                )

    # ------------------------------------------------------
    # 6. DISPLAY INSIGHT CARDS
    # ------------------------------------------------------

    if insights:

        for heading, message in insights:

            st.markdown(
                f"""
                <div class="insight-card">
                    <div class="insight-heading">
                        {html.escape(heading)}
                    </div>
                    <div class="insight-message">
                        {html.escape(message)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "No insights are available. Check whether the summary "
            "CSV files exist and contain usable columns."
        )

    # ------------------------------------------------------
    # 7. DATA READINESS
    # ------------------------------------------------------

    section("Data Readiness")

    status_df = pd.DataFrame(
        [
            {
                "Dataset": label.replace("_", " ").title(),
                "File": filename,
                "Status": (
                    "Available"
                    if (DATA_DIR / filename).exists()
                    else "Missing"
                ),
            }
            for label, filename in FILES.items()
        ]
    )

    show_table(status_df)


elif page == " CSV Data Explorer":
    page_title(
        "CSV Data Explorer",
        "Upload, preview, filter and export your own dataset."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
        key="csv_explorer_upload"
    )

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            if df.empty:
                st.warning("The uploaded CSV has no data.")
            else:
                st.success("CSV uploaded successfully!")

                c1, c2 = st.columns(2)
                c1.metric("Total Rows", f"{len(df):,}")
                c2.metric("Total Columns", f"{len(df.columns):,}")

                st.subheader(" Data Preview")
                st.dataframe(df.head(20), use_container_width=True)

                st.subheader(" Filters")
                filtered_df = df.copy()

                filter_columns = st.multiselect(
                    "Choose columns to filter",
                    options=df.columns.tolist(),
                    key="csv_explorer_columns"
                )

                for col in filter_columns:
                    st.markdown(f"**{col}**")

                    if pd.api.types.is_numeric_dtype(df[col]):
                        values = pd.to_numeric(
                            df[col], errors="coerce"
                        ).dropna()

                        if values.empty:
                            st.info(f"No numeric values in {col}.")
                            continue

                        low, high = float(values.min()), float(values.max())

                        if low < high:
                            selected = st.slider(
                                f"Range for {col}",
                                min_value=low,
                                max_value=high,
                                value=(low, high),
                                key=f"csv_range_{col}"
                            )

                            numbers = pd.to_numeric(
                                filtered_df[col], errors="coerce"
                            )
                            filtered_df = filtered_df[
                                numbers.between(selected[0], selected[1])
                            ]

                    else:
                        choices = sorted(
                            df[col].dropna().astype(str).unique().tolist()
                        )

                        selected = st.multiselect(
                            f"Values for {col}",
                            options=choices,
                            default=choices,
                            key=f"csv_values_{col}"
                        )

                        filtered_df = filtered_df[
                            filtered_df[col].astype("string").isin(selected)
                        ]

                st.subheader(" Filtered Results")
                st.write(
                    f"Showing **{len(filtered_df):,}** of "
                    f"**{len(df):,}** rows"
                )
                st.dataframe(filtered_df, use_container_width=True)

                csv_data = filtered_df.to_csv(
                    index=False
                ).encode("utf-8-sig")

                st.download_button(
                    " Download Filtered CSV",
                    data=csv_data,
                    file_name="retailpulse_filtered_data.csv",
                    mime="text/csv",
                    key="csv_explorer_download"
                )

        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as e:
            st.error(f"Unable to read CSV: {e}")
