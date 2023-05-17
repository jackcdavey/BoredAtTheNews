import discord
import os
from discord.ext import commands
from discord.ext import tasks
import openai
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import random


# Get the BBC headlines
url = 'https://www.bbc.com/news'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
headlines = soup.find_all(lambda tag: tag.name == 'a' and tag.find('h3'))


# Discord setup
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# Set the date
current_date = datetime.now().date()
formatted_date = current_date.strftime("%Y-%m-%d")

# I know putting API keys directly in code is a sin, don't plan to make the repo public
openai.api_key = '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'


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command(name='generate', help='Generates a sentence using OpenAI')
async def generate(ctx, *, user_prompt=None):
    print(f'Command received from {ctx.author}')

    # Pick a random headline and get its text and URL
    chosen_headline = random.choice(headlines)
    chosen_headline_text = chosen_headline.find('h3').text
    chosen_headline_url = chosen_headline.get('href')

    # Prepend the base URL if the href is a relative URL
    if not chosen_headline_url.startswith('http'):
        chosen_headline_url = 'https://www.bbc.com' + chosen_headline_url

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Announce the following news headline from the perspective of an annoyed, snarky teen running a news and gossip account on social media, in 2 or 3 sentences\n\n" +
            chosen_headline.text,
            temperature=0.5,
            max_tokens=300
        )
        # Send the current date, the top headline, and the generated text
        await ctx.send(formatted_date + ': ' + chosen_headline_text + '\n' + response['choices'][0]['text'] + '\n\n' + chosen_headline_url)

    except Exception as e:
        print(f'An error occurred: {e}')


# Analyze the user input to get a headline
def analyze_input(input):
    if input.startswith('http'):
        # The input is a URL
        response = requests.get(input)
        soup = BeautifulSoup(response.text, 'html.parser')
        headline = soup.find('h1').text
        url = input
    else:
        # The input is a headline
        headline = input
        url = None
    return headline, url


@bot.command(name='analyze', help='Analyzes a URL or a headline and generates a sentence using OpenAI')
async def analyze(ctx, *, user_input=None):
    print(f'Command received from {ctx.author}')
    try:
        # If the user didn't provide an input, use a default one
        if user_input is None:
            user_input = "Once upon a time"

        # Analyze the user input to get the headline and URL
        chosen_headline_text, chosen_headline_url = analyze_input(user_input)

        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="Announce the following news headline from the perspective of an annoyed, snarky teen running a news and gossip account on social media, in a couple sentences\n\n" +
            chosen_headline_text,
            temperature=0.5,
            max_tokens=200
        )
        # Send the current date, the headline, the generated text, and the URL (if available)
        message = formatted_date + ':' + chosen_headline_text + \
            '\n' + response['choices'][0]['text']
        if chosen_headline_url is not None:
            message += '\n\n' + chosen_headline_url
        await ctx.send(message)

    except Exception as e:
        print(f'An error occurred: {e}')


@bot.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(f'An error occurred: {str(error)}')

bot.run('MTEwODQ0NzUxODg3MTc4NTQ3Mg.GSmcxo.Kbrunool4lQ_JCQXfhB3qG-7oJ5wwryw7qDUO4')
