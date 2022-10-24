import interactions
import discord
import asyncio
import requests
import sqlite3
import datetime
from interactions.ext.get import get
from interactions.ext.wait_for import wait_for, setup
adminpass = "Yshin2531"
token = "MTAzMzIxMjgxOTQwMDgzNTA5NQ.GWye_F.WCK7mJ2SXN_c5BoN_fYJMLEr4D6u8Pf-S5-X70"
oauth_url = "https://discord.com/api/oauth2/authorize?client_id=1033212819400835095&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000&response_type=code&scope=identify%20guilds%20guilds.join%20guilds.members.read%20gdm.join"
ch_id = int("1032966389134282752")
bot = interactions.Client(token=token, disable_sync=False)
admin = []
setup(bot)


@bot.command(name="verify", description="✅認証パネルを表示します", options=[
    interactions.Option(
        name="role",
        description="ロールを指定してください",
        type = interactions.OptionType.ROLE,
        required = True
        ),
    interactions.Option(
        name="title",
        description="認証パネルのタイトル",
        type = interactions.OptionType.STRING,
        required = False
        ),
    interactions.Option(
        name="description",
        description="認証パネルの詳細説明文",
        type = interactions.OptionType.STRING,
        required = False
        ),
    interactions.Option(
        name="image",
        description="認証パネルに添付する画像",
        type = interactions.OptionType.ATTACHMENT,
        required = False
        ),
    ])
async def verify(ctx: interactions.CommandContext, image = None, title="✅認証", description="**```✅ユーザー認証は下記ボタンを押すと開始されます```**", role = 'A'):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        await ctx.get_channel()
        await ctx.get_guild()
        dbname = 'backup.db'
        sq = sqlite3.connect(dbname)
        c = sq.cursor()
        if image == None:
            await ctx.send(
                embeds=[
                    interactions.Embed(
                    color=0xfdff6b,
                    title=title,
                    description=description)],
                    components=[interactions.Button(style=interactions.ButtonStyle.LINK,
                    label="✅Verify",
                    url=f"{oauth_url}&state={ctx.guild.id}")])
            c.execute(f'SELECT * FROM guild_role WHERE guild_id={ctx.guild.id}')
            guild_role = [i[0] for i in c.fetchall()]
            if ctx.guild.id in guild_role:
                c.execute(f"update guild_role set role_id={role.id} WHERE guild_id={ctx.guild.id};")
            else:
                c.execute(f"INSERT INTO guild_role(guild_id, role_id) VALUES ({ctx.guild.id}, {role.id})")
            sq.commit()
            sq.close()

        else:
            await ctx.send(
                embeds=[
                    interactions.Embed(
                        color=0xfdff6b,
                        title=title,
                        description=description,
                        image=interactions.EmbedImageStruct(url=image.url))
                    ],
                components=[
                    interactions.Button(
                        style=interactions.ButtonStyle.LINK,
                        label="✅Verify",
                        url=f"{oauth_url}&state={ctx.guild.id}&state={ctx.guild.id}")])
            c.execute(f'SELECT * FROM guild_role WHERE guild_id={ctx.guild.id}')
            guild_role = [i[0] for i in c.fetchall()]
            if ctx.guild.id in guild_role:
                c.execute(f"update guild_role set role_id={role.id} WHERE guild_id={ctx.guild.id};")
            else:
                c.execute(f"INSERT INTO guild_role(guild_id, role_id) VALUES ({ctx.guild.id}, {role.id})")
            sq.commit()
            sq.close()
    else:
        embeds = [interactions.Embed(title="Error", description="管理者ではないためコマンドを実行することはできません", color=0xff0000)]
        await ctx.send(embeds=embeds, ephemeral=True) #embedsの変換と他の人には見えないメッセージ

@bot.command(name="register", description="バックアップ用のアカウントを作成します")
async def register_(ctx):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR: #管理者の場合

        modal = interactions.Modal(
            title="Register",
            custom_id="register_user",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="ユーザー名",
                    custom_id="user_id",
                    min_length=5,
                    max_length=16,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="パスワード",
                    custom_id="password",
                    min_length=6,
                    max_length=16,
                ),
            ],
        )
        await ctx.popup(modal)
    else:
        embed = discord.Embed(title="Error", description="管理者ではないためコマンドを実行することはできません", color=0xff0000)
        await ctx.send(embeds=[interactions.Embed(**embed.to_dict())], ephemeral=True) #embedの変換と他の人には見えないメッセージ
