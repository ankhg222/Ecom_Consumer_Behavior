-- Schema SQLite cho Ecommerce Consumer Behavior
-- Phase 1: Data Engineering
-- Author: 23110236_NguyenPhuocKhang

DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    Customer_ID                     TEXT PRIMARY KEY,
    Age                             INTEGER,
    Gender                          TEXT,
    Income_Level                    TEXT,          -- Low / Middle / High
    Marital_Status                  TEXT,
    Education_Level                 TEXT,
    Occupation                      TEXT,
    Location                        TEXT,
    Purchase_Category               TEXT,
    Purchase_Amount                 REAL,          -- đã clean, đơn vị USD
    Frequency_of_Purchase           INTEGER,
    Purchase_Channel                TEXT,          -- Online / In-Store / Mixed
    Brand_Loyalty                   INTEGER,       -- 1-5
    Product_Rating                  INTEGER,       -- 1-5
    Research_Hours                  REAL,          -- giờ nghiên cứu sản phẩm
    Social_Media_Influence          TEXT,          -- None / Low / Medium / High
    Discount_Sensitivity            TEXT,
    Return_Rate                     INTEGER,       -- số lần hoàn trả
    Customer_Satisfaction           INTEGER,       -- 1-10
    Engagement_with_Ads             TEXT,
    Device_Used_for_Shopping        TEXT,
    Payment_Method                  TEXT,
    Time_of_Purchase                TEXT,          -- datetime ISO
    Purchase_Month                  INTEGER,
    Purchase_Quarter                INTEGER,
    Purchase_DayOfWeek              INTEGER,       -- 0=Mon, 6=Sun
    Discount_Used                   INTEGER,       -- 0 / 1
    Customer_Loyalty_Program_Member INTEGER,       -- 0 / 1
    Purchase_Intent                 TEXT,          -- Impulsive / Planned / Need-based / Wants-based
    Shipping_Preference             TEXT,
    Time_to_Decision                INTEGER,       -- phút
    High_Satisfaction               INTEGER,       -- derived: 1 nếu satisfaction >= 7
    Is_Loyal                        INTEGER        -- derived: 1 nếu brand_loyalty >= 4
);

-- View: KPIs tổng quan
CREATE VIEW IF NOT EXISTS vw_kpi_overview AS
SELECT
    COUNT(*)                        AS total_orders,
    ROUND(AVG(Purchase_Amount), 2)  AS avg_order_value,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Return_Rate), 3)      AS avg_return_rate,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    SUM(Discount_Used)              AS total_discount_used,
    ROUND(100.0 * SUM(Discount_Used) / COUNT(*), 1) AS discount_usage_pct
FROM orders;

-- View: Doanh thu theo kênh mua
CREATE VIEW IF NOT EXISTS vw_revenue_by_channel AS
SELECT
    Purchase_Channel,
    COUNT(*)                        AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
GROUP BY Purchase_Channel
ORDER BY total_revenue DESC;

-- View: Phân tích theo nhân khẩu học
CREATE VIEW IF NOT EXISTS vw_demographics AS
SELECT
    Income_Level,
    Gender,
    Education_Level,
    COUNT(*)                        AS num_customers,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(AVG(Frequency_of_Purchase), 1) AS avg_frequency,
    ROUND(AVG(Brand_Loyalty), 2)    AS avg_brand_loyalty
FROM orders
GROUP BY Income_Level, Gender, Education_Level
ORDER BY num_customers DESC;
