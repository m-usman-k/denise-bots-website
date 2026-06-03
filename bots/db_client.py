import mysql.connector
import json

class SharedDatabase:
    def __init__(self):
        self.host = "13.212.150.216"
        self.port = 3306
        self.user = "simpleprog"
        self.password = "jf83hj032fjkldsa"
        self.database = "simpleprog_db"
        self._init_db()

    def get_connection(self):
        return mysql.connector.connect(
            host=self.host, port=self.port,
            user=self.user, password=self.password,
            database=self.database
        )

    def _init_db(self):
        conn = self.get_connection()
        c = conn.cursor()
        
        # Tickets
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_active_tickets (
            channel_id BIGINT PRIMARY KEY,
            owner_id BIGINT,
            claimed_by BIGINT DEFAULT NULL,
            category_name VARCHAR(255)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_nicknames (
            user_id BIGINT PRIMARY KEY,
            nickname VARCHAR(255)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_counts (
            category_name VARCHAR(255) PRIMARY KEY,
            count INT DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_settings (
            guild_id BIGINT PRIMARY KEY,
            ticket_category_id BIGINT,
            transcript_channel_id BIGINT,
            ticket_panel_channel_id BIGINT,
            ticket_panel_message_id BIGINT,
            use_dropdown INT DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS ticket_config (
            type VARCHAR(50),
            name VARCHAR(255),
            data JSON,
            PRIMARY KEY (type, name)
        )''')

        # Donations
        c.execute('''CREATE TABLE IF NOT EXISTS don_categories (
            guild_id BIGINT, name VARCHAR(255), PRIMARY KEY (guild_id, name)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS don_settings (
            guild_id BIGINT PRIMARY KEY, log_channel_id BIGINT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS don_managers (
            guild_id BIGINT, role_id BIGINT, PRIMARY KEY (guild_id, role_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS don_leaderboards (
            guild_id BIGINT, category_name VARCHAR(255), channel_id BIGINT, message_id BIGINT,
            PRIMARY KEY (guild_id, category_name)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS don_autoroles (
            guild_id BIGINT, category_name VARCHAR(255), threshold INT, role_id BIGINT,
            PRIMARY KEY (guild_id, category_name, threshold, role_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS don_donations (
            guild_id BIGINT, user_id BIGINT, category_name VARCHAR(255), amount INT,
            PRIMARY KEY (guild_id, user_id, category_name)
        )''')

        # Giveaways
        c.execute('''CREATE TABLE IF NOT EXISTS gw_giveaways (
            message_id BIGINT PRIMARY KEY,
            data JSON
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS gw_entries (
            message_id BIGINT,
            user_id BIGINT,
            PRIMARY KEY (message_id, user_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS gw_role_entries (
            role_id BIGINT PRIMARY KEY,
            entries INT
        )''')

        # Reputation
        c.execute('''CREATE TABLE IF NOT EXISTS rep_users (
            user_id BIGINT PRIMARY KEY, points INT DEFAULT 0,
            daily_cooldown BIGINT DEFAULT 0, hf_cooldown BIGINT DEFAULT 0, dice_cooldown BIGINT DEFAULT 0
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS rep_admin_roles (
            guild_id BIGINT, role_id BIGINT, PRIMARY KEY (guild_id, role_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS rep_autoroles (
            guild_id BIGINT, role_id BIGINT, threshold INT, PRIMARY KEY (guild_id, role_id)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS rep_settings (
            guild_id BIGINT PRIMARY KEY, log_channel_id BIGINT
        )''')

        # Win Tracker
        c.execute('''CREATE TABLE IF NOT EXISTS wt_games (
            name VARCHAR(255) PRIMARY KEY
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS wt_wins (
            user_id BIGINT, game VARCHAR(255), amount INT,
            PRIMARY KEY (user_id, game)
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS wt_tiers (
            role_id BIGINT PRIMARY KEY, threshold INT
        )''')

        conn.commit()
        conn.close()

    # --- TICKET BOT ---
    def get_ticket_config(self):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM ticket_config")
        rows = c.fetchall()
        conn.close()
        config = {"categories": {}, "buttons": {}}
        for r in rows:
            if r["type"] == "category": config["categories"][r["name"]] = json.loads(r["data"])
            elif r["type"] == "button": config["buttons"][r["name"]] = json.loads(r["data"])
        return config

    def update_ticket_config_item(self, type_, name, data):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO ticket_config (type, name, data) VALUES (%s, %s, %s)", (type_, name, json.dumps(data)))
        conn.commit()
        conn.close()

    def delete_ticket_config_item(self, type_, name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM ticket_config WHERE type=%s AND name=%s", (type_, name))
        conn.commit()
        conn.close()

    def get_ticket_settings(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM ticket_settings WHERE guild_id=%s", (guild_id,))
        row = c.fetchone()
        conn.close()
        return row if row else {}

    def update_ticket_settings(self, guild_id, **kwargs):
        conn = self.get_connection()
        c = conn.cursor()
        for k, v in kwargs.items():
            c.execute(f"INSERT INTO ticket_settings (guild_id, {k}) VALUES (%s, %s) ON DUPLICATE KEY UPDATE {k}=VALUES({k})", (guild_id, v))
        conn.commit()
        conn.close()

    def get_active_tickets(self):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM ticket_active_tickets")
        rows = c.fetchall()
        conn.close()
        return rows

    def add_active_ticket(self, channel_id, owner_id, category_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO ticket_active_tickets (channel_id, owner_id, category_name) VALUES (%s, %s, %s)", (channel_id, owner_id, category_name))
        conn.commit()
        conn.close()

    def remove_active_ticket(self, channel_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM ticket_active_tickets WHERE channel_id=%s", (channel_id,))
        conn.commit()
        conn.close()

    def update_ticket_claimer(self, channel_id, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE ticket_active_tickets SET claimed_by=%s WHERE channel_id=%s", (user_id, channel_id))
        conn.commit()
        conn.close()

    def get_ticket_nickname(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT nickname FROM ticket_nicknames WHERE user_id=%s", (user_id,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else None

    def set_ticket_nickname(self, user_id, nickname):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO ticket_nicknames (user_id, nickname) VALUES (%s, %s)", (user_id, nickname))
        conn.commit()
        conn.close()

    def get_ticket_count(self, category_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT count FROM ticket_counts WHERE category_name=%s", (category_name,))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0

    def increment_ticket_count(self, category_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO ticket_counts (category_name, count) VALUES (%s, 1) ON DUPLICATE KEY UPDATE count=count+1", (category_name,))
        conn.commit()
        c.execute("SELECT count FROM ticket_counts WHERE category_name=%s", (category_name,))
        row = c.fetchone()
        conn.close()
        return row[0]

    def reset_ticket_counts(self, category_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE ticket_counts SET count=0 WHERE category_name=%s", (category_name,))
        conn.commit()
        conn.close()


    # --- DONATION BOT ---
    def get_donation_categories(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM don_categories WHERE guild_id=%s", (guild_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def create_donation_category(self, guild_id, name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO don_categories (guild_id, name) VALUES (%s, %s)", (guild_id, name))
        conn.commit()
        conn.close()

    def rename_donation_category(self, guild_id, old_name, new_name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE don_categories SET name=%s WHERE guild_id=%s AND name=%s", (new_name, guild_id, old_name))
        c.execute("UPDATE don_donations SET category_name=%s WHERE guild_id=%s AND category_name=%s", (new_name, guild_id, old_name))
        c.execute("UPDATE don_autoroles SET category_name=%s WHERE guild_id=%s AND category_name=%s", (new_name, guild_id, old_name))
        c.execute("UPDATE don_leaderboards SET category_name=%s WHERE guild_id=%s AND category_name=%s", (new_name, guild_id, old_name))
        conn.commit()
        conn.close()

    def reset_donations_category(self, guild_id, category):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE don_donations SET amount=0 WHERE guild_id=%s AND category_name=%s", (guild_id, category))
        conn.commit()
        conn.close()
        
    def reset_user_donations(self, guild_id, user_id, category):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("UPDATE don_donations SET amount=0 WHERE guild_id=%s AND user_id=%s AND category_name=%s", (guild_id, user_id, category))
        conn.commit()
        conn.close()

    def delete_donation_category(self, guild_id, name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM don_categories WHERE guild_id=%s AND name=%s", (guild_id, name))
        c.execute("DELETE FROM don_donations WHERE guild_id=%s AND category_name=%s", (guild_id, name))
        c.execute("DELETE FROM don_autoroles WHERE guild_id=%s AND category_name=%s", (guild_id, name))
        conn.commit()
        conn.close()

    def get_user_donation(self, guild_id, uid, category):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT amount FROM don_donations WHERE guild_id=%s AND user_id=%s AND category_name=%s", (guild_id, uid, category))
        row = c.fetchone()
        conn.close()
        return row[0] if row else 0

    def update_user_donation(self, guild_id, uid, category, amount):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO don_donations (guild_id, user_id, category_name, amount) VALUES (%s, %s, %s, %s)", (guild_id, uid, category, amount))
        conn.commit()
        conn.close()

    def add_manager(self, guild_id, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO don_managers (guild_id, role_id) VALUES (%s, %s)", (guild_id, role_id))
        conn.commit()
        conn.close()

    def get_managers(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT role_id FROM don_managers WHERE guild_id=%s", (guild_id,))
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

    def remove_manager(self, guild_id, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM don_managers WHERE guild_id=%s AND role_id=%s", (guild_id, role_id))
        conn.commit()
        conn.close()

    def set_don_logs(self, guild_id, channel_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO don_settings (guild_id, log_channel_id) VALUES (%s, %s)", (guild_id, channel_id))
        conn.commit()
        conn.close()

    def get_autoroles(self, guild_id, category):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM don_autoroles WHERE guild_id=%s AND category_name=%s", (guild_id, category))
        rows = c.fetchall()
        conn.close()
        return rows
        
    def add_autorole(self, guild_id, category, role_id, threshold):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO don_autoroles (guild_id, category_name, threshold, role_id) VALUES (%s, %s, %s, %s)", (guild_id, category, threshold, role_id))
        conn.commit()
        conn.close()
        
    def remove_autorole(self, guild_id, category, role_id, threshold):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM don_autoroles WHERE guild_id=%s AND category_name=%s AND threshold=%s AND role_id=%s", (guild_id, category, threshold, role_id))
        conn.commit()
        conn.close()
        
    def get_all_autoroles(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM don_autoroles WHERE guild_id=%s", (guild_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def get_donation_leaderboard(self, guild_id, category):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, amount FROM don_donations WHERE guild_id=%s AND category_name=%s ORDER BY amount DESC LIMIT 100", (guild_id, category))
        rows = c.fetchall()
        conn.close()
        return rows

    def get_guild_settings(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM don_settings WHERE guild_id=%s", (guild_id,))
        row = c.fetchone()
        conn.close()
        return row if row else {}


    # --- GIVEAWAY BOT ---
    def get_giveaways(self):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM gw_giveaways")
        rows = c.fetchall()
        conn.close()
        for r in rows:
            r["data"] = json.loads(r["data"])
        
        # Format it exactly as memory dict
        return {r["message_id"]: r["data"] for r in rows}

    def save_giveaway(self, message_id, data_dict):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO gw_giveaways (message_id, data) VALUES (%s, %s)", (message_id, json.dumps(data_dict)))
        conn.commit()
        conn.close()

    def delete_giveaway(self, message_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM gw_giveaways WHERE message_id=%s", (message_id,))
        c.execute("DELETE FROM gw_entries WHERE message_id=%s", (message_id,))
        conn.commit()
        conn.close()

    def get_giveaway_entries(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT message_id, user_id FROM gw_entries")
        rows = c.fetchall()
        conn.close()
        res = {}
        for mid, uid in rows:
            if mid not in res: res[mid] = []
            res[mid].append(uid)
        return res

    def add_giveaway_entry(self, message_id, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO gw_entries (message_id, user_id) VALUES (%s, %s)", (message_id, user_id))
        conn.commit()
        conn.close()

    def remove_giveaway_entry(self, message_id, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM gw_entries WHERE message_id=%s AND user_id=%s", (message_id, user_id))
        conn.commit()
        conn.close()

    def get_role_entries(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT role_id, entries FROM gw_role_entries")
        rows = c.fetchall()
        conn.close()
        return {r[0]: r[1] for r in rows}
        
    def update_role_entry(self, role_id, entries):
        conn = self.get_connection()
        c = conn.cursor()
        if entries == 0:
            c.execute("DELETE FROM gw_role_entries WHERE role_id=%s", (role_id,))
        else:
            c.execute("REPLACE INTO gw_role_entries (role_id, entries) VALUES (%s, %s)", (role_id, entries))
        conn.commit()
        conn.close()


    # --- REPUTATION BOT ---
    def _ensure_rep_user(self, c, user_id):
        c.execute("INSERT IGNORE INTO rep_users (user_id) VALUES (%s)", (user_id,))

    def get_user_data(self, user_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        self._ensure_rep_user(c, user_id)
        c.execute("SELECT * FROM rep_users WHERE user_id=%s", (user_id,))
        row = c.fetchone()
        conn.close()
        return row

    def set_rep_points(self, user_id, points):
        conn = self.get_connection()
        c = conn.cursor()
        self._ensure_rep_user(c, user_id)
        c.execute("UPDATE rep_users SET points=%s WHERE user_id=%s", (points, user_id))
        conn.commit()
        conn.close()

    def get_rep_leaderboard(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, points FROM rep_users ORDER BY points DESC LIMIT 100")
        rows = c.fetchall()
        conn.close()
        return rows

    def get_rank(self, user_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id FROM rep_users ORDER BY points DESC")
        rows = c.fetchall()
        conn.close()
        for i, (uid,) in enumerate(rows, 1):
            if uid == user_id:
                return i
        return "N/A"

    def get_rep_points(self, user_id):
        row = self.get_user_data(user_id)
        return row["points"] if row else 0

    def update_daily_cooldown(self, user_id, timestamp):
        conn = self.get_connection()
        c = conn.cursor()
        self._ensure_rep_user(c, user_id)
        c.execute("UPDATE rep_users SET daily_cooldown=%s WHERE user_id=%s", (timestamp, user_id))
        conn.commit()
        conn.close()

    def update_hf_cooldown(self, user_id, timestamp):
        conn = self.get_connection()
        c = conn.cursor()
        self._ensure_rep_user(c, user_id)
        c.execute("UPDATE rep_users SET hf_cooldown=%s WHERE user_id=%s", (timestamp, user_id))
        conn.commit()
        conn.close()

    def update_dice_cooldown(self, user_id, timestamp):
        conn = self.get_connection()
        c = conn.cursor()
        self._ensure_rep_user(c, user_id)
        c.execute("UPDATE rep_users SET dice_cooldown=%s WHERE user_id=%s", (timestamp, user_id))
        conn.commit()
        conn.close()

    def get_rep_admin_roles(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT role_id FROM rep_admin_roles WHERE guild_id=%s", (guild_id,))
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

    def add_rep_admin_role(self, guild_id, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO rep_admin_roles (guild_id, role_id) VALUES (%s, %s)", (guild_id, role_id))
        conn.commit()
        conn.close()

    def remove_rep_admin_role(self, guild_id, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM rep_admin_roles WHERE guild_id=%s AND role_id=%s", (guild_id, role_id))
        conn.commit()
        conn.close()

    def get_rep_autoroles(self, guild_id):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT role_id, threshold FROM rep_autoroles WHERE guild_id=%s", (guild_id,))
        rows = c.fetchall()
        conn.close()
        return rows

    def add_rep_autorole(self, guild_id, role_id, threshold):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO rep_autoroles (guild_id, role_id, threshold) VALUES (%s, %s, %s)", (guild_id, role_id, threshold))
        conn.commit()
        conn.close()

    def remove_rep_autorole(self, guild_id, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM rep_autoroles WHERE guild_id=%s AND role_id=%s", (guild_id, role_id))
        conn.commit()
        conn.close()

    def set_rep_logs(self, guild_id, channel_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO rep_settings (guild_id, log_channel_id) VALUES (%s, %s)", (guild_id, channel_id))
        conn.commit()
        conn.close()


    # --- WIN TRACKER BOT ---
    def get_game_list(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT name FROM wt_games")
        rows = [r[0] for r in c.fetchall()]
        conn.close()
        return rows

    def add_game(self, name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO wt_games (name) VALUES (%s)", (name,))
        conn.commit()
        conn.close()

    def remove_game(self, name):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM wt_games WHERE name=%s", (name,))
        c.execute("DELETE FROM wt_wins WHERE game=%s", (name,))
        conn.commit()
        conn.close()

    def get_wins(self):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT user_id, game, amount FROM wt_wins")
        rows = c.fetchall()
        conn.close()
        res = {}
        for uid, g, a in rows:
            u_str = str(uid)
            if u_str not in res: res[u_str] = {}
            res[u_str][g] = a
        return res

    def update_user_wins(self, user_id, game, delta):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT amount FROM wt_wins WHERE user_id=%s AND game=%s", (user_id, game))
        row = c.fetchone()
        current = row[0] if row else 0
        new_amt = max(0, current + delta)
        c.execute("REPLACE INTO wt_wins (user_id, game, amount) VALUES (%s, %s, %s)", (user_id, game, new_amt))
        conn.commit()
        conn.close()
        return new_amt

    def get_reward_tiers(self):
        conn = self.get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT role_id, threshold FROM wt_tiers")
        rows = c.fetchall()
        conn.close()
        return rows

    def add_reward_tier(self, role_id, threshold):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("REPLACE INTO wt_tiers (role_id, threshold) VALUES (%s, %s)", (role_id, threshold))
        conn.commit()
        conn.close()

    def remove_reward_tier(self, role_id):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("DELETE FROM wt_tiers WHERE role_id=%s", (role_id,))
        conn.commit()
        conn.close()
