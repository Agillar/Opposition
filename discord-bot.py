import asyncio
import discord
from discord import Option
import sqlite3
from discord.ext import tasks, commands
# from config import setting
import time
import datetime

# from discord_ui import Button, ButtonStyle, UI, Slash

# bot
intents = discord.Intents.all()
discord.member = True
bot = commands.Bot(intents=intents, owner_id=642709511215513613)
# db
connection = sqlite3.connect("server")
cursor = connection.cursor()

# global_variable
guild_name = None
emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟", "🟦", "🟥", "🇺🇦", "🇷🇺", "👍", "👎"]
voice_members = []


# region events ...

@bot.event
async def on_ready():
    global guild_name
    guild_name = bot.get_guild(1038902776555642960).name.replace("-", "_").replace(" ", "")
    for x in bot.guilds:
        guild_name = x.name.replace("-", "_").replace(" ", "")
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_name} ("
                       f"name TEXT,"
                       f"id INT,"
                       f"exp INT,"
                       f"pexp REAL,"
                       f"voice_exp INT,"
                       f"cash INT)")

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_name}_warnings ("
                       f"author_mute_id INT,"
                       f"date_mute_unix INT,"
                       f"muted_member_id INT,"
                       f"reason TEXT)")

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_name}_admin_config ("
                       f"owner_id INT,"
                       f"admin_role_id INT,"
                       f"admin_role_id2 INT,"
                       f"forum_channel_id INT,"
                       f"forum_channel_id2 INT,"
                       f"greetings_channel_id INT)")

        cursor.execute(f"CREATE TABLE IF NOT EXISTS {guild_name}_reactions_role ("
                       f"message_id INT,"
                       f"role_id INT,"
                       f"reaction_id INT)")

        connection.commit()
        if cursor.execute(f"SELECT owner_id FROM {guild_name}_admin_config ORDER BY owner_id DESC").fetchone() is None:
            cursor.execute(f"INSERT INTO {guild_name}_admin_config VALUES ("
                           f"{x.owner.id},"
                           f"NULL,"
                           f"NULL,"
                           f"NULL,"
                           f"NULL,"
                           f"NULL)")
            connection.commit()

    for guilds in bot.guilds:
        for member in guilds.members:
            if cursor.execute(f"SELECT id FROM {guild_name} WHERE id = {member.id}").fetchone() is None:
                cursor.execute(f'INSERT INTO {guild_name} VALUES ("{member}", {member.id}, {0}, {0}, {0}, {0})')
            else:
                pass
    connection.commit()
    if status_role.is_running():
        print("passed start")
    else:
        status_role.start()
        voice_check.start()
        print("started")

    print('online!')

    for channel in bot.get_guild(1038902776555642960).channels:
        if str(channel.type) == "voice":
            if channel.members:
                for member in channel.members:
                    voice_members.append(member)


@tasks.loop(minutes=1)
async def voice_check():
    if len(voice_members) != 0:
        for member in voice_members:
            cursor.execute(f"UPDATE {guild_name} SET voice_exp = voice_exp + 1 "
                           f"WHERE id = {member.id}")
            connection.commit()


@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and not before.channel:
        voice_members.append(member)
    if before.channel and not after.channel:
        voice_members.pop(voice_members.index(member))


