-- ============================================================
-- SQL Queries - KPI Analysis
-- Phase 2: Data Analyst
-- Author: 23110236_NguyenPhuocKhang
-- DB: data/processed/ecommerce.db (SQLite)
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- 1. KPIs TỔNG QUAN
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                             AS total_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS avg_order_value,
    ROUND(SUM(Purchase_Amount), 2)       AS total_revenue,
    ROUND(AVG(Return_Rate), 3)           AS avg_return_rate,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(100.0 * SUM(Discount_Used) / COUNT(*), 1) AS discount_usage_pct,
    ROUND(100.0 * SUM(Customer_Loyalty_Program_Member) / COUNT(*), 1) AS loyalty_member_pct
FROM orders;

-- ────────────────────────────────────────────────────────────
-- 2. DOANH THU THEO KÊNH MUA HÀNG
-- ────────────────────────────────────────────────────────────
SELECT
    Purchase_Channel,
    COUNT(*)                             AS num_orders,
    ROUND(SUM(Purchase_Amount), 2)       AS total_revenue,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate
FROM orders
GROUP BY Purchase_Channel
ORDER BY total_revenue DESC;

-- ────────────────────────────────────────────────────────────
-- 3. TOP 10 DANH MỤC SẢN PHẨM (doanh thu)
-- ────────────────────────────────────────────────────────────
SELECT
    Purchase_Category,
    COUNT(*)                        AS num_orders,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(AVG(Return_Rate), 2)      AS avg_return_rate
FROM orders
GROUP BY Purchase_Category
ORDER BY total_revenue DESC
LIMIT 10;

-- ────────────────────────────────────────────────────────────
-- 4. PHÂN TÍCH NHÂN KHẨU HỌC: Thu nhập × Giới tính
-- ────────────────────────────────────────────────────────────
SELECT
    Income_Level,
    Gender,
    COUNT(*)                             AS num_customers,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Frequency_of_Purchase), 1) AS avg_frequency,
    ROUND(AVG(Brand_Loyalty), 2)         AS avg_brand_loyalty,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
GROUP BY Income_Level, Gender
ORDER BY Income_Level, Gender;

-- ────────────────────────────────────────────────────────────
-- 5. ẢNH HƯỞNG CỦA DISCOUNT đến SATISFACTION & RETURN RATE
-- ────────────────────────────────────────────────────────────
SELECT
    Discount_Sensitivity,
    CASE WHEN Discount_Used = 1 THEN 'Used Discount' ELSE 'No Discount' END AS Discount_Group,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate
FROM orders
GROUP BY Discount_Sensitivity, Discount_Group
ORDER BY Discount_Sensitivity, Discount_Group;

-- ────────────────────────────────────────────────────────────
-- 6. XU HƯỚNG MUA THEO THÁNG
-- ────────────────────────────────────────────────────────────
SELECT
    Purchase_Month,
    Purchase_Quarter,
    COUNT(*)                        AS num_orders,
    ROUND(SUM(Purchase_Amount), 2)  AS monthly_revenue,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
WHERE Purchase_Month IS NOT NULL
GROUP BY Purchase_Month
ORDER BY Purchase_Month;

-- ────────────────────────────────────────────────────────────
-- 7. PHƯƠNG THỨC THANH TOÁN
-- ────────────────────────────────────────────────────────────
SELECT
    Payment_Method,
    COUNT(*)                        AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(100.0 * SUM(Discount_Used) / COUNT(*), 1) AS discount_usage_pct
FROM orders
GROUP BY Payment_Method
ORDER BY num_orders DESC;

-- ────────────────────────────────────────────────────────────
-- 8. LOYALTY PROGRAM: Thành viên vs Không thành viên
-- ────────────────────────────────────────────────────────────
SELECT
    CASE WHEN Customer_Loyalty_Program_Member = 1 THEN 'Member' ELSE 'Non-Member' END AS Loyalty_Status,
    COUNT(*)                             AS num_customers,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Frequency_of_Purchase), 1) AS avg_frequency,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate,
    ROUND(AVG(Brand_Loyalty), 2)         AS avg_brand_loyalty
FROM orders
GROUP BY Loyalty_Status;

-- ────────────────────────────────────────────────────────────
-- 9. SOCIAL MEDIA ẢNH HƯỞNG đến PURCHASE INTENT
-- ────────────────────────────────────────────────────────────
SELECT
    Social_Media_Influence,
    Purchase_Intent,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
GROUP BY Social_Media_Influence, Purchase_Intent
ORDER BY Social_Media_Influence, num_orders DESC;

-- ────────────────────────────────────────────────────────────
-- 10. SHIPPING PREFERENCE vs SATISFACTION & TIME TO DECISION
-- ────────────────────────────────────────────────────────────
SELECT
    Shipping_Preference,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Time_to_Decision), 1)      AS avg_decision_time,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate
FROM orders
GROUP BY Shipping_Preference
ORDER BY avg_satisfaction DESC;

-- ────────────────────────────────────────────────────────────
-- 11. DEVICE vs PURCHASE CHANNEL (cross-tab)
-- ────────────────────────────────────────────────────────────
SELECT
    Device_Used_for_Shopping,
    Purchase_Channel,
    COUNT(*)                        AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)  AS aov
