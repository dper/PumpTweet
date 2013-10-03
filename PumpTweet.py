# coding=utf-8

from PumpLogin import PumpTweetParser
from pypump import PyPump
from MLStripper import strip_tags
from shorturl import shorten
from unicodedata import normalize

# Run the parser and grab useful values.
ptp = PumpTweetParser()
pump_me = ptp.get_pump_me()
pump_username = ptp.get_pump_username()
twitter_api = ptp.get_twitter_api()

# Returns recent outbox activities.
# If testing, don't stop at recent activity.
def get_new_activities(testing=False):
	print 'Looking at Pump outbox activity...'
	
	# Some of this can be replaced by 'since' if later implemented by PyPump.
	published = ptp.get_published()
	recent = ptp.get_recent()
	outbox = pump_me.outbox
	history = ptp.get_history()

	# Users with a lot of non-note activity might raise this.
	count = 20

	# The maximum number of notes to post at a time.
	# Posting too frequently might lead to errors on Twitter.
	# If this number is too small, consider a more frequent cronjob.
	allowable_posts = 3
	notes = []

	for activity in outbox.major[:count]:
		print '> ' + activity.obj.objectType + ' (' + str(activity.published) + ')'

		# Stop looking at the outbox upon finding old activity.
		if history and not testing:
			if recent == activity.id: break
			if published >= activity.published: break

		# Only post several notes. Others are forgotten.
		if len(notes) >= allowable_posts: break

		obj = activity.obj

		# Only post notes to Twitter.
		if obj.objectType != 'note': break

		# Skip deleted notes.
		if obj.deleted: break

		# Omit posts written by others and then shared.
		note_author = obj.author.id.lstrip('acct:')
		if note_author != pump_username: break

		notes.append(obj)
	return notes

# Make the text for a tweet that includes the contest of the note.
def make_tweet(note):
	max_length = 136
	private_url = note.id
	public_url = private_url.replace('/api/note/', '/dper/note/')
	short_url = shorten(public_url)
	max_length = max_length - len(short_url) - 1
	
	content = note.content
	content = content.replace('&#39;', "'")	# Replace HTML apostrophes.
	content = strip_tags(content)		# Strip HTML.

	ellipsis = False
	if len(content.splitlines()) > 1:
		ellipsis = True

	content = content.splitlines()[0]	# Keep only the first line.
	content = content.strip()		# Strip white space.

	current_length = len(content)

	if current_length > max_length:
		ellipsis = True

	if ellipsis:
		max_length = max_length - 1

	content = content[:max_length]

	if ellipsis:
		tweet = content + u'… ' + short_url
	else:
		tweet = content + ' ' + short_url

	return tweet

# Converts posts to tweets.
def make_tweets(notes):
	tweets = []
	for note in notes:
		tweets.append(make_tweet(note))
	return tweets

# Prints a list of tweets.
def print_tweets(tweets):
	print 'Printing tweets...'
	for tweet in tweets:
		normal = normalize('NFKD', tweet).encode('ascii', 'ignore')
		print '> ' + normal

# Posts a list of tweets.
def post_tweets(tweets):
	print 'Posting to Twitter...'
	print 'New tweet count: ' + str(len(tweets)) + '.'
	for tweet in tweets:
		twitter_api.PostUpdate(tweet)

# Updates the ini file with the most recent entry.
def update_recent():
	print 'Updating history...'
	activity = pump_me.outbox.major[0]
	latest = activity.id
	published = activity.published
	ptp.update_recent(latest, published)

# Pulls from Pump and produces text for some tweets.
# Nothing is sent to Twitter. This is for testing.
def pull_and_test():
	notes = get_new_activities(testing=True)
	tweets = make_tweets(notes)
	print_tweets(tweets)

# Pulls from Pump and pushes to Twitter.
def pull_and_push():
	notes = get_new_activities()
	tweets = make_tweets(notes)
	print_tweets(tweets)
	post_tweets(tweets)
	update_recent()

#pull_and_test()
pull_and_push()