@bot.event
async def on_raw_reaction_add(payload):
    message_ids = cursor.execute(f"SELECT message_id FROM {guild_name}_reactions_role "
                                 f"ORDER BY message_id DESC").fetchall()
    role_ids = cursor.execute(f"SELECT role_id FROM {guild_name}_reactions_role "
                              f"ORDER BY role_id DESC").fetchall()
    reaction_ids = cursor.execute(f"SELECT reaction_id FROM {guild_name}_reactions_role "
                                  f"ORDER BY reaction_id DESC").fetchall()

    for x, y, z in zip(message_ids, role_ids, reaction_ids):
        message_ids[message_ids.index(x)] = x[0]
        role_ids[role_ids.index(y)] = y[0]
        reaction_ids[reaction_ids.index(z)] = z[0]

    for message_id, role_id, reaction_id in zip(message_ids, role_ids, reaction_ids):
        if payload.emoji.id == reaction_id and payload.message_id == message_id:
            for role in payload.member.roles:
                if role.id == role_id:
                    break
            else:
                role = discord.utils.get(bot.get_guild(1038902776555642960).roles, id=role_id)
                await payload.member.add_roles(role)
            break

    if str(payload.emoji) == "<:ded:1039128844558413854>" and payload.message_id == 1040672037619904522:
        for role in payload.member.roles:
            if role.id == 1039811370004250664 or role.id == 1039843165538095134:
                break
        else:
            role = discord.utils.get(bot.get_guild(1038902776555642960).roles, name="Карасик")
            await payload.member.add_roles(role)
            for channel in bot.get_guild(1038902776555642960).channels:
                if channel.id == 1038902776555642963:
                    await bot.get_channel(channel.id).send(
                        f"Приветствую тебя юный карасик, {payload.member.mention}! "
                        f"Вижу ты наполнен мотивацией быть частью обитания нашей реки, "
                        f"и стать больше чем просто «карасик» в таких водах именуемым «Геймдев»,"
                        f" поэтому тебе нужно начало, и я тебе с этим помогу.\n"
                        f"Здесь в основном находится часть стаи - <#{1038902776555642963}>.\n"
                        f"И если твои плавники умеют вертеться, то можешь поделиться - <#{1039137892519387256}>.\n"
                        f"Ну и также если твои инстинкты хромают, то тебе сюда - <#{1039137910819127447}>.\n"
                        f"Остальные вопросы по реке, можешь спрашивать у стаи. Ну или у старших в стае - "
                        f"Администраторов.")


def get_count(role_id: int = None, member: bool = False):
    guild = bot.get_guild(1038902776555642960)
    if member:
        return guild.member_count
    else:
        count_role_member = ""
        for role in guild.roles:
            if role.id == role_id:
                count_role_member = len(role.members)
        return count_role_member


@tasks.loop(minutes=4)
async def status_role():
    members = bot.get_channel(1040409040544604251)
    karas = bot.get_channel(1039904346814545920)
    bivalyu = bot.get_channel(1039904614658621550)
    gulag = bot.get_channel(1039904403647365212)
    await members.edit(name=f"Участники: {get_count(member=True)}")
    await karas.edit(name=f"Карасики: {get_count(1039811370004250664)}")
    await bivalyu.edit(name=f"Бывалые: {get_count(1039884195780100176)}")
    await gulag.edit(name=f"Осужденные: {get_count(1039843165538095134)}")


@bot.event
async def on_member_join(member):
    if cursor.execute(f"SELECT id FROM {guild_name} WHERE id = {member.id}").fetchone() is None:
        cursor.execute(f"INSERT INTO {guild_name} VALUES ('{member}', {member.id}, 0, 0, 0, 0)")
        connection.commit()
    else:
        pass
    greetings_channel_id = cursor.execute(f"SELECT greetings_channel_id FROM {guild_name}_admin_config "
                                          f"WHERE owner_id = {member.guild.owner_id}").fetchone()[0]
    for channel in bot.get_guild(member.guild.id).channels:
        if channel.id == greetings_channel_id:
            await bot.get_channel(channel.id).send(
                f"Привет, {member.mention}! Ты стал {member.guild.member_count} участником!")
    print(member.guild.member_count)


@bot.event
async def on_member_remove(member):
    greetings_channel_id = cursor.execute(f"SELECT greetings_channel_id FROM {guild_name}_admin_config "
                                          f"WHERE owner_id = {member.guild.owner_id}").fetchone()[0]
    for channel in bot.get_guild(member.guild.id).channels:
        if channel.id == greetings_channel_id:
            await bot.get_channel(channel.id).send(
                f"<@{member.id}>[{member}] идёт нахуй.")
    print(member.guild.member_count)


