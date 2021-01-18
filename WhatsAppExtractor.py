import configparser
import unicodedata

config = configparser.ConfigParser()
config.read("WhatsAppExtractor.config")

# chatData
# [
#   "type",
#   "date",
#   "timestamp",
#   "from",
#   "msgData"
# ]
chatData = []

def decodeString(string):
    return unicodedata.normalize("NFKD", "".join(ch for ch in string if unicodedata.category(ch)[0]!="C"))

def changeUserName(username):
    if username == config['config']['chatNumber1']:
        name = config['config']['chatName1']
    elif username == config['config']['chatNumber2']:
        name = config['config']['chatName2']
    else:
        name = username
    return name

print("Reading messages..")

chatFile = open(config['config']['inputDir'] + "_chat.txt", "r", encoding="utf-8")
for line in chatFile:
    if "<Anhang:" in line:
        chatData.append({"type":"media", "date":str(line[2:10]), "timestamp":str(line[12:20]), "from":decodeString(str(line[22:]).split(":", 1)[0]), "msgData":decodeString(str(line[22:]).split(":", 1)[1][1:])})
    else:
        if line.startswith("["):
            chatData.append({"type":"text", "date":str(line[1:9]), "timestamp":str(line[11:19]), "from":decodeString(str(line[21:]).split(":", 1)[0]), "msgData":decodeString(str(line[21:]).split(":", 1)[1][1:])})
        else:
            chatData[len(chatData) - 1]["msgData"] += "\n" + decodeString(line)

chatFile.close()

print(str(len(chatData)) + " messages read")

print("Writing html file..")

htmlFile = open(config['config']['outputDir'] + "index.html", "a", encoding="utf-8")
htmlFile.write("<!DOCTYPE html>")
htmlFile.write("<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width, initial-scale=1'><title>WhatsApp Chat Export</title><link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css'></head>")
htmlFile.write("<body><div class='container'>")

for message in chatData:
    name = changeUserName(message["from"])

    if message["from"] != chatData[0]["from"]:
        align = "has-text-right"
    else:
        align = "has-text-left"

    if message["type"] == "text":
        htmlFile.write("<div class='box " + align + "'><article class='media'><div class='media-content'><div class='content'><p><strong>" + name + "</strong> <small>" + message["date"] + "</small> <small>" + message["timestamp"] + "</small><br>" + message["msgData"] + "</p></div></div></article></div>")
    elif message["type"] == "media":

        if "opus" in message["msgData"]:
            mediaFile = "<audio controls><source src='../in/" + message["msgData"][9:-1] + "'></audio>"
            htmlFile.write("<div class='box " + align + "'><article class='media'><div class='media-content'><div class='content'><p><strong>" + name + "</strong> <small>" + message["date"] + "</small> <small>" + message["timestamp"] + "</small><br>" + mediaFile + "</p></div></div></article></div>")
        elif "jpg" in message["msgData"] or "webp" in message["msgData"]:
            mediaFile = "<figure class='image'><img src='../in/" + message["msgData"][9:-1] + "' loading='lazy'></figure>"
            htmlFile.write("<div class='box " + align + "'><article class='media'><div class='media-content'><div class='content'><p><strong>" + name + "</strong> <small>" + message["date"] + "</small> <small>" + message["timestamp"] + "</small><br>" + mediaFile + "</p></div></div></article></div>")
        elif "mp4" in message["msgData"]:
            mediaFile = "<video controls><source src='../in/" + message["msgData"][9:-1] + "'></video>"
            htmlFile.write("<div class='box " + align + "'><article class='media'><div class='media-content'><div class='content'><p><strong>" + name + "</strong> <small>" + message["date"] + "</small> <small>" + message["timestamp"] + "</small><br>" + mediaFile + "</p></div></div></article></div>")
        else:
            #mediaFile = "<a href='../in/" + message["msgData"][9:-1] + "'>" + message["msgData"][9:-1] + "</a>"
            htmlFile.write("<div class='box " + align + "'><article class='media'><div class='media-content'><div class='content'><p><strong>" + name + "</strong> <small>" + message["date"] + "</small> <small>" + message["timestamp"] + "</small><br>Can't display file</p></div></div></article></div>")

htmlFile.write("</div></body>")
htmlFile.write("</html>")
htmlFile.close()

print("html file written")