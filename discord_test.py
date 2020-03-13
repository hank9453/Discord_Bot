import os
import discord
from discord.ext import commands
from datetime import timedelta
from datetime import datetime
import mysql.connector
import calendar
import operator
import re
import csv
class DB:
  mydb = None
  def __init__(self):
    self.mydb  = mysql.connector.connect( host="<mysql_host>",user="<mysql_user>",passwd="<mysql_password>",database="<mysql_databass>")
  def connect(self):
     self.mydb  = mysql.connector.connect( host="<mysql_host>",user="<mysql_user>",passwd="<mysql_password>",database="<mysql_databass>")
  def commit(self):
    self.mydb.commit()
  def query(self, sql ,val=None):
    cursor=None
    try:
      cursor = self.mydb.cursor()
      if val != None :
        cursor.execute(sql,val)
      else :
        cursor.execute(sql)
    except mysql.connector.Error as err:
      print(err)
      print(err.errno)
      if err.errno == -1 :
        self.connect()
        cursor = self.mydb.cursor()
        if val != None :
          cursor.execute(sql,val)
        else :
          cursor.execute(sql)
    return cursor
class member_info :
  def __init__(self, nickname,damage,times,compensation_times,first,second,third,fourth,fifth):
      self.nickname = nickname
      self.damage = damage
      self.times = times
      self.compensation_times = times
      self.first = first
      self.second = second
      self.third = third
      self.fourth = fourth
      self.fifth = fifth
bot = commands.Bot(command_prefix='!')
db = DB()
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
@bot.command()
async def 創立軍團(ctx):
     try :
        sql = "SHOW TABLES  LIKE '%s_member_list'"%str(ctx.guild.owner.id)
        result=db.query(sql)
        result = result.fetchall()
        if len(result) != 0 :
            await ctx.send("軍團已存在 一個頻道只能創建一個 :confounded:")
            return 0
        db.query("CREATE TABLE %s_member_list (Discord_id VARCHAR(255),NickName  VARCHAR(255))"%str(ctx.guild.owner.id))
        db.commit()
        await ctx.send("創建成功 👍")
     except :
        await ctx.send("創建失敗😨")
@bot.command()
async def 加入軍團(ctx ,name :str):
    sql = "SELECT * FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) != 0 :
        await ctx.send("已經註冊過了!🙄")
        return 0
    sql = "INSERT INTO %s_member_list"%str(ctx.guild.owner.id)+ "(Discord_id, NickName) VALUES (%s, %s)"%(str(ctx.author.id), name)
    db.query(sql)
    db.query("CREATE TABLE %s_%sdata (Time DATETIME,Boss TINYINT,Damage INT , Compensation BOOLEAN)"%(str(ctx.guild.owner.id),str(ctx.author.id)))
    db.commit()
    await ctx.send("%s已成功寫入數據庫👍"%ctx.author.mention)
@bot.command()
async def 退出軍團(ctx):
    sql = "SELECT * FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無此數據 退出失敗!😪")
        return 0
    sql = "DELETE  FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    db.query(sql)
    sql = "DROP TABLE IF EXISTS %s_%sdata"%(str(ctx.guild.owner.id),str(ctx.author.id))
    db.query(sql)
    db.commit()
    await ctx.send("%s退出成功😥" %ctx.author.mention)
@bot.command()
async def 強制退出(ctx ,discordid: str):
    id = re.sub('[<>@!]',"",discordid)
    if ctx.guild.owner.id == ctx.author.id :
        sql = "SELECT * FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(id))
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        if len(myresult) == 0 :
            await ctx.send("資料庫無此數據 退出失敗!😪")
            return 0
        sql = "DELETE  FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(id))
        db.query(sql)
        sql = "DROP TABLE IF EXISTS %s_%sdata"%(str(ctx.guild.owner.id),str(id))
        db.query(sql)
        db.commit()
        await ctx.send("%s退出成功😥"%discordid )
    else :
         await ctx.send("錯誤需要頻道創建者輸入👀")
