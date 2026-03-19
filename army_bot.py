import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import os

# ╔══════════════════════════════════════════╗
# ║         ARMY BOT | Meta RP               ║
# ║         Настройки и конфигурация         ║
# ╚══════════════════════════════════════════╝

TOKEN = os.getenv("TOKEN")

KADR_AUDIT_CHANNEL_ID = 1446272933805691078   # #кадровый-аудит
OTCHETY_CHANNEL_ID    = 1446272933805691078   # #личные-отчёты
SKLAD_CHANNEL_ID      = 1446272933805691078   # #отчёты-склад
REMINDER_CHANNEL_ID   = 1446272933805691078   # #напоминания

DAILY_REMINDER_HOUR = 18   # 21:00 МСК (UTC+3)
WEEKLY_REMINDER_DAY = 6    # Воскресенье

# ══════════════════════════════════════════════

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree


# ─── Запуск бота ───────────────────────────────

@bot.event
async def on_ready():
    await tree.sync()
    daily_reminder.start()
    weekly_reminder.start()
    print(f"✅ Бот {bot.user} запущен и готов к работе!")


# ─── Вспомогательная функция ───────────────────

def now_str():
    return datetime.datetime.now().strftime("%d.%m.%Y")


# ╔══════════════════════════════════════════╗
# ║             КАДРОВЫЙ АУДИТ              ║
# ╚══════════════════════════════════════════╝

@tree.command(name="принять", description="Принять нового бойца в ряды Army")
@app_commands.describe(
    кто_принял="Ваше имя и фамилия",
    новоприбывший="Имя и фамилия нового бойца",
    ранг="Выданный ранг",
    причина="Причина принятия"
)
async def prinyat(interaction: discord.Interaction, кто_принял: str, новоприбывший: str, ранг: str, причина: str):
    channel = bot.get_channel(KADR_AUDIT_CHANNEL_ID)

    embed = discord.Embed(title="📁 КАДРОВЫЙ АУДИТ | ARMY", color=0x2ecc71)
    embed.add_field(name="✅ Принял",         value=кто_принял,    inline=False)
    embed.add_field(name="🆕 Новоприбывший",  value=новоприбывший, inline=False)
    embed.add_field(name="🎖️ Выдан ранг",     value=ранг,          inline=False)
    embed.add_field(name="📝 Причина",        value=причина,       inline=False)
    embed.set_footer(text=f"📅 {now_str()}")

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Запись добавлена в кадровый аудит!", ephemeral=True)


@tree.command(name="повысить", description="Повышение или понижение бойца")
@app_commands.describe(
    боец="Имя и фамилия бойца",
    с_ранга="Текущий ранг",
    на_ранг="Новый ранг",
    кто_повысил="Ваше имя и фамилия",
    причина="Причина изменения",
    тип="Повышение или понижение"
)
@app_commands.choices(тип=[
    app_commands.Choice(name="⬆️ Повышение", value="up"),
    app_commands.Choice(name="⬇️ Понижение", value="down"),
])
async def povysit(interaction: discord.Interaction, боец: str, с_ранга: str, на_ранг: str, кто_повысил: str, причина: str, тип: str):
    channel = bot.get_channel(KADR_AUDIT_CHANNEL_ID)

    color = 0x3498db if тип == "up" else 0xe74c3c
    icon  = "⬆️ Повышен" if тип == "up" else "⬇️ Понижен"

    embed = discord.Embed(title="📁 КАДРОВЫЙ АУДИТ | ARMY", color=color)
    embed.add_field(name=icon,                   value=боец,                     inline=False)
    embed.add_field(name="🎖️ Изменение ранга",   value=f"{с_ранга} → {на_ранг}", inline=False)
    embed.add_field(name="✅ Решение принял",     value=кто_повысил,              inline=False)
    embed.add_field(name="📝 Причина",            value=причина,                  inline=False)
    embed.set_footer(text=f"📅 {now_str()}")

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Запись добавлена в кадровый аудит!", ephemeral=True)


# ╔══════════════════════════════════════════╗
# ║                 ОТЧЁТЫ                  ║
# ╚══════════════════════════════════════════╝

@tree.command(name="отчет", description="Отправить дневной или недельный отчёт")
@app_commands.describe(
    тип="Дневной или недельный",
    имя="Ваше имя и фамилия",
    звание="Ваше звание",
    поставки="Кол-во поставок",
    ограбления="Отбитых ограблений",
    ивенты="Участие в ивентах",
    столкновения="Боевых столкновений",
    примечание="Доп. информация или 'Нет'"
)
@app_commands.choices(тип=[
    app_commands.Choice(name="📋 Дневной",   value="daily"),
    app_commands.Choice(name="📊 Недельный", value="weekly"),
])
async def otchet(interaction: discord.Interaction, тип: str, имя: str, звание: str,
                 поставки: str, ограбления: str, ивенты: str, столкновения: str, примечание: str):
    channel = bot.get_channel(OTCHETY_CHANNEL_ID)
    now = datetime.datetime.now()

    if тип == "daily":
        title  = "📋 ДНЕВНОЙ ОТЧЁТ | ARMY"
        period = now.strftime("%d.%m.%Y")
        color  = 0x9b59b6
    else:
        week_start = (now - datetime.timedelta(days=now.weekday())).strftime("%d.%m.%Y")
        period = f"{week_start} — {now.strftime('%d.%m.%Y')}"
        title  = "📊 НЕДЕЛЬНЫЙ ОТЧЁТ | ARMY"
        color  = 0xf39c12

    embed = discord.Embed(title=title, color=color)
    embed.add_field(name="👤 Имя",               value=имя,          inline=True)
    embed.add_field(name="🎖️ Звание",             value=звание,       inline=True)
    embed.add_field(name="📅 Период",             value=period,       inline=False)
    embed.add_field(name="🚛 Поставок",           value=поставки,     inline=True)
    embed.add_field(name="🏪 Отбитых ограблений", value=ограбления,   inline=True)
    embed.add_field(name="🎯 Ивенты",             value=ивенты,       inline=True)
    embed.add_field(name="🔫 Столкновений",        value=столкновения, inline=True)
    embed.add_field(name="💬 Примечание",          value=примечание,   inline=False)

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Отчёт отправлен!", ephemeral=True)


