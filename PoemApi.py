import requests
import sqlalchemy as db
import pandas as pd

num_poems = int(input("How many random poems would you like to receive? ")) 
poems = [] 

while len(poems) < num_poems:
    # Make a GET request
    response = requests.get('https://poetrydb.org/random/1')

    # Parse the response data
    data = response.json()

    poem = data[0]  # Get the first/only poem in the response

    line_count = int(poem['linecount'])
    if line_count <= 20:
        poems.append(poem)

#method to make sure rank being entered is valid
def enter_rank():
    while True:
        try:
            rank = int(input("Enter the rank out of 10 for the poem: "))
            if rank < 1 or rank > 10:
                print("Invalid rank. Please enter a number between 1 and 10.")
            else:
                return rank
        except ValueError:
            print("Invalid input. Please enter a valid integer rank.")


df = pd.DataFrame()

# Iterate through the selected poems, display them, and prompt for ranking
for i, poem in enumerate(poems):
    print("\nPoem {}: ".format(i + 1))
    print("Title:", poem['title'],"\n")
    print("Author:", poem['author'])
    print("Lines:")
    for line in poem['lines']:
        print(line)
    print("Linecount:", poem['linecount'])
    rank = enter_rank()

# Create a DataFrame from the selected poems
    poem_df = pd.DataFrame({'Title': [poem['title']], 'Author': [poem['author']], 'Linecount': [poem['linecount']], 'Rank': [rank]})
    df = pd.concat([df, poem_df], ignore_index=True)

# Create an engine object
engine = db.create_engine('sqlite:///RankedAndRead.db')

# Create and send the SQL table from the DataFrame
df.to_sql('RankedPoems', con=engine, if_exists='replace', index=False)

# Function to query the poems based on user input
def query_poems(connection):
    query_choice = input("Enter query type - author/rank/lines: ")

    if query_choice == 'author':
        author_name = input("Enter author name: ")
        query = db.text("SELECT * FROM RankedPoems WHERE Author = :author")
        results = connection.execute(query, {"author": author_name}).fetchall()

    elif query_choice == 'rank':
        rank_value = int(input("Enter rank value: "))
        query = db.text("SELECT * FROM RankedPoems WHERE Rank = :rank")
        results = connection.execute(query, {"rank": rank_value}).fetchall()

    elif query_choice == 'lines':
        line_count = int(input("Enter number of lines: "))
        query = db.text("SELECT * FROM RankedPoems WHERE Linecount = :lines")
        results = connection.execute(query, {"lines": line_count}).fetchall()

    else:
        print("Invalid query type.")
        return

    # Query results
    if results:
        print("\nQuery Results:")
        for result in results:
            print("Title:", result[0])
            print("Author:", result[1])
            print("Rank:", result[3])
            print("----------------------")
    else:
        print("No results")


# Query the data based on author, rank, or number of lines
query_choice = input("Do you want to perform a query on the poems youv've read? (yes/no): ")

if query_choice.lower() == 'yes':
    with engine.connect() as connection:
        query_poems(connection)
