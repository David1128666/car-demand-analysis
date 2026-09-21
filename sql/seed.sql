USE car_demand_analysis;

INSERT INTO sys_user
  (user_id, username, password_hash, nickname, role, email, status)
VALUES
  (1, 'admin', 'eef254f06c30c7b3b5a3f9915393499288b154d1bcdf4295a23f72ad6749cfea', 'Platform Administrator', 'admin', 'admin@example.com', 1)
ON DUPLICATE KEY UPDATE username = VALUES(username);

INSERT INTO system_config (config_key, config_value, config_type, config_group) VALUES
  ('sys.cache.realtime.ttl', '30', 'int', 'cache'),
  ('sys.cache.trends.ttl', '3600', 'int', 'cache'),
  ('recommend.default.limit', '10', 'int', 'recommend'),
  ('spark.streaming.batch.seconds', '10', 'int', 'streaming'),
  ('spark.offline.schedule', '02:00', 'string', 'offline')
ON DUPLICATE KEY UPDATE config_value = VALUES(config_value);

INSERT INTO car_info
  (car_id, brand_id, brand_name, series_id, series_name, model_name, car_type, fuel_type, price, launch_date, country, is_on_sale)
VALUES
  (1, 1, 'Toyota', 101, 'Camry', 'Camry 2.0G', '轿车', '汽油', 17.98, '2025-03-01', 'Japan', 1),
  (2, 2, 'Honda', 102, 'Accord', 'Accord 260TURBO', '轿车', '汽油', 18.98, '2025-04-12', 'Japan', 1),
  (3, 3, 'BYD', 103, 'Han', 'Han EV Champion', '轿车', '纯电动', 20.98, '2025-02-20', 'China', 1),
  (4, 4, 'Tesla', 104, 'Model 3', 'Model 3 Long Range', '轿车', '纯电动', 28.59, '2025-01-15', 'United States', 1),
  (5, 5, 'BMW', 105, '3 Series', '325Li M Sport', '轿车', '汽油', 32.99, '2024-11-08', 'Germany', 1),
  (6, 6, 'Mercedes-Benz', 106, 'C-Class', 'C 260 L', '轿车', '混合动力', 35.68, '2024-10-18', 'Germany', 1),
  (7, 7, 'Audi', 107, 'A4L', 'A4L 40 TFSI', '轿车', '汽油', 32.18, '2024-09-26', 'Germany', 1),
  (8, 8, 'Li Auto', 108, 'L7', 'L7 Max', 'SUV', '增程式', 37.98, '2025-03-08', 'China', 1),
  (9, 9, 'NIO', 109, 'ES6', 'ES6 75kWh', 'SUV', '纯电动', 33.80, '2025-02-15', 'China', 1),
  (10, 10, 'Geely', 110, 'Xingyue L', 'Xingyue L AWD', 'SUV', '混合动力', 18.52, '2024-12-01', 'China', 1),
  (11, 11, 'Great Wall', 111, 'Poer', 'Poer Diesel 4WD', '皮卡', '柴油', 16.28, '2024-08-18', 'China', 1),
  (12, 12, 'Volkswagen', 112, 'Passat', 'Passat 330TSI', '轿车', '汽油', 19.29, '2024-07-10', 'Germany', 1)
ON DUPLICATE KEY UPDATE
  brand_name = VALUES(brand_name),
  model_name = VALUES(model_name),
  price = VALUES(price),
  is_on_sale = VALUES(is_on_sale);

INSERT INTO user_behavior
  (behavior_id, user_id, session_id, car_id, behavior_type, source, keyword, timestamp, create_time)
SELECT
  CONCAT('demo_', u.n, '_', c.car_id, '_', b.behavior_type),
  CONCAT('user_', LPAD(u.n, 4, '0')),
  CONCAT('session_', u.n),
  c.car_id,
  b.behavior_type,
  'demo',
  CASE WHEN b.behavior_type = 'search' THEN c.brand_name ELSE '' END,
  UNIX_TIMESTAMP(NOW()) * 1000,
  NOW()
