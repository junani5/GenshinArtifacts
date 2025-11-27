-- Genshin Artifact Optimizer Database Schema
-- This schema provides the foundation for storing character data,
-- artifact sets, and user inventory for the Discord bot.

-- Character table: Stores Genshin Impact character information
CREATE TABLE IF NOT EXISTS `CHARACTER` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    element VARCHAR(50) NOT NULL,
    weapon_type VARCHAR(50) NOT NULL,
    rarity INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Artifact Set table: Stores artifact set information
CREATE TABLE IF NOT EXISTS ARTIFACT_SET (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    two_piece_bonus TEXT,
    four_piece_bonus TEXT,
    max_rarity INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- User Inventory table: Stores user's artifacts
CREATE TABLE IF NOT EXISTS USER_INVENTORY (
    id INT AUTO_INCREMENT PRIMARY KEY,
    discord_user_id VARCHAR(50) NOT NULL,
    artifact_set_id INT NOT NULL,
    slot VARCHAR(50) NOT NULL COMMENT 'Flower, Plume, Sands, Goblet, Circlet',
    main_stat VARCHAR(50) NOT NULL,
    sub_stat_1 VARCHAR(50),
    sub_stat_1_value DECIMAL(10, 2),
    sub_stat_2 VARCHAR(50),
    sub_stat_2_value DECIMAL(10, 2),
    sub_stat_3 VARCHAR(50),
    sub_stat_3_value DECIMAL(10, 2),
    sub_stat_4 VARCHAR(50),
    sub_stat_4_value DECIMAL(10, 2),
    rarity INT NOT NULL DEFAULT 5,
    level INT NOT NULL DEFAULT 0,
    efficiency_score DECIMAL(5, 2) COMMENT 'Calculated sub-stat efficiency percentage',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (artifact_set_id) REFERENCES ARTIFACT_SET(id) ON DELETE CASCADE,
    INDEX idx_discord_user (discord_user_id),
    INDEX idx_artifact_set (artifact_set_id),
    INDEX idx_slot (slot)
);
