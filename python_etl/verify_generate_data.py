import random
import pandas as pd
from tqdm import tqdm
import time

# ==========================================
# [1] 설정 및 상수 정의 (Game Rules)
# ==========================================

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

# 부위별 등장 가능한 주옵션 (현실성 반영 확인용)
MAIN_STATS_RULE = {
    'Flower': ['HP_Flat'],
    'Plume': ['ATK_Flat'],
    'Sands': ['HP%', 'ATK%', 'DEF%', 'EM', 'ER'],
    'Goblet': ['Pyro_DMG', 'Hydro_DMG', 'Dendro_DMG', 'HP%', 'ATK%', 'DEF%', 'EM'],
    'Circlet': ['Crit_Rate', 'Crit_DMG', 'HP%', 'ATK%', 'DEF%', 'Healing_Bonus', 'EM']
}

# 부옵션 컬럼 리스트
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

    print(f"🚀 [시뮬레이션] {num_rows}개의 성유물 데이터 생성을 시작합니다...")
    time.sleep(0.5)  # 사용자가 메시지를 읽을 시간 제공

    for _ in tqdm(range(num_rows), desc="데이터 생성 중"):
        # 1. 기본 정보 랜덤 결정
        chosen_set = random.choice(SETS)
        chosen_slot = random.choice(SLOTS)

        # 2. 부위에 맞는 주옵션 결정
        possible_mains = MAIN_STATS_RULE[chosen_slot]
        chosen_main = random.choice(possible_mains)

        # 3. 부옵션 4개 랜덤 선정
        chosen_subs = random.sample(SUB_STATS_LIST, 4)

        # 4. 행 데이터 생성
        row = {
            'Set_Name': chosen_set,
            'Slot': chosen_slot,
            'Main_Stat': chosen_main,
            'Level': random.randint(0, 20),
            'Rarity': 5
        }

        # 5. 부옵션 초기화 및 수치 부여
        for sub in SUB_STATS_LIST:
            row[sub] = 0.0  # 기본값 0

        for sub in chosen_subs:
            val = 0.0
            if 'Crit' in sub:
                val = round(random.uniform(2.7, 7.8) * random.randint(1, 5), 1)
            elif 'Pct' in sub or 'ER' in sub:
                val = round(random.uniform(4.1, 5.8) * random.randint(1, 5), 1)
            elif 'EM' in sub:
                val = round(random.uniform(16, 23) * random.randint(1, 5), 0)
            else:
                val = round(random.uniform(16, 29) * random.randint(1, 5), 0)
            row[sub] = val

        data_list.append(row)

    return pd.DataFrame(data_list)


# ==========================================
# [3] 데이터 검증 로직 (Verification)
# ==========================================

def verify_data_logic(df):
    print("\n" + "=" * 50)
    print("📊 데이터 무결성 및 로직 검증 리포트")
    print("=" * 50)

    # 1. 데이터 개수 확인
    print(f"\n1. 생성된 총 데이터 개수: {len(df):,}개")

    # 2. 컬럼 확인
    print("\n2. 생성된 컬럼 목록:")
    print(list(df.columns))

    # 3. 샘플 데이터 출력 (상위 5개)
    print("\n3. 상위 5개 데이터 미리보기:")
    # Pandas 출력 옵션 설정 (잘리지 않고 다 보이게)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(df.head())

    # 4. 로직 검증: 꽃(Flower)은 주옵션이 무조건 HP_Flat이어야 함
    print("\n4. 로직 검증 (Flower 부위 주옵션 테스트):")
    flower_mains = df[df['Slot'] == 'Flower']['Main_Stat'].unique()
    print(f"   👉 꽃 부위에서 발견된 주옵션 종류: {flower_mains}")

    if len(flower_mains) == 1 and flower_mains[0] == 'HP_Flat':
        print("   ✅ 검증 성공: 꽃은 HP_Flat만 존재합니다.")
    else:
        print("   ❌ 검증 실패: 꽃에 이상한 주옵션이 섞여 있습니다!")

    # 5. 로직 검증: 부옵션은 0이 아닌 값이 4개여야 함 (간단 체크)
    print("\n5. 로직 검증 (첫 번째 데이터 부옵션 개수):")
    sample_row = df.iloc[0]
    non_zero_subs = 0
    for col in SUB_STATS_LIST:
        if sample_row[col] > 0:
            non_zero_subs += 1
    print(f"   👉 0이 아닌 부옵션 개수: {non_zero_subs}개 (정상: 4개)")


# ==========================================
# [4] 실행 부
# ==========================================

if __name__ == "__main__":
    # 테스트를 위해 100개만 생성해봅니다. (나중에 100,000으로 변경)
    TEST_COUNT = 100

    # 1. 생성
    df_result = generate_dummy_data(TEST_COUNT)

    # 2. 검증 출력
    verify_data_logic(df_result)

    print("\n" + "=" * 50)
    print("💡 [안내] DB 연결 코드는 현재 비활성화 상태입니다.")
    print("   데이터가 정상적으로 생성되는 것을 확인했으므로,")
    print("   추후 SQL 테이블을 생성한 뒤 to_sql 부분을 주석 해제하세요.")
    print("=" * 50)

    # [옵션] 눈으로 보고 싶다면 CSV로 저장
    # df_result.to_csv('verify_result.csv', index=False)
    # print("   (참고: verify_result.csv 파일로도 저장되었습니다.)")