-- seed-demo.sql
-- Demo data for the Dashboard live-location feature: 2 branches under the
-- existing "JoyTree Software" organization, 6 GPS cards, 6 tracked employees
-- (3 per branch), and one initial location fix per card so the map isn't
-- empty on first load. Safe to run once against a freshly patched DB.
--
--   mysql -h 127.0.0.1 -P 3306 -uroot -ptoor gps_tracker < api/v1/database/seed-demo.sql
--
-- Pair with scripts/simulate_locations.py to watch the markers move.

USE `gps_tracker`;

-- 2 branches under org_id=1 (JoyTree Software), in Pune (city_id=36) and Mumbai (city_id=35),
-- both under Maharashtra (state_id=14) / India (country_id=1).
INSERT INTO `branches`
    (`org_id`, `name`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `is_head_office`, `mobile`, `status`)
VALUES
    (1, 'Pune HQ', '221B Baner Road', 'Pune', '411045', 1, 14, 36, 1, '9822000001', 1),
    (1, 'Mumbai Branch', '45 Andheri East', 'Mumbai', '400069', 1, 14, 35, 0, '9822000002', 1);

-- 6 GPS tracker cards
INSERT INTO `cards` (`name`, `imei_number`, `sim_mobile`, `company`, `model`, `status`)
VALUES
    ('Tracker Card 01', '868000010000001', '9911000001', 'Concox', 'GT06N', 1),
    ('Tracker Card 02', '868000010000002', '9911000002', 'Concox', 'GT06N', 1),
    ('Tracker Card 03', '868000010000003', '9911000003', 'Concox', 'GT06N', 1),
    ('Tracker Card 04', '868000010000004', '9911000004', 'Concox', 'GT06N', 1),
    ('Tracker Card 05', '868000010000005', '9911000005', 'Concox', 'GT06N', 1),
    ('Tracker Card 06', '868000010000006', '9911000006', 'Concox', 'GT06N', 1);

-- 3 employees at Pune HQ, each carrying one of cards 01-03
INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Rahul Deshmukh', 'rahul.deshmukh@example.com', '9822111001', b.id, 'Baner', 'Pune', '411045', 1, 14, 36, c.id, '9822999001', 1
FROM `branches` b, `cards` c WHERE b.name = 'Pune HQ' AND c.imei_number = '868000010000001';

INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Sneha Kulkarni', 'sneha.kulkarni@example.com', '9822111002', b.id, 'Kothrud', 'Pune', '411038', 1, 14, 36, c.id, '9822999002', 1
FROM `branches` b, `cards` c WHERE b.name = 'Pune HQ' AND c.imei_number = '868000010000002';

INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Amit Joshi', 'amit.joshi@example.com', '9822111003', b.id, 'Viman Nagar', 'Pune', '411014', 1, 14, 36, c.id, '9822999003', 1
FROM `branches` b, `cards` c WHERE b.name = 'Pune HQ' AND c.imei_number = '868000010000003';

-- 3 employees at Mumbai Branch, each carrying one of cards 04-06
INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Priya Shah', 'priya.shah@example.com', '9822111004', b.id, 'Andheri East', 'Mumbai', '400069', 1, 14, 35, c.id, '9822999004', 1
FROM `branches` b, `cards` c WHERE b.name = 'Mumbai Branch' AND c.imei_number = '868000010000004';

INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Vikram Rao', 'vikram.rao@example.com', '9822111005', b.id, 'Bandra West', 'Mumbai', '400050', 1, 14, 35, c.id, '9822999005', 1
FROM `branches` b, `cards` c WHERE b.name = 'Mumbai Branch' AND c.imei_number = '868000010000005';

INSERT INTO `card_members`
    (`name`, `email`, `mobile`, `branch_id`, `address_line_1`, `city`, `pincode`, `country_id`, `state_id`, `city_id`, `card_id`, `emergency_contact_1`, `status`)
SELECT 'Neha Patil', 'neha.patil@example.com', '9822111006', b.id, 'Powai', 'Mumbai', '400076', 1, 14, 35, c.id, '9822999006', 1
FROM `branches` b, `cards` c WHERE b.name = 'Mumbai Branch' AND c.imei_number = '868000010000006';

-- One initial location fix per card, scattered around each branch's city center
-- so the map has something to show before the simulator starts moving them.
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 18.5204, 73.8567, 0, 92, 0 FROM `cards` c WHERE c.imei_number = '868000010000001';
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 18.5089, 73.8260, 12, 78, 0 FROM `cards` c WHERE c.imei_number = '868000010000002';
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 18.5679, 73.9143, 0, 65, 0 FROM `cards` c WHERE c.imei_number = '868000010000003';
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 19.1136, 72.8697, 5, 88, 0 FROM `cards` c WHERE c.imei_number = '868000010000004';
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 19.0596, 72.8295, 0, 54, 0 FROM `cards` c WHERE c.imei_number = '868000010000005';
INSERT INTO `locations` (`card_id`, `lat`, `lng`, `speed`, `battery`, `sos_button_pressed`)
SELECT c.id, 19.1197, 72.9051, 18, 71, 0 FROM `cards` c WHERE c.imei_number = '868000010000006';
