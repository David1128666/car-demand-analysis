CREATE DATABASE IF NOT EXISTS car_demand_analysis
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE car_demand_analysis;

CREATE TABLE IF NOT EXISTS sys_user (
  user_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL UNIQUE,
  password_hash VARCHAR(128) NOT NULL,
  nickname VARCHAR(100),
  role VARCHAR(20) NOT NULL DEFAULT 'user',
  email VARCHAR(128),
  phone VARCHAR(32),
  status TINYINT NOT NULL DEFAULT 1,
  last_login DATETIME,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS car_info (
  car_id BIGINT PRIMARY KEY,
  brand_id INT NOT NULL,
  brand_name VARCHAR(100) NOT NULL,
  series_id INT,
  series_name VARCHAR(100),
  model_name VARCHAR(200) NOT NULL,
  car_type VARCHAR(50),
  fuel_type VARCHAR(50),
  price DECIMAL(10,2),
  launch_date DATE,
  country VARCHAR(50),
  is_on_sale TINYINT NOT NULL DEFAULT 1,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS admin_added_cars (
  car_id BIGINT PRIMARY KEY,
  brand_name VARCHAR(100) NOT NULL,
  series_name VARCHAR(100),
  model_name VARCHAR(200) NOT NULL,
  car_type VARCHAR(50),
  fuel_type VARCHAR(50),
  price DECIMAL(10,2),
  launch_date DATE,
  is_on_sale TINYINT NOT NULL DEFAULT 1,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_behavior (
  behavior_id VARCHAR(64) PRIMARY KEY,
  user_id VARCHAR(64) NOT NULL,
  session_id VARCHAR(64),
  car_id BIGINT NOT NULL DEFAULT 0,
  behavior_type VARCHAR(30) NOT NULL,
  source VARCHAR(50),
  keyword VARCHAR(255),
  referrer_url VARCHAR(500),
  ip_address VARCHAR(64),
  user_agent VARCHAR(500),
  device_type VARCHAR(50),
  timestamp BIGINT,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_behavior_user (user_id),
  INDEX idx_behavior_car (car_id),
  INDEX idx_behavior_time (create_time)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_stats (
  stats_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stats_type VARCHAR(50) NOT NULL,
  target_id INT,
  target_name VARCHAR(100),
  car_type VARCHAR(50),
  fuel_type VARCHAR(50),
  pv BIGINT NOT NULL DEFAULT 0,
  uv BIGINT NOT NULL DEFAULT 0,
  search_count BIGINT NOT NULL DEFAULT 0,
  consult_count BIGINT NOT NULL DEFAULT 0,
  collect_count BIGINT NOT NULL DEFAULT 0,
  compare_count BIGINT NOT NULL DEFAULT 0,
  stats_date DATE NOT NULL,
  stats_hour INT NOT NULL,
  stats_minute VARCHAR(10) NOT NULL DEFAULT '00',
  INDEX idx_realtime_date (stats_date, stats_hour, stats_minute),
  INDEX idx_realtime_brand (target_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_price_stats (
  price_stat_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stat_hour VARCHAR(20) NOT NULL,
  window_start DATETIME,
  window_end DATETIME,
  brand_id INT,
  brand_name VARCHAR(100),
  car_type VARCHAR(50),
  avg_original_price DECIMAL(10,2),
  avg_quoted_price DECIMAL(10,2),
  avg_discount_rate DECIMAL(8,4),
  quote_count BIGINT NOT NULL DEFAULT 0,
  promotion_count BIGINT NOT NULL DEFAULT 0,
  top_promotion VARCHAR(255),
  price_change_reason VARCHAR(100),
  realtime_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_price_hour (stat_hour),
  INDEX idx_price_brand (brand_id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS realtime_loan_stats (
  loan_stat_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stat_hour VARCHAR(20) NOT NULL,
  window_start DATETIME,
  window_end DATETIME,
  brand_id INT,
  car_type VARCHAR(50),
  loan_type VARCHAR(50),
  avg_car_price DECIMAL(10,2),
  avg_loan_amount DECIMAL(10,2),
  avg_interest_rate DECIMAL(8,2),
  avg_monthly_payment DECIMAL(10,2),
  inquiry_count BIGINT NOT NULL DEFAULT 0,
  approval_rate DECIMAL(8,2),
  avg_credit_score DECIMAL(8,2),
  realtime_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_loan_hour (stat_hour)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS search_log (
  search_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64),
  session_id VARCHAR(64),
  keyword VARCHAR(255),
  search_type VARCHAR(50),
  timestamp BIGINT,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_search_keyword (keyword),
  INDEX idx_search_time (create_time)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS daily_stats (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  stats_type VARCHAR(50),
  target_id INT,
  target_name VARCHAR(100),
  pv BIGINT NOT NULL DEFAULT 0,
  uv BIGINT NOT NULL DEFAULT 0,
  search_count BIGINT NOT NULL DEFAULT 0,
  consult_count BIGINT NOT NULL DEFAULT 0,
  collect_count BIGINT NOT NULL DEFAULT 0,
  compare_count BIGINT NOT NULL DEFAULT 0,
  order_count BIGINT NOT NULL DEFAULT 0,
  conversion_rate DECIMAL(10,4) NOT NULL DEFAULT 0,
  stats_date DATE NOT NULL,
  INDEX idx_daily_date (stats_date)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS user_profile (
  profile_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL UNIQUE,
  preference_brand VARCHAR(500),
  preference_type VARCHAR(500),
  preference_price_min DECIMAL(10,2),
  preference_price_max DECIMAL(10,2),
  preference_fuel VARCHAR(200),
  tag_list VARCHAR(1000),
  score DECIMAL(10,2),
  update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recommendation (
  rec_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id VARCHAR(64) NOT NULL,
  car_id BIGINT NOT NULL,
  rec_type VARCHAR(30) NOT NULL,
  rec_position INT NOT NULL DEFAULT 0,
  score DECIMAL(10,4) NOT NULL DEFAULT 0,
  reason VARCHAR(255),
  reason_type VARCHAR(50),
  status TINYINT NOT NULL DEFAULT 0,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_recommendation (user_id, car_id),
  INDEX idx_recommendation_user (user_id, rec_position)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS recommendation_staging LIKE recommendation;

CREATE TABLE IF NOT EXISTS region_brand_rank (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  brand_id INT,
  brand_name VARCHAR(100),
  pv BIGINT,
  uv BIGINT,
  rank_pos INT,
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS market_share (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  brand_id INT,
  brand_name VARCHAR(100),
  pv BIGINT,
  share_pct DECIMAL(10,2),
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS keyword_stats (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  keyword VARCHAR(255),
  search_count BIGINT,
  unique_users BIGINT,
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS price_war_alert (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  brand_id INT,
  brand_name VARCHAR(100),
  car_type VARCHAR(50),
  avg_discount_7d DECIMAL(10,4),
  avg_discount_14d DECIMAL(10,4),
  discount_change DECIMAL(10,2),
  alert_level VARCHAR(20),
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS price_change_reason_stats (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  price_change_reason VARCHAR(100),
  occurrence_count BIGINT,
  avg_discount DECIMAL(10,4),
  affected_quotes BIGINT,
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS fuel_type_trend (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  fuel_type VARCHAR(50),
  pv BIGINT,
  uv BIGINT,
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS new_trending (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  car_id BIGINT,
  brand_id INT,
  brand_name VARCHAR(100),
  series_name VARCHAR(100),
  model_name VARCHAR(200),
  car_type VARCHAR(50),
  fuel_type VARCHAR(50),
  price DECIMAL(10,2),
  hot_score DECIMAL(10,2),
  total_pv BIGINT,
  total_uv BIGINT,
  total_collect BIGINT,
  total_consult BIGINT,
  stats_date DATE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS system_config (
  config_key VARCHAR(100) PRIMARY KEY,
  config_value VARCHAR(500) NOT NULL,
  config_type VARCHAR(30) NOT NULL DEFAULT 'string',
  config_group VARCHAR(50) NOT NULL DEFAULT 'general'
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS operation_log (
  log_id BIGINT PRIMARY KEY AUTO_INCREMENT,
  operator_id VARCHAR(64),
  operator_name VARCHAR(100),
  operation_type VARCHAR(100),
  operation_module VARCHAR(50),
  operation_desc VARCHAR(500),
  request_method VARCHAR(20),
  request_url VARCHAR(500),
  response_code VARCHAR(20),
  response_msg TEXT,
  status TINYINT DEFAULT 1,
  execution_time INT,
  ip_address VARCHAR(64),
  request_params TEXT,
  create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_log_module (operation_module),
  INDEX idx_log_time (create_time)
) ENGINE=InnoDB;

CREATE OR REPLACE VIEW v_car_full_info AS
SELECT
  car_id, brand_id, brand_name, series_id, series_name, model_name,
  car_type, fuel_type, price, launch_date, country, is_on_sale, create_time
FROM car_info
WHERE is_on_sale = 1;

CREATE OR REPLACE VIEW v_brand_popularity AS
SELECT
  target_id AS brand_id,
  target_name AS brand_name,
  SUM(uv) AS uv,
  SUM(pv) AS pv,
  SUM(search_count) AS search_count,
  SUM(consult_count) AS consult_count,
  SUM(collect_count) AS collect_count
FROM realtime_stats
WHERE stats_type LIKE 'beh_%'
GROUP BY target_id, target_name;

CREATE OR REPLACE VIEW v_user_behavior_stats AS
SELECT
  user_id,
  DATE(create_time) AS behavior_date,
  behavior_type,
  COUNT(*) AS behavior_count,
  COUNT(DISTINCT session_id) AS session_count,
  COUNT(DISTINCT car_id) AS car_count
FROM user_behavior
GROUP BY user_id, DATE(create_time), behavior_type;
