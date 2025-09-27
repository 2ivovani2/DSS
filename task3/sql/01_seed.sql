-- 02_seed.sql
SET search_path TO csgo, public;
INSERT INTO users (username, email) VALUES ('s1mple','s1mple@example.com'),('zonic','zonic@example.com'),('niko','niko@example.com') ON CONFLICT DO NOTHING;
INSERT INTO weapons (name, wclass) VALUES ('AK-47','Rifle'),('M4A4','Rifle'),('Desert Eagle','Pistol'),('Karambit','Knife') ON CONFLICT DO NOTHING;
WITH ak AS (SELECT id AS weapon_id FROM weapons WHERE name='AK-47'), m4 AS (SELECT id AS weapon_id FROM weapons WHERE name='M4A4'), deag AS (SELECT id AS weapon_id FROM weapons WHERE name='Desert Eagle'), knife AS (SELECT id AS weapon_id FROM weapons WHERE name='Karambit')
INSERT INTO skins (weapon_id,name,rarity,collection) VALUES ((SELECT weapon_id FROM ak),'Redline','Classified','The Phoenix Collection'),((SELECT weapon_id FROM ak),'Asiimov','Covert','Workshop Community'),((SELECT weapon_id FROM m4),'Howl','Contraband','N/A'),((SELECT weapon_id FROM deag),'Blaze','Classified','The Dust Collection'),((SELECT weapon_id FROM knife),'Doppler','Covert','Gamma') ON CONFLICT DO NOTHING;
WITH u1 AS (SELECT id AS uid FROM users WHERE username='s1mple'), u2 AS (SELECT id AS uid FROM users WHERE username='niko'), ak_redline AS (SELECT id AS sid FROM skins WHERE name='Redline'), m4_howl AS (SELECT id AS sid FROM skins WHERE name='Howl'), de_blaze AS (SELECT id AS sid FROM skins WHERE name='Blaze')
INSERT INTO items (skin_id, owner_id, wear, pattern, stattrak, stickers) VALUES ((SELECT sid FROM ak_redline),(SELECT uid FROM u1),0.12345,321,true,'[{"name":"Crown Foil","slot":1}]'),((SELECT sid FROM m4_howl),(SELECT uid FROM u2),0.45678,777,false,'[]'::jsonb),((SELECT sid FROM de_blaze),(SELECT uid FROM u1),0.02000,42,false,'[]'::jsonb);
WITH it AS (SELECT id FROM items LIMIT 1)
INSERT INTO listings (item_id, seller_id, price, currency, status)
VALUES ((SELECT id FROM it),(SELECT owner_id FROM items WHERE id=(SELECT id FROM it)),199.99,'USD','active') ON CONFLICT DO NOTHING;