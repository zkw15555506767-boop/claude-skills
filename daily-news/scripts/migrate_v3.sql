-- Daily News Database Migration V3
-- 新增 X/Twitter 推文专属字段 + WebSearch 信源支持

-- 1. items 表新增推文专属字段（可选列，非推文信源留空）
ALTER TABLE items ADD COLUMN author TEXT;
ALTER TABLE items ADD COLUMN likes INTEGER DEFAULT 0;
ALTER TABLE items ADD COLUMN views TEXT DEFAULT '0';
ALTER TABLE items ADD COLUMN full_text TEXT;       -- 推文原文（不截断）
ALTER TABLE items ADD COLUMN source_domain TEXT;   -- websearch 来源域名

-- 2. 更新 schema_version
INSERT INTO schema_version (version, applied_at, description)
VALUES (3, datetime('now'), 'Add Twitter/X fields and WebSearch domain field to items table');
