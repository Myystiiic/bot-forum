
import os
import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

STATE_FILE = Path("notifications_state.json")

WEBHOOK_ADMIN = os.environ["DISCORD_WEBHOOK_ADMIN"]
WEBHOOK_DEMANDES = os.environ["DISCORD_WEBHOOK_DEMANDES"]

TOPICS = [
    {
        "name": "Fiche terminée",
        "url": "https://veinsofrevenge.forumactif.com/t21-01-prevenir-que-ma-fiche-est-terminee",
        "webhook": WEBHOOK_ADMIN,
    },
    {
        "name": "Faire valider son formulaire",
        "url": "https://veinsofrevenge.forumactif.com/t19-01-faire-valider-son-formulaire",
        "webhook": WEBHOOK_ADMIN,
    },
    {
        "name": "Demandes de partenariats",
        "url": "https://veinsofrevenge.forumactif.com/t8-00-explications-et-codes",
        "webhook": WEBHOOK_ADMIN,
    },
    {
        "name": "Demande de RPs",
        "url": "https://veinsofrevenge.forumactif.com/t10-01-demande-de-rps",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Intervention MJ",
        "url": "https://veinsofrevenge.forumactif.com/t11-02-intervention-mj",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Intervention PNJ",
        "url": "https://veinsofrevenge.forumactif.com/t12-03-intervention-pnj",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Archiver ses RPs",
        "url": "https://veinsofrevenge.forumactif.com/t13-04-archiver-ses-rps",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Réclamer ses dollars",
        "url": "https://veinsofrevenge.forumactif.com/t14-05-reclamer-ses-dollars",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Boutique RP",
        "url": "https://veinsofrevenge.forumactif.com/t24-01-boutique-rp",
        "webhook": WEBHOOK_DEMANDES,
    },
    {
        "name": "Boutique hors RP",
        "url": "https://veinsofrevenge.forumactif.com/t25-02-boutique-hors-rp",
        "webhook": WEBHOOK_DEMANDES,
    },
]


def get_posts(topic_url):
    response = requests.get(topic_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    posts = []

    for post in soup.select(".post"):
        post_id = post.get("id")

        if not post_id or post_id == "0":
            continue

        author_element = post.select_one(
            ".postprofile-name strong, .postprofile-name"
        )
        author = (
            author_element.get_text(strip=True)
            if author_element
            else "Inconnu"
        )

        posts.append((post_id, author))

    return posts


def send_discord(topic, author):
    message = {
        "content": (
            f"📌 Nouveau message de **{author}**\n"
            f"📍 Sujet : **{topic['name']}**\n"
            f"{topic['url']}"
        ),
        "allowed_mentions": {"parse": []},
    }

    response = requests.post(
        topic["webhook"],
        json=message,
        timeout=30,
    )
    response.raise_for_status()


def load_state():
    if not STATE_FILE.exists():
        return None

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return set(json.load(file))


def save_state(seen_ids):
    temporary = STATE_FILE.with_suffix(".tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(
            sorted(seen_ids),
            file,
            ensure_ascii=False,
            indent=2,
        )

    temporary.replace(STATE_FILE)


def main():
    seen_ids = load_state()
    first_run = seen_ids is None

    if first_run:
        seen_ids = set()
        print("Première exécution : initialisation.")

    errors = []

    for topic in TOPICS:
        try:
            posts = get_posts(topic["url"])

            
if not posts:
    print(
        f"{topic['name']} : aucun message détecté "
        "(vérification HTML nécessaire)"
    )
    continue

print(f"{topic['name']} : {len(posts)} messages")


            for post_id, author in posts:
                unique_id = f"{topic['url']}#{post_id}"

                if unique_id in seen_ids:
                    continue

                if not first_run:
                    send_discord(topic, author)
                    print(f"Notification envoyée : {author}")

                seen_ids.add(unique_id)
                save_state(seen_ids)

        except Exception as error:
            errors.append(topic["name"])
            print(f"Erreur dans {topic['name']} : {error}")

    save_state(seen_ids)

    if errors:
        raise RuntimeError(
            "Vérification incomplète : " + ", ".join(errors)
        )

    print("Vérification terminée.")


if __name__ == "__main__":
    main()
