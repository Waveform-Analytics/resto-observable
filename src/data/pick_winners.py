import pandas as pd

df_visits_app = pd.read_csv("visits_with_users.csv", dtype={"phone": "string"})

df_app_entries = df_visits_app[["name_user", "email", "phone"]].copy()

df_app_entries["is_app_user"] = True

df_app_unique = df_app_entries.drop_duplicates(subset=["email"], keep="first")


df_paper_entries = pd.DataFrame(
    columns=["email", "name_user", "phone", "is_app_user"],
    data=[
        ["Ed Galati", None, None, False],
        ["Kristie Galati", None, None, False],
        ["Micah Vandall", None, None, False],
    ],
)

# Being explicit about column types (bc now pandas requires that)
for col in ["email", "name_user", "phone"]:
    if col in df_app_entries.columns and col in df_paper_entries.columns:
        df_app_entries[col] = df_app_entries[col].astype('object')
        df_paper_entries[col] = df_paper_entries[col].astype('object')

df_all_entries = pd.concat([df_app_entries, df_paper_entries], ignore_index=True)

# Every unique app user gets entered in a drawing for music festival tickets.
# The "magic number" is chosen by the Chamber and is used as the random seed for our
# prize drawings. Once this number is picked, the selection will be repeatable.
magic_number_for_drawing = 88434

music_fest_winner = df_app_unique.sample(n=1, random_state=magic_number_for_drawing)
raffle_winner = df_all_entries.sample(n=1, random_state=magic_number_for_drawing)

print("Announcing the music fest winner! Congratulations!\nuser name: ", music_fest_winner.iloc[0]["name_user"], "\nemail: ", music_fest_winner.iloc[0]["email"], "\nphone: ", music_fest_winner.iloc[0]["phone"], '\n---')
print("Announcing the raffle winner! Congratulations!\nuser name: ", raffle_winner.iloc[0]["name_user"], "\nemail: ", raffle_winner.iloc[0]["email"], "\nphone: ", raffle_winner.iloc[0]["phone"],)
print("---\nWinners selected on ", pd.Timestamp.now(), "using magic number", magic_number_for_drawing,)

print('pause')