@bot.event
async def on_message(message):
    if message.type == discord.MessageType.premium_guild_subscription:
        await message.channel.send("Нагана")

    forum_channel_ids = [cursor.execute(f"SELECT forum_channel_id FROM {guild_name}_admin_config "
                                        f"WHERE owner_id = {message.guild.owner.id}").fetchall()[0][0],
                         cursor.execute(f"SELECT forum_channel_id2 FROM {guild_name}_admin_config "
                                        f"WHERE owner_id = {message.guild.owner.id}").fetchall()[0][0]]

    if message.channel.id == 1040524790886322206:
        for emojie in emojis:
            if emojie in message.content: await message.add_reaction(emojie)

    for forum_channel_id in forum_channel_ids:
        forum = message.channel.id == forum_channel_id
        if forum:
            await message.add_reaction("👍")
            await message.add_reaction("👎")
            break

    try:
        if not message.author.bot:
            cursor.execute(f"UPDATE {guild_name} SET pexp = pexp + {len(message.content) / 10.0} WHERE id = "
                           f"{message.author.id}")
            connection.commit()
        if cursor.execute(f"SELECT pexp FROM {guild_name} WHERE id = {message.author.id}").fetchone()[0] > 7:
            mes = int(cursor.execute(f"SELECT pexp FROM {guild_name} WHERE id = {message.author.id}").fetchone()[0])
            cursor.execute(f"UPDATE {guild_name} SET exp = exp + {mes} WHERE id = {message.author.id}")
            connection.commit()
            cursor.execute(f"UPDATE {guild_name} SET pexp = 0 WHERE id = {message.author.id}")
            connection.commit()

        first: bool = None
        second: bool = None
        third: bool = None
        for role in message.author.roles:
            if role.id == 1051444582296080404: first = True
            if role.id == 1051444689410211860: second = True
            if role.id == 1048221888603754538: third = True

        exp = cursor.execute(f"SELECT exp FROM {guild_name} WHERE id = {message.author.id}").fetchone()[0]

        if 1000 <= exp < 5000 and not first:
            await message.author.add_roles(discord.utils.get(bot.get_guild(1038902776555642960).roles,
                                                             id=1051444582296080404))
        if 5000 <= exp < 15000 and not second:
            await message.author.add_roles(discord.utils.get(bot.get_guild(1038902776555642960).roles,
                                                             id=1051444689410211860))
        if 15000 <= exp and not third:
            await message.author.add_roles(discord.utils.get(bot.get_guild(1038902776555642960).roles,
                                                             id=1048221888603754538))
    except TypeError:
        pass


@bot.slash_command()
async def create_reaction_add_role(ctx,
                                   message_id: Option(str,
                                                      description="id message, where reaction",
                                                      required=True),
                                   role_name: Option(str,
                                                     description="name role, what will add to member",
                                                     required=True),
                                   reaction: Option(discord.Emoji,
                                                    description="reaction, format: <:name_reaction:id_reaction>",
                                                    required=True)):
    role = discord.utils.get(bot.get_guild(1038902776555642960).roles, name=role_name)
    await ctx.respond(f"created reaction_add_role with parameters: **\n"
                      f"message_id: {message_id}\n"
                      f"role: {role.name}\n"
                      f"reaction: {reaction}**")
    cursor.execute(f"INSERT INTO {guild_name}_reactions_role VALUES ("
                   f"{int(message_id)},"
                   f"{role.id},"
                   f"{reaction.id})")
    connection.commit()


@bot.slash_command()
async def warn(ctx,
               member: Option(discord.Member, description="Warn member", required=True),
               reason: Option(str, description="reason warn", required=True)
               ):
    admin = False
    owner = False
    admin_ids = [cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0],
                 cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]]
    for role in ctx.author.roles:
        for admin_id in admin_ids:
            if role.id == admin_id:
                admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        cursor.execute(f"UPDATE {guild_name} SET warns = warns + 1 WHERE id = {member.id}")
        connection.commit()
        interaction = await ctx.respond(f"{member.mention} warned by {ctx.author.mention}\n"
                                        f"**reason: {reason}**")
        message_response = await interaction.original_response()
        warns = cursor.execute(f"SELECT warns FROM {guild_name} WHERE id = {member.id}").fetchone()[0]
        date_unix = int(datetime.datetime.timestamp(message_response.created_at))
        cursor.execute(f"INSERT INTO {guild_name}_warnings VALUES("
                       f"{ctx.author.id},"
                       f"{date_unix},"
                       f"{member.id},"
                       f"{reason})")
        connection.commit()
        if warns == 3:
            await ctx.send(f"<@&{admin_ids[0]}>, {member.mention} Muted for a week because he has 3 warns")
            await mute(ctx=ctx, member=member, timer=10080, message=False)
        if warns == 6:
            await ctx.send(f"<@&{admin_ids[0]}>, {member.mention} Muted for because he has 6 warns, "
                           f"and waiting for a ban")
            await mute(ctx=ctx, member=member, message=False)


