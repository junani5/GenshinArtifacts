import discord
from discord.ext import commands
import pymysql

# ==========================================
# [1] 설정 (Configuration)
# ==========================================

# 1-1. 디스코드 봇 토큰 (주의: 깃허브에 올릴 땐 지우고 올리세요!)
TOKEN = '..'

# 1-2. DB 연결 정보 (generate_data.py와 동일)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kms050426!',  # 본인 비밀번호 확인
    'db': 'genshin_project',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# [1-3] 봇 권한 설정 (수정됨)
intents = discord.Intents.default()
intents.message_content = True
intents.presences = True  # 👈 [중요] 상태 표시 권한 활성화
intents.members = True    # 👈 서버 멤버 목록 권한 활성화

# help_command=None은 !help 쳤을 때 기본 메시지 끄는 옵션 (깔끔하게 하려고)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# ==========================================
# [2] DB 헬퍼 함수
# ==========================================

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)


# ==========================================
# [3] 봇 명령어 구현
# ==========================================

@bot.event
async def on_ready():
    print(f'✅ {bot.user} (으)로 로그인 성공! 성유물 DB와 연결되었습니다.')


@bot.command(name='추천')
async def recommend(ctx, character_name: str, slot: str = 'Flower'):
    """
    사용법: !추천 <캐릭터이름> <부위>
    예시: !추천 Hu Tao Flower
    """

    # 1. 입력값 보정 (영어 대소문자 등)
    # 실제로는 한글 이름 매핑 로직이 있으면 좋지만, 지금은 영어 이름 그대로 사용

    print(f"🔍 [요청] 캐릭터: {character_name}, 부위: {slot}")

    # 2. SQL 쿼리 작성 (핵심 로직: 가중치 점수 계산)
    # 이 쿼리가 프로젝트의 '꽃'입니다. DB가 직접 계산하고 정렬합니다.
    sql = """
    SELECT 
        A.ArtifactID,
        A.Set_Name,
        A.Main_Stat,
        A.Level,
        -- 점수 계산 (DB 내부 연산)
        ROUND(
            (A.Sub_HP_Pct * W.W_HP_Pct) +
            (A.Sub_ATK_Pct * W.W_ATK_Pct) +
            (A.Sub_Crit_Rate * W.W_Crit_Rate) +
            (A.Sub_Crit_DMG * W.W_Crit_DMG) +
            (A.Sub_EM * W.W_EM) +
            (A.Sub_ER * W.W_ER)
        , 2) AS Score,

        -- 부옵션 정보 보여주기용
        A.Sub_HP_Pct, A.Sub_Crit_Rate, A.Sub_Crit_DMG, A.Sub_EM

    FROM Artifacts A
    JOIN Character_Weights W ON W.Character_Name = %s
    WHERE A.Slot = %s
    ORDER BY Score DESC
    LIMIT 5;
    """

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(sql, (character_name, slot))
            results = cursor.fetchall()

        conn.close()

        # 3. 결과가 없을 경우
        if not results:
            await ctx.send(f"❌ '{character_name}'에 대한 가중치 데이터가 없거나 성유물이 없습니다.")
            return

        # 4. 디스코드 Embed(예쁜 상자) 만들기
        embed = discord.Embed(
            title=f"🏆 {character_name} {slot} 추천 성유물 Top 5",
            description="DB 알고리즘이 계산한 최적의 성유물입니다.",
            color=0xFFD700  # 금색
        )

        for rank, row in enumerate(results, 1):
            # 내용 꾸미기
            content = (
                f"**세트:** {row['Set_Name']}\n"
                f"**주옵:** {row['Main_Stat']}\n"
                f"**주요 스탯:** 치확 {row['Sub_Crit_Rate']}% | 치피 {row['Sub_Crit_DMG']}%\n"
                f"**점수:** `{row['Score']}점`"
            )
            embed.add_field(name=f"#{rank}위 (ID: {row['ArtifactID']})", value=content, inline=False)

        embed.set_footer(text="Powered by MySQL & Python")
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"🔥 에러 발생: {str(e)}")
        print(e)


# 봇 실행
bot.run(TOKEN)