import os
import logging
import ssl
import certifi
from slack_bolt import App

# Initializes your app with your bot token and signing secret
app = App(
	token="",
	signing_secret="",
)


#Create ssl
ssl_context=ssl.create_default_context(cafile=certifi.where())


#This will be used to get the right message to react to and get pinned
time = None
ms_time = None


#Starts when a new member joins team
@app.event("team_join")
def message_hello(event, say):
	#say() sends a message to the channel where the event was triggered
	user = event["user"]["name"]
	
	text = f"*Cześć <@{user}>! Witamy w ThinkTank! :wave: Bardzo się cieszymy, że tu jesteś. :blush:*\n\n Przygotowaliśmy dla Ciebie kilka wskazówek, które pozwolą Ci lepiej odnaleźć się na tej platformie."
	
	say(text=text, channel=event["user"]["id"])

	blocks = [
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Rozpocznij samouczek"
					},
					"style": "primary",
					"value": "agree",
					"action_id": "start_button"
				}
			]
		}
	]
	say(
		blocks=blocks,
		text="Rozpocznij samouczek",
		channel=event["user"]["id"]
	)


#Starts when user write hello to samouczek
@app.message("hello")
def message_hello(message, say):
	# say() sends a message to the channel where the event was triggered
	say(f"*Cześć <@{message['user']}>! Witamy w ThinkTank! :wave: Bardzo się cieszymy, że tu jesteś. :blush:*\n\n Przygotowaliśmy dla Ciebie kilka wskazówek, które pozwolą Ci lepiej odnaleźć się na tej platformie.")
	blocks = [
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Rozpocznij samouczek"
					},
					"style": "primary",
					"value": "agree",
					"action_id": "start_button"
				}
			]
		}
	]
	say(
		blocks=blocks,
		text="Rozpocznij samouczek",
	)


#Run after Rozpocznij samouczek was clicked
@app.action("start_button")
def message_rules(client, body, say, ack):
	# say() sends a message to the channel where the event was triggered
	ack()
	if "container" in body and "message_ts" in body["container"]:
		client.chat_delete(
			channel=body["channel"]["id"],
			ts=body["container"]["message_ts"],
	    )
	say(
		"*Po pierwsze zapoznaj się z regulaminem* :disguised_face:\n"
		":one: Zakaz publikowania czy udostępniania jakichkolwiek transmisji na żywo i filmów.\n"
		":two: Prosimy nie spamować, nie duplikować postów.\n"
		":three: Nie wklejamy linków innych grup.\n"
		":four: Nie wklejamy linków polecających.\n"
		":five: Zabronione jest wystawianie ofert na sprzedaż.\n"
		":six: Reklama własnej firmy/strony/profilu tylko za zgodą administratora.\n"
		":seven: Widzisz spam lub oszustwo? REAGUJ ! -> zgłoś adminom\n\n"
	)
	blocks = [
		{
			"type": "actions",
			"elements": [
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Przejdź dalej"
					},
					"style": "primary",
					"value": "agree",
					"action_id": "reaction_button"
				}
			]
		}
	]
	say(
		blocks=blocks,
		text="Przejdź dalej"
	)


#When Przejdź dalej was clicked
@app.action("reaction_button")
def message_reaction(client, body, say, ack):
	# say() sends a message to the channel where the event was triggered
	ack()
	if "container" in body and "message_ts" in body["container"]:
		client.chat_delete(
			channel=body["channel"]["id"],
			ts=body["container"]["message_ts"],
	    )
	response = say(
		"*Zareaguj emotikonem na tę wiadomość* :thinking_face:\n"
		"Używając emotikonów możesz szybko zareagować na każdą wiadomość w Slack. "
		"Reakcji można używać w wielu celach: głosowanie, zaznaczanie wykonanych czynności, okazanie ekscytacji.\n\n"
		"Aby zareagować na wiadomość:\n"
		":one: Najedź na wiadomość, na którą chcesz zareagować.\n"
		":two: Kliknij *ikonę reakcji (Add reaction)*.\n"
		":three: Wybierz *emotikonę*, którą chcesz zareagować.\n\n"
		":information_source: *<https://get.slack.help/hc/en-us/articles/206870317-Emoji-reactions|"
		"Więcej informacji o reagowaniu emotikonem (w języku angielskim)>*"
	)

	global time
	time = response["ts"]