@bot.slash_command()
async def warnings(ctx):
    authors = cursor.execute(f"SELECT author_mute_id FROM {guild_name}_warnings").fetchall()
    dates = cursor.execute(f"SELECT date_warn_unix FROM {guild_name}_warnings").fetchall()
    members = cursor.execute(f"SELECT muted_member_id FROM {guild_name}_warnings").fetchall()
    reasons = cursor.execute(f"SELECT reason FROM {guild_name}_warnings").fetchall()
    authors_id: [int, ...] = []
    dates_unix: [int, ...] = []
    members_id: [int, ...] = []
    reason_lis: [str, ...] = []
    value: str = ""
    lens: int = 0
    for author in authors:
        authors_id.append(author[0])
    for date in dates:
        dates_unix.append(date[0])
    for member in members:
        members_id.append(member[0])
    for reason in reasons:
        reason_lis.append(reason[0])
    authors_id = authors_id[::-1]
    dates_unix = dates_unix[::-1]
    members_id = members_id[::-1]
    reason_lis = reason_lis[::-1]
    while lens < len(members_id):
        value += f"<@{members_id[lens]}> warned by <@{authors_id[lens]}>\n" \
                 f"**reason: {reason_lis[lens]}**\n" \
                 f"<t:{dates_unix[lens]}:D>\n" \
                 f"--------------------------------------------------\n"
        lens += 1
    if value.endswith(endswith := "--------------------------------------------------\n"):
        value = value[:-len(endswith):]

    await ctx.respond(embed=discord.Embed()
                      .add_field(name="All warns",
                                 value=value,
                                 inline=True)
                      .set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url)
                      .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url))


@bot.slash_command()
async def greetings_channel(ctx,
                            channel: Option(discord.TextChannel, description="Channel to welcome new members")
                            ):
    admin = False
    owner = False
    admin_ids = [cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0],
                 cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]]
    for role in ctx.author.roles:
        for admin_id in admin_ids:
            if role.id == admin_id:
                admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        cursor.execute(f"UPDATE {guild_name}_admin_config SET greetings_channel_id = {channel.id} "
                       f"WHERE owner_id = {ctx.guild.owner.id}")


@bot.slash_command()
async def forum_channel(ctx,
                        channel1: Option(discord.TextChannel, description="Хуйня", required=False),
                        channel2: Option(discord.TextChannel, description="Хуйня", required=False)
                        ):
    admin = False
    owner = False
    admin_ids = [cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0],
                 cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                                f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]]
    for role in ctx.author.roles:
        for admin_id in admin_ids:
            if role.id == admin_id:
                admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        if channel1 is not None:
            channel = channel1.id
            cursor.execute(f"UPDATE {guild_name}_admin_config SET forum_channel_id = {channel} "
                           f"WHERE owner_id = {ctx.guild.owner.id}")
        if channel2 is not None:
            channel = channel2.id
            cursor.execute(f"UPDATE {guild_name}_admin_config SET forum_channel_id2 = {channel} "
                           f"WHERE owner_id = {ctx.guild.owner.id}")
        connection.commit()


@bot.slash_command()
async def role_admin(ctx,
                     role_admin_1: Option(discord.Role, description="Хуй", required=False),
                     role_admin_2: Option(discord.Role, description="Хуй", required=False)
                     ):
    admin = False
    owner = False
    admin_id = cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                              f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]
    for role in ctx.author.roles:
        if role.id == admin_id:
            admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        if role_admin_1 is not None:
            if role_admin_1 == "clear":
                role_admin_id = "NULL"
            else:
                role_admin_id = role_admin_1.id
            cursor.execute(f"UPDATE {guild_name}_admin_config SET admin_role_id = {role_admin_id} "
                           f"WHERE owner_id = {ctx.guild.owner.id}")
        if role_admin_2 is not None:
            if role_admin_2 == "clear":
                role_admin_id = "NULL"
            else:
                role_admin_id = role_admin_2.id
            cursor.execute(f"UPDATE {guild_name}_admin_config SET admin_role_id2 = {role_admin_id} "
                           f"WHERE owner_id = {ctx.guild.owner.id}")
        connection.commit()