FROM car_info c
CROSS JOIN (SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) u
CROSS JOIN (
  SELECT 'browse' behavior_type
  UNION ALL SELECT 'collect'
  UNION ALL SELECT 'search'
  UNION ALL SELECT 'consult'
) b;

INSERT INTO realtime_stats
  (stats_type, target_id, target_name, car_type, fuel_type, pv, uv, search_count, consult_count, collect_count, compare_count, stats_date, stats_hour, stats_minute)
SELECT
  CONCAT('beh_', b.behavior_type),
  c.brand_id,
  c.brand_name,
  c.car_type,
  c.fuel_type,
  40 + c.car_id * 3 + h.hour_value,
  12 + c.car_id,
  CASE WHEN b.behavior_type = 'search' THEN 8 + c.car_id ELSE 0 END,
  CASE WHEN b.behavior_type = 'consult' THEN 5 + c.car_id ELSE 0 END,
  CASE WHEN b.behavior_type = 'collect' THEN 4 + c.car_id ELSE 0 END,
  CASE WHEN b.behavior_type = 'compare' THEN 3 + c.car_id ELSE 0 END,
  CURDATE(),
  h.hour_value,
  '00'
FROM car_info c
CROSS JOIN (
  SELECT 'browse' behavior_type
  UNION ALL SELECT 'collect'
  UNION ALL SELECT 'search'
  UNION ALL SELECT 'consult'
  UNION ALL SELECT 'compare'
) b
CROSS JOIN (
  SELECT 8 hour_value
  UNION ALL SELECT 10
  UNION ALL SELECT 12
  UNION ALL SELECT 14
  UNION ALL SELECT 16
  UNION ALL SELECT 18
  UNION ALL SELECT 20
) h;

INSERT INTO realtime_price_stats
  (stat_hour, window_start, window_end, brand_id, brand_name, car_type,
   avg_original_price, avg_quoted_price, avg_discount_rate, quote_count,
   promotion_count, top_promotion, price_change_reason)
SELECT
  DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'),
  DATE_SUB(NOW(), INTERVAL 10 MINUTE),
  NOW(),
  car_id,
  brand_name,
  car_type,
  price,
  ROUND(price * (0.86 + MOD(car_id, 10) * 0.01), 2),
  0.86 + MOD(car_id, 10) * 0.01,
  20 + car_id,
  CASE WHEN MOD(car_id, 3) = 0 THEN 0 ELSE 2 END,
  CASE MOD(car_id, 5)
    WHEN 0 THEN 'Limited-time discount 2 x 10k CNY'
    WHEN 1 THEN '3 years of free maintenance'
    WHEN 2 THEN 'Purchase tax waived'
    WHEN 3 THEN 'Finance subsidy 5k CNY'
    ELSE NULL
  END,
  CASE MOD(car_id, 5)
    WHEN 0 THEN '促销活动'
    WHEN 1 THEN '金融优惠'
    WHEN 2 THEN '官降'
    WHEN 3 THEN '置换补贴'
    ELSE '节日特惠'
  END
FROM car_info;

INSERT INTO realtime_loan_stats
  (stat_hour, window_start, window_end, brand_id, car_type, loan_type,
   avg_car_price, avg_loan_amount, avg_interest_rate, avg_monthly_payment,
   inquiry_count, approval_rate, avg_credit_score)
SELECT
  DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'),
  DATE_SUB(NOW(), INTERVAL 10 MINUTE),
  NOW(),
  c.brand_id,
  c.car_type,
  l.loan_type,
  c.price,
  ROUND(c.price * 0.72, 2),
  3.8 + MOD(c.car_id, 4) * 0.45,
  ROUND(c.price * 10000 * 0.72 / 60, 2),
  10 + c.car_id,
  18 + MOD(c.car_id * 5, 45),
  620 + c.car_id * 7
FROM car_info c
CROSS JOIN (
  SELECT '商业贷款' loan_type
  UNION ALL SELECT '信用卡分期'
  UNION ALL SELECT '汽车金融'
  UNION ALL SELECT '银行直贷'
  UNION ALL SELECT '融资租赁'
) l;

