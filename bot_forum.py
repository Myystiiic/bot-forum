import requests
from bs4 import BeautifulSoup
import time

CHECK_INTERVAL = 60

WEBHOOK_PREZ_SCENAR_PARTOCH = "COLLE_ICI_LE_WEBHOOK_PREZ_SCENAR_PARTOCH"
WEBHOOK_DEMANDES_FOS = "COLLE_ICI_LE_WEBHOOK_DEMANDES_FOS"

TOPICS = [
    {
        "name": "Fiche terminée",
        "url": "https://veinsofrevenge.forumactif.com/t21-01-prevenir-que-ma-fiche-est-terminee",
        "webhook": "https://discord.com/api/webhooks/1500599105406369972/a7aW_2iZeAVvsnzvUhYppBQa66fA5g-mtIl0tkc_GPCFCbIK-SyWb7acZSEAV4bDSVde"
    },
    {
        "name": "Faire valider son formulaire",
        "url": "https://veinsofrevenge.forumactif.com/t19-01-faire-valider-son-formulaire",
        "webhook": "https://discord.com/api/webhooks/1500599105406369972/a7aW_2iZeAVvsnzvUhYppBQa66fA5g-mtIl0tkc_GPCFCbIK-SyWb7acZSEAV4bDSVde"
    },
    {
        "name": "Demandes de partenariats",
        "url": "https://veinsofrevenge.forumactif.com/t8-00-explications-et-codes",
        "webhook": "https://discord.com/api/webhooks/1500599105406369972/a7aW_2iZeAVvsnzvUhYppBQa66fA5g-mtIl0tkc_GPCFCbIK-SyWb7acZSEAV4bDSVde"
    },

    {
        "name": "Demande de RPs",
        "url": "https://veinsofrevenge.forumactif.com/t10-01-demande-de-rps",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Intervention MJ",
        "url": "https://veinsofrevenge.forumactif.com/t11-02-intervention-mj",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Intervention PNJ",
        "url": "https://veinsofrevenge.forumactif.com/t12-03-intervention-pnj",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Archiver ses RPs",
        "url": "https://veinsofrevenge.forumactif.com/t13-04-archiver-ses-rps",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Réclamer ses dollars",
        "url": "https://veinsofrevenge.forumactif.com/t14-05-reclamer-ses-dollars",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Boutique RP",
        "url": "https://veinsofrevenge.forumactif.com/t24-01-boutique-rp",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    },
    {
        "name": "Boutique hors RP",
        "url": "https://veinsofrevenge.forumactif.com/t25-02-boutique-hors-rp",
        "webhook": "https://discord.com/api/webhooks/1500604680412205206/1NAe_kPICVjdl9QV6vEe_mPTW75yKVgZUoX7kg6m5US5QmxAnzeSv6JHsJ8ESK0BLv0f"
    }
]

seen_ids = set()


def get_posts(topic_url):
    response = requests.get(topic_url)
    soup = BeautifulSoup(response.text, "html.parser")
    if "t12-03-intervention-pnj" in topic_url:
        print("DEBUG PNJ")
        print("URL finale :", response.url)
        print("Status :", response.status_code)
        print("Titre page :", soup.title.text.strip() if soup.title else "Pas de titre")
        print(response.text[:1000])

    posts = [
        post for post in soup.select(".post")
        if post.get("id") and post.get("id") != "0"
    ]

    result = []

    for post in posts:
        post_id = post.get("id")

        author_element = post.select_one(".postprofile-name strong, .postprofile-name")
        author = author_element.text.strip() if author_element else "Inconnu"

        result.append((post_id, author))

    return result


def send_discord(topic, author):
    data = {
        "content": (
            f"📌 Nouveau message de **{author}**\n"
            f"📍 Sujet : **{topic['name']}**\n"
            f"{topic['url']}"
        )
    }

    response = requests.post(topic["webhook"], json=data)

    print("Webhook utilisé :", topic["name"])
    print("Code Discord :", response.status_code)
    print("Réponse Discord :", response.text)


print("Surveillance lancée...")

for topic in TOPICS:
    try:
        for post_id, author in get_posts(topic["url"]):
            seen_ids.add(f"{topic['url']}#{post_id}")

        print(f"Initialisé : {topic['name']}")

    except Exception as e:
        print(f"Erreur pendant l'initialisation de {topic['name']} :", e)

print("Initialisation terminée.")


while True:
    try:
        for topic in TOPICS:
            posts = get_posts(topic["url"])

            print(f"Vérification : {topic['name']} — {len(posts)} messages trouvés")

            for post_id, author in posts:
                unique_id = f"{topic['url']}#{post_id}"

                if unique_id not in seen_ids:
                    print(f"Nouveau message détecté : {topic['name']} — {author} — ID {post_id}")
                    send_discord(topic, author)
                    seen_ids.add(unique_id)

    except Exception as e:
        print("Erreur :", e)

    time.sleep(CHECK_INTERVAL)