@bot.slash_command()
async def emoji(ctx, emojies: str):
    for emojie in bot.emojis:
        if str(emojie) == emojies:
            await ctx.respond(emojie)


# endregion


@bot.slash_command()
async def refresh(ctx):
    admin = False
    owner = False
    admin_id = cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                              f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]
    for role in ctx.author.roles:
        if role.id == admin_id:
            admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        await status_role()
        await ctx.respond(f"statistic refreshed")


@bot.slash_command()
async def mute(ctx, member: Option(discord.Member, description="mute member", required=True),
               timer: Option(int, description="time mute", required=False),
               message: Option(bool, description="spectate or not (True or False)", required=False)
               ):
    admin = False
    owner = False
    admin_id = cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                              f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]
    for role in ctx.author.roles:
        if role.id == admin_id:
            admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        role_live = discord.utils.get(ctx.guild.roles, name="Карасик")
        role_dead = discord.utils.get(ctx.guild.roles, name="Гнида")
        await member.remove_roles(role_live)
        await member.add_roles(role_dead)
        if timer is not None:
            if message:
                await ctx.respond(f"{ctx.author.mention} mute {member.mention} for {timer} minutes")
            await asyncio.sleep(timer * 60)
            await member.remove_roles(role_dead)
            await member.add_roles(role_live)
            print(f"{ctx.author} unmute {member}")
        else:
            if message or message is None:
                await ctx.respond(f"{ctx.author.mention} mute {member.mention}")


@bot.slash_command()
async def unmute(ctx,
                 member: Option(discord.Member, description="mute member", required=True)
                 ):
    admin = False
    owner = False
    admin_id = cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                              f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]
    for role in ctx.author.roles:
        if role.id == admin_id:
            admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        role_live = discord.utils.get(ctx.guild.roles, name="Карасик")
        role_dead = discord.utils.get(ctx.guild.roles, name="Гнида")
        await member.remove_roles(role_dead)
        await member.add_roles(role_live)
        await ctx.respond(f"{ctx.author.mention} unmute {member.mention}")
        print(f"{ctx.author} unmute {member}")


@bot.slash_command()
async def remove(ctx,
                 member: Option(discord.Member, description="что-то", required=True),
                 name_role: Option(str, description="Имя роли", required=True)
                 ):
    admin = False
    owner = False
    admin_id = cursor.execute(f"SELECT admin_role_id FROM {guild_name}_admin_config "
                              f"WHERE owner_id = {ctx.guild.owner.id}").fetchone()[0]
    for role in ctx.author.roles:
        if role.id == admin_id:
            admin = True
    if ctx.author.id == ctx.guild.owner.id:
        owner = True
    if admin or owner or ctx.author.id == 642709511215513613:
        role = discord.utils.get(bot.get_guild(1038902776555642960).roles, name=name_role)
        await member.remove_roles(role)


@bot.slash_command()
async def avatar(ctx, member: Option(discord.Member, description="Member", required=False)):
    if member is None:
        member = ctx.author
    await ctx.respond(
        embed=discord.Embed(title=f"Avatar {member.display_name}:").set_image(url=member.display_avatar.url))


