-- MySQL용 스키마 (Genshin Artifact Project)
-- 파이썬 코드(generate_data.py, discord_bot.py)와 호환되는 버전입니다.

-- 1. 데이터베이스 생성 및 선택
CREATE DATABASE IF NOT EXISTS genshin_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE genshin_project;

-- 2. 성유물 테이블 (Artifacts)
-- 설명: 조회 성능 최적화를 위해 부옵션을 컬럼으로 펼친 'Wide Table' 구조 (반정규화)
DROP TABLE IF EXISTS Artifacts;
CREATE TABLE Artifacts (
    ArtifactID INT AUTO_INCREMENT PRIMARY KEY,
    Set_Name VARCHAR(50) NOT NULL,
    Slot VARCHAR(20) NOT NULL,
    Main_Stat VARCHAR(20) NOT NULL,
    Level INT DEFAULT 20,
    Rarity INT DEFAULT 5,
    
    -- 부옵션 10종 데이터 (값이 없으면 0 처리)
    Sub_HP_Flat FLOAT DEFAULT 0,
    Sub_HP_Pct FLOAT DEFAULT 0,
    Sub_ATK_Flat FLOAT DEFAULT 0,
    Sub_ATK_Pct FLOAT DEFAULT 0,
    Sub_DEF_Flat FLOAT DEFAULT 0,
    Sub_DEF_Pct FLOAT DEFAULT 0,
    Sub_Crit_Rate FLOAT DEFAULT 0,
    Sub_Crit_DMG FLOAT DEFAULT 0,
    Sub_EM FLOAT DEFAULT 0,
    Sub_ER FLOAT DEFAULT 0,

    -- [성능 최적화] 자주 검색하는 조건에 대한 인덱스
    INDEX idx_slot_set (Slot, Set_Name),
    INDEX idx_main_stat (Main_Stat)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. 캐릭터별 가중치 테이블 (Character_Weights)
-- 설명: 특정 캐릭터가 어떤 스탯을 중요하게 여기는지 저장 (추천 알고리즘용)
DROP TABLE IF EXISTS Character_Weights;
CREATE TABLE Character_Weights (
    Character_Name VARCHAR(50) PRIMARY KEY,
    Preferred_Set VARCHAR(50),
    
    -- 가중치 점수 (예: 치확 2.0점, 원마 0.5점)
    W_HP_Pct FLOAT DEFAULT 0,
    W_ATK_Pct FLOAT DEFAULT 0,
    W_DEF_Pct FLOAT DEFAULT 0,
    W_Crit_Rate FLOAT DEFAULT 0,
    W_Crit_DMG FLOAT DEFAULT 0,
    W_EM FLOAT DEFAULT 0,
    W_ER FLOAT DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. 초기 필수 데이터 (Seed Data)
-- 설명: 봇이 작동하기 위해 필요한 최소한의 캐릭터 데이터
INSERT IGNORE INTO Character_Weights 
(Character_Name, Preferred_Set, W_HP_Pct, W_Crit_Rate, W_Crit_DMG, W_EM, W_ER)
VALUES 
('Raiden', 'Emblem of Severed Fate', 0, 2.0, 1.0, 0, 1.5),
('Nahida', 'Deepwood Memories', 0, 1.0, 1.0, 2.0, 0.5);