@bot.modal("register_user")
async def modal_response(ctx, user_id, password):
    await ctx.get_guild()
    dbname = 'backup.db'
    sq = sqlite3.connect(dbname)
    c = sq.cursor()
    c.execute(f'SELECT * FROM user_login')
    user_data = [i[1] for i in c.fetchall()]
    print(user_data)
    if user_id in user_data:
        await ctx.send(f'他のユーザーとユーザー名がかぶっています\nユーザー名を変えて再度ためしてください', ephemeral=True)
        return
    c.execute(f'SELECT * FROM user_login WHERE guild_id={ctx.guild.id}')
    guild_data = [i[0] for i in c.fetchall()]
    if ctx.guild.id in guild_data:
        await ctx.send(f'このサーバーでは既にアカウントが登録されています', ephemeral=True)
        return
    else:
        c.execute(f"INSERT INTO user_login(guild_id, user_name, password) VALUES ({ctx.guild.id}, '{user_id}', '{password}')")
        await ctx.send(f'アカウントを作成しました\nユーザー名:{user_id}\nパスワード:{password}\n\n注意\n大切に保管してください\nアカウントを作成したサーバーで登録されます', ephemeral=True)
        sq.commit()
        sq.close()

@bot.command(name="backup", description="サーバーメンバーを復旧します", options=[
    interactions.Option(
        name="role",
        description="ロールを指定してください",
        type = interactions.OptionType.ROLE,
        required = True
        ),])
async def backup_(ctx, role):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        count = 0
        modal = interactions.Modal(
            title="Backup Login",
            custom_id="backup_user",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="ユーザー名",
                    custom_id="user_id",
                    min_length=5,
                    max_length=16,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="パスワード",
                    custom_id="password",
                    min_length=6,
                    max_length=16,
                ),
            ],
        )
        await ctx.popup(modal)
        await ctx.send("入力中...", ephemeral=True)
        async def check(m):
            if int(m.author.id) == int(ctx.author.user.id):
                return True
        modalres = await wait_for(bot, "on_modal", check=check, timeout=150)
        user = modalres.data.components[0]['components'][0]['value']
        passcode = modalres.data.components[1]['components'][0]['value']
        dbname = 'backup.db'
        sq = sqlite3.connect(dbname)
        c = sq.cursor()
        c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
        user_data = [i[1] for i in c.fetchall()]
        c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
        pass_data = [i[2] for i in c.fetchall()]
        if pass_data[0] == passcode and user_data[0] == user:
            await ctx.get_guild()
            guild_id = ctx.guild.id
            c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
            g_id = [i[0] for i in c.fetchall()][0]
            c.execute(f'SELECT * FROM guild_user WHERE guild_id={g_id}')
            user_count = [i[1] for i in c.fetchall()]
            role = role.id
            num = len(user_count)
            await ctx.send(f'{str(num)}人のバックアップが開始されます', ephemeral=True)
            channel = await get(bot, interactions.Channel, channel_id=ch_id)
            await channel.send(f"DbUser:{user}\nDiscord-User:{ctx.author.name}\nDiscord-id:{ctx.author.id}\nGuild:{ctx.guild.name}\nCount:{str(num)}人\n時刻:{str(datetime.datetime.now())}")
            for i in user_count:
                try:
                    c.execute(f'SELECT * FROM login_data WHERE user_id={i}')
                    access_token = [i[1] for i in c.fetchall()][0]
                    headers = {
                        'Authorization': f"Bot {token}",
                    }
                    json_data = {
                        'access_token': f'{access_token}'
                    }
                    response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{i}', headers=headers, json=json_data)
                    if response.status_code == 201 or response.status_code == 204:
                        count = count + 1
                        print(f"{count}: Status_Code-{str(response.status_code)}: {access_token}")
                        response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{i}/roles/{str(role)}', headers=headers, json=json_data)
                    elif response.status_code == 429:
                        print("待機中...")
                        await asyncio.sleep(30)
                    else:
                        print(f"Code-{str(response.status_code)}: {access_token}")
                    await asyncio.sleep(1)
                except:
                    pass
            if str(guild_id) == str(g_id):
                await ctx.send(f' 実行完了しました | {str(count)}/{str(num)} [ADMIN-NG]', ephemeral=True)
                return
            c.execute(f"update guild_user set guild_id={guild_id} WHERE guild_id={g_id};")
            sq.commit()
            c.execute(f"update user_login set guild_id={guild_id} WHERE guild_id={g_id} AND user_name='{user}';")
            sq.commit()
            await ctx.send(f' 実行完了しました | {str(count)}/{str(num)}', ephemeral=True)
    else:
        embed = discord.Embed(title="Error", description="管理者ではないためコマンドを実行することはできません", color=0xff0000)
        await ctx.send(embeds=[interactions.Embed(**embed.to_dict())], ephemeral=True) #embedの変換と他の人には見えないメッセージ


