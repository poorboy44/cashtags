#!/bin/bash

head -n10 ~/projects/cashtags/cashtags.txt | while read tag; do
	count=$(search_api.py -f$tag timeline | jq -c '[.results[]["count"]] | add' )
	echo $tag, $count
done