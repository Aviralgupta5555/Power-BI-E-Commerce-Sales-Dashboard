# Power BI E-Commerce Sales Dashboard Implementation Guide

This guide details how to build a professional, high-performance E-Commerce Sales Dashboard using Microsoft Power BI Desktop and the generated datasets.

---

## 1. Importing the Datasets

1. Open **Power BI Desktop**.
2. Click on **Get Data** -> **Text/CSV**.
3. Import the three generated CSV files from your `data` folder:
   - `Dim_Customers.csv`
   - `Dim_Products.csv`
   - `Fact_Orders.csv`
4. In the preview window, click **Transform Data** to open the **Power Query Editor**.
5. **Verify and Adjust Data Types**:
   - `Fact_Orders`:
     - Ensure `Order_Date` and `Ship_Date` are set to **Date** type.
     - Ensure `Sales`, `Profit`, and `Shipping_Cost` are set to **Fixed Decimal Number** (Currency).
     - Ensure `Quantity` is set to **Whole Number**.
     - Ensure `Discount` is set to **Decimal Number** (Percentage).
   - `Dim_Customers`:
     - Ensure `Postal_Code` is set to **Text** (so leading zeros are preserved).
   - `Dim_Products`:
     - Ensure `Cost_Price` and `List_Price` are set to **Fixed Decimal Number** (Currency).
6. Click **Close & Apply** to load the data into the model.

---

## 2. Setting Up the Data Model (Star Schema)

Navigate to the **Model View** (left-hand sidebar, relationships icon) and verify or create the relationships:

1. Connect **Dim_Customers** to **Fact_Orders**:
   - Drag `Customer_ID` from `Dim_Customers` to `Customer_ID` in `Fact_Orders`.
   - **Relationship Type**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single` (Dim_Customers filters Fact_Orders)

2. Connect **Dim_Products** to **Fact_Orders**:
   - Drag `Product_ID` from `Dim_Products` to `Product_ID` in `Fact_Orders`.
   - **Relationship Type**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single` (Dim_Products filters Fact_Orders)

### Creating a Date Dimension (Dim_Date)
For advanced time intelligence functions (like Month-over-Month or Year-over-Year calculations), it is best practice to create a dedicated Date table.

1. In the **Report View** or **Data View**, click **New Table** on the ribbon and enter the following DAX:
   ```dax
   Dim_Date = 
   ADDCOLUMNS(
       CALENDAR(MIN(Fact_Orders[Order_Date]), MAX(Fact_Orders[Order_Date])),
       "Year", YEAR([Date]),
       "Quarter", "Q" & FORMAT([Date], "Q"),
       "Month Number", MONTH([Date]),
       "Month Name", FORMAT([Date], "MMMM"),
       "Month Short", FORMAT([Date], "MMM"),
       "Month-Year", FORMAT([Date], "MMM YYYY"),
       "Month-Year Sort", YEAR([Date]) * 100 + MONTH([Date]),
       "Day of Week", FORMAT([Date], "dddd"),
       "Day of Week Sort", WEEKDAY([Date], 2)
   )
   ```
2. Sort the columns to display correctly:
   - Select `Month Name` or `Month-Year` and click **Sort by column** -> Select `Month-Year Sort`.
   - Select `Day of Week` and click **Sort by column** -> Select `Day of Week Sort`.
3. In **Model View**, establish the relationship:
   - Drag `Date` from `Dim_Date` to `Order_Date` in `Fact_Orders`.
   - **Relationship Type**: `1 to Many (1:*)`
   - **Cross filter direction**: `Single`

---

## 3. Writing DAX Measures

It is recommended to create a blank table (e.g., `_Measures`) to store all calculations. Go to **Home** -> **Enter Data**, name the table `_Measures`, click **Load**, and then add the following measures there.

### Core KPI Measures

* **Total Sales**
  ```dax
  Total Sales = SUM(Fact_Orders[Sales])
  ```
  *Format as Currency ($)*

* **Total Profit**
  ```dax
  Total Profit = SUM(Fact_Orders[Profit])
  ```
  *Format as Currency ($)*

* **Profit Margin %**
  ```dax
  Profit Margin % = DIVIDE([Total Profit], [Total Sales], 0)
  ```
  *Format as Percentage (%)*

* **Total Orders**
  ```dax
  Total Orders = DISTINCTCOUNT(Fact_Orders[Order_ID])
  ```
  *Format as Whole Number*

