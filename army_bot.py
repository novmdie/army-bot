import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import asyncio

# ==================== НАСТРОЙКИ ====================
TOKEN = "MTQ4NDEyMDM3NDg1MjU4NzU0MA.GdXLSa.1ugsS4X5W7yvIVVWrpGqOTCUXOoMkyYv7F8yPo"  # Вставь токен сюда

# ID каналов — замени на свои
KADR_AUDIT_CHANNEL_ID = 123456789       # #кадровый-аудит
OTCHETY_CHANNEL_ID = 123456789          # #личные-отчёты
REMINDER_CHANNEL_ID = 123456789         # куда слать напоминания

# Время напоминаний (UTC, для МСК +3)
DAILY_REMINDER_HOUR = 18    # 21:00 МСК
WEEKLY_REMINDER_DAY = 6     # 0=Пн, 6=Вс
# ====================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    daily_reminder.start()
    weekly_reminder.start()
    print(f"✅ Бот {bot.user} запущен!")


# ==================== /принять ====================
@tree.command(name="принять", description="Принять нового бойца в ряды Army")
@app_commands.describe(
    кто_принял="Ваше имя и фамилия",
    новоприбывший="Имя и фамилия нового бойца",
    ранг="Выданный ранг",
    причина="Причина принятия"
)
async def prinyat(interaction: discord.Interaction, кто_принял: str, новоприбывший: str, ранг: str, причина: str):
    channel = bot.get_channel(KADR_AUDIT_CHANNEL_ID)
    now = datetime.datetime.now().strftime("%d.%m.%Y")

    embed = discord.Embed(
        title="📁 КАДРОВЫЙ АУДИТ | ARMY",
        color=0x2ecc71
    )
    embed.add_field(name="✅ Принял", value=кто_принял, inline=False)
    embed.add_field(name="🆕 Новоприбывший", value=новоприбывший, inline=False)
    embed.add_field(name="🎖️ Выдан ранг", value=ранг, inline=False)
    embed.add_field(name="📝 Причина", value=причина, inline=False)
    embed.set_footer(text=f"📅 {now}")

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Запись добавлена в кадровый аудит!", ephemeral=True)


# ==================== /повысить ====================
@tree.command(name="повысить", description="Повышение или понижение бойца")
@app_commands.describe(
    боец="Имя и фамилия бойца",
    с_ранга="Текущий ранг",
    на_ранг="Новый ранг",
    кто_повысил="Ваше имя и фамилия",
    причина="Причина повышения/понижения",
    тип="Повышение или понижение"
)
@app_commands.choices(тип=[
    app_commands.Choice(name="⬆️ Повышение", value="up"),
    app_commands.Choice(name="⬇️ Понижение", value="down"),
])
async def povysit(interaction: discord.Interaction, боец: str, с_ранга: str, на_ранг: str, кто_повысил: str, причина: str, тип: str):
    channel = bot.get_channel(KADR_AUDIT_CHANNEL_ID)
    now = datetime.datetime.now().strftime("%d.%m.%Y")

    color = 0x3498db if тип == "up" else 0xe74c3c
    icon = "⬆️ Повышен" if тип == "up" else "⬇️ Понижен"

    embed = discord.Embed(
        title="📁 КАДРОВЫЙ АУДИТ | ARMY",
        color=color
    )
    embed.add_field(name=icon, value=боец, inline=False)
    embed.add_field(name="🎖️ Изменение ранга", value=f"{с_ранга} → {на_ранг}", inline=False)
    embed.add_field(name="✅ Решение принял", value=кто_повысил, inline=False)
    embed.add_field(name="📝 Причина", value=причина, inline=False)
    embed.set_footer(text=f"📅 {now}")

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Запись добавлена в кадровый аудит!", ephemeral=True)


# ==================== /отчет ====================
@tree.command(name="отчет", description="Отправить дневной или недельный отчёт")
@app_commands.describe(
    тип="Дневной или недельный",
    имя="Ваше имя и фамилия",
    звание="Ваше звание",
    поставки="Кол-во поставок (напр: 2)",
    ограбления="Отбитых ограблений (напр: 1)",
    ивенты="Участие в ивентах (напр: учения)",
    столкновения="Боевых столкновений (напр: 1)",
    примечание="Доп. информация или 'Нет'"
)
@app_commands.choices(тип=[
    app_commands.Choice(name="📋 Дневной", value="daily"),
    app_commands.Choice(name="📊 Недельный", value="weekly"),
])
async def otchet(interaction: discord.Interaction, тип: str, имя: str, звание: str,
                 поставки: str, ограбления: str, ивенты: str, столкновения: str, примечание: str):
    channel = bot.get_channel(OTCHETY_CHANNEL_ID)
    now = datetime.datetime.now()

    if тип == "daily":
        title = "📋 ДНЕВНОЙ ОТЧЁТ | ARMY"
        period = now.strftime("%d.%m.%Y")
        color = 0x9b59b6
    else:
        week_start = (now - datetime.timedelta(days=now.weekday())).strftime("%d.%m.%Y")
        period = f"{week_start} — {now.strftime('%d.%m.%Y')}"
        title = "📊 НЕДЕЛЬНЫЙ ОТЧЁТ | ARMY"
        color = 0xf39c12

    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="👤 Имя", value=имя, inline=True)
    embed.add_field(name="🎖️ Звание", value=звание, inline=True)
    embed.add_field(name="📅 Период", value=period, inline=False)
    embed.add_field(name="🚛 Поставок", value=поставки, inline=True)
    embed.add_field(name="🏪 Отбитых ограблений", value=ограбления, inline=True)
    embed.add_field(name="🎯 Ивенты", value=ивенты, inline=True)
    embed.add_field(name="🔫 Столкновений", value=столкновения, inline=True)
    embed.add_field(name="💬 Примечание", value=примечание, inline=False)

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Отчёт отправлен!", ephemeral=True)


# ==================== НАПОМИНАНИЯ ====================
@tasks.loop(hours=24)
async def daily_reminder():
    now = datetime.datetime.utcnow()
    if now.hour == DAILY_REMINDER_HOUR:
        channel = bot.get_channel(REMINDER_CHANNEL_ID)
        if channel:
            await channel.send(
                "⏰ **Напоминание!**\n"
                "@everyone Не забудьте сдать **дневной отчёт**!\n"
                "Используй команду `/отчет` → Дневной 📋"
            )

@tasks.loop(hours=24)
async def weekly_reminder():
    now = datetime.datetime.utcnow()
    if now.weekday() == WEEKLY_REMINDER_DAY and now.hour == DAILY_REMINDER_HOUR:
        channel = bot.get_channel(REMINDER_CHANNEL_ID)
        if channel:
            await channel.send(
                "📊 **Конец недели!**\n"
                "@everyone Сдайте **недельный отчёт** до конца дня!\n"
                "Используй команду `/отчет` → Недельный 📊"
            )

bot.run(TOKEN)
