-- 01_schema.sql
CREATE SCHEMA IF NOT EXISTS csgo;
SET search_path TO csgo, public;
DO $$ BEGIN IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'listing_status') THEN DROP TYPE listing_status; END IF; END $$;
CREATE TYPE listing_status AS ENUM ('active', 'sold', 'cancelled');
CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL CHECK (length(username) BETWEEN 3 AND 32), email TEXT UNIQUE NOT NULL CHECK (position('@' in email) > 1), created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS weapons (id SERIAL PRIMARY KEY, name TEXT NOT NULL UNIQUE, wclass TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS skins (id SERIAL PRIMARY KEY, weapon_id INT NOT NULL REFERENCES weapons(id) ON DELETE RESTRICT, name TEXT NOT NULL, rarity TEXT NOT NULL, collection TEXT, UNIQUE (weapon_id, name));
CREATE TABLE IF NOT EXISTS items (id SERIAL PRIMARY KEY, skin_id INT NOT NULL REFERENCES skins(id) ON DELETE RESTRICT, owner_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, wear NUMERIC(6,5) NOT NULL CHECK (wear >= 0 AND wear <= 1), pattern INT CHECK (pattern BETWEEN 0 AND 1000), stattrak BOOLEAN NOT NULL DEFAULT FALSE, stickers JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS listings (id SERIAL PRIMARY KEY, item_id INT NOT NULL UNIQUE REFERENCES items(id) ON DELETE CASCADE, seller_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE, price NUMERIC(10,2) NOT NULL CHECK (price >= 0), currency TEXT NOT NULL DEFAULT 'USD', status listing_status NOT NULL DEFAULT 'active', created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE UNIQUE INDEX IF NOT EXISTS uniq_active_listing_per_item ON listings(item_id) WHERE status = 'active';
CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, listing_id INT NOT NULL REFERENCES listings(id) ON DELETE RESTRICT, buyer_id INT NOT NULL REFERENCES users(id) ON DELETE RESTRICT, price NUMERIC(10,2) NOT NULL CHECK (price >= 0), purchased_at TIMESTAMPTZ NOT NULL DEFAULT now());