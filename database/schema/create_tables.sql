PRAGMA foreign_keys = ON;

-- 캐릭터 기본 정보
CREATE TABLE IF NOT EXISTS Character (
    character_id INTEGER PRIMARY KEY,  --내부 캐릭터구분용
    name         TEXT NOT NULL UNIQUE
);

-- 성유물 부위(슬롯) 정의
CREATE TABLE IF NOT EXISTS ArtifactSlot (
    slot_id      INTEGER PRIMARY KEY,      -- 1~5 정도로
    code         TEXT NOT NULL UNIQUE,     -- 'flower', 'plume', 'sands', 'goblet', 'circlet'
    display_name TEXT NOT NULL             -- '꽃', '깃털', '모래시계', '성배', '왕관'
);

-- 성유물 세트 정보
CREATE TABLE IF NOT EXISTS ArtifactSet (
    set_id        INTEGER PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    rarity_min    INTEGER,
    rarity_max    INTEGER,
    two_piece_effect  TEXT,
    four_piece_effect TEXT
);

-- 스탯 타입 (HP%, 치확, 치피 등)
CREATE TABLE IF NOT EXISTS StatType (
    stat_id      INTEGER PRIMARY KEY,
    code         TEXT NOT NULL UNIQUE,   -- HP_FLAT, CRIT_RATE ...
    display_name TEXT NOT NULL,
    is_percentage INTEGER NOT NULL CHECK (is_percentage IN (0, 1))
);

-- 유저가 입력한 성유물 4개
CREATE TABLE IF NOT EXISTS UserArtifact (
    session_id      INTEGER NOT NULL,
    slot_id         INTEGER NOT NULL,      -- FK → ArtifactSlot
    set_id          INTEGER,               -- 나중에 세트까지 받으면
    main_stat_id    INTEGER NOT NULL,
    main_stat_value REAL,

    PRIMARY KEY (session_id, slot_id),  -- 한 세션에서 같은 부위 중복 방지
    FOREIGN KEY (session_id)   REFERENCES UserBuildSession(session_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id)      REFERENCES ArtifactSlot(slot_id),
    FOREIGN KEY (main_stat_id) REFERENCES StatType(stat_id),
    FOREIGN KEY (set_id)       REFERENCES ArtifactSet(set_id)
);

CREATE TABLE IF NOT EXISTS UserArtifactSubStat (
    session_id  INTEGER NOT NULL,
    slot_id     INTEGER NOT NULL,
    stat_id     INTEGER NOT NULL,
    value       REAL    NOT NULL,

    PRIMARY KEY (session_id, slot_id, stat_id),
    FOREIGN KEY (session_id, slot_id)
        REFERENCES UserArtifact(session_id, slot_id) ON DELETE CASCADE,
    FOREIGN KEY (stat_id) REFERENCES StatType(stat_id)
);

-- [중요] 추천 빌드 테이블(간단 버전이라도 있어야 FK가 안 터짐)
CREATE TABLE IF NOT EXISTS RecommendedBuild (
    build_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id  INTEGER NOT NULL,
    name          TEXT NOT NULL,

    FOREIGN KEY (character_id) REFERENCES Character(character_id)
);

CREATE TABLE UserBuildSession (
    session_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL,
    created_at   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS RecommendedMainStat (
    build_id  INTEGER NOT NULL,        -- FK → RecommendedBuild
    slot_id   INTEGER NOT NULL,        -- FK → ArtifactSlot
    stat_id   INTEGER NOT NULL,        -- FK → StatType
    is_mandatory INTEGER NOT NULL DEFAULT 1,  -- 꼭 이 메인옵이어야 하는지 (0/1)

    PRIMARY KEY (build_id, slot_id),
    FOREIGN KEY (build_id) REFERENCES RecommendedBuild(build_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id)  REFERENCES ArtifactSlot(slot_id),
    FOREIGN KEY (stat_id)  REFERENCES StatType(stat_id)
);

-- 빌드별 부옵 가중치
CREATE TABLE IF NOT EXISTS RecommendedSubStatWeight (
    build_id  INTEGER NOT NULL,
    stat_id   INTEGER NOT NULL,
    weight    REAL    NOT NULL,   -- 0.0 ~ 10.0

    PRIMARY KEY (build_id, stat_id),
    FOREIGN KEY (build_id) REFERENCES RecommendedBuild(build_id) ON DELETE CASCADE,
    FOREIGN KEY (stat_id)  REFERENCES StatType(stat_id)
);
