-- patch-dashboard.sql
-- One-off patch for databases created before the dashboard live-location feature.
-- mysql-init.sql only runs against a fresh volume, so already-running instances
-- need this applied manually:
--   mysql -h 127.0.0.1 -P 3306 -uroot -ptoor gps_tracker < api/v1/database/patch-dashboard.sql
--
-- Safe to re-run: every statement is idempotent.

USE `gps_tracker`;

-- Add locations.view / locations.create permissions if not already present,
-- and grant them to every role that already holds card_members.view / card_members.create
-- (the Super User role, seeded with every permission, picks these up automatically).
INSERT INTO `permissions` (`name`, `permission_key`, `description`, `status`)
SELECT 'View Locations', 'locations.view', 'Allows viewing live GPS locations of card members', 1
WHERE NOT EXISTS (SELECT 1 FROM `permissions` WHERE `permission_key` = 'locations.view');

INSERT INTO `permissions` (`name`, `permission_key`, `description`, `status`)
SELECT 'Create Locations', 'locations.create', 'Allows GPS devices to submit new location fixes', 1
WHERE NOT EXISTS (SELECT 1 FROM `permissions` WHERE `permission_key` = 'locations.create');

-- Grant the two new permissions to every role that already has card_members.view,
-- i.e. whatever roles were set up as "admin-like" for this app so far.
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT DISTINCT rp.role_id, p.id
FROM `role_permissions` rp
JOIN `permissions` existing ON existing.id = rp.permission_id AND existing.permission_key = 'card_members.view'
JOIN `permissions` p ON p.permission_key IN ('locations.view', 'locations.create')
WHERE NOT EXISTS (
    SELECT 1 FROM `role_permissions` rp2
    WHERE rp2.role_id = rp.role_id AND rp2.permission_id = p.id
);