@bot.command()
async def 軍團成員(ctx):
    sql = "SELECT * FROM %s_member_list "%str(ctx.guild.owner.id)
    myresult=db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無數據 失敗!😪")
        return 0
    else :
        embed = discord.Embed(title="軍團資料", description="下面是儲在數據庫的資料👀", color=0xeee657)
        for each in myresult :
            embed.add_field(name="遊戲暱稱 : %s"%each[1], value="Discord ID : %s"%each[0], inline=False)
        await ctx.send(embed=embed)
@bot.command()
async def 修改傷害(ctx,DATE : str,TIME : str ,Damage :int):
    sql = "SELECT * FROM %s_%sdata WHERE Time = '%s %s'"%(str(ctx.guild.owner.id),str(ctx.author.id),DATE,TIME)
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無此數據 退出失敗!😪")
        return 0
    else :
        sql = "UPDATE %s_%sdata SET Damage = '%s'  WHERE Time = '%s %s'"%(str(ctx.guild.owner.id),str(ctx.author.id),Damage,DATE,TIME)
        db.query(sql)
        db.commit()
        await ctx.send("%s修改成功"%ctx.author.mention)
@bot.command()
async def 個人資料(ctx):

    sql = "SELECT * FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無此數據 退出失敗!😪")
        return 0
    embed = discord.Embed(title="個人資料", description="%s下面是您儲在數據庫的資料👀"%ctx.author.mention, color=0xeee657)
    for each in myresult :
      embed.add_field(name="Discord ID ", value="%s"%each[0], inline=False)
      embed.add_field(name="遊戲暱稱", value="%s"%each[1], inline=False)
    times = 0
    now = datetime.utcnow()+timedelta(hours=8)
    month_lastday =calendar.monthrange(now.year, now.month)[1]
    if now.day==month_lastday and now.hour>5 :
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,23,59,59)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        for each in myresult :
            if each[3] == 1 :
                embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
                embed.add_field(name="傷害", value="%d"%each[2], inline=True)
                embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,23,59,59) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    elif now.hour < 5 :
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day-1,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        for each in myresult :
            if each[3] == 1 :
                    embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
                times +=1
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    else :
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day+1,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        for each in myresult :
            if each[3] == 1 :
                    embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day+1,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
@bot.command()
async def 查刀(ctx,tag : str):
    id = re.sub('[<>@!]',"",tag)
    now = datetime.utcnow()+timedelta(hours=8)
    month_lastday =calendar.monthrange(now.year, now.month)[1]
    if now.day==month_lastday and now.hour>5 :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,23,59,59)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="今日出刀資料", description="下列為%s今日出刀資列!👀"%tag, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,23,59,59) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    elif now.hour < 5 :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day-1,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="今日出刀資料", description="下列為%s今日出刀資列!👀"%tag, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
                times +=1
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    else :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day+1,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="今日出刀資料", description="下列為%s今日出刀資列!👀"%tag, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day+1,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
@bot.command()
async def 匯出(ctx ,year:int,month:int):
    total_data = []
    sql = "SELECT * FROM %s_member_list"%str(ctx.guild.owner.id)
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無此數據 退出失敗!😪")
        return 0
    for each in myresult :
      sql = "SELECT * FROM %s_%sdata WHERE Time > '%s-%s-1 00:00:00' AND Time< '%s-%s-1 00:00:00'"%(str(ctx.guild.owner.id),str(each[0]),year,month,year,month+1)
      myresult = db.query(sql)
      result = myresult.fetchall()
      if len(result) == 0 :
          continue
      name = each[1]
      normal = 0
      compensation = 0
      first = 0
      secend = 0
      third = 0
      fourth = 0
      fifth = 0
      for data in result :
          if data[1] == 1 :
              first += int(data[2])
          elif data[1]== 2 :
              secend += int(data[2])
          elif data[1]== 3 :
              third += int(data[2])
          elif data[1]== 4 :
              fourth += int(data[2])
          elif data[1]== 5 :
              fifth += int(data[2])
          if data[3] == 0 :
              normal += 1
          elif data[3] == 1 :
              compensation+=1
      damage = first+secend+third+fourth+fifth
      total_data.append(member_info(name,damage,normal,compensation,first/damage,secend/damage,third/damage,fourth/damage,fifth/damage))
    if len(total_data) == 0 :
        await ctx.send("資料庫無數據😜")
        return 0
    total_data.sort(key=operator.attrgetter('damage'),reverse=True)
    with open('%s.csv'%str(ctx.guild.owner.id), 'w', newline='',encoding = 'Big5') as csvfile:
      writer = csv.writer(csvfile)

      writer.writerow(['遊戲暱稱', '傷害排名', '總傷害','基礎刀數','補償刀數','一王','二王','三王','四王','五王'])
      for i in range(len(total_data)) :
           writer.writerow([total_data[i].nickname,i+1,
                           total_data[i].damage,total_data[i].times,
                           total_data[i].compensation_times,
                           "%d%%"%(total_data[i].first*100)
                           ,"%d%%"%(total_data[i].second*100)
                           ,"%d%%"%(total_data[i].third*100)
                           ,"%d%%"%(total_data[i].fourth*100)
                           ,"%d%%"%(total_data[i].fifth*100)])
    with open('%s.csv'%str(ctx.guild.owner.id), 'rb') as fp:
        await ctx.send(file=discord.File(fp, '%s.csv'%str(ctx.guild.owner.id)))
    os.remove('%s.csv'%str(ctx.guild.owner.id))