@bot.slash_command()
async def top(ctx,
              type: Option(str, description="TEXT or VOICE", required=False),
              page: int = 1):
    if page > 1:
        i = page * 10 - 10
    else:
        i = 0
    memberid_expdb = [x[0] for x in cursor.execute(f"SELECT id FROM {guild_name} "
                                                   f"ORDER BY exp DESC").fetchall()]
    memberid_voice_expdb = [x[0] for x in cursor.execute(f"SELECT id FROM {guild_name} "
                                                         f"ORDER BY voice_exp DESC").fetchall()]
    exp_db = [x[0] for x in cursor.execute(f"SELECT exp FROM {guild_name} "
                                           f"ORDER BY exp DESC").fetchall()]
    voice_exp_db = [x[0] for x in cursor.execute(f"SELECT voice_exp FROM {guild_name} "
                                                 f"ORDER BY voice_exp DESC").fetchall()]
    if type == "text" or type == "TEXT":
        topdescp = '**Exp users:**\n'
        while i < (page * 10) and i < len(memberid_expdb):
            topdescp += f"#{i + 1}| <@{memberid_expdb[i]}> is {exp_db[i]}\n"
            i += 1
        if str(ctx.author.id) not in topdescp:
            topdescp += f"**#{memberid_expdb.index(ctx.author.id) + 1}| " \
                        f"<@{memberid_expdb[memberid_expdb.index(ctx.author.id)]}>" \
                        f" is {exp_db[memberid_expdb.index(ctx.author.id)]}**\n"
        embed = discord.Embed(
            description=f"{topdescp}<:ded:1039128844558413854> ") \
            .set_author(name='List server leaders', icon_url=ctx.guild.icon.url) \
            .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
    elif type == "voice" or type == "VOICE":
        topdescp = '**Voice exp users:**\n'
        while i < (page * 10) and i < len(memberid_voice_expdb):
            topdescp += f"#{i + 1}| <@{memberid_voice_expdb[i]}> is {voice_exp_db[i]}\n"
            i += 1
        if str(ctx.author.id) not in topdescp:
            topdescp += f"**#{memberid_voice_expdb.index(ctx.author.id) + 1}| " \
                        f"<@{memberid_voice_expdb[memberid_voice_expdb.index(ctx.author.id)]}>" \
                        f" is {voice_exp_db[memberid_voice_expdb.index(ctx.author.id)]}**\n"
        embed = discord.Embed(
            description=f"{topdescp}<:ded:1039128844558413854> ") \
            .set_author(name='List server leaders', icon_url=ctx.guild.icon.url) \
            .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)
    else:
        topdescp = '**Exp users:**\n'
        while i < 5 and i < len(memberid_expdb):
            topdescp += f"#{i + 1}| <@{memberid_expdb[i]}> is {exp_db[i]}\n"
            i += 1
        i = 0
        if str(ctx.author.id) not in topdescp:
            topdescp += f"#{memberid_expdb.index(ctx.author.id) + 1}| " \
                        f"<@{memberid_expdb[memberid_expdb.index(ctx.author.id)]}>" \
                        f" is {exp_db[memberid_expdb.index(ctx.author.id)]}\n"

        topdescp += '**Voice exp users:**\n'
        while i < 5 and i < len(memberid_voice_expdb):
            topdescp += f"#{i + 1}| <@{memberid_voice_expdb[i]}> is {voice_exp_db[i]}\n"
            i += 1
        if str(ctx.author.id) not in topdescp:
            topdescp += f"#{memberid_voice_expdb.index(ctx.author.id) + 1}| " \
                        f"<@{memberid_voice_expdb[memberid_voice_expdb.index(ctx.author.id)]}>" \
                        f" is {voice_exp_db[memberid_voice_expdb.index(ctx.author.id)]}\n"

        embed = discord.Embed(
            description=f"{topdescp}<:ded:1039128844558413854> ") \
            .set_author(name='List server leaders', icon_url=ctx.guild.icon.url) \
            .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url)

    await ctx.respond(embed=embed)


@bot.slash_command()
async def user(ctx, member: Option(discord.Member, description="member", required=False)):
    if member is None:
        member = ctx.author
    await ctx.respond(embed=discord.Embed()
                      .add_field(name="join in discord:",
                                 value=f"<t:{int(time.mktime(member.created_at.timetuple()))}:R>",
                                 inline=True)
                      .add_field(name="join in server:",
                                 value=f"<t:{int(time.mktime(member.joined_at.timetuple()))}:R>",
                                 inline=True)
                      .set_author(name=member.display_name, icon_url=member.avatar.url)
                      .set_thumbnail(url=member.avatar.url)
                      .set_footer(text=ctx.author.name, icon_url=ctx.author.avatar.url))


@bot.slash_command()
async def times(ctx):
    await ctx.respond(f"<t:{int(time.time())}:D>")


@bot.slash_command()
async def roles(ctx):
    await ctx.respond(embed=discord.Embed(description="\n".join(x.mention for x in ctx.guild.roles[:0:-1])))


@bot.slash_command(description="i'll be schizophrenic")
async def say(ctx, text: Option(str, description="text what say bot", required=True)):
    print(f"{ctx.author} used bot say")
    await ctx.send(text)


# endregion

bot.run(token)
