# *trello* library

## Description

This command allow to add a new card to a trello list easily.
It is needed to set the following environment variables:

- TRELLO_API_KEY
- TRELLO_TOKEN

Please, see Trello API documentation to get those values (<https://trello.com/app-key>)

## Concurrency Type

Sync

## Input parameters

- **idList**: String. List id for add the new card
- **name**: String. Card title.
- **desc**: String. Card description.

## Output parameters

curl execution result

## Tools and services

The following commands need to be available in your command path:

- curl

## Example

Create a new card at list with id 609cf4drtd25e143c94afd42.
Please, see Trello API documentation to get this value (<https://developer.atlassian.com/cloud/trello/rest/api-group-actions/>)

``` text
include "trelloNewCard"
trelloNewCard("609cf4drtd25e143c94afd42", "Test Card", "Mi test card description")
```
