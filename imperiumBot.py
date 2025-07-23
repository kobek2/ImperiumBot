import discord 
from discord.ext import commands 
import re 
from collections import defaultdict

# election_id -> candidate -> points
elections = defaultdict(lambda: defaultdict(int))


TOKEN = "MTM5NzM2Njk2OTk5NjU0NjE1MQ.GCjb1I.0ObS6JCW-hfCuCfLcf40Qy33Q19qlwZqAH52jQ"

intents = discord.Intents.default() 
intents.message_content = True

bot = commands.Bot(command_prefix = '!', intents = intents)

#store elections in memory
elections = {}

#Points system based off word count
def count_points(text): 
    words = len(re.findall(r'\w+', text))  # Correct regex for word counting
    if 0<= words <= 150: 
        return 10
    if 150< words <= 300: 
        return 25
    if words>300: 
        return 40
    
@bot.event
async def on_ready(): 
    print (f'Logged in as {bot.user}')


@bot.command()
async def startElection(ctx, election_name, *candidate_mentions):
    if election_name in elections:
        await ctx.send("Election already exists")
        return
    candidates = {}
    for mention in candidate_mentions:
        # Extract user ID from mention string like <@123456789012345678>
        user_id = int(re.findall(r'\d+', mention)[0])
        candidates[user_id] = {"points": 0, "messages": []}
    elections[election_name] = {
        "candidates": candidates,
        "active": True
    }
    candidate_names = []
    for user_id in candidates:
        user = await bot.fetch_user(user_id)
        candidate_names.append(user.name)
    await ctx.send(f"Election '{election_name}' started with candidates: {', '.join(candidate_names)}")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.author.bot:
        return

    for election_name, data in elections.items():
        if not data["active"]:
            continue
        if message.author.id in data["candidates"]:
            points = count_points(message.content)
            data["candidates"][message.author.id]["points"] += points
            data["candidates"][message.author.id]["messages"].append(message.content)

#view stats
@bot.command()
async def stats(ctx, election_name):
    if election_name not in elections: 
        await ctx.send("Election not found")
        return 
    data = elections[election_name]
    response = f"Stats for '{election_name}':/n"
    for candidate, info in data["candidates"].items():
        response += f"-{candidate}: {info['points']} points\n"
    await ctx.send(response)

#end election
async def endElection(ctx, election_name):
    if election_name not in elections: 
        await ctx.send("Election not found")
        return 
    data = elections[election_name]
    data["active"] = False

    response = f"🏁 Election '{election_name}' has ended.\nFinal Results:\n"
    winner = None
    highest = -1
    for candidate, info in data["candidates"].items():
        points = info["points"]
        response += f"- {candidate}: {points} points\n"
        if points > highest:
            highest = points
            winner = candidate

    response += f"\n🏆 Winner: {winner}"
    await ctx.send(response)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"⚠️ Error: {str(error)}")
    print(f"Error: {error}")


bot.run("MTM5NzM2Njk2OTk5NjU0NjE1MQ.GCjb1I.0ObS6JCW-hfCuCfLcf40Qy33Q19qlwZqAH52jQ")
