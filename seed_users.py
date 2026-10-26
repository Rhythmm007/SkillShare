
from accounts.models import User
from skills.models import Skill, UserSkill

PASSWORD = "1234"

users = [
    {
        "username": "rahim_ahmed",
        "first_name": "Rahim",
        "last_name": "Ahmed",
        "email": "rahim@example.com",
        "location": "Dhaka, Bangladesh",
        "bio": "CSE student from Dhaka. I love programming and teaching Python.",
        "credits": 45,
        "teach": [
            ("Python", "Programming", "advanced"),
            ("Django", "Programming", "intermediate")
        ],
        "learn": [
            ("Graphic Design", "Design", "beginner"),
            ("English Speaking", "Language", "beginner")
        ]
    },
    {
        "username": "nusrat_jahan",
        "first_name": "Nusrat",
        "last_name": "Jahan",
        "email": "nusrat@example.com",
        "location": "Chattogram, Bangladesh",
        "bio": "Graphic designer who enjoys digital art and photography.",
        "credits": 35,
        "teach": [
            ("Graphic Design", "Design", "advanced"),
            ("Photoshop", "Design", "intermediate")
        ],
        "learn": [
            ("Python", "Programming", "beginner"),
            ("Web Development", "Programming", "beginner")
        ]
    },
    {
        "username": "tanvir_hasan",
        "first_name": "Tanvir",
        "last_name": "Hasan",
        "email": "tanvir@example.com",
        "location": "Rajshahi, Bangladesh",
        "bio": "Web developer who enjoys creating modern websites.",
        "credits": 60,
        "teach": [
            ("Web Development", "Programming", "advanced"),
            ("JavaScript", "Programming", "intermediate")
        ],
        "learn": [
            ("Django", "Programming", "beginner"),
            ("Photography", "Creative", "beginner")
        ]
    },
    {
        "username": "sadia_islam",
        "first_name": "Sadia",
        "last_name": "Islam",
        "email": "sadia@example.com",
        "location": "Sylhet, Bangladesh",
        "bio": "English tutor interested in language and communication.",
        "credits": 30,
        "teach": [
            ("English Speaking", "Language", "advanced"),
            ("Public Speaking", "Communication", "intermediate")
        ],
        "learn": [
            ("Graphic Design", "Design", "beginner"),
            ("Python", "Programming", "beginner")
        ]
    },
    {
        "username": "arif_mahmud",
        "first_name": "Arif",
        "last_name": "Mahmud",
        "email": "arif@example.com",
        "location": "Sirajganj, Bangladesh",
        "bio": "University student passionate about photography and video editing.",
        "credits": 50,
        "teach": [
            ("Photography", "Creative", "advanced"),
            ("Video Editing", "Creative", "intermediate")
        ],
        "learn": [
            ("JavaScript", "Programming", "beginner"),
            ("Public Speaking", "Communication", "beginner")
        ]
    }
]

for data in users:

    user, created = User.objects.get_or_create(
        username=data["username"],
        defaults={
            "first_name": data["first_name"],
            "last_name": data["last_name"],
            "email": data["email"],
            "location": data["location"],
            "bio": data["bio"],
            "credits": data["credits"],
            "role": "user"
        }
    )

    if created:
        user.set_password(PASSWORD)
        user.save()

    for kind in ["teach", "learn"]:
        for name, category, level in data[kind]:

            skill, _ = Skill.objects.get_or_create(
                name=name,
                defaults={"category": category}
            )

            UserSkill.objects.get_or_create(
                user=user,
                skill=skill,
                kind=kind,
                defaults={"level": level}
            )

    if created:
        print("Created:", user.username)
    else:
        print("Already exists:", user.username)

print("\nDone! Demo users are ready.")
