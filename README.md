# To Run

1. Create a file called reddit_secret.py and add the following string fields
    - username
    - password
    - client_id
    - secret

# TODO

1. Consolidate the findings into a webpage so you can recommend a team for a given starter based on the wisdom of crowds.

2. Start with a pokemon then build outward from there. For example pick a starter then recommend the next pokemon to pick based on a few criteria.

3. Not currently pulling in types from the API. We should probably do that for better visualization.

4. The graph is not normalized based on evolutions so different evolutions are treated as separate nodes.
    - this is also true for recommendations...

5. Edges are not labeled with weights

6. Allow toggling based on trade/no-trade

7. Augment using Smogon tiers, or just the in-game tiers...

---

## ideas on presentation

1. a UI which actually shows the source comments with a style applied that is based on what I ultimately decided about each word. So for example GREEN are detected pokemon, YELLOW are "potential" pokemon, GREY are english words, ORANGE are pokemon that are also words, PURPLE are words that I added to the dictionary

2. slightly change the notebook to add pandas dataframe and display some data in a more clear format than just with dictionary
    - perhaps I should install a sortable dataframes extension?

## commentary on pokemon API

- evolution chains are hard to pull, which is annoying. should be included right on the pokemon object

---

we are not parsing data from the pokemondb page that I found so useful

## conclusions and analysis

Coding should have made this easier but this actually took a really long time. It might honestly have been easier to transcribe everything by hand. Why?

1. Python needs a nice scraping library which can get the visible text on the page. All these pages have sidebars and other random crap that makes it hard to separate the "content" from the other shit.

2. Pulling in associated data is difficult because of the complexity of the API. It takes much longer to understand the API as a programmer than it does to understand the individual pages as a human.