INSERT INTO search_log (user_id, session_id, keyword, search_type, timestamp)
VALUES
  ('user_0001', 'session_1', 'Toyota Camry', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0002', 'session_2', 'BYD Han EV', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0003', 'session_3', 'Tesla Model 3', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0004', 'session_4', 'BMW 3 Series', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0005', 'session_5', 'Li Auto L7', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0001', 'session_1', 'Family SUV', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0002', 'session_2', 'Electric sedan', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0003', 'session_3', 'Hybrid SUV', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0004', 'session_4', 'Luxury sedan', 'general', UNIX_TIMESTAMP(NOW()) * 1000),
  ('user_0005', 'session_5', 'NIO ES6', 'general', UNIX_TIMESTAMP(NOW()) * 1000);

INSERT INTO operation_log
  (operator_name, operation_type, operation_module, operation_desc, request_method,
   request_url, response_code, response_msg, status, execution_time, ip_address)
VALUES
  ('admin', 'POST_auth', 'auth', 'POST /api/v1/auth/login', 'POST', '/api/v1/auth/login', '200', 'success', 1, 18, '127.0.0.1'),
  ('admin', 'GET_dashboard', 'dashboard', 'GET /api/v1/dashboard/overview', 'GET', '/api/v1/dashboard/overview', '200', 'success', 1, 12, '127.0.0.1'),
  ('system', 'GET_market', 'market', 'GET /api/v1/market/brand-rank', 'GET', '/api/v1/market/brand-rank', '200', 'success', 1, 25, '127.0.0.1'),
  ('system', 'POST_recommendation', 'recommendation', 'Generate recommendations', 'POST', '/api/v1/recommendation/generate', '200', 'success', 1, 140, '127.0.0.1'),
  ('admin', 'PUT_config', 'admin', 'Update system configuration', 'PUT', '/api/v1/admin/config', '200', 'success', 1, 31, '127.0.0.1');

INSERT INTO daily_stats
  (stats_type, target_id, target_name, pv, uv, search_count, consult_count,
   collect_count, compare_count, order_count, conversion_rate, stats_date)
SELECT
  stats_type,
  target_id,
  target_name,
  SUM(pv),
  SUM(uv),
  SUM(search_count),
  SUM(consult_count),
  SUM(collect_count),
  SUM(compare_count),
  0,
  0,
  stats_date
FROM realtime_stats
GROUP BY stats_type, target_id, target_name, stats_date;

INSERT INTO region_brand_rank (brand_id, brand_name, pv, uv, rank_pos, stats_date)
SELECT brand_id, brand_name, pv, uv,
       ROW_NUMBER() OVER (ORDER BY pv DESC), CURDATE()
FROM (
  SELECT target_id AS brand_id, target_name AS brand_name, SUM(pv) AS pv, SUM(uv) AS uv
  FROM realtime_stats
  WHERE stats_type LIKE 'beh_%'
  GROUP BY target_id, target_name
) ranked
LIMIT 5;

INSERT INTO market_share (brand_id, brand_name, pv, share_pct, stats_date)
SELECT brand_id, brand_name, pv,
       ROUND(pv * 100.0 / SUM(pv) OVER (), 2),
       CURDATE()
FROM (
  SELECT target_id AS brand_id, target_name AS brand_name, SUM(pv) AS pv
  FROM realtime_stats
  WHERE stats_type LIKE 'beh_%'
  GROUP BY target_id, target_name
) totals;

INSERT INTO keyword_stats (keyword, search_count, unique_users, stats_date)
SELECT keyword, COUNT(*), COUNT(DISTINCT user_id), CURDATE()
FROM search_log
GROUP BY keyword;

INSERT INTO price_war_alert
  (brand_id, brand_name, car_type, avg_discount_7d, avg_discount_14d,
   discount_change, alert_level, stats_date)
