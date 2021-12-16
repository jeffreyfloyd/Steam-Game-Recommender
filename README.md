# Steam Game Recommendation App

## Problem Statement
Frequently I’ll find myself having finished a game without another one lined up to play. Sometimes I’ll want to play something similar to what I just beat, sometimes I’ll get a craving to play a particular genre. The only common theme is that my ability to find good recommendations rarely come from the platforms where I get my games. At best when using the Steam platform I might get one or two similar titles but most often just DLC or completely unrelated titles. Rather than word of mouth, random interactions with ads or content creators playing the game of the month, I'd like to get a bit more of a scientific approach to where I get my recommendations from.

## Data Collection Cleaning and EDA
Game information was collected using the Steam Spy API to get a condensed and complete list of information from each game, alongside Steam’s own API to get a list of all available games on steam as of November 23rd 2021

### Data Dictionary
| File | Description |
|---|---|
| appid | Steam Application ID. If it's 999999, then data for this application is hidden on developer's request, sorry |
| name | game's name |
| developer | comma separated list of the developers of the game |
| publisher | comma separated list of the publishers of the game |
| score_rank | score rank of the game based on user reviews |
| owners | owners of this application on Steam as a range |
| average_forever | average playtime since March 2009. In minutes |
| average_2weeks | average playtime in the last two weeks. In minutes |
| median_forever | median playtime since March 2009. In minutes |
| median_2weeks | median playtime in the last two weeks. In minutes |
| ccu | peak CCU yesterday |
| price | current US price in cents |
| initialprice | original US price in cents |
| discount | current discount in percents |
| tags | game's tags with votes in JSON array |
| languages | list of supported languages |
| genre | list of genres |

## Recommendation Method
The biggest challenge was deciding which data to use to achieve the best results. Ultimately tags were chosen due to them being both the most specific and also diverse data point.
To help games with fewer total tags measure up to games with much larger tag counts every game was scaled based off the highest tag count it received.
The scaled tag values were then all compared to each other in a pairwise distance algorithm to compare which games were tagged the most similarly by users!

## Limitations
Currently only top 100 closest games are available on the streamlit app due to hardware and file size limitations
Games without any tags are unable to be considered
Less popular games still need a bit more representation
Users still need to have a game in mind to play
Can only search games available on the Steam Store
Series that are spread across different platforms aren’t represented well

## Conclusions
User tags are incredibly effective at helping users find similar games. The algorithm had already generated a successful game sale before it was fully deployed.
 
Based on early performance I’d recommend Valve look into implementing a similar system to help gamers everywhere find the games they’ll enjoy the most!

## Future Updates
Implement a filter search to help find a starting point for those who haven’t used Steam before
Expand to other platforms: itch.io, Epic Games Store, Humble Bundle
Explore Mean Average Precision as a scoring metric
Improve mature content filter and allow users more control of the results they receive