FROM orders
GROUP BY Device_Used_for_Shopping, Purchase_Channel
ORDER BY Device_Used_for_Shopping, num_orders DESC;

-- ────────────────────────────────────────────────────────────
-- 12. TOP 10 LOCATION theo doanh thu
-- ────────────────────────────────────────────────────────────
SELECT
    Location,
    COUNT(*)                        AS num_orders,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
GROUP BY Location
ORDER BY total_revenue DESC
LIMIT 10;

-- ────────────────────────────────────────────────────────────
-- 13. MARITAL STATUS → AOV & SATISFACTION
-- ────────────────────────────────────────────────────────────
SELECT
    Marital_Status,
    COUNT(*)                             AS num_customers,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Frequency_of_Purchase), 1) AS avg_frequency,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate
FROM orders
GROUP BY Marital_Status
ORDER BY aov DESC;

-- ────────────────────────────────────────────────────────────
-- 14. EDUCATION LEVEL → HÀNH VI MUA HÀNG
-- ────────────────────────────────────────────────────────────
SELECT
    Education_Level,
    COUNT(*)                             AS num_customers,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Frequency_of_Purchase), 1) AS avg_frequency,
    ROUND(AVG(Research_Hours), 2)        AS avg_research_hours,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Brand_Loyalty), 2)         AS avg_brand_loyalty
FROM orders
GROUP BY Education_Level
ORDER BY aov DESC;

-- ────────────────────────────────────────────────────────────
-- 15. OCCUPATION → DOANH THU & LOYALTY
-- ────────────────────────────────────────────────────────────
SELECT
    Occupation,
    COUNT(*)                        AS num_customers,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(AVG(Brand_Loyalty), 2)    AS avg_brand_loyalty,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
GROUP BY Occupation
ORDER BY total_revenue DESC;

-- ────────────────────────────────────────────────────────────
-- 16. PRODUCT RATING → SATISFACTION & RETURN RATE
-- ────────────────────────────────────────────────────────────
SELECT
    Product_Rating,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate,
    ROUND(AVG(Brand_Loyalty), 2)         AS avg_brand_loyalty
FROM orders
GROUP BY Product_Rating
ORDER BY Product_Rating;

-- ────────────────────────────────────────────────────────────
-- 17. TIME TO DECISION PHÂN NHÓM
-- ────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN Time_to_Decision <= 3  THEN 'Quick (<=3 min)'
        WHEN Time_to_Decision <= 7  THEN 'Normal (4-7 min)'
        WHEN Time_to_Decision <= 14 THEN 'Deliberate (8-14 min)'
        ELSE 'Slow (>14 min)'
    END AS Decision_Speed,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Return_Rate), 2)           AS avg_return_rate,
    ROUND(100.0 * SUM(Discount_Used) / COUNT(*), 1) AS discount_pct
FROM orders
GROUP BY Decision_Speed
ORDER BY AVG(Time_to_Decision);

-- ────────────────────────────────────────────────────────────
-- 18. ENGAGEMENT WITH ADS → PURCHASE INTENT & AOV
-- ────────────────────────────────────────────────────────────
SELECT
    Engagement_with_Ads,
    Purchase_Intent,
    COUNT(*)                             AS num_orders,
    ROUND(AVG(Purchase_Amount), 2)       AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction,
    ROUND(AVG(Brand_Loyalty), 2)         AS avg_brand_loyalty
FROM orders
GROUP BY Engagement_with_Ads, Purchase_Intent
ORDER BY Engagement_with_Ads, num_orders DESC;

-- ────────────────────────────────────────────────────────────
-- 19. MUA HÀNG THEO QUÝ & NGÀY TRONG TUẦN
-- ────────────────────────────────────────────────────────────
SELECT
    Purchase_Quarter,
    COUNT(*)                        AS num_orders,
    ROUND(SUM(Purchase_Amount), 2)  AS total_revenue,
    ROUND(AVG(Purchase_Amount), 2)  AS aov,
    ROUND(AVG(Customer_Satisfaction), 2) AS avg_satisfaction
FROM orders
WHERE Purchase_Quarter IS NOT NULL
GROUP BY Purchase_Quarter
ORDER BY Purchase_Quarter;

-- Day of week
SELECT
    CASE Purchase_DayOfWeek
        WHEN 0 THEN 'Monday'    WHEN 1 THEN 'Tuesday'
        WHEN 2 THEN 'Wednesday' WHEN 3 THEN 'Thursday'
        WHEN 4 THEN 'Friday'    WHEN 5 THEN 'Saturday'
        WHEN 6 THEN 'Sunday'
    END AS Day_Name,
    COUNT(*)                       AS num_orders,
    ROUND(SUM(Purchase_Amount), 2) AS total_revenue,
    ROUND(AVG(Purchase_Amount), 2) AS aov
FROM orders
WHERE Purchase_DayOfWeek IS NOT NULL
GROUP BY Purchase_DayOfWeek
ORDER BY Purchase_DayOfWeek;
