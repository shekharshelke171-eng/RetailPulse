\# RetailPulse - Data Dictionary



\## 1. Project Dataset



The project uses the Online Retail transaction dataset.



\- Total Records: 525,461

\- Total Columns: 14

\- Total Sales: £9,539,484.63

\- Unique Products (StockCode): 4,632

\- Unique Countries: 40

\- Unique Invoices: 28,816



\## 2. Column Description



| Column Name | Description |

|---|---|

| Invoice | Unique invoice number |

| StockCode | Product identification code |

| Description | Product name or description |

| Quantity | Number of products purchased |

| InvoiceDate | Date and time of transaction |

| Price | Unit price of product |

| Customer ID | Customer identification number |

| Country | Customer's country |

| TotalSales | Total transaction value |

| Year | Transaction year |

| Month | Transaction month |

| Day | Day of transaction |

| DayOfWeek | Day of the week |

| YearMonth | Year and month combination |



\## 3. Data Quality



\- Missing Description values: 2,928

\- Missing Customer ID values: 107,927

\- No missing values in the remaining columns.



\## 4. Derived Features



The feature-engineering process creates:



\- TotalSales

\- Year

\- Month

\- Day

\- DayOfWeek

\- YearMonth



\## 5. Notes



Customer ID missing values are important when performing customer-level analysis. Missing-value handling should follow the requirements of each analytical module.
