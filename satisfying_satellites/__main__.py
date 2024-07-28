import asyncio
import random
from collections import defaultdict

import discord
from discord import app_commands

from . import manipulators
from .secrets import TOKEN
from .trivia import trivia as trivia_module

TEST_GUILD = discord.Object(id=1263163851784978533)


class TriviaClient(discord.Client):
    """The team's triviabot."""

    def __init__(self, *, intents: discord.Intents) -> None:
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """Apply the latest version of the application commands to the test guild."""
        self.tree.copy_global_to(guild=TEST_GUILD)
        await self.tree.sync(guild=TEST_GUILD)


intents = discord.Intents.default()
client = TriviaClient(intents=intents)


@client.event
async def on_ready() -> None:
    """Log bot start."""
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
async def about(interaction: discord.Interaction) -> None:
    """Tell you about myself!"""  # noqa: D400
    await interaction.response.send_message(
        f"Hi, {interaction.user.mention}. I'm Satisfying Satellite's trivia bot for the 2024 code jam!",
    )


@client.tree.command()
@app_commands.rename(text_to_send="text")
@app_commands.describe(text_to_send="Text to munge on the way to this channel")
async def homophones(interaction: discord.Interaction, text_to_send: str) -> None:
    """Send the text into the current channel."""
    await interaction.response.send_message(manipulators.homophonify(text_to_send))


active_questions = []
VOTING_ICONS = {
    "🐱": "CAT",
    "🐶": "DOG",
    "💙": "BLUE HEART",
    "👶": "TEAM BABY",
}

TRIVIA_TIME = 5  # seconds


@client.tree.command()
@app_commands.describe()
async def trivia(interaction: discord.Interaction) -> None:
    """Start a round of overload trivia!"""  # noqa: D400
    # If no member is explicitly provided then we use the command user here
    manipulate = random.choice([manipulators.homophonify, manipulators.uwufy])

    question = random.choice(trivia_module.questions)
    munged_question = manipulate(question.question)
    munged_answers = [manipulate(i) for i in question.answers]

    embed = discord.Embed(
        title="Trivia!",
        description=f"""Vote for the best answer!\n### You have {TRIVIA_TIME} seconds to make your choice.""",
    )
    embed.set_author(name=question.category)

    embed.add_field(name="_ _", value="***" + munged_question + "***", inline=False)
    embed.add_field(name="_ _", value="", inline=False)

    embed.set_thumbnail(url="https://media.tenor.com/AvK7qHnqN2gAAAAi/alarm-clock-alarms.gif")

    selected_icons = list(VOTING_ICONS.items())[: len(munged_answers)]

    for icon, answer in zip(selected_icons, munged_answers, strict=False):
        embed.add_field(name=f"VOTE {icon[1]}", value=answer, inline=False)

    await interaction.response.send_message(embeds=[embed])

    msg = await interaction.original_response()

    for icon in selected_icons:
        await msg.add_reaction(icon[0])

    await asyncio.sleep(TRIVIA_TIME)

    embed.set_thumbnail(url=None)
    await msg.edit(embeds=[embed])

    # reload msg
    channel = await client.fetch_channel(msg.channel.id)
    msg = await channel.fetch_message(msg.id)

    reaction_totals = defaultdict(int)
    for reaction in msg.reactions:
        reaction_totals[reaction.emoji] += reaction.count

        if reaction.emoji in VOTING_ICONS and (reaction.emoji, VOTING_ICONS[reaction.emoji]) in selected_icons:
            # I put one there
            reaction_totals[reaction.emoji] -= 1

    # Remove zero's
    for r, t in list(reaction_totals.items()):
        if t == 0:
            del reaction_totals[r]

    embed = discord.Embed(
        title="Results!",
        description=f"And the question was:\n\n## {question.question}",
    )

    question_index = 0
    for reaction, votes in sorted(reaction_totals.items(), key=lambda x: (x[1], x[0])):
        if reaction in VOTING_ICONS and (reaction, VOTING_ICONS[reaction]) in selected_icons:
            embed.add_field(
                name=VOTING_ICONS[reaction],
                value=f"Votes: {votes}\n{question.answers[question_index]}",
            )
            question_index += 1
        else:
            embed.add_field(
                name="A cheater?",
                value=f"Votes: {votes} for {reaction}",
            )
    if not reaction_totals:
        embed.add_field(
            name="No Answer Selected",
            value="0 votes received",
        )

    await interaction.channel.send("And the winners are...", embeds=[embed])


client.run(TOKEN)