* **Average Order Value (AOV)**
  ```dax
  Average Order Value = DIVIDE([Total Sales], [Total Orders], 0)
  ```
  *Format as Currency ($)*

* **Total Quantity Sold**
  ```dax
  Total Quantity Sold = SUM(Fact_Orders[Quantity])
  ```
  *Format as Whole Number*

### Time Intelligence / Trend Measures

* **Sales Last Year (LY)**
  ```dax
  Sales LY = CALCULATE([Total Sales], SAMEPERIODLASTYEAR(Dim_Date[Date]))
  ```

* **Sales Year-over-Year (YoY) Growth %**
  ```dax
  Sales YoY Growth % = DIVIDE([Total Sales] - [Sales LY], [Sales LY], 0)
  ```
  *Format as Percentage (%)*

* **Profit Last Year (LY)**
  ```dax
  Profit LY = CALCULATE([Total Profit], SAMEPERIODLASTYEAR(Dim_Date[Date]))
  ```

* **Profit YoY Growth %**
  ```dax
  Profit YoY Growth % = DIVIDE([Total Profit] - [Profit LY], [Profit LY], 0)
  ```
  *Format as Percentage (%)*

---

## 4. Dashboard Design & Visual Layout

To build a professional dashboard matching modern aesthetic standards (e.g., a dark/glassmorphic or crisp modern corporate look), configure the canvas and visuals as follows:

### Theme and Canvas Setup
* **Background Canvas Color**: Dark Slate/Charcoal `#1E2229` or White `#F8F9FA` for light mode.
* **Fonts**: *Segoe UI* or *Inter*.

### Section 1: Interactive Slicers (Top Panel)
Create horizontal, compact slicers for user interaction:
* **Date Slicer**: Using `Dim_Date[Date]` configured as a date range slider.
* **Region Slicer**: Using `Dim_Customers[Region]` configured as a single/multi-select dropdown or horizontal tile.
* **Customer Segment**: Using `Dim_Customers[Segment]` configured as horizontal buttons/tiles.
* **Product Category**: Using `Dim_Products[Category]` configured as a dropdown.

### Section 2: Key Performance Indicators (KPI Cards - Top Row)
Place 5 card visuals side-by-side:
1. **Total Sales**: Display `[Total Sales]` (e.g., display units: Auto, rounded).
2. **Total Profit**: Display `[Total Profit]`. Apply conditional formatting to the font color: Green if `> 0`, Red if `< 0`.
3. **Profit Margin %**: Display `[Profit Margin %]`.
4. **Total Orders**: Display `[Total Orders]`.
5. **AOV**: Display `[Average Order Value]`.

### Section 3: Charts & Analytical Visuals (Main Body)

* **Sales and Profit Monthly Trend** (Left, Large)
  * **Visual**: *Line and stacked column chart* or *Line chart*.
  * **X-Axis**: `Dim_Date[Month-Year]` (Sorted chronologically by Sort column).
  * **Y-Axis**: `[Total Sales]` (Column or primary Line), `[Total Profit]` (Line on secondary Y-axis).
  * **Aesthetics**: Turn on Zoom Slider. Use smooth curves (Spline lines) and distinct colors (e.g., Violet for Sales, Cyan/Teal for Profit).

* **Sales by Category & Sub-Category** (Right, Top)
  * **Visual**: *Clustered Bar Chart* (Horizontal).
  * **Y-Axis**: `Dim_Products[Category]` -> `Dim_Products[Sub_Category]` (enabling drill-down).
  * **X-Axis**: `[Total Sales]`.
  * **Data Labels**: On.

* **Customer Segment Sales Split** (Right, Bottom)
  * **Visual**: *Donut Chart*.
  * **Legend**: `Dim_Customers[Segment]`.
  * **Values**: `[Total Sales]`.
  * **Details**: Show both category name and percentage.

### Section 4: Geographical Distribution (Bottom Row)
* **Regional Sales Map** (Left)
  * **Visual**: *Map* or *Filled Map*.
  * **Location**: `Dim_Customers[State]`.
  * **Bubble Size**: `[Total Sales]`.
  * **Bubble Color**: Color saturation based on `[Profit Margin %]` (revealing which states are most profitable).

* **Detailed Transactions Table** (Right)
  * **Visual**: *Matrix* or *Table*.
  * **Columns**: `Customer_Name`, `Product_Name`, `Category`, `Total Sales`, `Total Profit`, `Profit Margin %`.
  * **Features**: Sort by `Total Sales` descending. Turn on conditional formatting (data bars) for the Sales column to make it visually scannable.