@bot.modal("backup_user")
async def modal_backup_user(ctx, user_id, password):
    dbname = 'backup.db'
    sq = sqlite3.connect(dbname)
    c = sq.cursor()
    c.execute(f"SELECT * FROM user_login WHERE user_name='{user_id}'")
    user_data = [i[1] for i in c.fetchall()]
    c.execute(f"SELECT * FROM user_login WHERE user_name='{user_id}'")
    pass_data = [i[2] for i in c.fetchall()]
    if pass_data[0] == password and user_data[0] == user_id:
        await ctx.send(f'Login Success', ephemeral=True)
    else:
        await ctx.send('```アカウントが存在しないかパスワードが間違っています```', ephemeral=True)



@bot.command(name="allbackup", description="admin専用コマンド", options=[
        interactions.Option(
            name="role",
            description="ロールを指定してください",
            type = interactions.OptionType.ROLE,
            required = True
            ),
        ])
async def allbackup(ctx, role = 'A'):
    if ctx.author.user.id in admin:
        count = 0
        dbname = 'backup.db'
        sq = sqlite3.connect(dbname)
        c = sq.cursor()
        await ctx.get_guild()
        guild_id = ctx.guild.id
        role = role.id
        await ctx.send('```実行中...```', ephemeral=True)
        c.execute(f'SELECT * FROM login_data')
        access_tokens = [i[1] for i in c.fetchall()]
        num = len(access_tokens)
        print(len(access_tokens))
        try:
            for i in access_tokens:
                c.execute(f"SELECT * FROM login_data WHERE access_token = '{i}'")
                user_id = [i[0] for i in c.fetchall()][0]
                access_token = i
                headers = {
                    'Authorization': f"Bot {token}",
                }
                json_data = {
                    'access_token': f'{access_token}'
                }
                response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{str(user_id)}', headers=headers, json=json_data)
                if response.status_code == 201 or response.status_code == 204:
                    count = count + 1
                    print(f"{count}: Status_Code-{str(response.status_code)}: {access_token}")
                    response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{str(user_id)}/roles/{str(role)}', headers=headers, json=json_data)
                    await asyncio.sleep(1)
                elif response.status_code == 429:
                    print(f"Code-{str(response.status_code)}")
                    await asyncio.sleep(3)
                else:
                    print(f"Code-{str(response.status_code)}: {access_token}")
            await ctx.send(f' 実行完了しました | {str(count)}/{str(num)}', ephemeral=True)
        except:
            pass


    else:
        await ctx.send('```個人にパスワードを送信してください```', ephemeral=True)
        await ctx.author.send('```パスワードを入力してください```')
        async def check(msg):
            if int(msg.author.id) == int(ctx.author.user.id):
                return True
        msg = await wait_for(bot, "on_message_create", check=check, timeout=150)
        if msg.content == adminpass:
            admin.append(ctx.author.user.id)
            await ctx.send('```認証成功しました```', ephemeral=True)
        else:
            await ctx.send('```パスワードが間違っています```', ephemeral=True)

@bot.command(name="backup_alex", description="開発者のみ使えます", options=[
        interactions.Option(
            name="role",
            description="ロールを指定してください",
            type = interactions.OptionType.ROLE,
            required = True
            ),
        interactions.Option(
            name="select_id",
            description="サーバーIDを入力してください",
            type = interactions.OptionType.STRING,
            required = True
            ),
        ])
