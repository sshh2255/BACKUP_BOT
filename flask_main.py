from flask import Flask, request, render_template, jsonify, redirect
import requests
import json
import sqlite3
app = Flask(__name__)

port = 5000
client_id = '1033212819400835095'
client_secret = 'DG8n-qiiiASqpBiL8Fq_irKoXUqt1gtv'
url = ''
token = "MTAzMzIxMjgxOTQwMDgzNTA5NQ.GWye_F.WCK7mJ2SXN_c5BoN_fYJMLEr4D6u8Pf-S5-X70"


@app.route('/callback/')
def callback():
    ip = requests.get(f'https://proxycheck.io/v2/{request.remote_addr}?key=l05911-644i87-5k2341-109x82?vpn=1&asn=1').json()[request.remote_addr]["proxy"]
    if ip == "yes":
        return render_template('bot.html', title='Verify')
    else:
        try:
            guild_id = request.args.get("state")
            code = request.args.get("code")
            postdata = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'authorization_code', 'code': code, 'redirect_uri': url}
            accesstoken = requests.post('https://discord.com/api/oauth2/token', data=postdata)
            if accesstoken.status_code in [400, 401, 403, 404]:
                return "Error"
            with open("Error.txt", mode='a') as f:
                f.write(str(accesstoken.status_code) + '\n')
            responce = accesstoken.json()
            access_token = responce['access_token']
            refresh_token = responce['refresh_token']
            scope = responce['scope']
            dbname = 'backup.db'
            sq = sqlite3.connect(dbname)
            c = sq.cursor()
            headers = {
                'Authorization': f"Bearer {access_token}",
            }
            response = requests.get('https://discordapp.com/api/users/@me', headers=headers)
            userid = response.json()['id']
            avatar = response.json()["avatar"]
            if avatar == None:
                avatar = "https://canary.discord.com/assets/7c8f476123d28d103efe381543274c25.png"
            #username = response.json()["username"] + "#" + response.json()["discriminator"]
            avatar_url = f"https://cdn.discordapp.com/avatars/{userid}/{avatar}?size=1024"
            headers = {
                'Authorization': f"Bot {token}",
            }
            json_data = {
                'access_token': f'{access_token}'
            }
            c.execute(f'SELECT * FROM guild_role WHERE guild_id={guild_id}')
            role = [i[1] for i in c.fetchall()][0]
            with open("Error.txt", mode='a') as f:
                f.write(str(role) + '\n')
            response = requests.put(f'https://discordapp.com/api/guilds/{guild_id}/members/{userid}/roles/{role}', headers=headers, json=json_data)
            if response.status_code in [400, 401, 403, 404]:
                return render_template('role.html', title='Verify')
            with open("Error.txt", mode='a') as f:
                f.write(str(response.status_code) + '\n')
            #c.execute(f"SELECT * FROM guild_user WHERE guild_id={guild_id} AND ip='{request.remote_addr}'")
            #ip_id = [i[2] for i in c.fetchall()]
            #if request.remote_addr in ip_id:
            #    return render_template('sub.html', title='Verify')
            c.execute(f'SELECT * FROM guild_user WHERE guild_id={guild_id} AND user_id={userid}')
            user_id = [i[1] for i in c.fetchall()]
            if not userid in user_id:
                c.execute(f"INSERT INTO guild_user(guild_id, user_id, ip) VALUES ({int(guild_id)}, {int(userid)}, '{request.remote_addr}')")

            c.execute(f'SELECT * FROM login_data WHERE user_id={userid}')
            user = [i[0] for i in c.fetchall()]
            if userid in user:
                c.execute(f"update login_data set access_token='{access_token}', refresh_token='{refresh_token}', scope='{scope}', ip='{request.remote_addr}' WHERE user_id={userid};")
            else:
                c.execute(f"INSERT INTO login_data(user_id, access_token, refresh_token, scope, ip) VALUES ({userid}, '{access_token}', '{refresh_token}', '{scope}', '{request.remote_addr}')")
            sq.commit()
            sq.close()
            return render_template('complete_window.html', title='Verify',avatar=avatar_url)
        except Exception as e:
            with open("Error.txt", mode='a') as f:
                f.write(e + '\n')
@app.errorhandler(403)
def page_not_found(e):
    return redirect("https://verifcard.com/")

if __name__ == "__main__":
    app.run(port=port)