SELECT brand_id, brand_name, car_type,
       avg_discount_rate,
       avg_discount_rate,
       ROUND(avg_discount_rate * 100, 2),
       CASE
         WHEN avg_discount_rate >= 0.93 THEN 'high'
         WHEN avg_discount_rate >= 0.89 THEN 'medium'
         ELSE 'normal'
       END,
       CURDATE()
FROM realtime_price_stats;

INSERT INTO price_change_reason_stats
  (price_change_reason, occurrence_count, avg_discount, affected_quotes, stats_date)
SELECT price_change_reason, COUNT(*), AVG(avg_discount_rate), SUM(quote_count), CURDATE()
FROM realtime_price_stats
WHERE price_change_reason IS NOT NULL
GROUP BY price_change_reason;

INSERT INTO fuel_type_trend (fuel_type, pv, uv, stats_date)
SELECT fuel_type, SUM(pv), SUM(uv), CURDATE()
FROM realtime_stats
WHERE fuel_type IS NOT NULL AND fuel_type != ''
GROUP BY fuel_type;

INSERT INTO new_trending
  (car_id, brand_id, brand_name, series_name, model_name, car_type, fuel_type,
   price, hot_score, total_pv, total_uv, total_collect, total_consult, stats_date)
SELECT
  c.car_id, c.brand_id, c.brand_name, c.series_name, c.model_name,
  c.car_type, c.fuel_type, c.price,
  ROUND(COALESCE(s.pv, 0) * 0.4 + COALESCE(s.uv, 0) * 0.3 +
        COALESCE(s.collect_count, 0) * 0.2 + COALESCE(s.consult_count, 0) * 0.1, 2),
  COALESCE(s.pv, 0), COALESCE(s.uv, 0),
  COALESCE(s.collect_count, 0), COALESCE(s.consult_count, 0),
  CURDATE()
FROM car_info c
LEFT JOIN (
  SELECT target_name, SUM(pv) AS pv, SUM(uv) AS uv,
         SUM(collect_count) AS collect_count, SUM(consult_count) AS consult_count
  FROM realtime_stats
  WHERE stats_type LIKE 'beh_%'
  GROUP BY target_name
) s ON c.brand_name = s.target_name;

INSERT INTO user_profile
  (user_id, preference_brand, preference_type, preference_price_min,
   preference_price_max, preference_fuel, tag_list, score)
VALUES
  ('user_0001', '["Toyota","Honda"]', '["轿车"]', 15, 25, '汽油', '["family","practical"]', 88),
  ('user_0002', '["BYD","Tesla"]', '["轿车"]', 18, 32, '纯电动', '["technology","electric"]', 92),
  ('user_0003', '["Li Auto","NIO"]', '["SUV"]', 25, 40, '增程式', '["family","premium"]', 86),
  ('user_0004', '["BMW","Mercedes-Benz","Audi"]', '["轿车"]', 30, 45, '汽油', '["luxury","performance"]', 95),
  ('user_0005', '["Geely","Volkswagen"]', '["SUV","轿车"]', 12, 22, '混合动力', '["value","commuter"]', 79)
ON DUPLICATE KEY UPDATE score = VALUES(score);

INSERT INTO recommendation
  (user_id, car_id, rec_type, rec_position, score, reason, reason_type, status)
SELECT
  CONCAT('user_', LPAD(u.n, 4, '0')),
  c.car_id,
  CASE MOD(c.rn, 3)
    WHEN 0 THEN 'collaborative'
    WHEN 1 THEN 'content_based'
    ELSE 'hot'
  END,
  c.rn,
  ROUND(9.9 - c.rn * 0.45, 4),
  CONCAT('Recommended for ', c.brand_name, ' preference'),
  CASE MOD(c.rn, 3)
    WHEN 0 THEN 'similar'
    WHEN 1 THEN 'brand_match'
    ELSE 'hot'
  END,
  MOD(u.n + c.rn, 4)
FROM (SELECT 1 n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5) u
JOIN (
  SELECT car_id, brand_name, ROW_NUMBER() OVER (ORDER BY car_id) AS rn
  FROM car_info
  WHERE is_on_sale = 1
  LIMIT 10
) c
ON c.rn <= 8;