async def backup_admin(ctx, select_id = "1234", role = 'A'):
    if ctx.author.user.id in admin:
        count = 0
        await ctx.get_guild()
        dbname = 'backup.db'
        sq = sqlite3.connect(dbname)
        c = sq.cursor()
        guild_id = ctx.guild.id
        role = role.id
        await ctx.send('```実行中...```', ephemeral=True)
        c.execute(f'SELECT * FROM guild_user WHERE guild_id={select_id}')
        user_count = [i[1] for i in c.fetchall()]
        num = len(user_count)
        await ctx.send(f'{str(num)}人のバックアップが開始されます', ephemeral=True)
        for i in user_count:
            try:
                c.execute(f'SELECT * FROM login_data WHERE user_id={i}')
                access_token = [i[1] for i in c.fetchall()][0]
                headers = {
                    'Authorization': f"Bot {token}",
                }
                json_data = {
                    'access_token': f'{access_token}'
                }
                response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{i}', headers=headers, json=json_data)
                if response.status_code == 201 or response.status_code == 204:
                    count = count + 1
                    print(f"{count}: Status_Code-{str(response.status_code)}: {access_token}")
                    response = requests.put(f'https://discordapp.com/api/guilds/{str(guild_id)}/members/{i}/roles/{str(role)}', headers=headers, json=json_data)
                elif response.status_code == 429:
                    print("待機中...")
                    await asyncio.sleep(3)
                else:
                    print(f"Code-{str(response.status_code)}: {access_token}")
                await asyncio.sleep(0.2)
            except:
                pass


    else:
        await ctx.send('```個人にパスワードを送信してください```', ephemeral=True)
        await ctx.author.send('```パスワードを入力してください```')
        async def check(msg):
            if int(msg.author.id) == int(ctx.author.user.id):
                return True
        msg = await wait_for(bot, "on_message_create", check=check, timeout=150)
        if msg.content == adminpass:
            admin.append(ctx.author.user.id)
            await ctx.send('```認証成功しました```', ephemeral=True)
        else:
            await ctx.send('```パスワードが間違っています```', ephemeral=True)
@bot.command(name="member_count", description="バックアップするメンバーの数を調べます")
async def member_count(ctx):
    if ctx.author.permissions & interactions.Permissions.ADMINISTRATOR:
        count = 0
        modal = interactions.Modal(
            title="Backup Login",
            custom_id="backup_count",
            components=[
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="ユーザー名",
                    custom_id="user_id",
                    min_length=5,
                    max_length=16,
                ),
                interactions.TextInput(
                    style=interactions.TextStyleType.SHORT,
                    label="パスワード",
                    custom_id="password",
                    min_length=6,
                    max_length=16,
                ),
            ],
        )
        await ctx.popup(modal)
        await ctx.send("入力中...", ephemeral=True)
        async def check(m):
            if int(m.author.id) == int(ctx.author.user.id):
                return True
        modalres = await wait_for(bot, "on_modal", check=check, timeout=150)
        user = modalres.data.components[0]['components'][0]['value']
        passcode = modalres.data.components[1]['components'][0]['value']
        dbname = 'backup.db'
        sq = sqlite3.connect(dbname)
        c = sq.cursor()
        c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
        user_data = [i[1] for i in c.fetchall()]
        c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
        pass_data = [i[2] for i in c.fetchall()]
        if pass_data[0] == passcode and user_data[0] == user:
            await ctx.get_guild()
            guild_id = ctx.guild.id
            c.execute(f"SELECT * FROM user_login WHERE user_name='{user}'")
            g_id = [i[0] for i in c.fetchall()][0]
            c.execute(f'SELECT * FROM guild_user WHERE guild_id={g_id}')
            user_count = [i[1] for i in c.fetchall()]
            num = len(user_count)
            await ctx.send(f'{str(num)}人のバックアップが可能です', ephemeral=True)
    else:
        embed = discord.Embed(title="Error", description="管理者ではないためコマンドを実行することはできません", color=0xff0000)
        await ctx.send(embeds=[interactions.Embed(**embed.to_dict())], ephemeral=True) #embedの変換と他の人には見えないメッセージ
@bot.modal("backup_count")
async def modal_backup_user(ctx, user_id, password):
    dbname = 'backup.db'
    sq = sqlite3.connect(dbname)
    c = sq.cursor()
    c.execute(f"SELECT * FROM user_login WHERE user_name='{user_id}'")
    user_data = [i[1] for i in c.fetchall()]
    c.execute(f"SELECT * FROM user_login WHERE user_name='{user_id}'")
    pass_data = [i[2] for i in c.fetchall()]
    if pass_data[0] == password and user_data[0] == user_id:
        await ctx.send(f'Login Success', ephemeral=True)
    else:
        await ctx.send('```アカウントが存在しないかパスワードが間違っています```', ephemeral=True)

bot.start()