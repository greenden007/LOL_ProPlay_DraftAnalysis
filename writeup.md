# Optimal League of Legends Pro-Play Draft Strategies
_______
## Judgement Criteria
- **Player Proficiencies**: Associate champions which players are comfortable with as higher priority picks.
- **Team Composition**: Ensure that the team composition is balanced and synergistic (i.e. balancing AP and AD in team comp).
- **Counter Picks**: Ensure that the team composition is able to counter the enemy team composition during draft.
- **Meta Picks**: Ensure that the team composition is meta relevant using pick/ban match data on the current patch.
- **Champion Flexibility**: Prioritize picking champions which have flexibility to play multiple roles/lanes.
- **Side Acknowledgement**: Acknowledge which side of the map the team is playing on (Blue/Red) and adjust draft strategy accordingly, as pick order changes.
- **Bans**: Ensure that the team is banning champions which are meta relevant, player favorites or counter the team composition.

## League of Legends Pro-Play Drafting
In pro play, teams "flex" picks, which means that despite always picking in a specific player order, these champions can be swapped at the end of draft to their correct positions. This means that the model should NOT take into account the current player drafting, and instead, simply use a metric of which players on its team that its drafting for.

There is also a concept of banning champions in ranked and pro-play league. In ranked, players are allowed one ban each before the pick phase, which generally means that each player just bans champions which counter or are strong against the role they play. In pro-play, bans come before picks like ranked, but happen in the following order instead (blue always picks first, and always in this order): 
- Bans: Blue bans 1 champion, Red bans 2 champions, Blue bans 2 champion, Red bans 1 champion
- Picks: Blue picks first, and then Red picks 2 champions, and then Blue picks 2 champions, and then Red picks 1 champion
- Bans: Blue bans 1 champion, Red bans 2 champions, Blue bans 1 champion
- Picks: Blue picks 1 champion, Red picks 2 champions, Blue picks 1 champion

Sometimes the ban order differs by region (LTA, EUW, Worlds (written) vs. LPL, LCK), but this format generally holds true

## Data Collection
All data will be (or already has been) scraped from gol.gg. All credit for data accumulation goes to them.

Why specifically gol.gg?\
gol.gg provides unparalleled data on pro-play in terms of depth of statistics for match evaluation. Generally win/loss on each champion does not give enough information in order to justify champion strength/proficiency. League of Legends is a chaotic game, and when there are moments like major objective steals (which can best be compared to a football drive which goes all the way to the 1 yard line, but then the quarterback throws an interception which is ran back for a touchdown the other way), some champions are likely to have bloated statistics. Instead, the pick/ban% of each champion by game patch tells the story of how strong/how prioritized each champion actually is on the current game patch. 
In addition, similar to how an eval bar works in chess, the best metric relative to League in how to measure team strength is the in-game gold difference. Gold allows you to buy items (which give bonus stats and such) which makes champions stronger. Matches which hold a 0 gold difference through the entire game are coin-flip matches. The more gold difference, the more the game is able to snowball in one team's direction. The other major metric to measure performance is the number of major objectives taken. This includes
towers, dragons, void grubs, rift heralds, baron nashors, (and latest, atakhan); each produces a unique major buff to the team.