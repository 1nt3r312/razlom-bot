import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
from datetime import datetime
import os
from database import init_db, get_event_channel, set_event_channel
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')

MSK = pytz.timezone("Europe/Moscow")
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
scheduler = AsyncIOScheduler(timezone=MSK)

# Инициализация базы
init_db()

async def send_event_notification(guild_id, text: str):
    """Отправляет уведомление в канал сервера"""
    channel_id = get_event_channel(guild_id)
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send(text)

@bot.event
async def on_ready():
    print(f"✅ Razlom Bot {bot.user} запущен!")
    
    # Расписание для каждого сервера
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour="11,19,23", minute=30, timezone=MSK),
        args=["⚠ Разлом откроется через 30 минут!"]
    )
    
    scheduler.add_job(
        check_and_notify,
        CronTrigger(hour="11,19,23", minute=45, timezone=MSK),
        args=["⚠ Разлом откроется через 15 минут!"]
    )
    
    scheduler.add_job(
        check_and_notify, 
        CronTrigger(hour="12,20,0", minute=0, timezone=MSK),
        args=["🔥 Разлом открыт!"]
    )
    
    scheduler.start()

async def check_and_notify(text: str):
    """Проверяет все сервера и отправляет уведомления"""
    for guild in bot.guilds:
        await send_event_notification(guild.id, f"@everyone {text}")

@bot.command()
@commands.has_permissions(administrator=True)
async def уведомления(ctx, канал: discord.TextChannel = None):
    """🔔 Настроить канал для уведомлений"""
    if канал:
        set_event_channel(ctx.guild.id, канал.id)
        await ctx.send(f"✅ Уведомления будут приходить в {канал.mention}")
        
        # Тестовое уведомление
        await канал.send("🔔 **Тестовое уведомление** - Razlom Bot настроен и готов к работе!")
    else:
        await ctx.send("❌ Укажите канал: `!уведомления #канал`")

@bot.command()
async def расписание(ctx):
    """⏰ Показать расписание уведомлений"""
    embed = discord.Embed(title="⏰ Расписание уведомлений Razlom Bot", color=0xffaa00)
    embed.add_field(
        name="🕛 События разлома",
        value="**12:00, 20:00, 00:00** по МСК\n• За 30 минут\n• За 15 минут  \n• В момент начала",
        inline=False
    )
    embed.add_field(
        name="🔧 Настройка",
        value="Используйте `!уведомления #канал` чтобы настроить канал для уведомлений",
        inline=False
    )
    await ctx.send(embed=embed)

@bot.command()
async def время(ctx):
    """🕒 Показать текущее время по МСК"""
    now_msk = datetime.now(MSK).strftime("%H:%M:%S %d.%m.%Y")
    await ctx.send(f"🕒 **Московское время:** `{now_msk}`")

@bot.command()
async def тест(ctx):
    """🧪 Проверить работу бота"""
    channel_id = get_event_channel(ctx.guild.id)
    if channel_id:
        channel = bot.get_channel(int(channel_id))
        if channel:
            await channel.send("✅ **Тестовое сообщение** - Razlom Bot работает корректно!")
            await ctx.send("✅ Тестовое сообщение отправлено в канал уведомлений!")
        else:
            await ctx.send("❌ Канал уведомлений не найден")
    else:
        await ctx.send("❌ Канал уведомлений не настроен. Используйте `!уведомления #канал`")

@bot.event
async def on_guild_join(guild):
    print(f"✅ Razlom Bot добавлен на сервер: {guild.name}")
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(title="⏰ Razlom Bot добавлен на сервер!", color=0xffaa00)
            embed.description = "Автоматические уведомления о разломе"
            embed.add_field(
                name="Быстрая настройка", 
                value="1. `!уведомления #канал` - настроить канал\n2. `!расписание` - посмотреть расписание\n3. Бот работает автоматически!",
                inline=False
            )
            await channel.send(embed=embed)
            break

if __name__ == "__main__":
    bot.run(BOT_TOKEN)