#When reaction is added to right message
@app.event("reaction_added")
def update_emoji(event, say):
	messagets = event["item"]["ts"]
	if messagets == time :
		say(
			":white_check_mark: "
			":tada: Gratulacje, reakcja została dodana. :tada:"
		)

		pin_message = say(
			"*Przypnij tę wiadomość* :round_pushpin:\n"
			"Ważne wiadomości i pliki mogą zostać przypięte do okienka szczegółów w kanale albo"
			" bezpośredniej wiadomości, nawet grupowej, aby ułatwić odniesienie.\n\n"
			"Aby przypiąć wiadomość:\n"
			":one: Najedź na wiadomość, którą chcesz przypiąć.\n"
			":two: Kliknij pierwszą od prawej *ikonę akcji z trzema pionowymi kropkami (More actions)*.\n"
			":three: Wybierz *Pin to channel* lub *Pin to this conversation* w wiadomości bezpośredniej.\n\n"
			":information_source: *<https://get.slack.help/hc/en-us/articles/205239997-Pinning-messages-and-files"
			"|Więcej informacji o przypinaniu wiadomości (w języku angielskim)>*"
		)

		global ms_time
		ms_time = pin_message["ts"]

		
#When pin is added to right message				
@app.event("pin_added")
def update_emoji(event, say):
	# say() sends a message to the channel where the event was triggered
	message_ts = event["item"]["message"]["ts"]
	if message_ts == ms_time :
		say(
			":white_check_mark:"
			":tada: Gratulacje, wiadomość została przypięta. :tada:"
		)
		blocks = [
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*Dodatkowe informacje* :mag:\n"
				}
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Poniżej prezentujemy screeny z kompleksowej obsługi ThinkTank.\n"
				}
			},
			{
				"type": "image",
				"title": {
					"type": "plain_text",
					"text": "Pasek boczny"
				},
				"image_url": "https://i.imgur.com/FrUuGQh.png",
				"alt_text": "sidebar viev"
			},
			{
				"type": "image",
				"title": {
					"type": "plain_text",
					"text": "Tworzenie wiadomości"
				},
				"image_url": "https://i.imgur.com/S0fLKbA.png",
				"alt_text": "message view"
			},
			{
				"type": "image",
				"title": {
					"type": "plain_text",
					"text": "Kanał"
				},
				"image_url": "https://i.imgur.com/qYniUTu.png",
				"alt_text": "channel view"
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Jeśli masz jeszcze jakieś wątpliwości, wejdź w link i obejrzyj krótki filmik instruktażowy. Jeśli to nie rozwiąże problemu, skontaktuj się z ThinkTankSupport.\n\n"
				}
			},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": ":information_source: *<https://slack.com/intl/en-pl/help/articles/360059928654-How-to-use-Slack--your-quick-start-guide|Dodatkowe informacje o Slack (języku angielskim)>*\n\n"
				}
			},
		]
		say(
			blocks=blocks
		)
		block = [
			{
				"type": "actions",
				"elements": [
					{
						"type": "button",
						"text": {
							"type": "plain_text",
							"text": "Zakończ samouczek"
						},
						"style": "primary",
						"value": "agree",
						"action_id": "finish_button"
					}
				]
			}
		]
		say(
			blocks=block,
			text="Zakończ samouczek"
		)	


#Ending the tutorial		
@app.action("finish_button")
def message_pin(client, body, say, ack):
	# say() sends a message to the channel where the event was triggered
	ack()
	if "container" in body and "message_ts" in body["container"]:
		client.chat_delete(
			channel=body["channel"]["id"],
			ts=body["container"]["message_ts"],
	   	)
	say(
		"*:tada: Gratulacje, samouczek ukończony :tada:*\n"
		"Życzymy miłego korzystania z ThinkTank :smiling_face_with_3_hearts:"
	)





# Start your app
if __name__ == "__main__":
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	logger.addHandler(logging.StreamHandler())
	app.start(port=3000)
