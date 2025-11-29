-- 1. 성유물 테이블: 고유 ID(artifact_id) 추가
-- [MySQL 버전] UserArtifact 테이블 생성
CREATE TABLE UserArtifact (
    artifact_id INTEGER NOT NULL AUTO_INCREMENT PRIMARY KEY, -- [수정] MySQL 문법
    session_id  INTEGER NOT NULL,
    slot_id     INTEGER NOT NULL,
    main_stat_id INTEGER NOT NULL,
    FOREIGN KEY (session_id) REFERENCES UserBuildSession(session_id)
    -- ...
);

-- 2. 부옵션 테이블: (session_id, slot_id) 대신 artifact_id 참조
CREATE TABLE UserArtifactSubStat (
    artifact_id INTEGER NOT NULL, -- [변경] 상위 테이블의 PK를 참조
    stat_id     INTEGER NOT NULL,
    value       REAL NOT NULL,
    PRIMARY KEY (artifact_id, stat_id), -- [변경] PK 구조 변경
    FOREIGN KEY (artifact_id) REFERENCES UserArtifact(artifact_id) ON DELETE CASCADE
);

-- =========================================================
-- [최종 수정본] artifact_id를 기준으로 정확하게 계산하는 버전
-- =========================================================

WITH ArtifactScore AS (
    SELECT 
        ua.artifact_id, -- [중요] 개별 성유물을 식별하기 위해 추가
        ua.session_id,
        ua.slot_id,
        ast.display_name AS slot_name,
        ua.main_stat_id,
        ua.set_id,
        
        -- [A] 메인 옵션 적합성 체크
        CASE 
            WHEN COALESCE(rms.is_mandatory, 0) = 1 AND rms.stat_id != ua.main_stat_id THEN 0
            ELSE 1
        END AS is_valid_main_stat,

        -- [B] 부 옵션 점수 계산
        (
            SELECT COALESCE(SUM(uass.value * rbw.weight), 0)
            FROM UserArtifactSubStat uass
            JOIN RecommendedSubStatWeight rbw 
              ON uass.stat_id = rbw.stat_id 
              AND rbw.build_id = @TARGET_BUILD_ID
            WHERE uass.artifact_id = ua.artifact_id -- [핵심 수정] ID로 1:1 매칭
        ) AS sub_stat_score

    FROM UserArtifact ua
    JOIN ArtifactSlot ast ON ua.slot_id = ast.slot_id
    LEFT JOIN RecommendedMainStat rms 
      ON ua.slot_id = rms.slot_id 
      AND rms.build_id = @TARGET_BUILD_ID
    WHERE ua.session_id = @CURRENT_SESSION_ID
)

SELECT 
    T.slot_name AS '부위',
    st.display_name AS '주옵션',
    sets.name AS '세트명',
    T.sub_stat_score AS '성유물 점수',
    
    (
        SELECT GROUP_CONCAT(CONCAT(sty.display_name, ': ', uass.value) SEPARATOR ', ')
        FROM UserArtifactSubStat uass
        JOIN StatType sty ON uass.stat_id = sty.stat_id
        WHERE uass.artifact_id = T.artifact_id -- [핵심 수정] ID로 조회
    ) AS '부옵션 상세'

FROM (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY slot_id 
            ORDER BY sub_stat_score DESC, set_id DESC
        ) as rn
    FROM ArtifactScore
    WHERE is_valid_main_stat = 1
) T
JOIN StatType st ON T.main_stat_id = st.stat_id
LEFT JOIN ArtifactSet sets ON T.set_id = sets.set_id
WHERE T.rn = 1
ORDER BY T.slot_id;