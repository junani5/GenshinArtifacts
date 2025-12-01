import random
import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm  # 진행률 표시바 (있어 보임)

# ==========================================
# [1] 설정 및 상수 정의 (Game Rules)
# ==========================================

# DB 연결 정보 (본인 환경에 맞게 수정 필수!)
DB_USER = 'root'  # MySQL 아이디
DB_PASS = 'kms050426!'  # MySQL 비밀번호
DB_HOST = 'localhost'  # 주소
DB_PORT = '3306'  # 포트
DB_NAME = 'genshin_project'

# 원신 데이터 상수
SETS = [
    'Crimson Witch of Flames',  # 마녀
    'Emblem of Severed Fate',  # 절연
    'Deepwood Memories',  # 숲의 기억
    'Gilded Dreams',  # 도금
    'Noblesse Oblige',  # 왕실
    'Viridescent Venerer'  # 청록
]

SLOTS = ['Flower', 'Plume', 'Sands', 'Goblet', 'Circlet']

# 부위별 등장 가능한 주옵션 (현실성 반영)
MAIN_STATS_RULE = {
    'Flower': ['HP_Flat'],
    'Plume': ['ATK_Flat'],
    'Sands': ['HP%', 'ATK%', 'DEF%', 'EM', 'ER'],
    'Goblet': ['Pyro_DMG', 'Hydro_DMG', 'Dendro_DMG', 'HP%', 'ATK%', 'DEF%', 'EM'],
    'Circlet': ['Crit_Rate', 'Crit_DMG', 'HP%', 'ATK%', 'DEF%', 'Healing_Bonus', 'EM']
}

# 부옵션 컬럼 리스트 (DB 컬럼명과 일치해야 함)
SUB_STATS_LIST = [
    'Sub_HP_Flat', 'Sub_HP_Pct',
    'Sub_ATK_Flat', 'Sub_ATK_Pct',
    'Sub_DEF_Flat', 'Sub_DEF_Pct',
    'Sub_Crit_Rate', 'Sub_Crit_DMG',
    'Sub_EM', 'Sub_ER'
]


# ==========================================
# [2] 데이터 생성 로직 (Generator)
# ==========================================

def generate_dummy_data(num_rows):
    data_list = []

    print(f"🚀 {num_rows}개의 성유물 데이터 생성을 시작합니다...")

    for _ in tqdm(range(num_rows)):  # tqdm으로 진행률 표시
        # 1. 기본 정보 랜덤 결정
        chosen_set = random.choice(SETS)
        chosen_slot = random.choice(SLOTS)

        # 2. 부위에 맞는 주옵션 결정 (규칙 적용)
        possible_mains = MAIN_STATS_RULE[chosen_slot]
        chosen_main = random.choice(possible_mains)

        # 3. 부옵션 4개 랜덤 선정 (중복 없이)
        # (심화: 주옵션과 똑같은 부옵션은 제외해야 하지만, 과제용으론 단순 랜덤도 OK)
        chosen_subs = random.sample(SUB_STATS_LIST, 4)

        # 4. 딕셔너리 생성 (Row Data)
        row = {
            'Set_Name': chosen_set,
            'Slot': chosen_slot,
            'Main_Stat': chosen_main,
            'Level': random.randint(0, 20),  # 0~20강 랜덤
            'Rarity': 5
        }

        # 5. 모든 부옵션 컬럼을 0으로 초기화
        for sub in SUB_STATS_LIST:
            row[sub] = 0.0

        # 6. 선택된 4개 부옵션에만 수치 부여
        for sub in chosen_subs:
            val = 0.0
            # 대략적인 수치 범위 설정 (현실성)
            if 'Crit' in sub:
                val = round(random.uniform(2.7, 7.8) * random.randint(1, 5), 1)  # 치명타
            elif 'Pct' in sub or 'ER' in sub:
                val = round(random.uniform(4.1, 5.8) * random.randint(1, 5), 1)  # 퍼센트
            elif 'EM' in sub:
                val = round(random.uniform(16, 23) * random.randint(1, 5), 0)  # 원마
            else:
                val = round(random.uniform(16, 29) * random.randint(1, 5), 0)  # 깡스탯

            row[sub] = val

        data_list.append(row)

    return pd.DataFrame(data_list)


# ==========================================
# [3] DB 적재 로직 (ETL)
# ==========================================

def upload_to_db(df):
    # SQLAlchemy 연결 엔진 생성
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(db_url)

    print("💾 데이터베이스에 업로드 중... (시간이 조금 걸립니다)")

    try:
        # 'Artifacts' 테이블에 데이터 밀어넣기
        # chunksize: 한 번에 1000개씩 끊어서 전송 (메모리 절약)
        df.to_sql(name='Artifacts', con=engine, if_exists='append', index=False, chunksize=1000)
        print("✅ 업로드 완료! MySQL에서 확인해보세요.")

    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        print("Tip: DB 연결 정보가 맞는지, 테이블이 생성되어 있는지 확인하세요.")


# ==========================================
# [4] 실행 부
# ==========================================

if __name__ == "__main__":
    # 1. 10만 개 데이터 생성
    target_count = 100000
    df_artifacts = generate_dummy_data(target_count)

    # 2. 데이터 미리보기 (검증)
    print("\n[생성된 데이터 미리보기]")
    print(df_artifacts.head())

    # 3. DB 업로드 실행
    upload_to_db(df_artifacts)