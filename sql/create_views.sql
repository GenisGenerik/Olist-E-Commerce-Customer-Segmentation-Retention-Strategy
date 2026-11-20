CREATE VIEW vw_delivered_order AS
SELECT 
	o.order_id,
	c.customer_unique_id,
	c.customer_city,
	c.customer_state,
	o.order_purchase_timestamp,
	YEAR(o.order_purchase_timestamp) AS tahun_order,
	MONTH(o.order_purchase_timestamp) AS bulan_order,
	oi.product_id,
	ISNULL(p.product_category_name,'uncategorized') AS product_category,
	oi.price,
	oi.freight_value,
	(oi.price+oi.freight_value) AS total_pembayaran

FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
LEFT JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'delivered';
GO

CREATE VIEW vw_rfm_customers AS
WITH max_date AS (
SELECT MAX(order_purchase_timestamp) AS last_order_date FROM vw_delivered_order
)

SELECT 
	customer_unique_id,
	DATEDIFF(DAY,MAX(order_purchase_timestamp),(SELECT last_order_date FROM max_date)) AS hari_semenjak_pembelian_terakhir,
	COUNT(DISTINCT order_id) AS frekuensi_pembelian,
	SUM(price) AS total_nilai_pembelian
FROM vw_delivered_order
GROUP BY customer_unique_id
GO