@tree.command(name="склад", description="Отчёт по складу")
@app_commands.describe(
    предмет="Название предмета (напр: Heavy Sniper Corp)",
    количество="Количество (напр: 2шт)",
    остаток="Остаток на складе после операции (напр: 5шт)",
    принято="Принято за период (напр: 10шт)",
    отправлено="Отправлено за период (напр: 5шт)",
    ответственный="Ваше имя и фамилия"
)
async def sklad(interaction: discord.Interaction, предмет: str, количество: str, остаток: str, принято: str, отправлено: str, ответственный: str):
    channel = bot.get_channel(SKLAD_CHANNEL_ID)

    embed = discord.Embed(title="🏭 ОТЧЁТ СКЛАДА | ARMY", color=0xe67e22)
    embed.add_field(name="📅 Дата",              value=now_str(),        inline=False)
    embed.add_field(name="📦 Предмет",           value=предмет,          inline=True)
    embed.add_field(name="🔢 Количество",        value=количество,       inline=True)
    embed.add_field(name="🏪 Остаток на складе", value=остаток,          inline=False)
    embed.add_field(name="📥 Принято",           value=f"+{принято}",    inline=True)
    embed.add_field(name="📤 Отправлено",        value=f"-{отправлено}", inline=True)
    embed.add_field(name="👤 Ответственный",     value=ответственный,    inline=False)

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Отчёт склада отправлен!", ephemeral=True)


# ╔══════════════════════════════════════════╗
# ║            МАССОВЫЙ ОТЧЁТ СКЛАДА        ║
# ╚══════════════════════════════════════════╝

@tree.command(name="склад_масс", description="Массовый отчёт склада — несколько предметов сразу")
@app_commands.describe(
    предметы="Предметы через запятую (напр: Хилка-5, AK74-2, Патроны-200)",
    тип="Тип операции",
    ответственный="Ваше имя и фамилия"
)
@app_commands.choices(тип=[
    app_commands.Choice(name="📥 Приход",  value="in"),
    app_commands.Choice(name="📤 Расход",  value="out"),
    app_commands.Choice(name="🔧 Крафт",   value="craft"),
])
async def sklad_mass(interaction: discord.Interaction, предметы: str, тип: str, ответственный: str):
    channel = bot.get_channel(SKLAD_CHANNEL_ID)

    # Парсим строку предметов
    items = []
    for item in предметы.split(","):
        item = item.strip()
        if "-" in item:
            parts = item.rsplit("-", 1)
            items.append(f"• **{parts[0].strip()}** — {parts[1].strip()}")
        else:
            items.append(f"• {item}")

    icons = {"in": "📥 Приход", "out": "📤 Расход", "craft": "🔧 Крафт"}
    colors = {"in": 0x2ecc71, "out": 0xe74c3c, "craft": 0x3498db}

    embed = discord.Embed(title=f"🏭 ОТЧЁТ СКЛАДА | {icons[тип]}", color=colors[тип])
    embed.add_field(name="📅 Дата",          value=now_str(),          inline=True)
    embed.add_field(name="👤 Ответственный", value=ответственный,      inline=True)
    embed.add_field(name="📦 Предметы",      value="\n".join(items),   inline=False)
    embed.set_footer(text=f"Всего позиций: {len(items)}")

    await channel.send(embed=embed)
    await interaction.response.send_message("✅ Массовый отчёт склада отправлен!", ephemeral=True)


# ╔══════════════════════════════════════════╗
# ║              НАПОМИНАНИЯ                ║
# ╚══════════════════════════════════════════╝

@tasks.loop(hours=24)
async def daily_reminder():
    now = datetime.datetime.now(datetime.UTC)
    if now.hour == DAILY_REMINDER_HOUR:
        channel = bot.get_channel(REMINDER_CHANNEL_ID)
        if channel:
            await channel.send(
                "⏰ **Напоминание!**\n"
                "@everyone Не забудьте сдать **дневной отчёт**!\n"
                "Используй команду `/отчет` → 📋 Дневной"
            )

@tasks.loop(hours=24)
async def weekly_reminder():
    now = datetime.datetime.now(datetime.UTC)
    if now.weekday() == WEEKLY_REMINDER_DAY and now.hour == DAILY_REMINDER_HOUR:
        channel = bot.get_channel(REMINDER_CHANNEL_ID)
        if channel:
            await channel.send(
                "📊 **Конец недели!**\n"
                "@everyone Сдайте **недельный отчёт** до конца дня!\n"
                "Используй команду `/отчет` → 📊 Недельный"
            )

# ══════════════════════════════════════════════
bot.run(TOKEN)