@bot.command()
async def 改名(ctx,name :str):

    sql = "SELECT * FROM %s_member_list WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult) == 0 :
        await ctx.send("資料庫無此數據 退出失敗!😪")
        return 0
    else :
        sql = "UPDATE %s_member_list SET NickName = '%s' WHERE Discord_id = '%s'"%(str(ctx.guild.owner.id),name,str(ctx.author.id))
        db.query(sql)
        db.commit()
        await ctx.send("%s修改成功"%ctx.author.mention)
@bot.command()
async def 填表(ctx,boss:int,damage : int,compesation :str = None):
    if boss <0 or boss > 6 :
        await ctx.send("輸入有誤")
        return 0
    sql = "SHOW TABLES  LIKE '%s_%sdata'"%(str(ctx.guild.owner.id),str(ctx.author.id))
    myresult = db.query(sql)
    result = myresult.fetchone()
    if result == None :
        await ctx.send("%s請先加入軍團"%ctx.author.mention)
        return 0
    now = datetime.utcnow()+timedelta(hours=8)
    sql = "INSERT INTO %s_%sdata"%(str(ctx.guild.owner.id),str(ctx.author.id))+"(Time,Boss,Damage,Compensation)VALUES (%s,%s,%s,%s)"
    if compesation=="補償" :
      val = (str(now),boss,damage,True)
    else :
      val = (str(now),boss,damage,False)
    db.query(sql,val)
    db.commit()
    month_lastday =calendar.monthrange(now.year, now.month)[1]
    if now.day==month_lastday and now.hour>5 :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,23,59,59)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="個人資料", description="%s填寫成功!👀"%ctx.author.mention, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,23,59,59) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    elif now.hour < 5 :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day-1,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="個人資料", description="%s填寫成功!👀"%ctx.author.mention, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
                times +=1
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    else :
        times = 0
        sql = "SELECT * FROM %s_%sdata "%(str(ctx.guild.owner.id),str(ctx.author.id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day+1,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)
        myresult = db.query(sql)
        myresult = myresult.fetchall()
        embed = discord.Embed(title="個人資料", description="%s填寫成功!👀"%ctx.author.mention, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day+1,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
@bot.command()
async def 代填(ctx,tag : str,boss:int,damage : int,compesation :str = None):
    if boss <0 or boss > 6 :
        await ctx.send("輸入有誤")
        return 0
    id = re.sub('[<>@!]',"",tag)
    sql = "SHOW TABLES  LIKE '%s_%sdata'"%(str(ctx.guild.owner.id),id)
    myresult = db.query(sql)
    myresult = myresult.fetchall()
    if len(myresult)== 0:
        await ctx.send("無目標資料庫")
        return 0
    now = datetime.utcnow()+timedelta(hours=8)
    sql = "INSERT INTO %s_%sdata"%(str(ctx.guild.owner.id),str(ctx.author.id))+"(Time,Boss,Damage,Compensation)VALUES (%s,%s,%s,%s)"
    if compesation=="補償" :
      val = (str(now),boss,damage,True)
    else :
      val = (str(now),boss,damage,False)
    db.query(sql,val)
    db.commit()
    month_lastday =calendar.monthrange(now.year, now.month)[1]
    embed = discord.Embed(title="今日出刀資料", description="以下為%s今日出刀資料👀"%tag ,color=0xeee657)
    if now.day==month_lastday and now.hour>5 :
        times = 0
        sql = "SELECT * FROM  %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,23,59,59)
        result = db.query(sql)
        myresult = result.fetchall()
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,23,59,59) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    elif now.hour < 5 :
        times = 0
        sql ="SELECT * FROM  %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day-1,5,0,0)
        result = db.query(sql)
        myresult = result.fetchall()
        embed = discord.Embed(title="個人資料", description="%s填寫成功!👀"%ctx.author.mention, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
                times +=1
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
    else :
        times = 0
        sql ="SELECT * FROM  %s_%sdata "%(str(ctx.guild.owner.id),str(id))+"WHERE Time<'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day+1,5,0,0)+"AND  Time>'%s-%s-%s %s:%s:%s'"%(now.year,now.month,now.day,5,0,0)
        result = db.query(sql)
        myresult = result.fetchall()
        embed = discord.Embed(title="個人資料", description="%s填寫成功!👀"%ctx.author.mention, color=0xeee657)
        for each in myresult :
            if each[3] == 1 :
                 embed.add_field(name="Boss", value="%d王補償"%each[1], inline=True)
            else :
                times +=1
                embed.add_field(name="Boss", value="%d王"%each[1], inline=True)
            embed.add_field(name="傷害", value="%d"%each[2], inline=True)
            embed.add_field(name="時間", value="%s"%each[0], inline=True)
        await ctx.send(embed=embed)
        gap = datetime(now.year,now.month,now.day+1,5,0,0) - now
        seconds = gap.total_seconds()
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        if times >3 :
            await ctx.send("本日多填 **%d**刀 \n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(times-3,hours,minutes,seconds))
        else :
            await ctx.send("本日還剩 **%d** 刀\n距離本日戰對戰結束還剩 **%d** 小時 **%d** 分鐘 **%d** 秒"%(3-times,hours,minutes,seconds))
bot.remove_command('help')  
@bot.command()
async def help(ctx):
    embed = discord.Embed(title="姆咪機器人", description="所有資料都是姆咪手動填上去的唷👍\n有參數必須在前加空格才能正常使用:", color=0xeee657)
    embed.add_field(name="!help", value="查看幫助", inline=False)
    embed.add_field(name="!創立軍團", value="創建軍團資料庫", inline=False)
    embed.add_field(name="!加入軍團 +您的遊戲暱稱", value="把您的數據寫入資料庫", inline=False)
    embed.add_field(name="!軍團成員", value="查詢整個軍團資料", inline=False)
    embed.add_field(name="!退出軍團", value="把您的數據從資料庫刪除", inline=False)
    embed.add_field(name="!強制退出 +標記目標", value="僅限 **頻道創建者** 使用把您指定的數據從資料庫刪除", inline=False)
    embed.add_field(name="!個人資料", value="查詢個人資料", inline=False)
    embed.add_field(name="!填表 +Boss + 傷害 +補償(選擇填寫)", value="把您的傷害寫入資料庫 \n ex:\n !填表 1 3000000 \n!填表 4 3000000 補償", inline=False)
    embed.add_field(name="!代填 + 標記目標+Boss + 傷害 +補償(選擇填寫)", value="把您的傷害寫入資料庫 \n ex:\n !填表 @姆咪 1 3000000 \n!填表 @姆咪 4 3000000 補償", inline=False)
    embed.add_field(name="!修改傷害 +年月 + 時間 +傷害", value="修改已填入傷害 \n ex:\n !修改傷害 2020-03-11 02:08:01 300000", inline=False)
    embed.add_field(name="!改名 +您的遊戲暱稱", value="修改個人資料", inline=False)
    embed.add_field(name="!查刀 +標記目標", value="查詢目標本日出刀狀況", inline=False)
    embed.add_field(name="!匯出 +年分 + 月分", value="匯出指定年月份的數據 \n ex: \n !匯出 2020 03", inline=False)
    await ctx.send(embed=embed)
bot.run('<your token>')
